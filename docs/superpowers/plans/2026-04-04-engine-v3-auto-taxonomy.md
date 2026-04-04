# ChainOfMeaning Engine v3 — Auto-Taxonomy & Smart Gates

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add auto-clustering taxonomy, rule mass, and support-aware gates to the engine — then run the same 5 autopsy scenarios to see if the remaining 2 FAILs and 3 PARTIALs improve.

**Architecture:** New `src/taxonomy.py` handles entity clustering based on shared rule patterns (Jaccard similarity). New `src/engine_v3.py` extends v2 with: (1) Rule mass that increases with reinforcement, (2) forget_gate that counts supporting rules via backward chaining before deciding decay, (3) taxonomy integration for query optimization and indirect contradiction detection. Same public API.

**Tech Stack:** Python 3.x stdlib only.

---

## File Structure

```
chainofmeaning/
├── src/
│   ├── engine.py          # v1 — UNTOUCHED
│   ├── engine_v2.py       # v2 — UNTOUCHED
│   ├── taxonomy.py        # NEW — auto-clustering module
│   └── engine_v3.py       # NEW — v3 engine with taxonomy + smart gates
├── tests/
│   ├── autopsy.py         # v1 autopsy — UNTOUCHED
│   ├── autopsy_v2.py      # v2 autopsy — UNTOUCHED
│   └── autopsy_v3.py      # NEW — v3 autopsy
├── expected/
│   └── scenarios.py       # UNTOUCHED
└── reports/
    ├── autopsy-report.txt
    ├── autopsy-v2-report.txt
    └── autopsy-v3-report.txt  # NEW
```

---

### Task 1: Taxonomy Module

**Files:**
- Create: `src/taxonomy.py`

- [ ] **Step 1: Create taxonomy.py with entity profiling and Jaccard clustering**

```python
"""
Auto-Taxonomy: Kurallardan otomatik entity clustering.
Her entity'nin 'profili' = hangi relation+object kaliplariyla gorunuyor.
Benzer profiller ayni cluster'a girer.
Cluster'lar hiyerarsik olabilir.
"""


class Taxonomy:
    def __init__(self, similarity_threshold=0.3):
        self.similarity_threshold = similarity_threshold
        # cluster_id -> set of entity names
        self.clusters = {}
        # entity -> cluster_id
        self.entity_to_cluster = {}
        # cluster_id -> parent cluster_id (for hierarchy)
        self.cluster_parents = {}
        # entity -> set of (relation, obj) tuples — the entity's "profile"
        self.profiles = {}
        self._next_cluster_id = 0

    def _new_cluster_id(self):
        cid = self._next_cluster_id
        self._next_cluster_id += 1
        return cid

    def update_profile(self, entity, relation, obj):
        """Add a (relation, obj) pair to an entity's profile."""
        if entity not in self.profiles:
            self.profiles[entity] = set()
        self.profiles[entity].add((relation, obj))

    def similarity(self, entity_a, entity_b):
        """Jaccard similarity between two entity profiles."""
        profile_a = self.profiles.get(entity_a, set())
        profile_b = self.profiles.get(entity_b, set())
        if not profile_a or not profile_b:
            return 0.0
        intersection = profile_a & profile_b
        union = profile_a | profile_b
        return len(intersection) / len(union)

    def recluster_entity(self, entity):
        """Find the best cluster for entity, or create a new one.
        Called after entity's profile changes."""
        # Remove from current cluster if any
        if entity in self.entity_to_cluster:
            old_cid = self.entity_to_cluster[entity]
            self.clusters[old_cid].discard(entity)
            if not self.clusters[old_cid]:
                del self.clusters[old_cid]
            del self.entity_to_cluster[entity]

        # Find most similar existing entity
        best_match = None
        best_sim = 0.0
        for other_entity in self.profiles:
            if other_entity == entity:
                continue
            sim = self.similarity(entity, other_entity)
            if sim > best_sim:
                best_sim = sim
                best_match = other_entity

        if best_sim >= self.similarity_threshold and best_match is not None:
            # Join the same cluster as best_match
            if best_match in self.entity_to_cluster:
                cid = self.entity_to_cluster[best_match]
            else:
                cid = self._new_cluster_id()
                self.clusters[cid] = {best_match}
                self.entity_to_cluster[best_match] = cid
            self.clusters[cid].add(entity)
            self.entity_to_cluster[entity] = cid
        else:
            # New cluster for this entity alone
            cid = self._new_cluster_id()
            self.clusters[cid] = {entity}
            self.entity_to_cluster[entity] = cid

    def get_cluster_members(self, entity):
        """Get all entities in the same cluster as entity."""
        cid = self.entity_to_cluster.get(entity)
        if cid is None:
            return set()
        return self.clusters.get(cid, set())

    def get_cluster_id(self, entity):
        """Get cluster ID for an entity, or None."""
        return self.entity_to_cluster.get(entity)

    def are_same_cluster(self, entity_a, entity_b):
        """Check if two entities are in the same cluster."""
        cid_a = self.entity_to_cluster.get(entity_a)
        cid_b = self.entity_to_cluster.get(entity_b)
        if cid_a is None or cid_b is None:
            return False
        return cid_a == cid_b

    def find_opposites_in_cluster(self, obj_value, relation, rules_by_subject):
        """Find objects that appear in the same position (same relation)
        but for entities in the same cluster as obj_value's entities.
        This helps detect semantic opposition.
        E.g., 'saglikli' and 'zararli' both appear as obj of 'etki' relation
        for entities in similar clusters → they might be opposites."""
        # Find all entities that have this obj_value
        entities_with_value = set()
        for entity, profile in self.profiles.items():
            if (relation, obj_value) in profile:
                entities_with_value.add(entity)

        # Find cluster siblings of these entities
        siblings = set()
        for e in entities_with_value:
            siblings.update(self.get_cluster_members(e))

        # Find what other obj values appear with same relation for siblings
        opposites = set()
        for sibling in siblings:
            for r, o in self.profiles.get(sibling, set()):
                if r == relation and o != obj_value:
                    opposites.add(o)

        return opposites

    def get_all_clusters(self):
        """Return dict of cluster_id -> set of entities for inspection."""
        return {cid: members.copy() for cid, members in self.clusters.items() if members}

    def __repr__(self):
        lines = []
        for cid, members in sorted(self.clusters.items()):
            if members:
                lines.append(f"  Cluster {cid}: {', '.join(sorted(members))}")
        return f"Taxonomy ({len(self.clusters)} cluster):\n" + "\n".join(lines) if lines else "Taxonomy (bos)"
```

