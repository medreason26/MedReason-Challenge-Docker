# MedReason Challenge Docker Examples

This repository provides Dockerized pipelines, example containers, and public evaluation utilities for the **MedReason Challenge @ MICCAI 2026**. It includes a model-agnostic submission template, a runnable Qwen2.5-VL reference baseline, and public scripts for submission validation and metric aggregation.

MedReason evaluates whether medical MLLM systems can perform clinically grounded visual question answering under domain shift. Submissions are expected to package a complete inference system inside a Docker container. The system may be a single MLLM, an ensemble, a retrieval-augmented pipeline, an agentic workflow, a visual self-verification pipeline, or another fully automated method, as long as it follows the official input/output contract.

## Repository Structure

```text
├── MedReason-Docker/
│   ├── Dockerfile
│   ├── process.py             # Official container entry point
│   ├── build.sh               # Build the participant Docker image
│   ├── test.sh                # Verify the Docker I/O contract with smoke data
│   ├── export.sh              # Export the Docker image for submission
│   ├── requirements.txt
│   ├── medreason_docker/
│   │   ├── schema.py          # Shared case and prediction schema
│   │   ├── io.py              # Input/output helpers
│   │   ├── validation.py      # Output contract validation
│   │   ├── runner.py          # System loading and inference runner
│   │   └── systems/
│   │       ├── base.py        # MedReasonSystem interface
│   │       ├── custom_system.py
│   │       ├── hf_vlm_system.py
│   │       └── smoke_system.py
│   ├── test/
│   │   ├── cases.json
│   │   └── images/
│   ├── tools/
│   │   └── validate_output.py
│   └── README.md              # Detailed participant-template instructions
│
├── MedReason-Docker-Example-Qwen25VL/
│   ├── Dockerfile
│   ├── process.py             # Qwen2.5-VL baseline inference pipeline
│   ├── build.sh
│   ├── test.sh
│   ├── export.sh
│   ├── requirements.txt
│   ├── medreason_baseline/
│   │   ├── cases.py           # Case loading and path resolution
│   │   ├── prompts.py         # MCQ and open-ended MedReason prompts
│   │   ├── qwen25vl.py        # Qwen2.5-VL loading and generation utilities
│   │   ├── parsing.py         # JSON/text parsing and MCQ normalization
│   │   └── validation.py      # Prediction validation
│   ├── models/
│   │   └── README.md          # Where to place Qwen2.5-VL checkpoints
│   ├── test/
│   │   ├── cases.json
│   │   ├── expected_output.json
│   │   └── images/
│   ├── tools/
│   │   └── validate_output.py
│   └── README.md              # Detailed baseline example instructions
│
├── MedReason-Evaluation/
│   ├── scoring.py             # Public metric aggregation script
│   ├── validate_submission.py # Validate zipped submission format
│   ├── sample_submission.zip  # Example results.json submission archive
│   ├── test/
│   │   ├── cases.json
│   │   ├── ground_truth.json
│   │   └── judge_scores.json
│   ├── docs/
│   │   ├── evaluation.md
│   │   └── submission_format.md
│   └── README.md              # Detailed evaluation and submission instructions
│
└── README.md                  # This file
```

## Supported Components

### Participant Docker Template (`MedReason-Docker/`)

A model-agnostic Docker template for packaging a complete MedReason MLLM system. Participants should implement their method by following the `MedReasonSystem` interface. The submitted container must read official input files from `/input`, run inference fully inside the container, and write `/output/results.json`.

The template supports systems beyond a single model, including multi-model pipelines, retrieval modules, agentic reasoning, self-verification, uncertainty handling, and rule-based post-processing. Internet access, external APIs, or manual intervention should not be required during official evaluation.

### Qwen2.5-VL Baseline Example (`MedReason-Docker-Example-Qwen25VL/`)

A runnable reference baseline aligned with the challenge Docker interface. It demonstrates a simple but complete MedReason system:

```text
Qwen2.5-VL checkpoint
    → MedReason-specific prompt
    → model generation
    → JSON/text parsing
    → MCQ option normalization
    → required answer + reasoning_trace formatting
    → /output/results.json
```

This example is provided as a reference implementation, not as a restriction on participant methods. Participants may replace it with any fully automated MLLM system that follows the same I/O contract.

### Public Evaluation Utilities (`MedReason-Evaluation/`)

