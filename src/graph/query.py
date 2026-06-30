"""
Graph Query — advanced graph traversal and analysis.

Provides neighborhood exploration, shortest path, PageRank,
community detection, and co-occurrence analysis.
All operations are read-heavy; only update_importance writes back.
"""

from __future__ import annotations

import sys
from collections import defaultdict, deque
from typing import Any

LOG = lambda msg: sys.stderr.write(f"[memory-graph] {msg}\n")


class GraphQuery:
    """Advanced graph queries built on top of GraphStore."""

    def __init__(self, store: "GraphStore") -> None:
        from graph.store import GraphStore  # noqa: F811 — deferred import for type safety
        if not isinstance(store, GraphStore):
            raise TypeError("store must be a GraphStore instance")
        self.store = store
        self.db = store.db

    # ──────────────────────────────────────────────
    # Traversal
    # ──────────────────────────────────────────────

    def neighborhood(
        self,
        node_id: str,
        depth: int = 2,
        types: list[str] | None = None,
        edge_families: list[str] | None = None,
    ) -> dict[str, Any]:
        """BFS traversal returning a subgraph around a node.

        Args:
            node_id: Starting node.
            depth: Maximum traversal depth (1-5, clamped).
            types: Optional filter — only include nodes of these types.

        Returns:
            {"nodes": [node_dict, ...], "edges": [edge_dict, ...]}
        """
        depth = max(1, min(depth, 5))

        origin = self.store.get_node(node_id)
        if origin is None:
            return {"nodes": [], "edges": []}

        visited_nodes: dict[str, dict] = {node_id: origin}
        collected_edges: list[dict] = []
        seen_edge_ids: set[str] = set()
        frontier: set[str] = {node_id}

        for _ in range(depth):
            if not frontier:
                break
            next_frontier: set[str] = set()
            for nid in frontier:
                edges = self.store.get_edges(
                    nid, direction="both", edge_families=edge_families,
                )
                for edge in edges:
                    if edge["id"] in seen_edge_ids:
                        continue
                    seen_edge_ids.add(edge["id"])

                    neighbor_id = (
                        edge["target_id"]
                        if edge["source_id"] == nid
                        else edge["source_id"]
                    )

                    if neighbor_id not in visited_nodes:
                        neighbor = self.store.get_node(neighbor_id)
                        if neighbor is None:
                            continue
                        # Apply type filter
                        if types and neighbor["type"] not in types:
                            continue
                        visited_nodes[neighbor_id] = neighbor
                        next_frontier.add(neighbor_id)

                    # Only include edge if both endpoints are in our subgraph
                    if (
                        edge["source_id"] in visited_nodes
                        and edge["target_id"] in visited_nodes
                    ):
                        collected_edges.append(edge)

            frontier = next_frontier

        return {
            "nodes": list(visited_nodes.values()),
            "edges": collected_edges,
        }

    def shortest_path(
        self,
        from_id: str,
        to_id: str,
        max_depth: int = 5,
    ) -> list[dict[str, Any]] | None:
        """BFS shortest path between two nodes.

        Returns a list of edge dicts forming the path, or None if no path found.
        The path is ordered from source to target.
        """
        if from_id == to_id:
            return []

        # Verify both nodes exist
        if self.store.get_node(from_id) is None or self.store.get_node(to_id) is None:
            return None

        # BFS with parent tracking: {node_id: (parent_node_id, edge_dict)}
        visited: dict[str, tuple[str | None, dict | None]] = {from_id: (None, None)}
        queue: deque[tuple[str, int]] = deque([(from_id, 0)])

        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue

            edges = self.store.get_edges(current, direction="both")
            for edge in edges:
                neighbor = (
                    edge["target_id"]
                    if edge["source_id"] == current
                    else edge["source_id"]
                )
                if neighbor in visited:
                    continue

                visited[neighbor] = (current, edge)

                if neighbor == to_id:
                    # Reconstruct path
                    path: list[dict] = []
                    node = to_id
                    while visited[node][0] is not None:
                        _, edge_on_path = visited[node]
                        path.append(edge_on_path)
                        node = visited[node][0]
                    path.reverse()
                    return path

                queue.append((neighbor, depth + 1))

        return None  # no path found

    def common_ancestors(
        self,
        node_ids: list[str],
        depth: int = 3,
    ) -> list[dict[str, Any]]:
        """Find nodes reachable from ALL given nodes within the specified depth.

        Useful for finding shared concepts between multiple entities.
        Returns a list of node dicts sorted by importance.
        """
        if not node_ids:
            return []

        depth = max(1, min(depth, 5))

        # For each node, collect all reachable nodes within depth
        reachable_sets: list[set[str]] = []
        for nid in node_ids:
            reachable: set[str] = set()
            frontier: set[str] = {nid}
            for _ in range(depth):
                if not frontier:
                    break
                next_frontier: set[str] = set()
                for fid in frontier:
                    edges = self.store.get_edges(fid, direction="both")
                    for edge in edges:
                        neighbor = (
                            edge["target_id"]
                            if edge["source_id"] == fid
                            else edge["source_id"]
                        )
                        if neighbor not in reachable and neighbor != nid:
                            reachable.add(neighbor)
                            next_frontier.add(neighbor)
                frontier = next_frontier
            reachable_sets.append(reachable)

        # Intersect all reachable sets — exclude the input nodes themselves
        common = reachable_sets[0]
        for rs in reachable_sets[1:]:
            common &= rs
        common -= set(node_ids)

        # Fetch and sort by importance
        results = []
        for nid in common:
            node = self.store.get_node(nid)
            if node and node["status"] == "active":
                results.append(node)

        results.sort(key=lambda n: n.get("importance", 0), reverse=True)
        return results

    def find_by_concepts(self, concept_names: list[str]) -> list[dict[str, Any]]:
        """Find all nodes connected to the given concept names.

        Looks up nodes by name, then finds their direct neighbors.
        Returns unique neighbor nodes sorted by edge weight.
        """
        if not concept_names:
            return []

        concept_ids: set[str] = set()
        for name in concept_names:
            node = self.store.get_node_by_name(name)
            if node:
                concept_ids.add(node["id"])

        if not concept_ids:
            return []

        # Collect neighbors of all concepts with their max weight
        neighbor_weights: dict[str, float] = {}
        for cid in concept_ids:
            edges = self.store.get_edges(cid, direction="both")
            for edge in edges:
                neighbor = (
                    edge["target_id"]
                    if edge["source_id"] == cid
                    else edge["source_id"]
                )
                if neighbor in concept_ids:
                    continue  # skip other concepts
                w = edge["weight"]
                if neighbor not in neighbor_weights or neighbor_weights[neighbor] < w:
                    neighbor_weights[neighbor] = w

        # Fetch node details, sorted by weight
        results = []
        for nid, weight in sorted(neighbor_weights.items(), key=lambda x: x[1], reverse=True):
            node = self.store.get_node(nid)
            if node and node["status"] == "active":
                node["_edge_weight"] = weight
                results.append(node)

        return results

    # ──────────────────────────────────────────────
    # PageRank
    # ──────────────────────────────────────────────

    def pagerank(
        self,
        iterations: int = 20,
        damping: float = 0.85,
    ) -> dict[str, float]:
        """Compute PageRank scores for all active nodes.

        Uses the standard iterative algorithm with damping factor.
        Edges are treated as undirected (both directions contribute).
        Edge weights are used to proportion outgoing rank.

        Returns:
            Dict mapping node_id to PageRank score.
        """
        # Load all active nodes
        rows = self.db.execute(
            "SELECT id FROM graph_nodes WHERE status = 'active'"
        ).fetchall()
        node_ids = [r["id"] for r in rows]

        if not node_ids:
            return {}

        n = len(node_ids)
        node_set = set(node_ids)

        # Build adjacency: for each node, list of (neighbor, weight)
        outgoing: dict[str, list[tuple[str, float]]] = defaultdict(list)
        all_edges = self.db.execute(
            "SELECT source_id, target_id, weight FROM graph_edges"
        ).fetchall()

        for edge in all_edges:
            src, tgt, w = edge["source_id"], edge["target_id"], edge["weight"]
            if src in node_set and tgt in node_set:
                outgoing[src].append((tgt, w))
                outgoing[tgt].append((src, w))  # treat as undirected

        # Precompute outgoing weight sums
        out_weight_sum: dict[str, float] = {}
        for nid in node_ids:
            total = sum(w for _, w in outgoing.get(nid, []))
            out_weight_sum[nid] = total if total > 0 else 1.0

        # Initialize scores uniformly
        scores: dict[str, float] = {nid: 1.0 / n for nid in node_ids}
        base = (1.0 - damping) / n

        for _ in range(iterations):
            new_scores: dict[str, float] = {}
            for nid in node_ids:
                rank_sum = 0.0
                # Incoming contributions (since we treat as undirected,
                # we iterate outgoing neighbors and check what they contribute)
                for neighbor, weight in outgoing.get(nid, []):
                    rank_sum += scores[neighbor] * (weight / out_weight_sum[neighbor])
                new_scores[nid] = base + damping * rank_sum
            scores = new_scores

        # Normalize so scores sum to 1.0
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def update_importance(self) -> None:
        """Run PageRank and update the importance field on all active nodes."""
        scores = self.pagerank()
        if not scores:
            return

        # Scale scores to [0, 1] range relative to max
        max_score = max(scores.values()) if scores else 1.0
        if max_score == 0:
            max_score = 1.0

        for node_id, score in scores.items():
            importance = round(score / max_score, 4)
            self.db.execute(
                "UPDATE graph_nodes SET importance = ? WHERE id = ?",
                (importance, node_id),
            )

        self.db.commit()
        LOG(f"Updated importance for {len(scores)} nodes via PageRank")

    # ──────────────────────────────────────────────
    # Community detection
    # ──────────────────────────────────────────────

    def find_communities(self, min_size: int = 3) -> list[list[str]]:
        """Simple community detection via connected components (Union-Find).

        Returns list of communities (each is a list of node_ids),
        filtered by minimum size, sorted largest first.
        """
        # Load all active nodes
        rows = self.db.execute(
            "SELECT id FROM graph_nodes WHERE status = 'active'"
        ).fetchall()
        node_ids = [r["id"] for r in rows]

        if not node_ids:
            return []

        # Union-Find
        parent: dict[str, str] = {nid: nid for nid in node_ids}
        rank: dict[str, int] = {nid: 0 for nid in node_ids}
        node_set = set(node_ids)

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]  # path compression
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            if rank[ra] == rank[rb]:
                rank[ra] += 1

        # Process all edges
        all_edges = self.db.execute(
            "SELECT source_id, target_id FROM graph_edges"
        ).fetchall()
        for edge in all_edges:
            src, tgt = edge["source_id"], edge["target_id"]
            if src in node_set and tgt in node_set:
                union(src, tgt)

        # Group by root
        communities: dict[str, list[str]] = defaultdict(list)
        for nid in node_ids:
            communities[find(nid)].append(nid)

        # Filter by min_size and sort by size descending
        result = [c for c in communities.values() if len(c) >= min_size]
        result.sort(key=len, reverse=True)
        return result

    # ──────────────────────────────────────────────
    # Co-occurrence analysis
    # ──────────────────────────────────────────────

    def find_cooccurrences(
        self,
        window_days: int = 30,
        min_count: int = 3,
    ) -> list[tuple[str, str, int]]:
        """Find nodes that frequently appear together in knowledge records.

        Two nodes "co-occur" when they are both linked to the same knowledge record
        within the given time window.

        Returns:
            List of (node_id_a, node_id_b, count) sorted by count descending.
        """
        # Find knowledge records within the time window
        rows = self.db.execute(
            """SELECT kn1.node_id AS node_a, kn2.node_id AS node_b, COUNT(*) AS cnt
               FROM knowledge_nodes kn1
               JOIN knowledge_nodes kn2
                 ON kn1.knowledge_id = kn2.knowledge_id
                 AND kn1.node_id < kn2.node_id
               JOIN knowledge k ON kn1.knowledge_id = k.id
               WHERE k.created_at >= datetime('now', ?)
                 AND k.status = 'active'
               GROUP BY kn1.node_id, kn2.node_id
               HAVING cnt >= ?
               ORDER BY cnt DESC""",
            (f"-{window_days} days", min_count),
        ).fetchall()

        return [(r["node_a"], r["node_b"], r["cnt"]) for r in rows]

    # ──────────────────────────────────────────────
    # Subgraph extraction
    # ──────────────────────────────────────────────

    def get_subgraph(self, node_ids: list[str]) -> dict[str, Any]:
        """Get all nodes and edges between a set of nodes.

        Returns:
            {"nodes": [node_dict, ...], "edges": [edge_dict, ...]}
        """
        if not node_ids:
            return {"nodes": [], "edges": []}

        # Fetch nodes
        placeholders = ",".join("?" * len(node_ids))
        node_rows = self.db.execute(
            f"SELECT * FROM graph_nodes WHERE id IN ({placeholders})",
            node_ids,
        ).fetchall()

        # Fetch edges where both endpoints are in the set
        edge_rows = self.db.execute(
            f"""SELECT * FROM graph_edges
                WHERE source_id IN ({placeholders})
                  AND target_id IN ({placeholders})""",
            node_ids + node_ids,
        ).fetchall()

        from graph.store import _row_to_dict

        return {
            "nodes": [_row_to_dict(r) for r in node_rows],
            "edges": [dict(r) for r in edge_rows],
        }
