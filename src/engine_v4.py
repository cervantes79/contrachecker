"""
ChainOfMeaning v4 - SQLite Persistent Engine
v3'un tum ozelliklerini icerirken SQLite ile kalici depolama ekler.

Mimari:
  - SQLite: kalicilik katmani (program kapansa bile kurallar korunur)
  - RAM indeksleri: hiz katmani (sorgu performansi v3 ile ayni)
  - Write-through: her islem hem RAM'e hem SQLite'a yazilir
  - bulk_load(): 1M+ kural icin hizli yukleme (gate islemi atlanir)

Yeni ozellikler:
  - db_path parametresi ile dosya bazli kalicilik
  - save() / load() metotlari
  - bulk_load() ile toplu kural yukleme
  - Istatistik raporlama
"""

from collections import defaultdict, deque
from src.taxonomy import Taxonomy
from src.storage import RuleStore
from src.decision_tree import DecisionTreeRouter


class Rule:
    """Hafif kural nesnesi - RAM indekslerinde tutulur."""
    __slots__ = ['id', 'subject', 'relation', 'obj', 'confidence', 'source', 'mass']

    def __init__(self, subject, relation, obj, confidence=1.0, source=None, mass=1, rule_id=None):
        self.id = rule_id
        self.subject = subject.lower()
        self.relation = relation.lower()
        self.obj = obj.lower()
        self.confidence = confidence
        self.source = source or "direct"
        self.mass = mass

    def __repr__(self):
        return f"[{self.confidence:.1f}|m{self.mass}] {self.subject} --{self.relation}--> {self.obj}"

    def matches_topic(self, other):
        return self.subject == other.subject and self.relation == other.relation

    def contradicts(self, other):
        return self.matches_topic(other) and self.obj != other.obj