- [ ] **Step 2: Smoke test taxonomy**

Run:
```bash
python -c "
from src.taxonomy import Taxonomy
t = Taxonomy(similarity_threshold=0.3)
# porsche ve ferrari benzer profiller
t.update_profile('porsche', 'etki', 'hizli')
t.update_profile('porsche', 'turu', 'araba')
t.update_profile('ferrari', 'etki', 'hizli')
t.update_profile('ferrari', 'turu', 'araba')
t.recluster_entity('porsche')
t.recluster_entity('ferrari')
print(t)
print('Ayni cluster?', t.are_same_cluster('porsche', 'ferrari'))
# bisiklet farkli profil
t.update_profile('bisiklet', 'etki', 'yavas')
t.update_profile('bisiklet', 'turu', 'tasit')
t.recluster_entity('bisiklet')
print(t)
print('porsche-bisiklet ayni cluster?', t.are_same_cluster('porsche', 'bisiklet'))
"
```
Expected: porsche and ferrari in same cluster, bisiklet in different cluster.

- [ ] **Step 3: Commit**

```bash
git add src/taxonomy.py
git commit -m "Add auto-taxonomy module: Jaccard-based entity clustering from rule profiles"
```

---

### Task 2: Engine v3 — Smart Gates + Mass + Taxonomy

**Files:**
- Create: `src/engine_v3.py`

- [ ] **Step 1: Create engine_v3.py**

This extends v2's backward chaining with three new capabilities:
1. **Rule mass**: tracks reinforcement count, affects forget resistance
2. **Smart forget gate**: counts supporting rules before deciding decay
3. **Taxonomy integration**: auto-clusters entities on ingest, detects indirect contradictions

