"""
ChainOfMeaning v3 - Auto-Taxonomy, Smart Gates, Rule Mass
v2'nin Prolog-tarzi zincirleme ve kalitim mantigi üzerine:
  1. Rule mass: Tekrarlanan kurallar agirlik kazanir, unutulmaya direnir.
  2. Smart forget_gate: Destek sayisi + mass ile direnc hesaplar.
  3. Dolayli celiski tespiti: Zincir uzerinden celiski bulur.
  4. Taxonomy entegrasyonu: Entity profilleri ve otomatik kümeleme.
"""

from collections import defaultdict, deque
from src.taxonomy import Taxonomy


class Rule:
    def __init__(self, subject, relation, obj, confidence=1.0, source=None):
        self.subject = subject.lower()
        self.relation = relation.lower()
        self.obj = obj.lower()
        self.confidence = confidence
        self.source = source or "direct"
        self.mass = 1

    def __repr__(self):
        return f"[{self.confidence:.1f}|m{self.mass}] {self.subject} --{self.relation}--> {self.obj}"

    def matches_topic(self, other):
        return self.subject == other.subject and self.relation == other.relation

    def contradicts(self, other):
        return self.matches_topic(other) and self.obj != other.obj


class RuleEngineV3:
    def __init__(self):
        self.state = []
        self.history = []
        self._by_subject = defaultdict(list)
        self._by_obj = defaultdict(list)
        self._max_depth = 10
        self.taxonomy = Taxonomy(similarity_threshold=0.3)

    # --- Support counting ---

    def _count_support(self, rule):
        """Count how many other rules support this belief.
        Sources of support:
          1. Same-subject rules (other properties of same entity)
          2. Rules that chain into this rule (X -> rule.subject)
          3. Cluster siblings with same pattern (relation, obj)
        """
        support = 0

        # 1. Same-subject rules (other properties of same entity)
        for r in self._by_subject.get(rule.subject, []):
            if r is not rule and r.confidence >= 0.2:
                support += 1

        # 2. Rules that chain into this rule (something -> rule.subject)
        for r in self._by_obj.get(rule.subject, []):
            if r is not rule and r.confidence >= 0.2:
                support += 1

        # 3. Cluster siblings with same (relation, obj) pattern
        cluster_members = self.taxonomy.get_cluster_members(rule.subject)
        for member in cluster_members:
            if member == rule.subject:
                continue
            for r in self._by_subject.get(member, []):
                if r.relation == rule.relation and r.obj == rule.obj and r.confidence >= 0.2:
                    support += 1

        return support

    # --- Smart forget_gate ---

    def forget_gate(self, new_rule):
        """Support-aware forgetting. Decay = resistance / (resistance + new_mass)
        where resistance = existing_mass + support_count."""
        forgotten = []
        for existing in self.state:
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
        return forgotten

    # --- Input gate with mass reinforcement ---

    def input_gate(self, new_rule):
        integrated = []
        for existing in self.state:
            if (
                existing.subject == new_rule.subject
                and existing.relation == new_rule.relation
                and existing.obj == new_rule.obj
            ):
                old_conf = existing.confidence
                old_mass = existing.mass
                existing.confidence = min(1.0, existing.confidence + 0.2)
                existing.mass += 1
                integrated.append(
                    f"  INPUT: '{existing}' guclendi ({old_conf:.2f} -> {existing.confidence:.2f}, "
                    f"mass: {old_mass} -> {existing.mass})"
                )
                return integrated
        self.state.append(new_rule)
        self._by_subject[new_rule.subject].append(new_rule)
        self._by_obj[new_rule.obj].append(new_rule)
        integrated.append(f"  INPUT: Yeni kural eklendi -> '{new_rule}'")
        return integrated

    # --- Indirect contradiction detection ---

    def _detect_indirect_contradictions(self, new_rule):
        """Check if new_rule indirectly contradicts existing rules through chains.
        Example: 'kafein etki zararli' arrives, 'kahve etki saglikli' exists,
        and there's a path kahve -> kafein (via kahve icerir kafein).
        If same relation but different obj -> indirect contradiction."""
        indirect_hits = []

        # For each existing rule with the same relation but different obj
        for existing in self.state:
            if existing.relation != new_rule.relation:
                continue
            if existing.obj == new_rule.obj:
                continue
            if existing.subject == new_rule.subject:
                continue  # Direct contradiction handled by forget_gate
            if existing.confidence < 0.2:
                continue

            # Check if there's a path from existing.subject to new_rule.subject
            path = self._find_path(existing.subject, new_rule.subject)
            if path:
                # Indirect contradiction found!
                # Apply gentle decay to existing rule
                old_conf = existing.confidence
                decay = 0.85  # Gentle decay for indirect contradiction
                existing.confidence *= decay
                indirect_hits.append(
                    f"  INDIRECT: '{existing}' dolayli celiski "
                    f"(zincir: {' -> '.join(path)}, yeni: {new_rule}) "
                    f"({old_conf:.2f} -> {existing.confidence:.2f})"
                )

        return indirect_hits

    def _find_path(self, start, target, max_depth=None):
        """BFS to find any path from start to target through rule chains."""
        if max_depth is None:
            max_depth = min(self._max_depth, 6)  # Limit for performance
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

    # --- Bridge contradiction detection ---

    def _detect_bridge_contradictions(self, new_rule):
        """After a new rule is added, check if it creates a bridge between
        existing rules that are now indirectly contradictory.
        Example: 'kahve icerir kafein' is added, connecting
        'kahve etki saglikli' and 'kafein etki zararli'."""
        bridge_hits = []

        # The new rule connects new_rule.subject -> new_rule.obj
        # Check: are there rules about new_rule.subject and rules about new_rule.obj
        # that share a relation but have different objects?
        for rule_a in self._by_subject.get(new_rule.subject, []):
            if rule_a is new_rule:
                continue
            if rule_a.confidence < 0.2:
                continue
            for rule_b in self.state:
                if rule_b.confidence < 0.2:
                    continue
                if rule_b.subject == rule_a.subject:
                    continue
                if rule_b.relation != rule_a.relation:
                    continue
                if rule_b.obj == rule_a.obj:
                    continue
                # rule_a and rule_b have same relation, different obj, different subject
                # Check if there's a path from rule_a.subject to rule_b.subject through the new bridge
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

        return bridge_hits

    # --- Ingest ---

    def ingest(self, new_rule):
        forget_log = self.forget_gate(new_rule)
        indirect_log = self._detect_indirect_contradictions(new_rule)
        input_log = self.input_gate(new_rule)

        # After insertion, check if the new rule bridges existing contradictions
        bridge_log = self._detect_bridge_contradictions(new_rule)

        # Clean dead rules
        dead = [r for r in self.state if r.confidence < 0.1]
        for d in dead:
            self.state.remove(d)
            if d in self._by_subject.get(d.subject, []):
                self._by_subject[d.subject].remove(d)
            if d in self._by_obj.get(d.obj, []):
                self._by_obj[d.obj].remove(d)

        # Update taxonomy
        self.taxonomy.update_profile(new_rule.subject, new_rule.relation, new_rule.obj)
        self.taxonomy.recluster_entity(new_rule.subject)

    # --- Inheritance: resolve parent types via "turu" ---

    def _resolve_subject(self, entity):
        """Follow 'turu' chains upward: elma -> meyve -> yiyecek -> ..."""
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
        """For compound terms like 'yesil elma', also check if any token
        is a known subject with 'turu' relationships."""
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

    # --- Forward chaining: BFS from a start node ---

    def _find_chains(self, start, max_depth=None):
        """BFS forward: follow rules from start through obj -> subject links."""
        if max_depth is None:
            max_depth = self._max_depth
        chains = []
        queue = deque([(start, [start], 1.0)])
        visited_paths = set()

        while queue:
            current, path, conf = queue.popleft()
            if len(path) - 1 >= max_depth:
                continue

            for rule in self._by_subject.get(current, []):
                if rule.confidence < 0.2:
                    continue
                next_node = rule.obj
                if next_node in path:
                    continue
                new_path = path + [next_node]
                new_conf = conf * rule.confidence
                path_key = tuple(new_path)
                if path_key not in visited_paths:
                    visited_paths.add(path_key)
                    chains.append((new_path, new_conf))
                    queue.append((next_node, new_path, new_conf))

        return chains

    # --- Backward chaining: BFS backward from a target node ---

    def _find_chains_backward(self, target, max_depth=None):
        """BFS backward: trace rules backward from target."""
        if max_depth is None:
            max_depth = self._max_depth
        chains = []
        queue = deque([(target, [target], 1.0)])
        visited_paths = set()

        while queue:
            current, path, conf = queue.popleft()
            if len(path) - 1 >= max_depth:
                continue

            for rule in self._by_obj.get(current, []):
                if rule.confidence < 0.2:
                    continue
                prev_node = rule.subject
                if prev_node in path:
                    continue
                new_path = [prev_node] + path
                new_conf = conf * rule.confidence
                path_key = tuple(new_path)
                if path_key not in visited_paths:
                    visited_paths.add(path_key)
                    chains.append((new_path, new_conf))
                    queue.append((prev_node, new_path, new_conf))

        return chains

    # --- Query ---

    def query(self, question, terms):
        terms = [t.lower() for t in terms]
        conclusions = []
        seen_chains = set()

        # Adaptive depth for large state sizes
        effective_depth = self._max_depth
        if len(self.state) > 500:
            effective_depth = min(self._max_depth, 5)

        # 1. Direct rules matching any term
        for rule in self.state:
            if rule.confidence < 0.2:
                continue
            if rule.subject in terms or rule.obj in terms:
                conclusions.append({
                    "type": "direct",
                    "rule": rule,
                    "confidence": rule.confidence,
                })

        # 2. Forward chaining from each term
        for term in terms:
            for path, conf in self._find_chains(term, max_depth=effective_depth):
                chain_str = " -> ".join(path)
                if chain_str not in seen_chains and len(path) > 2:
                    seen_chains.add(chain_str)
                    conclusions.append({
                        "type": "chained",
                        "chain": chain_str,
                        "confidence": conf,
                    })

        # 3. Backward chaining to each term
        for term in terms:
            for path, conf in self._find_chains_backward(term, max_depth=effective_depth):
                chain_str = " -> ".join(path)
                if chain_str not in seen_chains and len(path) > 2:
                    seen_chains.add(chain_str)
                    conclusions.append({
                        "type": "chained",
                        "chain": chain_str,
                        "confidence": conf,
                    })

        # 4. Inheritance
        for term in terms:
            parents = self._resolve_subject_with_substring(term)
            for parent, parent_conf in parents:
                for rule in self._by_subject.get(parent, []):
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

        # 5. Cross-term chain connections
        if len(terms) >= 2:
            term_set = set(terms)
            for term in terms:
                for path, conf in self._find_chains(term, max_depth=effective_depth):
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
        return conclusions if conclusions else None

    def _build_type_chain(self, entity, target_parent):
        """Build the path from entity to target_parent through 'turu' links."""
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
        """BFS to find a path from start to target following 'turu' relationships."""
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
