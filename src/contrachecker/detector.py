"""Core contradiction detection engine.

Adapted from ChainOfMeaning v4 engine. Detects three types of contradictions
between claims: direct, indirect (via reasoning chains), and bridge
(a new claim connecting previously unrelated conflicting claims).
"""
from __future__ import annotations

from collections import defaultdict, deque

from .models import Claim, Contradiction


class ContradictionDetector:
    """Stateless contradiction detector for a set of claims.

    Args:
        max_chain_depth: Maximum BFS depth for indirect/bridge detection.
        min_confidence: Ignore claims below this confidence threshold.
    """

    def __init__(self, max_chain_depth: int = 4, min_confidence: float = 0.0):
        self.max_chain_depth = max_chain_depth
        self.min_confidence = min_confidence

    def detect(self, claims: list[Claim]) -> list[Contradiction]:
        """Detect all contradictions among the given claims.

        Builds temporary indexes from the claims list and runs three
        detection passes: direct, indirect, and bridge.

        Args:
            claims: List of Claim objects to analyze.

        Returns:
            List of Contradiction objects sorted by confidence (highest first).
        """
        claims = [c for c in claims if c.confidence >= self.min_confidence]
        if len(claims) < 2:
            return []

        by_subject: dict[str, list[Claim]] = defaultdict(list)
        by_object: dict[str, list[Claim]] = defaultdict(list)
        by_topic: dict[tuple[str, str], list[Claim]] = defaultdict(list)

        for claim in claims:
            by_subject[claim.subject].append(claim)
            by_object[claim.object].append(claim)
            by_topic[(claim.subject, claim.relation)].append(claim)

        results: list[Contradiction] = []
        seen: set[tuple[str, str, str, str]] = set()

        # 1. Direct contradictions
        for topic_claims in by_topic.values():
            for i, a in enumerate(topic_claims):
                for b in topic_claims[i + 1:]:
                    if a.object != b.object:
                        item_key = (a.subject, a.relation, a.object, b.object)
                        if item_key not in seen:
                            seen.add(item_key)
                            results.append(
                                Contradiction(
                                    type="direct",
                                    claim_a=a,
                                    claim_b=b,
                                    confidence=min(a.confidence, b.confidence),
                                    explanation=(
                                        f"Both claim '{a.subject}' has '{a.relation}' "
                                        f"but disagree: '{a.object}' vs '{b.object}'"
                                    ),
                                )
                            )

        # 2. Indirect contradictions
        self._detect_indirect(claims, by_subject, by_object, by_topic, results)

        # 3. Bridge contradictions
        self._detect_bridges(claims, by_subject, by_topic, results)

        results.sort(key=lambda c: c.confidence, reverse=True)
        return results

    def _detect_indirect(self, claims, by_subject, by_object, by_topic, results):
        """Detect indirect contradictions via reasoning chains.

        For each claim, BFS backward from its subject through the claim graph
        (using the by_object index). If any reachable entity has the same
        relation but a different object, that is an indirect contradiction.
        """
        by_relation: dict[str, list[Claim]] = defaultdict(list)
        for claim in claims:
            by_relation[claim.relation].append(claim)

        seen_indirect: set[tuple[str, str]] = set()

        for claim in claims:
            reachable = self._bfs_backward(claim.subject, by_object)
            if not reachable:
                continue

            for other in by_relation.get(claim.relation, []):
                if other.subject not in reachable:
                    continue
                if other.subject == claim.subject:
                    continue
                if other.object == claim.object:
                    continue

                key = tuple(sorted([
                    f"{claim.subject}:{claim.object}",
                    f"{other.subject}:{other.object}",
                ]))
                if key in seen_indirect:
                    continue
                seen_indirect.add(key)

                chain = self._find_path(other.subject, claim.subject, by_subject)
                if chain:
                    results.append(
                        Contradiction(
                            type="indirect",
                            claim_a=other,
                            claim_b=claim,
                            confidence=min(other.confidence, claim.confidence) * 0.8,
                            explanation=(
                                f"'{other.subject}' reaches '{claim.subject}' "
                                f"via chain {' -> '.join(chain)}, but they disagree "
                                f"on '{claim.relation}': '{other.object}' vs '{claim.object}'"
                            ),
                            chain=chain,
                        )
                    )

    def _detect_bridges(self, claims, by_subject, by_topic, results):
        """Detect bridge contradictions.

        For each claim, look at its subject's other claims (siblings). Then
        BFS forward from the subject to find reachable entities. If any
        reachable entity has a claim on the same relation as a sibling but
        with a different object, and a path exists, that is a bridge.
        """
        seen_bridge: set[tuple[str, str]] = set()

        for claim in claims:
            sibling_claims = by_subject.get(claim.subject, [])
            reachable = self._bfs_forward(claim.subject, by_subject)
            if not reachable:
                continue

            for sibling in sibling_claims:
                if sibling is claim:
                    continue
                for entity in reachable:
                    if entity == claim.subject:
                        continue
                    for other in by_subject.get(entity, []):
                        if other.relation != sibling.relation:
                            continue
                        if other.object == sibling.object:
                            continue
                        if other.subject == sibling.subject:
                            continue

                        key = tuple(sorted([
                            f"{sibling.subject}:{sibling.object}",
                            f"{other.subject}:{other.object}",
                        ]))
                        if key in seen_bridge:
                            continue
                        seen_bridge.add(key)

                        chain = self._find_path(sibling.subject, other.subject, by_subject)
                        if chain:
                            results.append(
                                Contradiction(
                                    type="bridge",
                                    claim_a=sibling,
                                    claim_b=other,
                                    confidence=min(sibling.confidence, other.confidence) * 0.7,
                                    explanation=(
                                        f"'{claim.subject} {claim.relation} {claim.object}' "
                                        f"bridges '{sibling.subject}' to '{other.subject}', "
                                        f"revealing conflict on '{sibling.relation}': "
                                        f"'{sibling.object}' vs '{other.object}'"
                                    ),
                                    chain=chain,
                                )
                            )

    def _bfs_backward(self, start: str, by_object: dict[str, list[Claim]]) -> set[str]:
        """BFS backward through the claim graph using the by_object index.

        Finds all entities that can reach `start` through claim chains
        (i.e., entities whose claims' objects eventually lead to `start`).
        """
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(start, 0)])
        while queue:
            current, depth = queue.popleft()
            if depth >= self.max_chain_depth:
                continue
            for claim in by_object.get(current, []):
                prev = claim.subject
                if prev not in visited:
                    visited.add(prev)
                    queue.append((prev, depth + 1))
        return visited

    def _bfs_forward(self, start: str, by_subject: dict[str, list[Claim]]) -> set[str]:
        """BFS forward through the claim graph using the by_subject index.

        Finds all entities reachable from `start` by following claim objects.
        """
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(start, 0)])
        while queue:
            current, depth = queue.popleft()
            if depth >= self.max_chain_depth:
                continue
            for claim in by_subject.get(current, []):
                next_node = claim.object
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, depth + 1))
        return visited

    def _find_path(
        self, start: str, target: str, by_subject: dict[str, list[Claim]]
    ) -> list[str] | None:
        """Find a path from start to target through the claim graph.

        Returns the path as a list of entity names, or None if no path exists
        within max_chain_depth.
        """
        if start == target:
            return [start]
        queue: deque[tuple[str, list[str]]] = deque([(start, [start])])
        visited: set[str] = {start}
        while queue:
            current, path = queue.popleft()
            if len(path) - 1 >= self.max_chain_depth:
                continue
            for claim in by_subject.get(current, []):
                next_node = claim.object
                if next_node == target:
                    return path + [next_node]
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        return None
