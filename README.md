# LLM-Assisted Analysis and Quality Assessment for Batch-Aware ML Experiment Results

## Project Overview

This project builds an evidence-grounded LLM-assisted analysis pipeline for evaluating cross-batch robustness in biomedical machine learning experiments. The project starts from RNA-seq classification outputs generated under different batch-separation settings, converts raw ML results into structured summaries, extracts rule-based robustness patterns, uses an LLM to generate scientific interpretations, evaluates whether the LLM output is grounded in the evidence, and finally presents the results through a reproducible demo chatbot.

Standard random train-test splits may overestimate biomedical ML performance when training and test samples share batch-specific artifacts. This project therefore evaluates model behavior under increasingly separated batch settings and studies whether LLMs can help turn complex robustness results into reliable, interpretable, and evaluable scientific summaries.

The project is designed to answer two main questions:

1. Do standard random-split evaluations overestimate biomedical ML performance under batch effects?
2. Can LLMs assist in interpreting complex ML robustness experiments while remaining grounded in structured evidence?


## Method Design Framework

The following framework summarizes the full design of the project, from RNA-seq data preparation and batch modeling to robustness evaluation, failure evidence extraction, LLM-assisted analysis, and LLM output evaluation.

<img width="1149" height="1369" alt="8813" src="https://github.com/user-attachments/assets/755f247c-73c3-4156-b998-e53a9d9da34d" />


The framework contains eight layers:

1. **Data Layer**: prepare expression matrices, labels, metadata, and filtered features.
2. **Batch Modeling**: use known batch metadata or infer unknown batch structure through low-quality markers, UMAP, and clustering/geometric segmentation.
3. **Split Strategy**: construct random split, cross-batch split, and continuous mixing settings.
4. **Model Layer**: evaluate multiple classifiers and normalization strategies.
5. **Evaluation Layer**: compute error, error-vs-split curves, generalization gaps, and robustness patterns.
6. **Failure Evidence Extraction**: extract structured evidence such as curve trends, batch-label comparison, model consistency, and anomalies.
7. **LLM Analysis Layer**: use structured inputs to generate interpretable reasoning and insights.
8. **Evaluation of LLM**: assess coverage, consistency, alignment with structured evidence, and answer-level quality.


## Pipeline Summary

The project is organized as a modular pipeline:

```text
Raw RNA-seq ML outputs
        ↓
Module 1: Structured Summary Builder
        ↓
Module 2: Pattern Detection Engine
        ↓
Module 3: LLM Analysis Generator + Grounding Evaluation
        ↓
Module 4: Demo Chatbot + Answer Quality Check
        ↓
Module 4C: Optional API-Enabled Interactive Chatbot
        ↓
Final Validation Tests
```

## Repository Structure

The repository is organized to make the full pipeline reproducible.

```text
project-root/
│
├── README.md
├── requirements.txt
├── data/
│
├── module1_structured_summary_builder.ipynb
├── module2_pattern_detection_engine.ipynb
├── module3_llm_analysis_generator.ipynb
├── module4_demo_chatbot_quality_check.ipynb
├── module4C_api_interactive_demo_chatbot.ipynb
├── final_validation_tests.ipynb
│
├── module1_outputs/
├── module2_outputs/
├── module3_outputs/
├── module4_outputs/
│
└── figures/
    └── method_design_framework.png
```

```markdown
### Main folders

- `data/`: Contains the original RNA-seq metadata, expression matrix, R scripts, and raw ML result files.
- `module1_outputs/`: Structured tables generated from raw ML outputs.
- `module2_outputs/`: Rule-based error-curve patterns, classifier summaries, and LLM-ready JSON files.
- `module3_outputs/`: Evidence packs, LLM-generated analysis, and grounding evaluation summaries.
- `module4_outputs/`: Demo chatbot transcripts, answer logs, and answer-level quality summaries.
```


## Installation Instructions

This project was implemented using Python and Jupyter Notebook.

Recommended environment:

Python 3.9 or above
Jupyter Notebook, JupyterLab, or VS Code with the Jupyter extension

### 1. Clone the repository

```bash
git clone https://github.com/Todaisy-wang/LLM-Assisted-Batch-Aware-ML-Analysis.git
cd LLM-Assisted-Batch-Aware-ML-Analysis
```

### 2. Create a virtual environment

Using `conda`:
```bash
conda create -n batch-llm-project python=3.10 -y
conda activate batch-llm-project
```

Or using `venv`:
```bash
python -m venv .venv
source .venv/bin/activate #For macOS/Linux
# .venv\Scripts\activate  #For Windows
```

