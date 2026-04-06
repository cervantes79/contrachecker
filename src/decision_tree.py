"""
Decision Tree Router - Kurallardan otomatik hiyerarsik agac olusturur.

Kelime anlamini BILMEZ. Sadece kural yapisini kullanir:
  1. "turu" iliskileri → dogrudan agac hiyerarsisi
  2. Pattern benzerligi → agaca yerlestirme (turu yoksa)

Sorgu gelince: entity'nin dalini bul, sadece o dalda calis.
1M kural → 4 seviye → ~50 entity. O(log n).
"""

from collections import defaultdict, deque


class DecisionTreeRouter:
    def __init__(self):
        # Agac yapisi
        self._parent = {}          # entity -> parent entity
        self._children = defaultdict(set)  # entity -> set of child entities
        self._roots = set()        # Kok dugumler (parent'i olmayan)

        # Her dugumun altindaki TUM entity'ler (subtree cache)
        self._subtree = defaultdict(set)  # entity -> set of all descendants + self

        # Entity -> agactaki yer (hangi dalda)
        self._branch_root = {}     # entity -> en ust dal koku

        # Pattern-based placement icin
        self._patterns = defaultdict(set)  # entity -> set of (relation, obj)

        self._dirty = True  # Agac degisti, subtree cache yeniden hesaplanmali

    # --- Agac olusturma ---

    def add_turu_relation(self, child, parent):
        """'X turu Y' iliskisinden agac dali olustur."""
        child = child.lower()
        parent = parent.lower()

        # Eski parent varsa kaldir
        if child in self._parent:
            old_parent = self._parent[child]
            self._children[old_parent].discard(child)

        self._parent[child] = parent
        self._children[parent].add(child)

        # Root'lari guncelle
        self._roots.discard(child)
        if parent not in self._parent:
            self._roots.add(parent)

        self._dirty = True

    def add_pattern(self, entity, relation, obj):
        """Entity'nin pattern profilini guncelle (turu disindaki iliskiler)."""
        entity = entity.lower()
        self._patterns[entity].add((relation.lower(), obj.lower()))

    def place_by_pattern(self, entity, min_similarity=0.3):
        """turu iliskisi olmayan entity'yi pattern benzerligine gore agaca yerlestir."""
        entity = entity.lower()
        if entity in self._parent:
            return  # Zaten agacta

        entity_pattern = self._patterns.get(entity, set())
        if not entity_pattern:
            return  # Pattern yok, yerlestiremeyiz

        # En benzer agac dugumunu bul
        best_match = None
        best_sim = 0.0

        for node in list(self._parent.keys()) + list(self._roots):
            node_pattern = self._patterns.get(node, set())
            if not node_pattern:
                continue
            # Jaccard similarity
            intersection = entity_pattern & node_pattern
            union = entity_pattern | node_pattern
            sim = len(intersection) / len(union) if union else 0
            if sim > best_sim:
                best_sim = sim
                best_match = node

        if best_sim >= min_similarity and best_match is not None:
            # best_match'in parent'ina yerlestir (kardes yap)
            parent = self._parent.get(best_match)
            if parent:
                self.add_turu_relation(entity, parent)
            else:
                # best_match root ise, onun altina koy
                self.add_turu_relation(entity, best_match)

    # --- Subtree cache ---

    def _rebuild_subtree_cache(self):
        """Her dugum icin altindaki tum entity'leri hesapla."""
        if not self._dirty:
            return

        self._subtree.clear()
        self._branch_root.clear()

        # Her entity kendi subtree'sine dahil
        all_entities = set(self._parent.keys()) | self._roots
        for entity in all_entities:
            self._subtree[entity].add(entity)

        # Yapraklardan koklere dogru propagate et
        # Once derinlikleri hesapla
        depth = {}
        for entity in all_entities:
            d = 0
            current = entity
            while current in self._parent:
                current = self._parent[current]
                d += 1
            depth[entity] = d

        # En derin dugumlerden baslayarak subtree'leri birlestir
        for entity in sorted(all_entities, key=lambda e: depth.get(e, 0), reverse=True):
            if entity in self._parent:
                parent = self._parent[entity]
                self._subtree[parent].update(self._subtree[entity])

        # Branch root: her entity'nin hangi kok dala ait oldugunu bul
        for entity in all_entities:
            current = entity
            while current in self._parent:
                current = self._parent[current]
            self._branch_root[entity] = current

        self._dirty = False

    # --- Sorgu routing ---

    def get_relevant_entities(self, terms, max_entities=500):
        """Sorgu terimleri icin ilgili entity'leri dondur.

        Strateji:
        1. Her terimin agactaki yerini bul
        2. Terimin parent'ina git (1 seviye yukari)
        3. O parent'in subtree'sindeki entity'leri al
        4. Birden fazla terim varsa, subtree'leri birlestur
        5. max_entities'den fazlaysa, en yakin dali sec
        """
        self._rebuild_subtree_cache()

        terms = [t.lower() for t in terms]
        relevant = set(terms)

        for term in terms:
            # Adim 1: Terimin agactaki yerini bul
            if term not in self._parent and term not in self._roots:
                # Agacta degil — pattern ile yerlestirmeyi dene
                self.place_by_pattern(term)
                self._rebuild_subtree_cache()

            # Adim 2: Parent'a git ve subtree'yi al
            # Once kendi subtree'si
            relevant.update(self._subtree.get(term, set()))

            # Sonra parent'in subtree'si — AMA sadece parent kucukse
            parent = self._parent.get(term)
            if parent:
                parent_size = len(self._subtree.get(parent, set()))
                if parent_size <= max_entities:
                    relevant.update(self._subtree.get(parent, set()))
                else:
                    # Parent cok buyuk — sadece kardes dallari ekle, parent'in diger cocuklarini degil
                    # Yani: term'in kendi subtree'si + kardes subtree'leri (ayni parent'in cocuklari)
                    for sibling in self._children.get(parent, set()):
                        sib_size = len(self._subtree.get(sibling, set()))
                        # Sadece kucuk kardesleri ekle
                        if sib_size <= 50:
                            relevant.update(self._subtree.get(sibling, set()))

            # Adim 3: Eger hala cok az entity varsa (< 5), bir seviye daha cik
            if len(relevant) < 5:
                parent = self._parent.get(term)
                if parent:
                    grandparent = self._parent.get(parent)
                    if grandparent:
                        gp_size = len(self._subtree.get(grandparent, set()))
                        if gp_size <= max_entities:
                            relevant.update(self._subtree.get(grandparent, set()))

        # Hard cap
        if len(relevant) > max_entities:
            # En yakin olanlari tut — terimlerle ayni parent'i paylasanlari oncelikle
            scored = []
            for entity in relevant:
                dist = self._distance_to_any_term(entity, terms)
                scored.append((dist, entity))
            scored.sort()
            relevant = set(e for _, e in scored[:max_entities])
            relevant.update(terms)  # Terimlerin kendisi her zaman dahil

        return relevant

    def _distance_to_any_term(self, entity, terms):
        """Entity'nin herhangi bir terime olan agac mesafesi."""
        min_dist = 999
        for term in terms:
            dist = self._tree_distance(entity, term)
            min_dist = min(min_dist, dist)
        return min_dist

    def _tree_distance(self, a, b):
        """Iki entity arasindaki agac mesafesi (LCA uzerinden)."""
        # a'nin atalari
        ancestors_a = {}
        current = a
        depth = 0
        while current:
            ancestors_a[current] = depth
            current = self._parent.get(current)
            depth += 1

        # b'den yukari cikarken ilk kesisimi bul
        current = b
        depth = 0
        while current:
            if current in ancestors_a:
                return ancestors_a[current] + depth
            current = self._parent.get(current)
            depth += 1

        return 999  # Farkli dallarda, baglanti yok

    # --- Bilgi ---

    def get_tree_depth(self):
        """Agacin maksimum derinligi."""
        if not self._parent:
            return 0
        max_depth = 0
        for entity in self._parent:
            d = 0
            current = entity
            while current in self._parent:
                current = self._parent[current]
                d += 1
            max_depth = max(max_depth, d)
        return max_depth

    def get_branch_count(self):
        """Kac ana dal var (root sayisi)."""
        self._rebuild_subtree_cache()
        return len(self._roots)

    def get_node_count(self):
        """Agactaki toplam dugum sayisi."""
        return len(set(self._parent.keys()) | self._roots)

    def get_branch_sizes(self):
        """Her dalın boyutu."""
        self._rebuild_subtree_cache()
        return {root: len(self._subtree[root]) for root in self._roots}

    def __repr__(self):
        self._rebuild_subtree_cache()
        lines = [f"DecisionTree: {self.get_node_count()} node, {len(self._roots)} root, depth={self.get_tree_depth()}"]
        for root in sorted(self._roots):
            size = len(self._subtree[root])
            children = sorted(self._children[root])
            lines.append(f"  [{root}] ({size} node): {', '.join(children[:5])}{'...' if len(children) > 5 else ''}")
        return "\n".join(lines)

    def print_tree(self, max_depth=3):
        """Agaci gorsel olarak yazdir."""
        self._rebuild_subtree_cache()
        for root in sorted(self._roots):
            self._print_node(root, "", True, 0, max_depth)

    def _print_node(self, node, prefix, is_last, depth, max_depth):
        connector = "+--" if is_last else "|--"
        subtree_size = len(self._subtree.get(node, set()))
        print(f"{prefix}{connector}{node} ({subtree_size})")

        if depth >= max_depth:
            children = sorted(self._children.get(node, set()))
            if children:
                new_prefix = prefix + ("    " if is_last else "|")
                print(f"{new_prefix}+--... ({len(children)} alt dal)")
            return

        children = sorted(self._children.get(node, set()))
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1)
            new_prefix = prefix + ("    " if is_last else "|")
            self._print_node(child, new_prefix, is_child_last, depth + 1, max_depth)
