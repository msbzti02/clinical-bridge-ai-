# Reflective Analysis: ClinicalBridge Project

## Overview
This document serves as a reflective analysis of the development process for the ClinicalBridge capstone project, discussing what worked, what broke, prompt iteration learnings, and considerations for future iterations.

## What Broke During Development
The biggest challenge during the development of this multi-agent system was handling edge cases where data was sparse or contradictory. 
Initially, the `EHRRetrievalAgent` (in its v1.0 and v2.0 prompts) had a strong tendency to hallucinate "normal" findings when the vector store returned no relevant chunks for a clinical question. If asked "Is there a history of chronic kidney disease?", instead of explicitly stating that no data was found, the model would occasionally synthesize a response like "Patient has no history of chronic kidney disease," which is a dangerous assumption in a clinical context. We mitigated this in v3.0 by explicitly providing few-shot examples that demonstrate how to handle empty or irrelevant retrieval results safely.

Another significant breaking point was the string-based parsing of JSON outputs from the LLMs. Relying on `response_text.find("{")` was brittle. Whenever the model decided to include markdown formatting (like ```json), the parsing would occasionally fail or require hacky workarounds. Moving to LangChain's `.with_structured_output()` and utilizing Pydantic models directly resolved this fragility completely, ensuring that our downstream pipeline receives strongly typed objects.

## Prompt Iteration Learnings
The evolution from v1.0 to v3.0 prompts revealed the power of negative constraints. In early iterations of the `TriageAgent` and `SynthesisAgent`, the models would often slip into diagnostic language (e.g., "This indicates the patient has heart failure"). We learned that simply saying "Do not diagnose" was insufficient. The v3.0 prompts introduced explicit "WHAT NOT TO DO" blocks and provided concrete examples of acceptable, non-diagnostic phrasing ("Findings are consistent with..."). 

Furthermore, the addition of a `reasoning_trace` proved invaluable not just for auditability, but for the model's own performance. Forcing the model to output its step-by-step logic before making a final classification (like determining urgency) noticeably reduced misclassifications in edge cases.

## What I Would Do Differently
If starting this project again:
1. **Adopt LangChain Sooner**: I initially built custom LLM wrappers because it felt simpler, but as the need for structured outputs and complex prompts grew, the custom code became a liability. Leveraging LangChain from day one would have saved significant refactoring time.
2. **More Diverse Edge Cases**: While we have 5 defined scenarios (including a missed medication and a false alarm), I would invest more time upfront in generating "noisy" or "dirty" EHR data to test the retrieval agent's robustness against typos and medical abbreviations.
3. **Automate Prompt Evaluation**: Evaluating prompt v1 vs v2 was largely manual. I would build a parameterized evaluation suite that automatically runs a subset of test cases against multiple prompt versions simultaneously to quantitatively measure improvement.
