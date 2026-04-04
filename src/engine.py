"""
ChainOfMeaning - LSTM-Style Rule Engine Simulation
Gate'ler sayisal degil, kurallar uzerinde calisir.
"""


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


class RuleEngine:
    def __init__(self):
        self.state = []
        self.history = []

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
        integrated.append(f"  INPUT: Yeni kural eklendi -> '{new_rule}'")
        return integrated

    def output_gate(self, query_terms):
        activated = []
        terms = [t.lower() for t in query_terms]
        for rule in self.state:
            if rule.confidence < 0.2:
                continue
            relevance = 0
            if rule.subject in terms:
                relevance += 1
            if rule.obj in terms:
                relevance += 1
            for other_rule in self.state:
                if other_rule.obj == rule.subject and other_rule.subject in terms:
                    relevance += 0.5
                if rule.obj == other_rule.subject and other_rule.subject in terms:
                    relevance += 0.5
            if relevance > 0:
                activated.append((rule, relevance))
        activated.sort(key=lambda x: x[1] * x[0].confidence, reverse=True)
        return activated

    def ingest(self, new_rule):
        forget_log = self.forget_gate(new_rule)
        input_log = self.input_gate(new_rule)
        dead = [r for r in self.state if r.confidence < 0.1]
        for d in dead:
            self.state.remove(d)

    def query(self, question, terms):
        activated = self.output_gate(terms)
        if not activated:
            return None
        return self._chain_reasoning(terms, activated)

    def _chain_reasoning(self, terms, activated):
        conclusions = []
        for rule, _ in activated:
            conclusions.append(
                {"type": "direct", "rule": rule, "confidence": rule.confidence}
            )
        for r1, _ in activated:
            for r2, _ in activated:
                if r1.obj == r2.subject and r1 != r2:
                    chained_confidence = r1.confidence * r2.confidence
                    conclusions.append(
                        {
                            "type": "chained",
                            "chain": f"{r1.subject} -> {r1.obj} -> {r2.obj}",
                            "confidence": chained_confidence,
                        }
                    )
        return conclusions
