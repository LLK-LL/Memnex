"""MAGMA-style edge family taxonomy for the memory graph.

The existing schema stores only ``relation_type``.  This module maps those
relation labels into stable multi-graph families without requiring a DB
migration.
"""

from __future__ import annotations

from typing import Iterable

EDGE_FAMILIES = ("semantic", "temporal", "causal", "entity", "procedural")

_RELATION_FAMILIES: dict[str, str] = {
    # Semantic graph
    "related_to": "semantic",
    "similar_to": "semantic",
    "part_of": "semantic",
    "contains": "semantic",
    "belongs_to": "semantic",
    "uses": "semantic",
    "integrates_with": "semantic",
    "depends_on": "semantic",
    # Temporal graph
    "precedes": "temporal",
    "succeeds": "temporal",
    "before": "temporal",
    "after": "temporal",
    "during": "temporal",
    "concurrent": "temporal",
    "same_session": "temporal",
    # Causal graph
    "causes": "causal",
    "caused_by": "causal",
    "leads_to": "causal",
    "because_of": "causal",
    "enables": "causal",
    "prevents": "causal",
    "blocks": "causal",
    "blocked_by": "causal",
    "breaks": "causal",
    "broke": "causal",
    # Entity graph
    "mentions": "entity",
    "mentioned_in": "entity",
    "refers_to": "entity",
    "owns": "entity",
    "owned_by": "entity",
    "created_by": "entity",
    "maintained_by": "entity",
    "works_on": "entity",
    "works_with": "entity",
    # Procedural graph
    "fixed_by": "procedural",
    "resolved_by": "procedural",
    "step_after": "procedural",
    "step_before": "procedural",
    "workflow_depends_on": "procedural",
    "requires_step": "procedural",
    "implemented_by": "procedural",
    "tested_by": "procedural",
}


def _normalize_relation(relation_type: str | None) -> str:
    return (relation_type or "").strip().lower().replace("-", "_").replace(" ", "_")


def edge_family_for_relation(relation_type: str | None) -> str:
    """Return the MAGMA-style family for an existing relation label."""
    relation = _normalize_relation(relation_type)
    return _RELATION_FAMILIES.get(relation, "semantic")


def normalize_edge_families(families: Iterable[str] | None) -> list[str]:
    """Normalize, validate, and dedupe requested edge families."""
    if not families:
        return []
    valid = set(EDGE_FAMILIES)
    seen: set[str] = set()
    out: list[str] = []
    for family in families:
        norm = (family or "").strip().lower().replace("-", "_")
        if norm not in valid or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


def relation_allowed_by_families(
    relation_type: str | None,
    families: Iterable[str] | None,
) -> bool:
    """Return True when a relation passes the optional family filter."""
    normalized = normalize_edge_families(families)
    if not normalized:
        return True
    return edge_family_for_relation(relation_type) in set(normalized)
