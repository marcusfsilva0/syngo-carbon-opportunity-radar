# Honest build account – complete after running and testing v0.2

I built a Streamlit application that combines a SAM.gov public-opportunities search (when a user supplies an API key) with Google News RSS discovery. It deduplicates findings, classifies procurement stage and early market signals, captures deadlines where available, and screens each item against a curated syngo Carbon capability profile derived from the two supplied brochures. It includes a labelled evaluation case set and optional LLM second-pass analysis.

AI assistance was used to generate and revise application code, search-query ideas, the product-matching taxonomy, and the structured LLM assessment prompt. I selected the business problem and scope, supplied the reference RFP/RFI examples and product collateral, and should explain how the source connectors, rules, deadline parsing, scoring and LLM assessment work.

Before submission, I should document:
- Which code sections I can explain and which I still need to understand.
- Whether the SAM.gov key worked and which notices the API returned.
- What RSS sources returned and what they missed.
- Which tests I ran, including the active VA solicitation and expired New Jersey RFI.
- False positives, false negatives, source errors, date errors and unsupported product inferences found.
- What I changed in response to actual test failures.
- What remains unverified, especially bid compliance and technical requirements.

Do not submit this template unchanged. Replace it with an accurate account of what actually ran, what AI generated, what you reviewed or changed, and what you still do not understand.
