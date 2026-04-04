# ChainOfMeaning Engine v2 — Prolog-Style Inference

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the v1 engine's fixed 2-step chaining with a Prolog-style backward chaining inference engine that supports N-depth chains, unification (inheritance), and confidence propagation — then run the same 5 autopsy scenarios to compare.

**Architecture:** New engine in `src/engine_v2.py` with same public API as v1 (`Rule`, `RuleEngineV2` with `ingest()` and `query()`). Core change: `query()` uses backward chaining with BFS to find all paths between terms, propagating confidence along chains. `"turu"` relation enables inheritance. Forget/input gates stay. New autopsy runner `tests/autopsy_v2.py` imports from v2 and runs same scenarios.

**Tech Stack:** Python 3.x stdlib only. No external dependencies.

---

## File Structure

```
chainofmeaning/
├── src/
│   ├── engine.py          # v1 — UNTOUCHED
│   └── engine_v2.py       # v2 — Prolog-style backward chaining
├── tests/
│   ├── autopsy.py         # v1 autopsy — UNTOUCHED
│   └── autopsy_v2.py      # v2 autopsy — same scenarios, imports engine_v2
├── expected/
│   └── scenarios.py       # UNTOUCHED — same scenarios for both
└── reports/
    ├── autopsy-report.txt     # v1 results (existing)
    └── autopsy-v2-report.txt  # v2 results (new)
```

---

### Task 1: Backward Chaining Core

**Files:**
- Create: `src/engine_v2.py`

- [ ] **Step 1: Create engine_v2.py with Rule class (same as v1) and RuleEngineV2 skeleton**

