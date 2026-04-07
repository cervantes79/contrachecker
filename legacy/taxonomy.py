"""
ChainOfMeaning v3 - Auto-Taxonomy Clustering Module
Entity'leri paylasilan kural kaliplarina gore otomatik kümeler.
Jaccard benzerlik indeksi ile profil eslestirme.
"""

from collections import defaultdict


class Taxonomy:
    def __init__(self, similarity_threshold=0.3):
        self.similarity_threshold = similarity_threshold
        # entity -> set of (relation, obj) pairs
        self._profiles = defaultdict(set)
        # cluster_id -> set of entities
        self._clusters = defaultdict(set)
        # entity -> cluster_id
        self._entity_cluster = {}
        self._next_cluster_id = 0
        # Inverted index: (relation, obj) -> set of entity names
        self._pattern_index = defaultdict(set)
        # Dirty entities needing reclustering
        self._dirty = set()

    def update_profile(self, entity, relation, obj):
        """Add a (relation, obj) pair to an entity's profile."""
        entity = entity.lower()
        relation = relation.lower()
        obj = obj.lower()
        pattern = (relation, obj)
        self._profiles[entity].add(pattern)
        self._pattern_index[pattern].add(entity)

    def _jaccard(self, set_a, set_b):
        """Jaccard similarity index between two sets."""
        if not set_a and not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union)

    def recluster_entity(self, entity):
        """Find best cluster for entity based on Jaccard similarity, or create new one.
        Uses inverted index to only compare against entities sharing at least one pattern."""
        entity = entity.lower()
        profile = self._profiles.get(entity)
        if not profile:
            return

        # Remove from current cluster if any
        if entity in self._entity_cluster:
            old_cluster = self._entity_cluster[entity]
            self._clusters[old_cluster].discard(entity)
            if not self._clusters[old_cluster]:
                del self._clusters[old_cluster]
            del self._entity_cluster[entity]

        # Use inverted index to find candidate entities sharing at least one pattern
        candidates = set()
        for pattern in profile:
            candidates.update(self._pattern_index.get(pattern, set()))
        candidates.discard(entity)

        # Find best matching cluster among candidates only
        best_cluster = None
        best_similarity = 0.0

        for candidate in candidates:
            candidate_profile = self._profiles.get(candidate, set())
            sim = self._jaccard(profile, candidate_profile)
            if sim > best_similarity:
                best_similarity = sim
                candidate_cluster = self._entity_cluster.get(candidate)
                if candidate_cluster is not None:
                    best_cluster = candidate_cluster
                    # Early exit if perfect match
                    if sim >= 1.0:
                        break

        if best_similarity >= self.similarity_threshold and best_cluster is not None:
            self._clusters[best_cluster].add(entity)
            self._entity_cluster[entity] = best_cluster
        else:
            # Create new cluster
            cluster_id = self._next_cluster_id
            self._next_cluster_id += 1
            self._clusters[cluster_id].add(entity)
            self._entity_cluster[entity] = cluster_id

    def mark_dirty(self, entity):
        """Mark an entity as needing reclustering."""
        self._dirty.add(entity.lower())

    def flush_dirty(self):
        """Recluster all dirty entities at once."""
        if not self._dirty:
            return
        dirty = self._dirty.copy()
        self._dirty.clear()
        for entity in dirty:
            self.recluster_entity(entity)

    def get_cluster_members(self, entity):
        """Get all entities in the same cluster as entity."""
        entity = entity.lower()
        cluster_id = self._entity_cluster.get(entity)
        if cluster_id is None:
            return set()
        return set(self._clusters.get(cluster_id, set()))

    def are_same_cluster(self, a, b):
        """Check if two entities share a cluster."""
        a = a.lower()
        b = b.lower()
        cluster_a = self._entity_cluster.get(a)
        cluster_b = self._entity_cluster.get(b)
        if cluster_a is None or cluster_b is None:
            return False
        return cluster_a == cluster_b

    def get_all_clusters(self):
        """Return all clusters as dict {cluster_id: set of members}."""
        return dict(self._clusters)

    def get_multi_member_clusters(self):
        """Return clusters with more than 1 member."""
        return {cid: members for cid, members in self._clusters.items() if len(members) > 1}

    def __repr__(self):
        lines = ["Taxonomy State:"]
        for cluster_id, members in sorted(self._clusters.items()):
            members_str = ", ".join(sorted(members))
            lines.append(f"  Cluster {cluster_id}: [{members_str}]")
            for m in sorted(members):
                profile = self._profiles.get(m, set())
                if profile:
                    pairs = ", ".join(f"{r}:{o}" for r, o in sorted(profile))
                    lines.append(f"    {m}: {pairs}")
        if not self._clusters:
            lines.append("  (bos)")
        return "\n".join(lines)
