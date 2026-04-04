"""
ChainOfMeaning v2 - Prolog-Style Backward Chaining Rule Engine
BFS-tabanli ileri/geri zincirleme, tur kalitimi, guven yayilimi.
"""

from collections import defaultdict, deque


class Rule:
    def __init__(self, subject, relation, obj, confidence=1.0, source=None):
        self.subject = subject.lower()
        self.relation = relation.lower()
        self.obj = obj.lower()
        self.confidence = confidence
        self.source = source or "direct"

    def __repr__(self):
        return f"[{self.confidence:.1f}] {self.subject} --{self.relation}--> {self.obj}"

    def matches_topic(self, other):
        return self.subject == other.subject and self.relation == other.relation

    def contradicts(self, other):
        return self.matches_topic(other) and self.obj != other.obj


class RuleEngineV2:
    def __init__(self):
        self.state = []
        self.history = []
        self._by_subject = defaultdict(list)
        self._by_obj = defaultdict(list)
        self._max_depth = 10

    # --- Gates (identical to v1) ---

    def forget_gate(self, new_rule):
        forgotten = []
        for existing in self.state:
            if existing.contradicts(new_rule):
                old_conf = existing.confidence
                existing.confidence *= 0.3
                forgotten.append(
                    f"  FORGET: '{existing}' guven dustu ({old_conf:.1f} -> {existing.confidence:.1f})"
                )
        return forgotten

    def input_gate(self, new_rule):
        integrated = []
        for existing in self.state:
            if (
                existing.subject == new_rule.subject
                and existing.relation == new_rule.relation
                and existing.obj == new_rule.obj
            ):
                old_conf = existing.confidence
                existing.confidence = min(1.0, existing.confidence + 0.2)
                integrated.append(
                    f"  INPUT: '{existing}' guclendi ({old_conf:.1f} -> {existing.confidence:.1f})"
                )
                return integrated
        self.state.append(new_rule)
        self._by_subject[new_rule.subject].append(new_rule)
        self._by_obj[new_rule.obj].append(new_rule)
        integrated.append(f"  INPUT: Yeni kural eklendi -> '{new_rule}'")
        return integrated

    # --- Ingest ---

    def ingest(self, new_rule):
        forget_log = self.forget_gate(new_rule)
        input_log = self.input_gate(new_rule)
        dead = [r for r in self.state if r.confidence < 0.1]
        for d in dead:
            self.state.remove(d)
            self._by_subject[d.subject].remove(d)
            self._by_obj[d.obj].remove(d)

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
            # Try substring matching: 'yesil elma' -> check 'elma'
            # Only for compound terms (multiple words)
            tokens = entity.split()
            if len(tokens) < 2:
                return parents
            for token in tokens:
                if token in self._by_subject:
                    token_parents = self._resolve_subject(token)
                    # Include the token itself as a "parent" with confidence 0.9
                    # (slight penalty for substring match)
                    parents.append((token, 0.9))
                    for p, c in token_parents:
                        parents.append((p, c * 0.9))
        return parents

    # --- Forward chaining: BFS from a start node ---

    def _find_chains(self, start, max_depth=None):
        """BFS forward: follow rules from start through obj -> subject links.
        Returns list of (chain_path, chain_confidence) tuples."""
        if max_depth is None:
            max_depth = self._max_depth
        chains = []
        # queue items: (current_node, path, accumulated_confidence)
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
                # Avoid cycles
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
        """BFS backward: trace rules backward from target through subject -> obj links.
        Returns list of (chain_path, chain_confidence) tuples.
        Path is returned in forward order (origin -> ... -> target)."""
        if max_depth is None:
            max_depth = self._max_depth
        chains = []
        # queue items: (current_node, reverse_path, accumulated_confidence)
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

        # 4. Inheritance: for each term, resolve parent types and find their properties
        for term in terms:
            parents = self._resolve_subject_with_substring(term)
            for parent, parent_conf in parents:
                for rule in self._by_subject.get(parent, []):
                    if rule.relation == "turu":
                        continue  # Skip type relationships themselves
                    if rule.confidence < 0.2:
                        continue
                    inherited_conf = parent_conf * rule.confidence
                    # Build inheritance chain string
                    chain_str = f"{term} -> {parent} -> {rule.obj}"
                    if parent != term:
                        # Find intermediate steps
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

        # 5. Check if forward chains from one term reach another term
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

        # Deduplicate and sort by confidence
        conclusions.sort(key=lambda c: c["confidence"], reverse=True)
        return conclusions if conclusions else None

    def _build_type_chain(self, entity, target_parent):
        """Build the path from entity to target_parent through 'turu' links.
        Also checks substring matching for compound terms."""
        # Direct path
        path = self._bfs_type_path(entity, target_parent)
        if path:
            return path

        # Substring path: 'yesil elma' -> 'elma' -> ...
        tokens = entity.split()
        for token in tokens:
            if token in self._by_subject:
                sub_path = self._bfs_type_path(token, target_parent)
                if sub_path:
                    return [entity] + sub_path[0:]  # replace token start with full entity
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
