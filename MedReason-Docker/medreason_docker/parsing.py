from __future__ import annotations

import json
import re
from typing import Any

from .schema import MedReasonCase

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _try_parse_json_object(text: str) -> dict[str, Any] | None:
    match = _JSON_RE.search(text or "")
    if not match:
        return None
    try:
        obj = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def parse_reasoning_and_answer(text: str, case: MedReasonCase) -> tuple[str, str]:
    """Parse a model response into `(reasoning_trace, answer)`.

    The recommended model output is JSON, but this parser also accepts common
    free-text formats to make the template robust during development.
    """

    raw = (text or "").strip()
    obj = _try_parse_json_object(raw)
    if obj is not None:
        reasoning = str(obj.get("reasoning_trace", obj.get("rationale", ""))).strip()
        answer = str(obj.get("answer", obj.get("final_answer", ""))).strip()
        return reasoning, answer

    reasoning = raw
    answer = raw
    for marker in ["Final answer:", "Answer:", "ANSWER:", "Final:"]:
        if marker in raw:
            prefix, suffix = raw.rsplit(marker, 1)
            reasoning = prefix.strip()
            answer = suffix.strip()
            break
    return reasoning, answer


def normalize_mcq_answer(answer: str, case: MedReasonCase) -> str:
    labels = sorted(case.option_labels, key=lambda x: (len(x), x))
    clean = (answer or "").strip()
    if clean in case.option_labels:
        return clean

    # Match answers like "B", "(B)", "B. finding", "Option B".
    for label in labels:
        escaped = re.escape(label)
        patterns = [
            rf"^\(?{escaped}\)?[\s\.:\-)]*$",
            rf"^\(?{escaped}\)?[\s\.:\-)]",
            rf"\boption\s+{escaped}\b",
            rf"\b{escaped}\b",
        ]
        for pattern in patterns:
            if re.search(pattern, clean, flags=re.IGNORECASE):
                return label

    # Fallback: if the model copied the option text exactly, map it back to the label.
    lowered = clean.lower()
    for option in case.options:
        if option.text.lower() in lowered or lowered in option.text.lower():
            return option.label

    return clean