```python
"""
ChainOfMeaning v2 - Prolog-Style Backward Chaining Engine
Kurallar uzerinde geriye dogru zincirleme ile N-adim cikarim.
"""

from collections import deque


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
        # Index: subject -> list of rules where rule.subject == key
        self._by_subject = {}
        # Index: obj -> list of rules where rule.obj == key
        self._by_obj = {}

    def _index_rule(self, rule):
        self._by_subject.setdefault(rule.subject, []).append(rule)
        self._by_obj.setdefault(rule.obj, []).append(rule)

    def _unindex_rule(self, rule):
        if rule.subject in self._by_subject:
            self._by_subject[rule.subject] = [
                r for r in self._by_subject[rule.subject] if r is not rule
            ]
        if rule.obj in self._by_obj:
            self._by_obj[rule.obj] = [
                r for r in self._by_obj[rule.obj] if r is not rule
            ]

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
        self._index_rule(new_rule)
        integrated.append(f"  INPUT: Yeni kural eklendi -> '{new_rule}'")
        return integrated

    def ingest(self, new_rule):
        self.forget_gate(new_rule)
        self.input_gate(new_rule)
        dead = [r for r in self.state if r.confidence < 0.1]
        for d in dead:
            self.state.remove(d)
            self._unindex_rule(d)

    def _get_rules_by_subject(self, subject):
        return [r for r in self._by_subject.get(subject, []) if r.confidence >= 0.2]

    def _get_rules_by_obj(self, obj):
        return [r for r in self._by_obj.get(obj, []) if r.confidence >= 0.2]

    def _resolve_subject(self, entity):
        """Resolve entity through 'turu' inheritance chain.
        'yesil elma' has no rules, but if we find 'yesil elma' as a
        substring of 'elma' or vice versa, we check 'turu' links.
        Returns list of (resolved_entity, inheritance_confidence) tuples.
        """
        results = [(entity, 1.0)]
        # Follow 'turu' chain upward: elma --turu--> meyve --turu--> bitki
        visited = {entity}
        queue = deque([(entity, 1.0)])
        while queue:
            current, conf = queue.popleft()
            for rule in self._get_rules_by_subject(current):
                if rule.relation == "turu" and rule.obj not in visited:
                    inherited_conf = conf * rule.confidence
                    results.append((rule.obj, inherited_conf))
                    visited.add(rule.obj)
                    queue.append((rule.obj, inherited_conf))
        return results

    def _find_chains(self, start, target=None, max_depth=10):
        """BFS forward from start, find all reachable chains.
        Each chain: list of rules forming a path.
        If target is given, only return chains that reach target.
        """
        # Each queue item: (current_node, chain_so_far, confidence_so_far)
        results = []
        queue = deque([(start, [], 1.0)])
        visited_paths = set()

        while queue:
            current, chain, conf = queue.popleft()

            if len(chain) >= max_depth:
                continue

            for rule in self._get_rules_by_subject(current):
                path_key = (current, rule.obj, len(chain))
                if path_key in visited_paths:
                    continue
                visited_paths.add(path_key)

                new_chain = chain + [rule]
                new_conf = conf * rule.confidence

                # Record this chain
                results.append((new_chain, new_conf))

                # Continue exploring from rule.obj
                queue.append((rule.obj, new_chain, new_conf))

        if target:
            results = [
                (chain, conf) for chain, conf in results
                if chain[-1].obj == target
            ]

        return results

    def query(self, question, terms):
        terms = [t.lower() for t in terms]
        conclusions = []

        for term in terms:
            # Resolve through inheritance
            resolved = self._resolve_subject(term)

            for entity, inherit_conf in resolved:
                # Find all chains from this entity
                chains = self._find_chains(entity)

                for chain, chain_conf in chains:
                    total_conf = inherit_conf * chain_conf

                    if len(chain) == 1:
                        conclusions.append({
                            "type": "direct",
                            "rule": chain[0],
                            "confidence": total_conf,
                        })
                    else:
                        path_parts = [chain[0].subject]
                        for r in chain:
                            path_parts.append(r.obj)
                        chain_str = " -> ".join(path_parts)
                        conclusions.append({
                            "type": "chained",
                            "chain": chain_str,
                            "confidence": total_conf,
                        })

        # Also find chains that REACH a term (backward)
        for term in terms:
            backward_chains = self._find_chains_backward(term)
            for chain, conf in backward_chains:
                if any(chain[0].subject in terms for _ in [1]):
                    continue  # Already found in forward pass
                # Check if chain start is reachable from another term
                for other_term in terms:
                    if other_term == term:
                        continue
                    resolved = self._resolve_subject(other_term)
                    for entity, inherit_conf in resolved:
                        if entity == chain[0].subject:
                            path_parts = [chain[0].subject]
                            for r in chain:
                                path_parts.append(r.obj)
                            chain_str = " -> ".join(path_parts)
                            total_conf = inherit_conf * conf
                            conclusions.append({
                                "type": "chained",
                                "chain": chain_str,
                                "confidence": total_conf,
                            })

        # Deduplicate
        seen = set()
        unique = []
        for c in conclusions:
            key = (c["type"], str(c.get("rule", "")), c.get("chain", ""))
            if key not in seen:
                seen.add(key)
                unique.append(c)

        # Sort by confidence
        unique.sort(key=lambda x: x["confidence"], reverse=True)

        return unique if unique else None

    def _find_chains_backward(self, target, max_depth=10):
        """BFS backward from target: find rules whose obj matches, then recurse on subject."""
        results = []
        queue = deque([(target, [], 1.0)])
        visited_paths = set()

        while queue:
            current, chain, conf = queue.popleft()

            if len(chain) >= max_depth:
                continue

            for rule in self._get_rules_by_obj(current):
                path_key = (rule.subject, current, len(chain))
                if path_key in visited_paths:
                    continue
                visited_paths.add(path_key)

                new_chain = [rule] + chain
                new_conf = rule.confidence * conf

                results.append((new_chain, new_conf))
                queue.append((rule.subject, new_chain, new_conf))

        return results
```

- [ ] **Step 2: Verify it loads**