class RuleEngineV4:
    def __init__(self, db_path=":memory:", taxonomy_threshold=0.3):
        """
        db_path=":memory:" -> RAM-only (test icin)
        db_path="brain.db"  -> dosyaya kalici kayit
        """
        self.store = RuleStore(db_path)
        self.db_path = db_path
        self.state = []  # Tum Rule nesneleri
        self._by_subject = defaultdict(list)
        self._by_obj = defaultdict(list)
        self._by_subject_relation = defaultdict(list)
        self._by_relation = defaultdict(list)
        self._by_domain = defaultdict(set)  # domain -> set of entity names
        self._entity_domains = defaultdict(set)  # entity -> set of domain names
        self._max_depth = 10
        self.taxonomy = Taxonomy(similarity_threshold=taxonomy_threshold)
        self.decision_tree = DecisionTreeRouter()

        # Eger veritabaninda mevcut kurallar varsa, yukle
        existing = self.store.count()
        if existing > 0:
            self._load_from_store()

    def _load_from_store(self):
        """SQLite'dan RAM indekslerine yukle."""
        rows = self.store.load_all_rules()
        for row in rows:
            rule_id, subject, relation, obj, confidence, mass, source = row
            rule = Rule(subject, relation, obj, confidence, source, mass, rule_id)
            self.state.append(rule)
            self._by_subject[rule.subject].append(rule)
            self._by_obj[rule.obj].append(rule)
            key = (rule.subject, rule.relation)
            self._by_subject_relation[key].append(rule)
            self._by_relation[rule.relation].append(rule)
            # Domain indeksi
            if rule.source and rule.source != "direct":
                self._by_domain[rule.source].add(rule.subject)
                self._by_domain[rule.source].add(rule.obj)
                self._entity_domains[rule.subject].add(rule.source)
                self._entity_domains[rule.obj].add(rule.source)
            # Decision tree
            if rule.relation == "turu":
                self.decision_tree.add_turu_relation(rule.subject, rule.obj)
            else:
                self.decision_tree.add_pattern(rule.subject, rule.relation, rule.obj)

        # Taxonomy profillerini yukle
        profiles = self.store.load_all_profiles()
        for entity, relation, obj in profiles:
            self.taxonomy.update_profile(entity, relation, obj)

        # Cluster atamalarini yukle
        clusters = self.store.load_all_clusters()
        for entity, cluster_id in clusters:
            self.taxonomy._entity_cluster[entity] = cluster_id
            self.taxonomy._clusters[cluster_id].add(entity)
            if cluster_id >= self.taxonomy._next_cluster_id:
                self.taxonomy._next_cluster_id = cluster_id + 1

    # --- Support counting (v3'den) ---

    def _count_support(self, rule):
        """Bu kurali destekleyen diger kural sayisi."""
        support = 0

        # 1. Ayni subject'e sahip diger kurallar
        for r in self._by_subject.get(rule.subject, []):
            if r is not rule and r.confidence >= 0.2:
                support += 1

        # 2. Bu kurala zincirlenen kurallar (sey -> rule.subject)
        for r in self._by_obj.get(rule.subject, []):
            if r is not rule and r.confidence >= 0.2:
                support += 1

        # 3. Ayni clusterdaki kardesler
        cluster_members = self.taxonomy.get_cluster_members(rule.subject)
        for member in cluster_members:
            if member == rule.subject:
                continue
            for r in self._by_subject.get(member, []):
                if r.relation == rule.relation and r.obj == rule.obj and r.confidence >= 0.2:
                    support += 1

        return support

    # --- Smart forget_gate (v3'den) ---

    def forget_gate(self, new_rule):
        """Destek-duyarli unutma. Decay = resistance / (resistance + new_mass)"""
        forgotten = []
        key = (new_rule.subject, new_rule.relation)
        for existing in self._by_subject_relation.get(key, []):
            if existing.contradicts(new_rule):
                support = self._count_support(existing)
                resistance = existing.mass + support
                decay = resistance / (resistance + new_rule.mass)
                old_conf = existing.confidence
                existing.confidence *= decay
                forgotten.append(
                    f"  FORGET: '{existing}' guven dustu ({old_conf:.2f} -> {existing.confidence:.2f}) "
                    f"[mass={existing.mass}, support={support}, decay={decay:.2f}]"
                )
                # SQLite'a da yaz
                if existing.id is not None:
                    self.store.update_confidence(existing.id, existing.confidence)
        return forgotten

    # --- Input gate with mass reinforcement (v3'den) ---

    def input_gate(self, new_rule):
        integrated = []
        key = (new_rule.subject, new_rule.relation)
        for existing in self._by_subject_relation.get(key, []):
            if existing.obj == new_rule.obj:
                old_conf = existing.confidence
                old_mass = existing.mass
                existing.confidence = min(1.0, existing.confidence + 0.2)
                existing.mass += 1
                integrated.append(
                    f"  INPUT: '{existing}' guclendi ({old_conf:.2f} -> {existing.confidence:.2f}, "
                    f"mass: {old_mass} -> {existing.mass})"
                )
                # SQLite'a da yaz
                if existing.id is not None:
                    self.store.reinforce(existing.id, 0.2)
                return integrated

        # Yeni kural - once SQLite'a yaz, id al
        rule_id = self.store.insert_rule(
            new_rule.subject, new_rule.relation, new_rule.obj,
            new_rule.confidence, new_rule.mass, new_rule.source
        )
        new_rule.id = rule_id

        self.state.append(new_rule)
        self._by_subject[new_rule.subject].append(new_rule)
        self._by_obj[new_rule.obj].append(new_rule)
        self._by_subject_relation[key].append(new_rule)
        self._by_relation[new_rule.relation].append(new_rule)
        integrated.append(f"  INPUT: Yeni kural eklendi -> '{new_rule}'")
        return integrated

    # --- Indirect contradiction detection (v3'den) ---

    def _detect_indirect_contradictions(self, new_rule):
        """Zincir uzerinden dolayli celiski tespiti."""
        indirect_hits = []

        same_rel_rules = self._by_relation.get(new_rule.relation, [])
        if not same_rel_rules:
            return indirect_hits

        max_depth = min(self._max_depth, 6)
        can_reach = set()
        queue = deque([(new_rule.subject, 0)])
        visited = {new_rule.subject}
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for rule in self._by_obj.get(current, []):
                if rule.confidence < 0.2:
                    continue
                prev_node = rule.subject
                if prev_node not in visited:
                    visited.add(prev_node)
                    can_reach.add(prev_node)
                    queue.append((prev_node, depth + 1))

        if not can_reach:
            return indirect_hits

        for existing in same_rel_rules:
            if existing.subject not in can_reach:
                continue
            if existing.obj == new_rule.obj:
                continue
            if existing.subject == new_rule.subject:
                continue
            if existing.confidence < 0.2:
                continue

            path = self._find_path(existing.subject, new_rule.subject)
            if path:
                old_conf = existing.confidence
                decay = 0.85
                existing.confidence *= decay
                indirect_hits.append(
                    f"  INDIRECT: '{existing}' dolayli celiski "
                    f"(zincir: {' -> '.join(path)}, yeni: {new_rule}) "
                    f"({old_conf:.2f} -> {existing.confidence:.2f})"
                )
                if existing.id is not None:
                    self.store.update_confidence(existing.id, existing.confidence)

        return indirect_hits

    def _find_path(self, start, target, max_depth=None):
        """BFS ile start'tan target'a yol bul."""
        if max_depth is None:
            max_depth = min(self._max_depth, 6)
        if start == target:
            return [start]
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            current, path = queue.popleft()
            if len(path) - 1 >= max_depth:
                continue
            for rule in self._by_subject.get(current, []):
                if rule.confidence < 0.2:
                    continue
                next_node = rule.obj
                if next_node == target:
                    return path + [next_node]
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        return None

    # --- Bridge contradiction detection (v3'den) ---

    def _detect_bridge_contradictions(self, new_rule):
        """Yeni kural mevcut celiski kopruleri olusturuyor mu?"""
        bridge_hits = []

        rules_a = self._by_subject.get(new_rule.subject, [])
        if not rules_a:
            return bridge_hits

        rule_a_relations = set()
        for rule_a in rules_a:
            if rule_a is not new_rule and rule_a.confidence >= 0.2:
                rule_a_relations.add(rule_a.relation)
        if not rule_a_relations:
            return bridge_hits

        max_depth = min(self._max_depth, 6)
        reachable = set()
        queue = deque([(new_rule.subject, 0)])
        visited = {new_rule.subject}
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for rule in self._by_subject.get(current, []):
                if rule.confidence < 0.2:
                    continue
                next_node = rule.obj
                if next_node not in visited:
                    visited.add(next_node)
                    reachable.add(next_node)
                    queue.append((next_node, depth + 1))

        if not reachable:
            return bridge_hits

        for rule_a in rules_a:
            if rule_a is new_rule:
                continue
            if rule_a.confidence < 0.2:
                continue
            for subj in reachable:
                for rule_b in self._by_subject.get(subj, []):
                    if rule_b.relation != rule_a.relation:
                        continue
                    if rule_b.confidence < 0.2:
                        continue
                    if rule_b.subject == rule_a.subject:
                        continue
                    if rule_b.obj == rule_a.obj:
                        continue
                    path = self._find_path(rule_a.subject, rule_b.subject)
                    if path:
                        old_conf = rule_a.confidence
                        decay = 0.85
                        rule_a.confidence *= decay
                        bridge_hits.append(
                            f"  BRIDGE: '{rule_a}' dolayli celiski (kopru: {new_rule}, "
                            f"zincir: {' -> '.join(path)}, celisen: {rule_b}) "
                            f"({old_conf:.2f} -> {rule_a.confidence:.2f})"
                        )
                        if rule_a.id is not None:
                            self.store.update_confidence(rule_a.id, rule_a.confidence)

        return bridge_hits

    # --- Ingest (v3 + SQLite write-through) ---

    def ingest(self, new_rule):
        """Kural isle: forget -> indirect -> input -> bridge -> cleanup -> taxonomy"""
        forget_log = self.forget_gate(new_rule)
        indirect_log = self._detect_indirect_contradictions(new_rule)
        input_log = self.input_gate(new_rule)

        bridge_log = self._detect_bridge_contradictions(new_rule)

        # Olu kurallari temizle
        dead = [r for r in self.state if r.confidence < 0.1]
        if dead:
            dead_set = set(id(d) for d in dead)
            self.state = [r for r in self.state if id(r) not in dead_set]
            for d in dead:
                subj_list = self._by_subject.get(d.subject)
                if subj_list:
                    self._by_subject[d.subject] = [r for r in subj_list if r is not d]
                obj_list = self._by_obj.get(d.obj)
                if obj_list:
                    self._by_obj[d.obj] = [r for r in obj_list if r is not d]
                key = (d.subject, d.relation)
                sr_list = self._by_subject_relation.get(key)
                if sr_list:
                    self._by_subject_relation[key] = [r for r in sr_list if r is not d]
                rel_list = self._by_relation.get(d.relation)
                if rel_list:
                    self._by_relation[d.relation] = [r for r in rel_list if r is not d]

            # SQLite'dan da sil
            self.store.delete_dead(0.1)

        # Taxonomy guncelle
        self.taxonomy.update_profile(new_rule.subject, new_rule.relation, new_rule.obj)
        self.taxonomy.recluster_entity(new_rule.subject)

        # Taxonomy'yi SQLite'a kaydet
        self.store.save_profile(new_rule.subject, new_rule.relation, new_rule.obj)

    # --- Bulk load (1M kural icin - gate islemleri atlanir) ---

    def bulk_load(self, rules_list, source="bulk", batch_size=50000, skip_taxonomy=False):
        """
        Cok sayida kurali hizlica yukle. Gate islemleri ATLANIR.
        rules_list = [(subject, relation, obj), ...] veya
                     [(subject, relation, obj, confidence, mass, source), ...]

        Strateji:
          1. Toplu SQL insert (batch'ler halinde)
          2. RAM indekslerini tek seferde kur
          3. Taxonomy'yi opsiyonel olarak guncelle

        NOT: Bu metot celiski tespiti YAPMAZ. Cekirdek kurallar icin ingest() kullan.
        """
        total = len(rules_list)
        loaded = 0

        # Kural formatini kontrol et ve normalize et
        full_format = len(rules_list[0]) == 6 if rules_list else False

        for i in range(0, total, batch_size):
            batch = rules_list[i:i + batch_size]

            if full_format:
                # (subject, relation, obj, confidence, mass, source)
                normalized = [(s.lower(), r.lower(), o.lower(), c, m, src)
                              for s, r, o, c, m, src in batch]
                self.store.bulk_insert_full(normalized)
            else:
                # (subject, relation, obj)
                normalized = [(s.lower(), r.lower(), o.lower()) for s, r, o in batch]
                self.store.bulk_insert(normalized)

            loaded += len(batch)

        # Simdi SQLite'dan RAM'e yukle (indeksleri kur)
        self._rebuild_indexes()

        # Taxonomy guncelle (buyuk veri setlerinde opsiyonel)
        if not skip_taxonomy:
            self._rebuild_taxonomy()

        return loaded

    def _rebuild_indexes(self):
        """RAM indekslerini SQLite'dan tamamen yeniden kur.
        Buyuk veri setleri icin cursor iterator kullanir (peak RAM azaltir)."""
        self.state.clear()
        self._by_subject.clear()
        self._by_obj.clear()
        self._by_subject_relation.clear()
        self._by_relation.clear()
        self._by_domain.clear()
        self._entity_domains.clear()
        self.decision_tree = DecisionTreeRouter()

        cursor = self.store.conn.execute(
            "SELECT id, subject, relation, obj, confidence, mass, source FROM rules WHERE confidence >= 0.1"
        )
        batch_size = 10000
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                rule_id, subject, relation, obj, confidence, mass, source = row
                rule = Rule(subject, relation, obj, confidence, source, mass, rule_id)
                self.state.append(rule)
                self._by_subject[rule.subject].append(rule)
                self._by_obj[rule.obj].append(rule)
                key = (rule.subject, rule.relation)
                self._by_subject_relation[key].append(rule)
                self._by_relation[rule.relation].append(rule)
                # Domain indeksi
                if source and source != "direct" and source != "bulk":
                    self._by_domain[source].add(subject)
                    self._by_domain[source].add(obj)
                    self._entity_domains[subject].add(source)
                    self._entity_domains[obj].add(source)
                # Decision tree: turu iliskileri agac olusturur
                if relation == "turu":
                    self.decision_tree.add_turu_relation(subject, obj)
                else:
                    self.decision_tree.add_pattern(subject, relation, obj)

    def _rebuild_taxonomy(self):
        """Taxonomy'yi tum kurallardan yeniden kur."""
        for rule in self.state:
            self.taxonomy.update_profile(rule.subject, rule.relation, rule.obj)

        # Profilleri SQLite'a kaydet (toplu)
        profiles = []
        for entity, patterns in self.taxonomy._profiles.items():
            for relation, obj in patterns:
                profiles.append((entity, relation, obj))
        if profiles:
            self.store.save_profiles_bulk(profiles)

        # Clustering'i toplu yap - sadece benzersiz subject'ler icin
        unique_subjects = set(r.subject for r in self.state)
        for subj in unique_subjects:
            self.taxonomy.recluster_entity(subj)

    # --- Inheritance (v3'den) ---

    def _resolve_subject(self, entity):
        """'turu' zincirlerini takip et: elma -> meyve -> yiyecek -> ..."""
        parents = []
        visited = set()
        queue = deque([entity])
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for rule in self._by_subject.get(current, []):
                if rule.relation == "turu" and rule.confidence >= 0.2:
                    parents.append((rule.obj, rule.confidence))
                    queue.append(rule.obj)
        return parents

    def _resolve_subject_with_substring(self, entity):
        """Bilesik terimler icin: 'yesil elma' -> 'elma' alt kelimelerini kontrol et."""
        parents = self._resolve_subject(entity)
        if not parents:
            tokens = entity.split()
            if len(tokens) < 2:
                return parents
            for token in tokens:
                if token in self._by_subject:
                    token_parents = self._resolve_subject(token)
                    parents.append((token, 0.9))
                    for p, c in token_parents:
                        parents.append((p, c * 0.9))
        return parents

    # --- Decision tree + domain routing ---

    def _get_relevant_entities(self, terms):
        """Find entities relevant to query terms.

        Priority:
        1. Decision tree (turu hierarchy) — best isolation
        2. Domain index — fallback for entities not in tree
        3. Direct neighbors — last resort
        """
        terms_lower = [t.lower() for t in terms]

        # 1. Try decision tree first
        tree_entities = self.decision_tree.get_relevant_entities(terms_lower)
        if tree_entities and len(tree_entities) > len(terms_lower):
            # Tree found relevant branch — also add direct neighbors of terms
            # for non-turu relationships (etki, ozellik, etc.)
            relevant = set(tree_entities)
            for term in terms_lower:
                for rule in self._by_subject.get(term, [])[:50]:
                    relevant.add(rule.obj)
                for rule in self._by_obj.get(term, [])[:50]:
                    relevant.add(rule.subject)
            return relevant

        # 2. Fallback: domain index
        relevant_domains = set()
        for term in terms_lower:
            domains = self._entity_domains.get(term, set())
            relevant_domains.update(domains)
            for rule in self._by_subject.get(term, [])[:30]:
                relevant_domains.update(self._entity_domains.get(rule.obj, set()))

        if relevant_domains:
            relevant = set(terms_lower)
            for domain in relevant_domains:
                domain_entities = self._by_domain[domain]
                for term in terms_lower:
                    if term in domain_entities:
                        for rule in self._by_subject.get(term, [])[:50]:
                            if rule.obj in domain_entities:
                                relevant.add(rule.obj)
                        for rule in self._by_obj.get(term, [])[:50]:
                            if rule.subject in domain_entities:
                                relevant.add(rule.subject)
                for entity in list(relevant):
                    if len(relevant) > 500:
                        break
                    for rule in self._by_subject.get(entity, [])[:20]:
                        if rule.obj in domain_entities:
                            relevant.add(rule.obj)
            return relevant

        # 3. Last resort: direct neighbors
        relevant = set(terms_lower)
        for term in terms_lower:
            for rule in self._by_subject.get(term, [])[:50]:
                relevant.add(rule.obj)
            for rule in self._by_obj.get(term, [])[:50]:
                relevant.add(rule.subject)

        return relevant if len(relevant) > len(terms_lower) else None

    # --- Forward chaining ---

    def _find_chains(self, start, max_depth=None, max_nodes=5000, max_fanout=50, allowed_nodes=None):
        """Ileri zincirleme: BFS ile start'tan ilerle.
        max_nodes: BFS'in ziyaret edecegi maksimum dugum (buyuk graflarda patlama onleme)
        max_fanout: Her dugumden takip edilecek maksimum kural (en yuksek guvenli olanlar)
        allowed_nodes: If set, only explore nodes in this set."""
        if max_depth is None:
            max_depth = self._max_depth
        chains = []
        queue = deque([(start, [start], 1.0)])
        visited_nodes = {start}
        nodes_visited = 0

        while queue:
            current, path, conf = queue.popleft()
            nodes_visited += 1
            if nodes_visited > max_nodes:
                break
            if len(path) - 1 >= max_depth:
                continue

            # Fan-out limiti: en yuksek guvenli kurallari sec
            candidates = self._by_subject.get(current, [])
            if len(candidates) > max_fanout:
                candidates = sorted(candidates, key=lambda r: r.confidence, reverse=True)[:max_fanout]

            for rule in candidates:
                if rule.confidence < 0.2:
                    continue
                next_node = rule.obj
                # Skip if not in allowed nodes (cluster-aware filtering)
                if allowed_nodes is not None and next_node not in allowed_nodes:
                    continue
                if next_node in path:
                    continue
                if next_node in visited_nodes:
                    # Yine de zincir olarak kaydet ama kuyruğa ekleme
                    new_path = path + [next_node]
                    new_conf = conf * rule.confidence
                    chains.append((new_path, new_conf))
                    continue
                visited_nodes.add(next_node)
                new_path = path + [next_node]
                new_conf = conf * rule.confidence
                chains.append((new_path, new_conf))
                queue.append((next_node, new_path, new_conf))

        return chains

    # --- Backward chaining ---

    def _find_chains_backward(self, target, max_depth=None, max_nodes=5000, max_fanout=50, allowed_nodes=None):
        """Geri zincirleme: BFS ile target'a dogru gerile.
        max_nodes: BFS'in ziyaret edecegi maksimum dugum.
        max_fanout: Her dugumden takip edilecek maksimum kural.
        allowed_nodes: If set, only explore nodes in this set."""
        if max_depth is None:
            max_depth = self._max_depth
        chains = []
        queue = deque([(target, [target], 1.0)])
        visited_nodes = {target}
        nodes_visited = 0

        while queue:
            current, path, conf = queue.popleft()
            nodes_visited += 1
            if nodes_visited > max_nodes:
                break
            if len(path) - 1 >= max_depth:
                continue

            candidates = self._by_obj.get(current, [])
            if len(candidates) > max_fanout:
                candidates = sorted(candidates, key=lambda r: r.confidence, reverse=True)[:max_fanout]

            for rule in candidates:
                if rule.confidence < 0.2:
                    continue
                prev_node = rule.subject
                # Skip if not in allowed nodes (cluster-aware filtering)
                if allowed_nodes is not None and prev_node not in allowed_nodes:
                    continue
                if prev_node in path:
                    continue
                if prev_node in visited_nodes:
                    new_path = [prev_node] + path
                    new_conf = conf * rule.confidence
                    chains.append((new_path, new_conf))
                    continue
                visited_nodes.add(prev_node)
                new_path = [prev_node] + path
                new_conf = conf * rule.confidence
                chains.append((new_path, new_conf))
                queue.append((prev_node, new_path, new_conf))

        return chains

    # --- Query (v3'den, buyuk veri icin optimize) ---

    def query(self, question, terms, max_results=500):
        terms = [t.lower() for t in terms]
        conclusions = []
        seen_chains = set()

        # Buyuk veri setlerinde derinlik, BFS dugum, ve fan-out siniri
        state_size = len(self.state)
        effective_depth = self._max_depth
        max_nodes = 50000
        max_fanout = 200
        max_direct = 1000  # Dogrudan sonuc limiti (per term)
        if state_size > 500:
            effective_depth = min(self._max_depth, 5)
        if state_size > 100000:
            effective_depth = min(self._max_depth, 4)
            max_nodes = 2000
            max_fanout = 20
            max_direct = 100
        if state_size > 500000:
            effective_depth = min(self._max_depth, 3)
            max_nodes = 500
            max_fanout = 10
            max_direct = 50

        # --- Domain-aware routing ---
        # Use domain index to narrow search space BEFORE BFS
        allowed_nodes = None
        if state_size > 10000:
            relevant = self._get_relevant_entities(terms)
            if relevant is not None and len(relevant) > 0:
                allowed_nodes = relevant
                # Keep tight limits even with routing — don't inflate
                # Domain routing reduces the GRAPH, not the search depth

        # 1. Dogrudan eslesme (limitli)
        # Note: direct results are NOT filtered by allowed_nodes since they
        # are cheap O(1) lookups and we want to preserve accuracy
        for term in terms:
            count = 0
            rules_for_term = self._by_subject.get(term, [])
            # En yuksek guvenli kurallari once al
            if len(rules_for_term) > max_direct:
                rules_for_term = sorted(rules_for_term, key=lambda r: r.confidence, reverse=True)[:max_direct]
            for rule in rules_for_term:
                if rule.confidence < 0.2:
                    continue
                conclusions.append({
                    "type": "direct",
                    "rule": rule,
                    "confidence": rule.confidence,
                })
                count += 1

            count = 0
            rules_for_obj = self._by_obj.get(term, [])
            if len(rules_for_obj) > max_direct:
                rules_for_obj = sorted(rules_for_obj, key=lambda r: r.confidence, reverse=True)[:max_direct]
            for rule in rules_for_obj:
                if rule.confidence < 0.2:
                    continue
                conclusions.append({
                    "type": "direct",
                    "rule": rule,
                    "confidence": rule.confidence,
                })
                count += 1

        # 2. Ileri zincirleme
        for term in terms:
            chains = self._find_chains(term, max_depth=effective_depth, max_nodes=max_nodes,
                                       max_fanout=max_fanout, allowed_nodes=allowed_nodes)
            for path, conf in chains:
                chain_str = " -> ".join(path)
                if chain_str not in seen_chains and len(path) > 2:
                    seen_chains.add(chain_str)
                    conclusions.append({
                        "type": "chained",
                        "chain": chain_str,
                        "confidence": conf,
                    })

        # 3. Geri zincirleme
        for term in terms:
            chains = self._find_chains_backward(term, max_depth=effective_depth, max_nodes=max_nodes,
                                                max_fanout=max_fanout, allowed_nodes=allowed_nodes)
            for path, conf in chains:
                chain_str = " -> ".join(path)
                if chain_str not in seen_chains and len(path) > 2:
                    seen_chains.add(chain_str)
                    conclusions.append({
                        "type": "chained",
                        "chain": chain_str,
                        "confidence": conf,
                    })

        # 4. Kalitim
        for term in terms:
            parents = self._resolve_subject_with_substring(term)
            for parent, parent_conf in parents:
                parent_rules = self._by_subject.get(parent, [])
                if len(parent_rules) > max_direct:
                    parent_rules = sorted(parent_rules, key=lambda r: r.confidence, reverse=True)[:max_direct]
                for rule in parent_rules:
                    if rule.relation == "turu":
                        continue
                    if rule.confidence < 0.2:
                        continue
                    inherited_conf = parent_conf * rule.confidence
                    chain_str = f"{term} -> {parent} -> {rule.obj}"
                    if parent != term:
                        type_chain = self._build_type_chain(term, parent)
                        if type_chain:
                            chain_str = " -> ".join(type_chain + [rule.obj])

                    if chain_str not in seen_chains:
                        seen_chains.add(chain_str)
                        conclusions.append({
                            "type": "chained",
                            "chain": chain_str,
                            "confidence": inherited_conf,
                        })

        # 5. Terimler arasi baglanti
        # With cluster routing this is cheap, so always run it
        if len(terms) >= 2 and (allowed_nodes is not None or state_size < 500000):
            term_set = set(terms)
            for term in terms:
                for path, conf in self._find_chains(term, max_depth=effective_depth, max_nodes=max_nodes,
                                                    max_fanout=max_fanout, allowed_nodes=allowed_nodes):
                    endpoint = path[-1]
                    if endpoint in term_set and endpoint != term:
                        chain_str = " -> ".join(path)
                        if chain_str not in seen_chains:
                            seen_chains.add(chain_str)
                            conclusions.append({
                                "type": "chained",
                                "chain": chain_str,
                                "confidence": conf,
                            })

        conclusions.sort(key=lambda c: c["confidence"], reverse=True)
        # Sonuc limitesi
        if len(conclusions) > max_results:
            conclusions = conclusions[:max_results]
        return conclusions if conclusions else None

    def _build_type_chain(self, entity, target_parent):
        """Entity'den target_parent'a 'turu' yolunu kur."""
        path = self._bfs_type_path(entity, target_parent)
        if path:
            return path
        tokens = entity.split()
        for token in tokens:
            if token in self._by_subject:
                sub_path = self._bfs_type_path(token, target_parent)
                if sub_path:
                    return [entity] + sub_path[0:]
        return None

    def _bfs_type_path(self, start, target):
        """BFS ile start'tan target'a 'turu' iliskisi uzerinden yol bul."""
        if start == target:
            return [start]
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            current, path = queue.popleft()
            for rule in self._by_subject.get(current, []):
                if rule.relation == "turu" and rule.confidence >= 0.2:
                    next_node = rule.obj
                    if next_node == target:
                        return path + [next_node]
                    if next_node not in visited:
                        visited.add(next_node)
                        queue.append((next_node, path + [next_node]))
        return None

    # --- Istatistikler ---

    def stats(self):
        """Motor istatistikleri."""
        db_stats = self.store.stats()
        ram_stats = {
            "ram_rules": len(self.state),
            "ram_subjects": len(self._by_subject),
            "ram_objects": len(self._by_obj),
            "ram_relations": len(self._by_relation),
            "clusters": len(self.taxonomy.get_all_clusters()),
            "multi_member_clusters": len(self.taxonomy.get_multi_member_clusters()),
        }
        return {**db_stats, **ram_stats}

    # --- Save / Load / Close ---

    def save(self):
        """Taxonomy durumunu SQLite'a kaydet."""
        # Cluster atamalarini kaydet
        clusters = [(entity, cid) for entity, cid in self.taxonomy._entity_cluster.items()]
        if clusters:
            self.store.save_clusters_bulk(clusters)

    def close(self):
        """Kaydet ve kapat."""
        self.save()
        self.store.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __len__(self):
        return len(self.state)
