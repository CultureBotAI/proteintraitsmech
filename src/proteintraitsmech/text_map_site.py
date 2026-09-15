"""Prepare a configured common text map before a site build can change files.

All artifact validation and atomic publication belong to CLAW's shared runtime.
This adapter only supplies fresh full-corpus semantic inputs and site policy.
"""

from __future__ import annotations

import importlib.util
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import yaml

from proteintraitsmech.text_map_inputs import export_inputs


@dataclass
class PreparedTextMap:
    pipeline: ModuleType
    source: Path
    inputs: Path

    def stage(self, site: Path) -> None:
        self.pipeline.stage_map(self.source, site / "text-map", input_path=self.inputs)


def load_pipeline(root: Path) -> ModuleType:
    path = root / "scripts" / "embedding_pipeline.py"
    if not path.is_file() or path.is_symlink():
        raise ValueError(
            "enabled text map requires the CLAW-governed scripts/embedding_pipeline.py"
        )
    spec = importlib.util.spec_from_file_location("proteintraitsmech_embedding_pipeline", path)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load the CLAW embedding pipeline")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "stage_map", None)):
        raise ValueError("CLAW embedding pipeline does not provide validated map staging")
    return module


@contextmanager
def prepare_text_map(root: Path) -> Iterator[PreparedTextMap | None]:
    config = root / "conf" / "text_map.yaml"
    if config.is_symlink():
        raise ValueError("text map configuration must not be a symlink")
    if not config.is_file():
        raise ValueError("text map enablement requires conf/text_map.yaml")
    settings = yaml.safe_load(config.read_text(encoding="utf-8"))
    if (
        not isinstance(settings, dict)
        or set(settings) != {"enabled"}
        or type(settings["enabled"]) is not bool
    ):
        raise ValueError("text map configuration must contain only an explicit enabled boolean")
    if not settings["enabled"]:
        yield None
        return
    source = root / "data" / "text_map"
    if source.is_symlink() or not (source / "current.json").is_file():
        raise ValueError("enabled text map requires data/text_map/current.json")
    pipeline = load_pipeline(root)
    with tempfile.TemporaryDirectory(prefix="proteintraitsmech-text-map-") as directory:
        inputs = Path(directory) / "inputs.jsonl"
        receipt = export_inputs(root, inputs)
        if receipt["scope"] != "full":
            raise ValueError("site publication requires fresh full-corpus inputs")
        manifest = pipeline.validate_bundle(pipeline.current_bundle(source), input_path=inputs)
        if manifest["projection"]["implementation"] != "pacmap.PaCMAP":
            raise ValueError("site publication requires the actual PaCMAP implementation")
        profile = manifest["encoder"]
        if (
            profile["model"] != pipeline.MODEL
            or profile["revision"] != pipeline.MODEL_REVISION
            or profile["dimension"] != pipeline.MODEL_DIMENSION
        ):
            raise ValueError("common semantic map requires the pinned fleet BGE encoder profile")
        yield PreparedTextMap(pipeline, source, inputs)
