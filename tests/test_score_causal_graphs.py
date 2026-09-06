from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "score_causal_graphs.py"
sys.path.insert(0, str(REPO / "scripts"))


def _load():
    spec = importlib.util.spec_from_file_location("score_causal_graphs", SCRIPT)
    assert spec is not None
    assert isinstance(spec.loader, SourceFileLoader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


S = _load()


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _record(*, body: str) -> str:
    return f"""identifier: X:1
label: test
trait_axis: FUNCTION
trait_category: FUNC_RESISTANCE
mapping_status: REVIEWED
{body}
license: CC0
"""


def test_score_path_reports_a_complete_graph(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "complete.yaml",
        _record(
            body="""causal_graphs:
- graph_id: resistance
  title: Resistance mechanism
  description: Complete test graph.
  nodes:
  - node_id: determinant
    label: determinant
    node_type: PROTEIN
    grounding: ARO:1
  - node_id: activity
    label: activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:1
  edges:
  - subject: determinant
    predicate: enables
    predicate_id: RO:0002327
    object: activity
    description: The determinant enables the activity.
    evidence:
    - reference: PMID:1
      snippet: activity evidence
    - reference: PMID:2
      snippet: independent evidence
""",
        ),
    )

    score = S.score_path(path)

    assert score.score == 100
    assert score.graphs == 1
    assert score.nodes == 2
    assert score.edges == 1
    assert score.grounded_groundable_nodes == 2
    assert score.multi_reference_edges == 1
    assert score.reasons == ()


def test_score_path_prioritizes_incomplete_graphs(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "incomplete.yaml",
        _record(
            body="""causal_graphs:
- graph_id: resistance
  title: Resistance mechanism
  nodes:
  - node_id: determinant
    label: determinant
    node_type: PROTEIN
  - node_id: activity
    label: activity
    node_type: MOLECULAR_FUNCTION
    grounding: GO:1
  edges:
  - subject: determinant
    predicate: enables
    object: activity
    evidence:
    - reference: PMID:1
""",
        ),
    )

    score = S.score_path(path)

    assert score.score == 25
    assert score.grounded_groundable_nodes == 1
    assert score.predicate_id_edges == 0
    assert score.snippet_edges == 0
    assert score.described_edges == 0
    assert score.documented_graphs == 0
    assert score.quality_warnings == 3
    assert score.reasons == (
        "quality_warnings=3",
        "grounded_groundable_nodes=1/2",
        "predicate_id_edges=0/1",
        "multi_reference_edges=0/1",
        "snippet_edges=0/1",
        "described_edges=0/1",
        "documented_graphs=0/1",
    )


def test_described_state_nodes_do_not_need_grounding(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "state.yaml",
        _record(
            body="""causal_graphs:
- graph_id: resistance
  title: Resistance mechanism
  description: A graph with a local reaction state.
  nodes:
  - node_id: determinant
    label: determinant
    node_type: PROTEIN
    grounding: ARO:1
  - node_id: state
    label: local catalytic state
    node_type: STATE
    description: Local state with no stable external CURIE.
  edges:
  - subject: determinant
    predicate: causally upstream of
    predicate_id: RO:0002411
    object: state
    description: The determinant creates a local state.
    evidence:
    - reference: PMID:1
      snippet: state evidence
    - reference: PMID:2
      snippet: independent evidence
""",
        ),
    )

    score = S.score_path(path)

    assert score.groundable_nodes == 1
    assert score.grounded_groundable_nodes == 1


def test_include_missing_scores_no_graph_records_as_zero(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "missing.yaml",
        _record(body="definition: no graph\n"),
    )

    assert S.candidate_files([tmp_path], include_missing=True) == [path]

    score = S.score_path(path)

    assert score.score == 0
    assert score.identifier == "X:1"
    assert score.reasons == ("no causal_graphs",)


def test_graph_discovery_includes_hidden_and_gitignored_files(tmp_path: Path) -> None:
    _write(tmp_path / ".gitignore", "ignored/\n")
    visible = _write(
        tmp_path / "visible.yaml",
        _record(body="causal_graphs: []\n"),
    )
    ignored = _write(
        tmp_path / "ignored" / "hidden.yaml",
        _record(body="causal_graphs: []\n"),
    )

    assert S.candidate_files([tmp_path]) == [ignored, visible]


def test_write_scores_sorts_by_score_then_file(tmp_path: Path) -> None:
    first = S.CausalGraphScore(score=10, file="b.yaml")
    second = S.CausalGraphScore(score=10, file="a.yaml")
    third = S.CausalGraphScore(score=0, file="z.yaml")
    out = tmp_path / "scores.tsv"

    with out.open("w", encoding="utf-8", newline="") as handle:
        S.write_scores([first, second, third], handle)

    assert out.read_text(encoding="utf-8").splitlines() == [
        "\t".join(S.FIELDS),
        "0\tz.yaml\t\t\t\t\t\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t",
        "10\ta.yaml\t\t\t\t\t\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t",
        "10\tb.yaml\t\t\t\t\t\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t0\t",
    ]
