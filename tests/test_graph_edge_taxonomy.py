import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from graph.edge_taxonomy import (
    edge_family_for_relation,
    normalize_edge_families,
    relation_allowed_by_families,
)


def test_maps_known_relations_to_magma_families():
    assert edge_family_for_relation("similar_to") == "semantic"
    assert edge_family_for_relation("precedes") == "temporal"
    assert edge_family_for_relation("caused_by") == "causal"
    assert edge_family_for_relation("mentions") == "entity"
    assert edge_family_for_relation("fixed_by") == "procedural"


def test_unknown_relations_default_to_semantic():
    assert edge_family_for_relation("custom_project_link") == "semantic"


def test_normalize_edge_families_dedupes_and_drops_unknowns():
    assert normalize_edge_families(["causal", "semantic", "causal", "bogus"]) == [
        "causal",
        "semantic",
    ]


def test_relation_allowed_by_families_accepts_empty_filter():
    assert relation_allowed_by_families("uses", None)
    assert relation_allowed_by_families("uses", [])


def test_relation_allowed_by_families_filters_by_family():
    assert relation_allowed_by_families("caused_by", ["causal"])
    assert not relation_allowed_by_families("caused_by", ["semantic"])