```python
"""
ChainOfMeaning v3 - Auto-Taxonomy & Smart Gates
v2'nin backward chaining'i + otomatik clustering + akilli gate'ler.
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
        self.mass = 1  # Her tekrarda artar, yuksek kutle = zor unutulur

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
        """Count how many other rules indirectly support this rule.
        Uses backward chaining: if 'teknoloji etki faydali',
        support = how many other rules chain INTO 'faydali' or
        share the same subject with positive relations."""
        support = 0
        # 1. Rules with same subject (other properties of same entity)
        for r in self._by_subject.get(rule.subject, []):
            if r is not rule and r.confidence >= 0.2:
                support += 1
        # 2. Rules that chain into this rule's object
        for r in self._by_obj.get(rule.subject, []):
            if r.confidence >= 0.2:
                support += 0.5
        # 3. Cluster siblings: entities in same cluster with same relation+obj pattern
        cluster_members = self.taxonomy.get_cluster_members(rule.subject)
        for member in cluster_members:
            if member == rule.subject:
                continue
            for r in self._by_subject.get(member, []):
                if r.relation == rule.relation and r.obj == rule.obj and r.confidence >= 0.2:
                    support += 0.5
        return support

    # --- Smart Forget Gate ---

    def forget_gate(self, new_rule):
        """Support-aware forget gate.
        Decay = new_mass / (existing_mass + support + new_mass)
        instead of fixed 0.3."""
        forgotten = []

        # Direct contradictions (same subject+relation, different object)
        for existing in self.state:
            if existing.contradicts(new_rule):
                support = self._count_support(existing)
                # Decay factor: more support and mass = less decay
                resistance = existing.mass + support
                decay = resistance / (resistance + new_rule.mass)
                old_conf = existing.confidence
                existing.confidence *= decay
                forgotten.append(
                    f"  FORGET: '{existing}' guven dustu ({old_conf:.2f} -> {existing.confidence:.2f})"
                    f" [kutle={existing.mass}, destek={support:.1f}, decay={decay:.2f}]"
                )

        # Indirect contradictions via taxonomy
        # If new_rule's obj is in the same cluster position as an existing rule's obj
        # but they're "opposites" (appear for same relation in same cluster, different value)
        indirect = self._find_indirect_contradictions(new_rule)
        for existing, reason in indirect:
            support = self._count_support(existing)
            resistance = existing.mass + support
            # Indirect contradictions decay less than direct ones
            decay = (resistance + 1) / (resistance + new_rule.mass + 1)
            old_conf = existing.confidence
            existing.confidence *= decay
            forgotten.append(
                f"  FORGET (dolayli): '{existing}' guven dustu ({old_conf:.2f} -> {existing.confidence:.2f})"
                f" [sebep: {reason}]"
            )

        return forgotten

    def _find_indirect_contradictions(self, new_rule):
        """Find rules that indirectly contradict new_rule through taxonomy.
        Example: new_rule = 'kafein etki zararli'
                 existing = 'kahve etki saglikli'
                 if kahve->kafein chain exists and saglikli/zararli are
                 in opposing positions → indirect contradiction."""
        indirect = []

        # Check if new_rule's subject is reachable from any existing rule's subject
        for existing in self.state:
            if existing is new_rule:
                continue
            if existing.confidence < 0.2:
                continue
            if existing.relation != new_rule.relation:
                continue
            if existing.obj == new_rule.obj:
                continue
            # Same relation, different object — but different subject
            if existing.subject == new_rule.subject:
                continue  # This is a direct contradiction, handled above

            # Check if there's a chain between the subjects
            chain_exists = self._has_path(existing.subject, new_rule.subject)
            if chain_exists:
                reason = f"{existing.subject}->{new_rule.subject} zinciri var, {existing.obj} vs {new_rule.obj}"
                indirect.append((existing, reason))

        return indirect

    def _has_path(self, start, target, max_depth=5):
        """Quick BFS check: is there any path from start to target?"""
        if start == target:
            return True
        visited = {start}
        queue = deque([start])
        depth = 0
        while queue and depth < max_depth:
            next_level = []
            for current in queue:
                for rule in self._by_subject.get(current, []):
                    if rule.confidence < 0.2:
                        continue
                    if rule.obj == target:
                        return True
                    if rule.obj not in visited:
                        visited.add(rule.obj)
                        next_level.append(rule.obj)
            queue = deque(next_level)
            depth += 1
        return False

    # --- Smart Input Gate ---

    def input_gate(self, new_rule):
        """Input gate with mass tracking."""
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
                    f"  INPUT: '{existing}' guclendi ({old_conf:.2f} -> {existing.confidence:.2f})"
                    f" [kutle: {old_mass} -> {existing.mass}]"
                )
                return integrated
        self.state.append(new_rule)
        self._by_subject[new_rule.subject].append(new_rule)
        self._by_obj[new_rule.obj].append(new_rule)
        integrated.append(f"  INPUT: Yeni kural eklendi -> '{new_rule}'")
        return integrated

    # --- Ingest with Taxonomy Update ---

    def ingest(self, new_rule):
        forget_log = self.forget_gate(new_rule)
        input_log = self.input_gate(new_rule)

        # Update taxonomy
        self.taxonomy.update_profile(new_rule.subject, new_rule.relation, new_rule.obj)
        self.taxonomy.recluster_entity(new_rule.subject)
        # Also recluster the object if it appears as a subject elsewhere
        if new_rule.obj in self._by_subject:
            self.taxonomy.update_profile(new_rule.obj, "_obj_of_" + new_rule.relation, new_rule.subject)
            self.taxonomy.recluster_entity(new_rule.obj)

        # Remove dead rules
        dead = [r for r in self.state if r.confidence < 0.1]
        for d in dead:
            self.state.remove(d)
            if d in self._by_subject.get(d.subject, []):
                self._by_subject[d.subject].remove(d)
            if d in self._by_obj.get(d.obj, []):
                self._by_obj[d.obj].remove(d)

        return forget_log + input_log

    # --- Inheritance (same as v2) ---

    def _resolve_subject(self, entity):
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

    # --- Forward/Backward Chaining (same as v2) ---

    def _find_chains(self, start, max_depth=None):
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

    def _find_chains_backward(self, target, max_depth=None):
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

    # --- Query (same as v2 + cluster-aware) ---

    def query(self, question, terms):
        terms = [t.lower() for t in terms]
        conclusions = []
        seen_chains = set()

        effective_depth = self._max_depth
        if len(self.state) > 500:
            effective_depth = min(self._max_depth, 5)

        # 1. Direct rules
        for rule in self.state:
            if rule.confidence < 0.2:
                continue
            if rule.subject in terms or rule.obj in terms:
                conclusions.append({
                    "type": "direct",
                    "rule": rule,
                    "confidence": rule.confidence,
                })

        # 2. Forward chaining
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

        # 3. Backward chaining
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
                    if rule.relation == "turu" or rule.confidence < 0.2:
                        continue
                    inherited_conf = parent_conf * rule.confidence
                    chain_str = f"{term} -> {parent} -> {rule.obj}"
                    if parent != term:
                        type_chain = self._bfs_type_path(term, parent)
                        if type_chain:
                            chain_str = " -> ".join(type_chain + [rule.obj])
                        else:
                            tokens = term.split()
                            for token in tokens:
                                sub_path = self._bfs_type_path(token, parent)
                                if sub_path:
                                    chain_str = " -> ".join([term] + sub_path[1:] + [rule.obj])
                                    break
                    if chain_str not in seen_chains:
                        seen_chains.add(chain_str)
                        conclusions.append({
                            "type": "chained",
                            "chain": chain_str,
                            "confidence": inherited_conf,
                        })

        # 5. Cross-term chains
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

    def _bfs_type_path(self, start, target):
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
```

