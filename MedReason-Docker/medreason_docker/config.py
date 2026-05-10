from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeConfig:
    """Runtime configuration for the participant container.

    The official evaluator will mount `/input` and `/output`. Environment variables
    are provided mainly to make local testing easier.
    """

    input_dir: Path
    output_dir: Path
    output_file: Path
    system_name: str
    submission_name: str
    model_path: str | None
    max_new_tokens: int
    temperature: float

    @property
    def cases_file(self) -> Path:
        return self.input_dir / "cases.json"

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        input_dir = Path(os.environ.get("MEDREASON_INPUT_DIR", "/input"))
        output_dir = Path(os.environ.get("MEDREASON_OUTPUT_DIR", "/output"))
        output_file = Path(os.environ.get("MEDREASON_OUTPUT_FILE", str(output_dir / "results.json")))
        return cls(
            input_dir=input_dir,
            output_dir=output_dir,
            output_file=output_file,
            system_name=os.environ.get("MEDREASON_SYSTEM", "custom").strip().lower(),
            submission_name=os.environ.get("MEDREASON_SUBMISSION_NAME", "MedReason system submission"),
            model_path=os.environ.get("MEDREASON_MODEL_PATH"),
            max_new_tokens=int(os.environ.get("MEDREASON_MAX_NEW_TOKENS", "512")),
            temperature=float(os.environ.get("MEDREASON_TEMPERATURE", "0.0")),
        )