Run: `python -c "from src.engine_v2 import Rule, RuleEngineV2; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Quick smoke test — Sokrates 4-step chain**

Run:
```bash
python -c "
from src.engine_v2 import Rule, RuleEngineV2
e = RuleEngineV2()
e.ingest(Rule('sokrates', 'turu', 'insan'))
e.ingest(Rule('insan', 'ozellik', 'olumlu'))
e.ingest(Rule('olumlu', 'deneyim', 'aci'))
e.ingest(Rule('aci', 'gelistirir', 'empati'))
results = e.query('sokrates empati?', ['sokrates', 'empati'])
for r in results:
    print(r.get('chain', str(r.get('rule', ''))))
"
```
Expected: Should show a chain containing `sokrates -> insan -> olumlu -> aci -> empati`

- [ ] **Step 4: Quick smoke test — Inheritance**

Run:
```bash
python -c "
from src.engine_v2 import Rule, RuleEngineV2
e = RuleEngineV2()
e.ingest(Rule('meyve', 'etki', 'saglikli'))
e.ingest(Rule('elma', 'turu', 'meyve'))
results = e.query('elma saglikli mi?', ['elma', 'saglikli'])
for r in results:
    print(r.get('chain', str(r.get('rule', ''))))
"
```
Expected: Should show `meyve --etki--> saglikli` found through inheritance (elma→meyve→saglikli)

- [ ] **Step 5: Commit**

```bash
git add src/engine_v2.py
git commit -m "Add v2 engine: Prolog-style backward chaining with inheritance and confidence propagation"
```

---

### Task 2: Build v2 Autopsy Runner

**Files:**
- Create: `tests/autopsy_v2.py`

- [ ] **Step 1: Create autopsy_v2.py**

This is the same structure as `tests/autopsy.py` but imports from `engine_v2` instead of `engine`. The evaluation logic is identical — same scenarios, same 3-layer checks, same PASS/PARTIAL/FAIL criteria.

```python
"""
ChainOfMeaning v2 Otopsi Testi
Ayni 5 senaryo, ayni 3 katman degerlendirme.
v1 ile birebir karsilastirma icin.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine_v2 import Rule, RuleEngineV2 as RuleEngine
from expected.scenarios import (
    scenario_a_contradiction,
    scenario_b_deep_chaining,
    scenario_c_hierarchy,
    scenario_d_evolution,
    scenario_e_stress,
)


# --- Yardimci fonksiyonlar ---

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


# --- Senaryo A ---

def run_scenario_a():
    scenario = scenario_a_contradiction()
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
    expected = q["expected"]

    # Katman 1: Mekanik
    rules_count = len(engine.state)
    expected_count = expected["mechanical"]["check_rules_count"]
    all_confidence_1 = all(r.confidence == 1.0 for r in engine.state)

    if rules_count == expected_count and all_confidence_1:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi, hicbir confidence dusmedi.")
    elif rules_count == expected_count:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            f"{rules_count} kural var ama confidence degisti.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Beklenen {expected_count} kural, bulunan {rules_count}.")

    # Katman 2: Cikarim
    has_direct_kahve = False
    has_chain_kahve_kafein = False
    if conclusions:
        for c in conclusions:
            if c["type"] == "direct" and "kahve" in str(c.get("rule", "")):
                has_direct_kahve = True
            if c["type"] == "chained" and "kahve" in c.get("chain", "") and "kafein" in c.get("chain", ""):
                has_chain_kahve_kafein = True

    if has_direct_kahve and has_chain_kahve_kafein:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            "Hem dogrudan 'kahve' kurali hem de 'kahve->kafein' zinciri bulundu.")
    elif has_direct_kahve or has_chain_kahve_kafein:
        found = "dogrudan kural" if has_direct_kahve else "zincir"
        missing = "zincir" if has_direct_kahve else "dogrudan kural"
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"{found} bulundu ama {missing} eksik.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Ne dogrudan kural ne de zincir bulundu.")

    # Katman 3: Anlam
    contradiction_detected = False
    if conclusions:
        positive = any("saglikli" in str(c.get("rule", "")) or "saglikli" in c.get("chain", "") for c in conclusions)
        negative = any("zararli" in str(c.get("rule", "")) or "zararli" in c.get("chain", "") for c in conclusions)
        if positive and negative:
            contradiction_detected = True

    if contradiction_detected:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            "Hem olumlu hem olumsuz sonuc var ama sistem celiskiyi acikca RAPORLAMIYOR.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Celiski tespit edilemedi.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo B ---

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

    # Katman 1: Mekanik
    rules_count = len(engine.state)
    expected_count = q["expected"]["mechanical"]["check_rules_count"]
    if rules_count == expected_count:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi, conflict yok.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Beklenen {expected_count} kural, bulunan {rules_count}.")

    # Katman 2: Cikarim — 4 adimlik zincir
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
            f"Zincir var ama sokrates->empati baglanamadi. Max derinlik: {max_chain_depth}")
    elif max_chain_depth > 0:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"Sadece {max_chain_depth} adimlik zincir. 4 adim gerekiyor.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Hicbir zincir kurulamadi.")

    # Katman 3: Anlam
    if links_sokrates_empati:
        a = evaluate_layer("Anlam Testi", "PASS",
            "Sokrates'ten empatiye anlam zinciri kuruldu.")
    elif conclusions and len(conclusions) > 0:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Bazi kurallar aktive oldu ama sokrates->empati baglantisi kurulamadi.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Hicbir anlam cikarimi yapilmadi.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo C ---

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

    # Katman 1: Mekanik
    rules_count = len(engine.state)
    if rules_count == 3:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Beklenen 3 kural, bulunan {rules_count}.")

    # Katman 2: Cikarim — inheritance zinciri
    links_saglikli = False
    has_any_result = False
    if conclusions:
        has_any_result = True
        for c in conclusions:
            text = c.get("chain", str(c.get("rule", "")))
            if "saglikli" in text:
                # Check if it connects through elma or meyve
                if "elma" in text or "meyve" in text:
                    links_saglikli = True

    if links_saglikli:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            "Inheritance uzerinden saglikli baglantisi kuruldu!")
    elif has_any_result:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            "Sonuclar var ama inheritance zinciri kurulamadi.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Hicbir sonuc donmedi.")

    # Katman 3: Anlam
    if links_saglikli:
        a = evaluate_layer("Anlam Testi", "PASS",
            "Tur hiyerarsisi uzerinden kalitim yapildi.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Inheritance mantigi yok.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo D ---

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
            rule = Rule(s, r, o)
            engine.ingest(rule)

        conclusions = engine.query(query_info["question"], query_info["terms"])

        tech_rules = [r for r in engine.state if r.subject == "teknoloji"]
        snapshot = {
            "book": book["name"],
            "tech_rules": [(str(r), r.confidence) for r in tech_rules],
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

    print_subheader("Degerlendirme")

    # Katman 1: Mekanik
    first_confidences = [r[1] for r in snapshots[0]["tech_rules"]] if snapshots[0]["tech_rules"] else []
    last_confidences = [r[1] for r in snapshots[-1]["tech_rules"]] if snapshots[-1]["tech_rules"] else []
    confidence_changed = first_confidences != last_confidences or len(first_confidences) != len(last_confidences)

    any_confidence_below_1 = any(
        conf < 1.0
        for snap in snapshots
        for _, conf in snap["tech_rules"]
    )

    if confidence_changed and any_confidence_below_1:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            "Confidence skorlari evrildi ve forget gate tetiklendi.")
    elif confidence_changed:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            "Kural sayisi degisti ama forget gate hic tetiklenmedi.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            "Confidence skorlari hic degismedi.")

    # Katman 2: Cikarim — trend
    def sentiment_score(conclusions):
        if not conclusions:
            return 0
        positive_words = {"olumlu", "faydali", "iyi", "gerekli", "hayat kurtarir", "umut verici"}
        negative_words = {"zararli", "olumsuz", "tehlikeli", "yikici", "kotu"}
        pos = 0
        neg = 0
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
            "Kismi trend: ya basi ya ortasi dogru ama ikisi birden degil.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Anlamsiz trend. Sistem kitaplara duyarsiz.")

    # Katman 3: Anlam
    confidence_pattern_mechanical = True
    for snap in snapshots:
        for rule_str, conf in snap["tech_rules"]:
            if conf not in [1.0, 0.3, 0.09, 0.027] and conf != round(conf, 1):
                confidence_pattern_mechanical = False

    if not confidence_pattern_mechanical:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            "Confidence desenleri mekanik 0.3 carpanindan farkli.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Confidence desenleri tamamen mekanik (0.3 carpani). Sayac tutuyor, ogrenmiyoruz.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo E ---

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

    # Katman 1: Mekanik
    if ingest_time < 5.0 and avg_query_time < 1.0:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"Performans kabul edilebilir. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")
    elif ingest_time < 30.0 and avg_query_time < 5.0:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            f"Yavas ama calisiyor. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Cok yavas. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")

    # Katman 2: Cikarim — noise
    max_results = max(query_results)
    if noise_from_nonexistent == 0 and max_results < 100:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            f"Noise dusuk. Var olmayan terim 0 sonuc. Max sonuc: {max_results}")
    elif noise_from_nonexistent == 0:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"Var olmayan terim filtrelendi ama noise yuksek (max: {max_results}).")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            f"Var olmayan terim bile {noise_from_nonexistent} sonuc donduruyor.")

    # Katman 3: Anlam
    a = evaluate_layer("Anlam Testi", "FAIL",
        "1000 random kuralda anlam aramak anlamsiz — mekanik/performans testi.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Ana rapor ---

def run_all():
    print("\n" + "#" * 70)
    print("#  CHAINOFMEANING v2 OTOPSI RAPORU")
    print("#  Prolog-tarzi backward chaining motoru.")
    print("#" * 70)

    results = {}
    results["A"] = run_scenario_a()
    results["B"] = run_scenario_b()
    results["C"] = run_scenario_c()
    results["D"] = run_scenario_d()
    results["E"] = run_scenario_e()

    # Ozet tablosu
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

    print("\n" + "=" * 70)
    print("  v2 OTOPSI TAMAMLANDI")
    print("=" * 70)

    return results


if __name__ == "__main__":
    run_all()
```

- [ ] **Step 2: Verify it loads**

Run: `python -c "import tests.autopsy_v2"`
Expected: No import error (won't run since no `__main__` trigger)

- [ ] **Step 3: Commit**

```bash
git add tests/autopsy_v2.py
git commit -m "Add v2 autopsy runner with same scenarios and evaluation criteria"
```

---

### Task 3: Run v2 Autopsy and Save Comparison Report

**Files:**
- Create: `reports/autopsy-v2-report.txt`

- [ ] **Step 1: Run v2 autopsy**

Run: `python tests/autopsy_v2.py 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | tee reports/autopsy-v2-report.txt`

Review the output. Expected improvements over v1:
- Scenario B (deep chaining): Should go from PARTIAL→PASS on inference
- Scenario C (hierarchy): Should go from FAIL→PASS on inference (via "turu" inheritance)

- [ ] **Step 2: If any errors, debug and fix engine_v2.py**

If the autopsy crashes or produces unexpected results, read the error, fix `src/engine_v2.py`, and re-run. Common issues:
- Infinite loop in BFS (check visited set)
- Missing index entries after forget gate kills rules
- Inheritance not triggering (check `_resolve_subject` logic)

- [ ] **Step 3: Commit report**

```bash
git add reports/autopsy-v2-report.txt
git commit -m "Add v2 autopsy report: Prolog-style engine results"
```

- [ ] **Step 4: Print side-by-side comparison**

After both reports exist, create a quick comparison by reading both report files and printing the summary tables side by side. This is manual review — read `reports/autopsy-report.txt` and `reports/autopsy-v2-report.txt`, compare the OZET TABLOSU sections.