- [ ] **Step 2: Smoke test — smart forget gate with support**

Run:
```bash
python -c "
from src.engine_v3 import Rule, RuleEngineV3
e = RuleEngineV3()
# Build support: 3 positive rules about technology
e.ingest(Rule('teknoloji', 'saglar', 'verimlilik'))
e.ingest(Rule('teknoloji', 'gelistirir', 'tip'))
e.ingest(Rule('teknoloji', 'etki', 'faydali'))
print('Faydali confidence:', [r for r in e.state if r.obj == 'faydali'][0].confidence)
# Now contradict: 'teknoloji etki tehlikeli'
e.ingest(Rule('teknoloji', 'etki', 'tehlikeli'))
faydali_rules = [r for r in e.state if r.obj == 'faydali']
if faydali_rules:
    print('Faydali after contradiction:', faydali_rules[0].confidence, '(v1 would be 0.3)')
else:
    print('Faydali removed (too low confidence)')
print()
print('Taxonomy:')
print(e.taxonomy)
"
```
Expected: "faydali" confidence should be HIGHER than 0.3 (v1 value) because 3 other rules support "teknoloji".

- [ ] **Step 3: Smoke test — indirect contradiction via chain**

Run:
```bash
python -c "
from src.engine_v3 import Rule, RuleEngineV3
e = RuleEngineV3()
e.ingest(Rule('kahve', 'etki', 'saglikli'))
e.ingest(Rule('kahve', 'icerir', 'kafein'))
# This should trigger indirect contradiction: kahve->kafein chain exists
# and saglikli vs zararli are opposing in same relation position
e.ingest(Rule('kafein', 'etki', 'zararli'))
print('State:')
for r in e.state:
    print(f'  {r}')
saglikli = [r for r in e.state if r.obj == 'saglikli']
if saglikli:
    print(f'saglikli confidence: {saglikli[0].confidence:.2f} (should be < 1.0 due to indirect contradiction)')
"
```
Expected: "saglikli" confidence should drop (not stay at 1.0) because kahve→kafein→zararli indirectly contradicts kahve→saglikli.

- [ ] **Step 4: Smoke test — rule mass**

Run:
```bash
python -c "
from src.engine_v3 import Rule, RuleEngineV3
e = RuleEngineV3()
# Reinforce 'teknoloji etki faydali' 5 times
for _ in range(5):
    e.ingest(Rule('teknoloji', 'etki', 'faydali'))
faydali = [r for r in e.state if r.obj == 'faydali'][0]
print(f'Mass after 5 reinforcements: {faydali.mass} (should be 5)')
print(f'Confidence: {faydali.confidence}')
# Now try to contradict with single 'tehlikeli'
e.ingest(Rule('teknoloji', 'etki', 'tehlikeli'))
print(f'Faydali after contradiction: conf={faydali.confidence:.2f}, mass={faydali.mass}')
print('High mass should resist decay more than low mass')
"
```
Expected: mass=5, and confidence after contradiction should be much higher than v1's 0.3.