Public scripts and examples for submission checking and metric aggregation. The public `scoring.py` defines:

- MCQ exact-match scoring;
- open-ended GT aggregation;
- open-ended VA aggregation;
- threshold-gated computation of `VA_final` from `VA_answer` and `RVF_trace`;
- dataset-level metric averaging.

During official hidden-test evaluation, case-level open-ended judge scores are produced organizer-side and then aggregated according to the public scoring script. Hidden labels, hidden images, and private judge outputs are not included in this public package.

## Submission Output Format

All participant systems must produce one JSON file:

```text
/output/results.json
```

The output file must contain one prediction for every input case:

```json
{
  "name": "MedReason predictions",
  "type": "Medical visual reasoning",
  "answers": [
    {
      "case_id": "case_mcq_001",
      "task_type": "mcq",
      "answer": "B",
      "reasoning_trace": "Optional brief rationale.",
      "confidence": 0.73
    },
    {
      "case_id": "case_open_001",
      "task_type": "open",
      "reasoning_trace": "Image-grounded reasoning trace.",
      "answer": "Concise final answer."
    }
  ],
  "version": {
    "major": 1,
    "minor": 0
  }
}
```

For MCQ cases, `answer` must match one of the official option labels. For open-ended cases, both `reasoning_trace` and `answer` are required.

## Quickstart

### Prerequisites

- Docker Engine or Docker Desktop.
- NVIDIA Container Toolkit for GPU-based model inference.
- NVIDIA drivers and CUDA-compatible GPU for real model inference.
- Python 3.10+ for local validation scripts.

Smoke tests do not require a GPU or a downloaded model checkpoint.

## Building and Testing

### Test the model-agnostic participant template

```bash
cd MedReason-Docker
docker build -t medreason-docker .
./test.sh medreason-docker
```

### Test the Qwen2.5-VL baseline example in smoke mode

```bash
cd MedReason-Docker-Example-Qwen25VL
docker build -t medreason-qwen25vl-example .
./test.sh medreason-qwen25vl-example
```

The smoke test verifies the container interface and output format without loading the full Qwen2.5-VL checkpoint.

### Run the Qwen2.5-VL example with a real checkpoint

Place the model files under:

```text
MedReason-Docker-Example-Qwen25VL/models/Qwen2.5-VL/
```

Then build and run the container without smoke-test mode. See the README inside `MedReason-Docker-Example-Qwen25VL/` for detailed instructions.

### Validate a submission archive

```bash
cd MedReason-Evaluation
python validate_submission.py sample_submission.zip --cases-json test/cases.json
```

### Run public metric aggregation on toy examples

```bash
cd MedReason-Evaluation
python scoring.py \
  --predictions sample_submission/results.json \
  --ground-truth test/ground_truth.json \
  --judge-scores test/judge_scores.json \
  --pretty
```

## Exporting for Submission

For a Docker-based submission, run the export script inside the participant Docker folder:

```bash
cd MedReason-Docker
./export.sh medreason-docker medreason_submission.tar.gz
```

or, if using the Qwen2.5-VL example as a starting point:

```bash
cd MedReason-Docker-Example-Qwen25VL
./export.sh medreason-qwen25vl-example medreason_qwen25vl_submission.tar.gz
```

The exported Docker archive should be uploaded to cloud storage, and the download link should be sent to the organizers according to the instructions on the MedReason challenge website.

## Relationship Between the Three Components

- Use `MedReason-Docker/` if you want a clean template for implementing your own system.
- Use `MedReason-Docker-Example-Qwen25VL/` if you want a runnable reference baseline that follows the official Docker interface.
- Use `MedReason-Evaluation/` if you want to validate submission format and inspect the public metric aggregation logic.

The official hidden leaderboard evaluation is performed organizer-side by running submitted Docker containers on hidden evaluation data.

## Links

- Challenge website: https://medreason26.github.io/challenge.html
- Synapse participation page: https://www.synapse.org/Synapse:syn74403682/wiki/640168
- Data access page: https://www.synapse.org/Synapse:syn74403682/wiki/640171
- Contact: medreason26@googlegroups.com

## License

The released participant-facing MedReason resources are provided for non-commercial research use under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0), unless otherwise specified by the corresponding dataset owners or source institutions.

Canonical license URL: https://creativecommons.org/licenses/by-nc/4.0/