### 3. Install Dependencies:

```bash
pip install -r requirements.txt
```
The project also uses Python standard libraries such as json, re, pathlib, sys, subprocess, and importlib. These do not need to be installed separately.

### 4. Launch Jupyter

```bash
jupyter notebook
```


## Environment Setup Guide

This project can be run in two modes:

### Mode 1: Fully reproducible offline mode

The main pipeline can be reproduced without calling the OpenAI API by using the saved intermediate outputs and deterministic template-based chatbot in Module 4.

Recommended notebooks for offline reproduction:

1. `module1_structured_summary_builder.ipynb`
2. `module2_pattern_detection_engine.ipynb`
3. `module3_llm_analysis_generator.ipynb`
4. `module4_demo_chatbot_quality_check.ipynb`
5. `final_validation_tests.ipynb`

### Mode 2: Optional API-enabled mode

The optional interactive chatbot in Module 4C can call the OpenAI API for live answer generation. To use this mode, create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```
The deterministic fallback will still be used when the API key is unavailable.


## Data and Input Files

The original ML process is stored under the `data/` folder.

Main input files:

| File | Description |
|---|---|
| `eTable1.xlsx` | Clinical metadata at the sample level. |
| `expression_matrix.csv` | Main RNA-seq expression matrix used as high-dimensional input features. |
| `Jama1.Rmd` | Main ML experiment script. It loads expression and clinical data, aligns samples, constructs binary labels, defines batch proxy variables, runs ML pipelines, and exports classifier results. |
| `Summary.Rmd` | Summarizes ML results, plots error curves, checks split-level error patterns, and supports preliminary conclusions. |
| `jama_scenario1_3_*_result.csv` | Raw classifier result files used as direct input for Module 1. |


## How to Run the Pipeline

Run the notebooks in the following order:

1. `module1_structured_summary_builder.ipynb`
2. `module2_pattern_detection_engine.ipynb`
3. `module3_llm_analysis_generator.ipynb`
4. `module4_demo_chatbot_quality_check.ipynb`
5. `final_validation_tests.ipynb`

Optional interactive demo:

- `module4C_api_interactive_demo_chatbot.ipynb`

Each module writes output files that are used by downstream modules. Therefore, the notebooks should be run in order unless the required output folders are already present.


## Module Summary

| Module | Purpose | Main Outputs |
|---|---|---|
| Module 1 | Converts raw ML result files into structured performance summaries. | `module1_outputs/module1_performance_summary.csv` |
| Module 2 | Extracts error-curve patterns and rule-based robustness evidence. | `module2_outputs/module2_llm_ready_patterns.json`, `module2_outputs/module2_pattern_table_with_sentences.csv` |
| Module 3 | Generates LLM-assisted analysis and evaluates grounding quality. | `module3_outputs/module3D_llm_analysis.json`, `module3_outputs/module3E_grounding_summary.json` |
| Module 4 | Builds a reproducible demo chatbot and checks answer quality. | `module4_outputs/module4_demo_transcript.md`, `module4_outputs/module4_answer_quality_summary.json` |
| Module 4C | Provides an optional API-enabled interactive chatbot. | Gradio interactive demo |
| Final Validation | Checks output completeness and cross-module consistency. | Validation summary in notebook output |


## Demo

The main reproducible demo is provided in:
```text
module4_demo_chatbot_quality_check.ipynb
```

This notebook builds a deterministic evidence-grounded chatbot, runs fixed demo questions, performs answer-level quality checks, and exports:
```text
module4_outputs/module4_demo_transcript.md
module4_outputs/module4_answer_quality_summary.json
```

For a live interactive interface, run:
```text
module4C_api_interactive_demo_chatbot.ipynb
```

The API-enabled demo is optional and includes a template-based fallback when no API key is available.


## Validation and Reproducibility

The final validation notebook provides lightweight integration tests for the full project pipeline:

```text
final_validation_tests.ipynb
```

It checks whether required outputs from Modules 1–4 exist, whether expected schemas are satisfied, and whether downstream modules can consume upstream outputs.

The main demo is deterministic, so the chatbot transcript can be reproduced without requiring a live API call.


## Troubleshooting

- If a notebook reports missing input files, run the previous module first.
- If API generation fails in Module 4C, use the deterministic Module 4 demo.
- If package imports fail, rerun `pip install -r requirements.txt` and restart the kernel.
- If validation fails, rerun the notebooks in order from Module 1 to Module 4 before running `final_validation_tests.ipynb`.