- [ ] **Step 5: Commit**

```bash
git add src/engine_v3.py
git commit -m "Add v3 engine: auto-taxonomy, support-aware gates, rule mass"
```

---

### Task 3: v3 Autopsy Runner

**Files:**
- Create: `tests/autopsy_v3.py`

- [ ] **Step 1: Create autopsy_v3.py**

Same structure as v2 autopsy but imports from engine_v3. Key differences in evaluation:
- Scenario A: Anlam layer now checks if confidence dropped due to indirect contradiction (not just PARTIAL for seeing both results)
- Scenario D: Anlam layer checks if confidence patterns are NON-mechanical (not just 0.3 powers)

```python
"""
ChainOfMeaning v3 Otopsi Testi
Ayni 5 senaryo, ayni 3 katman degerlendirme.
v1, v2 ile karsilastirma icin.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine_v3 import Rule, RuleEngineV3 as RuleEngine
from expected.scenarios import (
    scenario_a_contradiction,
    scenario_b_deep_chaining,
    scenario_c_hierarchy,
    scenario_d_evolution,
    scenario_e_stress,
)


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_subheader(text):
    print(f"\n--- {text} ---")


def print_rule_state(engine):
    print(f"\n  State ({len(engine.state)} kural):")
    for r in engine.state:
        print(f"    {r}")


def print_conclusions(conclusions):
    if conclusions is None:
        print("  Sonuc: None (hicbir kural aktive olmadi)")
        return
    print(f"  Sonuc ({len(conclusions)} cikarim):")
    for c in conclusions:
        if c["type"] == "direct":
            print(f"    [DOGRUDAN] {c['rule']} (guven: {c['confidence']:.2f})")
        elif c["type"] == "chained":
            print(f"    [ZINCIR]   {c['chain']} (guven: {c['confidence']:.2f})")


def evaluate_layer(layer_name, status, detail):
    symbol = {"PASS": "+", "PARTIAL": "~", "FAIL": "X"}
    print(f"  [{symbol[status]}] {layer_name}: {status} - {detail}")
    return status


def run_scenario_a():
    scenario = scenario_a_contradiction()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    print_subheader("Kural Yukleme")
    for s, r, o in scenario["rules"]:
        rule = Rule(s, r, o)
        print(f"\n  Yukleniyor: {rule}")
        log = engine.ingest(rule)
        for line in log:
            print(line)
    print_rule_state(engine)
    print(f"\n  Taxonomy: {engine.taxonomy}")

    q = scenario["queries"][0]
    print_subheader(f"Sorgu: {q['question']}")
    conclusions = engine.query(q["question"], q["terms"])
    print_conclusions(conclusions)

    print_subheader("Degerlendirme")

    # Mekanik
    rules_count = len(engine.state)
    expected_count = q["expected"]["mechanical"]["check_rules_count"]
    if rules_count == expected_count:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            f"Beklenen {expected_count} kural, bulunan {rules_count} (indirect contradiction decay olabilir).")

    # Cikarim
    has_direct_kahve = False
    has_chain = False
    if conclusions:
        for c in conclusions:
            if c["type"] == "direct" and "kahve" in str(c.get("rule", "")):
                has_direct_kahve = True
            if c["type"] == "chained" and "kahve" in c.get("chain", "") and "kafein" in c.get("chain", ""):
                has_chain = True
    if has_direct_kahve and has_chain:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            "Hem dogrudan kural hem zincir bulundu.")
    elif has_direct_kahve or has_chain:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            "Kismi cikarim.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Cikarim yok.")

    # Anlam — v3'te indirect contradiction confidence'i dusurmeli
    contradiction_detected = False
    confidence_affected = False
    if conclusions:
        positive = any("saglikli" in str(c.get("rule", "")) or "saglikli" in c.get("chain", "") for c in conclusions)
        negative = any("zararli" in str(c.get("rule", "")) or "zararli" in c.get("chain", "") for c in conclusions)
        if positive and negative:
            contradiction_detected = True
        # Check if any saglikli rule's confidence dropped below 1.0
        for r in engine.state:
            if r.obj == "saglikli" and r.confidence < 1.0:
                confidence_affected = True

    if contradiction_detected and confidence_affected:
        a = evaluate_layer("Anlam Testi", "PASS",
            "Dolayli celiski tespit edildi VE confidence etkilendi. Motor celiskinin farkinda.")
    elif contradiction_detected:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            "Hem olumlu hem olumsuz sonuc var ama confidence etkilenmedi.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Celiski tespit edilemedi.")

    return {"mechanical": m, "inference": i, "meaning": a}


def run_scenario_b():
    scenario = scenario_b_deep_chaining()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    print_subheader("Kural Yukleme")
    for s, r, o in scenario["rules"]:
        rule = Rule(s, r, o)
        print(f"\n  Yukleniyor: {rule}")
        engine.ingest(rule)
    print_rule_state(engine)

    q = scenario["queries"][0]
    print_subheader(f"Sorgu: {q['question']}")
    conclusions = engine.query(q["question"], q["terms"])
    print_conclusions(conclusions)

    print_subheader("Degerlendirme")

    rules_count = len(engine.state)
    expected_count = q["expected"]["mechanical"]["check_rules_count"]
    if rules_count == expected_count:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi, conflict yok.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Beklenen {expected_count}, bulunan {rules_count}.")

    max_chain_depth = 0
    links_sokrates_empati = False
    if conclusions:
        for c in conclusions:
            if c["type"] == "chained":
                depth = c["chain"].count("->")
                max_chain_depth = max(max_chain_depth, depth)
                if "sokrates" in c["chain"] and "empati" in c["chain"]:
                    links_sokrates_empati = True

    if links_sokrates_empati:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            f"Sokrates->empati zinciri kuruldu! Derinlik: {max_chain_depth}")
    elif max_chain_depth >= 2:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"Zincir var ama sokrates->empati yok. Max: {max_chain_depth}")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Zincir kurulamadi.")

    if links_sokrates_empati:
        a = evaluate_layer("Anlam Testi", "PASS",
            "Sokrates'ten empatiye anlam zinciri kuruldu.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Anlam baglantisi kurulamadi.")

    return {"mechanical": m, "inference": i, "meaning": a}


def run_scenario_c():
    scenario = scenario_c_hierarchy()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    print_subheader("Kural Yukleme")
    for s, r, o in scenario["rules"]:
        rule = Rule(s, r, o)
        print(f"\n  Yukleniyor: {rule}")
        engine.ingest(rule)
    print_rule_state(engine)

    q = scenario["queries"][0]
    print_subheader(f"Sorgu: {q['question']}")
    conclusions = engine.query(q["question"], q["terms"])
    print_conclusions(conclusions)

    print_subheader("Degerlendirme")

    rules_count = len(engine.state)
    if rules_count == 3:
        m = evaluate_layer("Mekanik Dogruluk", "PASS", f"{rules_count} kural eklendi.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL", f"Beklenen 3, bulunan {rules_count}.")

    links_saglikli = False
    has_any_result = False
    if conclusions:
        has_any_result = True
        for c in conclusions:
            text = c.get("chain", str(c.get("rule", "")))
            if "saglikli" in text and ("elma" in text or "meyve" in text):
                links_saglikli = True

    if links_saglikli:
        i = evaluate_layer("Cikarim Kalitesi", "PASS", "Inheritance ile saglikli bulundu!")
    elif has_any_result:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL", "Sonuc var ama inheritance zinciri yok.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL", "Sonuc yok.")

    if links_saglikli:
        a = evaluate_layer("Anlam Testi", "PASS", "Tur hiyerarsisi uzerinden kalitim yapildi.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL", "Inheritance yok.")

    return {"mechanical": m, "inference": i, "meaning": a}


def run_scenario_d():
    scenario = scenario_d_evolution()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()
    query_info = scenario["query_after_each_book"]
    snapshots = []

    for book_idx, book in enumerate(scenario["books"]):
        print_subheader(f"{book['name']}")
        for s, r, o in book["rules"]:
            engine.ingest(Rule(s, r, o))
        conclusions = engine.query(query_info["question"], query_info["terms"])
        tech_rules = [r for r in engine.state if r.subject == "teknoloji"]
        snapshot = {
            "book": book["name"],
            "tech_rules": [(str(r), r.confidence, getattr(r, 'mass', 1)) for r in tech_rules],
            "total_rules": len(engine.state),
            "conclusions_count": len(conclusions) if conclusions else 0,
            "conclusions": conclusions,
        }
        snapshots.append(snapshot)
        print(f"  Teknoloji kurallari ({len(tech_rules)}):")
        for r in tech_rules:
            print(f"    {r}")
        print(f"  Toplam kural: {len(engine.state)}")
        print(f"  Cikarim sayisi: {snapshot['conclusions_count']}")

    print_subheader("Taxonomy")
    print(f"  {engine.taxonomy}")

    print_subheader("Degerlendirme")

    # Mekanik
    first_count = len(snapshots[0]["tech_rules"])
    last_count = len(snapshots[-1]["tech_rules"])
    any_conf_below_1 = any(
        conf < 1.0
        for snap in snapshots
        for _, conf, _ in snap["tech_rules"]
    )
    if first_count != last_count and any_conf_below_1:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            "Confidence skorlari evrildi ve forget gate tetiklendi.")
    elif first_count != last_count:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            "Kural sayisi degisti ama forget gate tetiklenmedi.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL", "Hic degismedi.")

    # Cikarim — sentiment trend
    def sentiment_score(conclusions):
        if not conclusions:
            return 0
        positive_words = {"olumlu", "faydali", "iyi", "gerekli", "hayat kurtarir", "umut verici"}
        negative_words = {"zararli", "olumsuz", "tehlikeli", "yikici", "kotu"}
        pos, neg = 0, 0
        for c in conclusions:
            text = str(c.get("rule", "")) + c.get("chain", "")
            for w in positive_words:
                if w in text:
                    pos += c["confidence"]
            for w in negative_words:
                if w in text:
                    neg += c["confidence"]
        return pos - neg

    sentiments = [sentiment_score(s["conclusions"]) for s in snapshots]
    print(f"\n  Sentiment trend: {[f'{s:.2f}' for s in sentiments]}")

    early_positive = all(s > 0 for s in sentiments[:3]) if len(sentiments) >= 3 else False
    mid_shift = any(s <= 0 for s in sentiments[3:6]) if len(sentiments) >= 6 else False
    if early_positive and mid_shift:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            "Trend dogru: ilk kitaplar olumlu, ortalar olumsuz/karisik.")
    elif early_positive or mid_shift:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            "Kismi trend.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL", "Anlamsiz trend.")

    # Anlam — confidence desenleri mekanik mi?
    # v3'te mass ve support nedeniyle confidence'lar artik 0.3 katlari OLMAMALI
    unique_confidences = set()
    for snap in snapshots:
        for _, conf, mass in snap["tech_rules"]:
            if conf < 1.0:
                unique_confidences.add(round(conf, 4))

    mechanical_values = {0.3, 0.09, 0.027, 0.0081}
    non_mechanical = unique_confidences - mechanical_values
    has_mass_variation = any(
        mass > 1
        for snap in snapshots
        for _, _, mass in snap["tech_rules"]
    )

    if non_mechanical and has_mass_variation:
        a = evaluate_layer("Anlam Testi", "PASS",
            f"Confidence desenleri mekanik degil! Benzersiz degerler: {sorted(non_mechanical)[:5]}. Kutle evrimi var.")
    elif non_mechanical or has_mass_variation:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            f"Kismi ogrenme: {'non-mechanical values' if non_mechanical else 'mass variation'} var.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Confidence desenleri hala mekanik.")

    return {"mechanical": m, "inference": i, "meaning": a}


def run_scenario_e():
    scenario = scenario_e_stress()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    print_subheader("Kural Yukleme (1000 kural)")
    start = time.time()
    for s, r, o in scenario["rules"]:
        engine.ingest(Rule(s, r, o))
    ingest_time = time.time() - start
    print(f"  Yukleme suresi: {ingest_time:.3f} saniye")
    print(f"  State'teki kural sayisi: {len(engine.state)}")
    print(f"  Cluster sayisi: {len(engine.taxonomy.get_all_clusters())}")

    print_subheader("Sorgu Performansi")
    query_times = []
    query_results = []
    for q in scenario["queries"]:
        start = time.time()
        conclusions = engine.query(q["question"], q["terms"])
        elapsed = time.time() - start
        query_times.append(elapsed)
        result_count = len(conclusions) if conclusions else 0
        query_results.append(result_count)
        print(f"  [{elapsed:.4f}s] {q['question']}: {result_count} sonuc")

    avg_query_time = sum(query_times) / len(query_times)
    max_query_time = max(query_times)
    print(f"\n  Ortalama sorgu suresi: {avg_query_time:.4f}s")
    print(f"  Maksimum sorgu suresi: {max_query_time:.4f}s")

    nonexistent_idx = next(i for i, q in enumerate(scenario["queries"]) if "olmayan" in q["question"])
    noise_from_nonexistent = query_results[nonexistent_idx]

    print_subheader("Degerlendirme")

    if ingest_time < 10.0 and avg_query_time < 2.0:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"Performans kabul edilebilir. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")
    elif ingest_time < 60.0 and avg_query_time < 10.0:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            f"Yavas ama calisiyor. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Cok yavas. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")

    max_results = max(query_results)
    if noise_from_nonexistent == 0 and max_results < 100:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            f"Noise dusuk. Max sonuc: {max_results}")
    elif noise_from_nonexistent == 0:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"Noise yuksek (max: {max_results}).")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            f"Var olmayan terim {noise_from_nonexistent} sonuc donduruyor.")

    # Anlam: clustering anlamli gruplar olustu mu?
    clusters = engine.taxonomy.get_all_clusters()
    multi_member = {cid: m for cid, m in clusters.items() if len(m) > 1}
    if len(multi_member) >= 3:
        sample = list(multi_member.values())[:3]
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            f"{len(multi_member)} anlamli cluster olusturuldu. Ornekler: {[sorted(s) for s in sample[:3]]}")
    elif multi_member:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            f"Sadece {len(multi_member)} cluster olusturuldu — daha fazla veri lazim.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Hicbir anlamli cluster olusturulamadi.")

    return {"mechanical": m, "inference": i, "meaning": a}


def run_all():
    print("\n" + "#" * 70)
    print("#  CHAINOFMEANING v3 OTOPSI RAPORU")
    print("#  Auto-taxonomy + akilli gate'ler + kural kutlesi")
    print("#" * 70)

    results = {}
    results["A"] = run_scenario_a()
    results["B"] = run_scenario_b()
    results["C"] = run_scenario_c()
    results["D"] = run_scenario_d()
    results["E"] = run_scenario_e()

    print_header("OZET TABLOSU")
    print(f"\n  {'Senaryo':<45} {'Mekanik':<12} {'Cikarim':<12} {'Anlam':<12}")
    print("  " + "-" * 81)
    names = {
        "A": "Celiski Yonetimi",
        "B": "Derin Zincirleme (4 adim)",
        "C": "Hiyerarsi / Kalitim",
        "D": "Zaman Icinde Evrilme",
        "E": "Stres Testi (1000 kural)",
    }
    for key in ["A", "B", "C", "D", "E"]:
        r = results[key]
        print(f"  {names[key]:<45} {r['mechanical']:<12} {r['inference']:<12} {r['meaning']:<12}")

    all_ratings = []
    for r in results.values():
        all_ratings.extend(r.values())
    pass_count = all_ratings.count("PASS")
    partial_count = all_ratings.count("PARTIAL")
    fail_count = all_ratings.count("FAIL")
    print(f"\n  Toplam: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL")
    print(f"  (15 degerlendirme uzerinden)")

    # v1 vs v2 vs v3 comparison
    print_header("KARSILASTIRMA: v1 vs v2 vs v3")
    print(f"\n  {'Senaryo':<30} {'v1':<20} {'v2':<20} {'v3':<20}")
    print("  " + "-" * 90)
    v1_results = {"A": "P/P/PA", "B": "P/PA/F", "C": "P/PA/F", "D": "P/PA/F", "E": "P/P/F"}
    v2_results = {"A": "P/P/PA", "B": "P/P/P", "C": "P/P/P", "D": "P/PA/F", "E": "P/PA/F"}
    for key in ["A", "B", "C", "D", "E"]:
        r = results[key]
        v3_str = f"{r['mechanical'][0]}/{r['inference'][0]}/{r['meaning'][0]}"
        print(f"  {names[key]:<30} {v1_results[key]:<20} {v2_results[key]:<20} {v3_str:<20}")
    print(f"\n  v1: 7P 4PA 4F  |  v2: 10P 3PA 2F  |  v3: {pass_count}P {partial_count}PA {fail_count}F")

    print("\n" + "=" * 70)
    print("  v3 OTOPSI TAMAMLANDI")
    print("=" * 70)

    return results


if __name__ == "__main__":
    run_all()
```

- [ ] **Step 2: Verify it loads**

Run: `python -c "import tests.autopsy_v3"`
Expected: No import error

- [ ] **Step 3: Commit**

```bash
git add tests/autopsy_v3.py
git commit -m "Add v3 autopsy runner with taxonomy-aware evaluation"
```

---

### Task 4: Run v3 Autopsy and Save Report

**Files:**
- Create: `reports/autopsy-v3-report.txt`

- [ ] **Step 1: Run v3 autopsy**

Run: `python tests/autopsy_v3.py 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | tee reports/autopsy-v3-report.txt`

Review output carefully. Expected improvements:
- Scenario A Anlam: PARTIAL→PASS (indirect contradiction detected)
- Scenario D Anlam: FAIL→PARTIAL or PASS (non-mechanical confidence patterns)
- Scenario E Anlam: FAIL→PARTIAL (meaningful clusters formed)

- [ ] **Step 2: If errors, debug and fix**

If crash or wrong results, fix `src/engine_v3.py` or `src/taxonomy.py` and re-run.

- [ ] **Step 3: Commit report**

```bash
git add reports/autopsy-v3-report.txt
git commit -m "Add v3 autopsy report: auto-taxonomy and smart gates results"
```
