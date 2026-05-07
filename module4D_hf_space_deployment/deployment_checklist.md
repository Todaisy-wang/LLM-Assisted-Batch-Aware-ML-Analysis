# Module 4D Hugging Face Spaces Deployment Checklist

- [x] `app.py` created
- [x] `requirements.txt` created
- [x] `README.md` created
- [x] Required lightweight evidence files copied
- [x] No API key included
- [x] Deterministic fallback available
- [x] Gradio app defined
- [x] `app.py` syntax check passed
- [x] Local import smoke test passed with dependency stubs

## Validation Notes

- `python -m py_compile module4D_hf_space_deployment/app.py` passed.
- Plain local import was not possible because this environment does not have `gradio` installed.
- A dependency-stub import smoke test passed and confirmed:
  - `demo` is defined
  - evidence corpus is built
  - `chatbot_response(...)` returns a response
  - missing API key uses deterministic fallback

## Evidence Files

- [x] `module2_outputs/module2_llm_ready_patterns.json`
- [x] `module2_outputs/module2_pattern_table_with_sentences.csv`
- [x] `module2_outputs/module2_classifier_summary.csv`
- [x] `module3_outputs/module3B_evidence_pack.json`
- [x] `module3_outputs/module3D_llm_analysis.json`
- [x] `module3_outputs/module3E_grounding_summary.json`
- [x] `module4_outputs/module4_answer_quality_summary.json`

## Upload Steps

1. Create a new Hugging Face Space with SDK set to Gradio.
2. Upload all contents of `module4D_hf_space_deployment/`.
3. Add `OPENAI_API_KEY` as a Space Secret for API-generated answers.
4. Leave the secret unset to use deterministic fallback mode.
