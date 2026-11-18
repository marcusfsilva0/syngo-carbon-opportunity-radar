# Reference-case logic smoke test results (v0.2)

**Test type:** Offline logic smoke test using the two hand-curated reference records embedded in `app.py`. This verifies deadline parsing, classification and brochure-theme matching logic only. It does NOT verify the live SAM.gov API connector, Google News RSS retrieval, the OpenAI API call, or the full deployed application.

| Reference case | Expected classification | Observed classification | Deadline parsed | Screening score | Brochure-theme match result | Result |
|---|---|---|---|---:|---|---|
| VA / 36C10B27R0003 | Active procurement | Active procurement | 2026-12-09 | 67 | Strong potential thematic alignment | Pass |
| New Jersey / SW-121250 | Expired / historical procurement signal | Expired / historical procurement signal | 2026-11-10 | 35 | Partial thematic alignment | Pass |

## Interpretation

- The test confirms the app does not treat the New Jersey sources-sought RFI as an open opportunity after its response deadline.
- The VA notice is classified as an active solicitation and receives a relatively high screening score due to multiple enterprise imaging/VNA/PACS/workflow terms.
- The score is deliberately a screening heuristic, not a probability of bid success or evidence that all requirements are met.
- The VA secondary listing uses AI-generated scope summaries. Detailed figures and requirements such as exam volume, migration volume, cloud architecture, uptime, regulatory status and OEM requirements must be verified against the official SAM.gov solicitation attachments.
- The New Jersey item includes cloud, cardiology, nuclear medicine and message-broker requirements that the two supplied brochures do not fully substantiate.

## Remaining validation before calling the MVP end-to-end tested

1. Install dependencies from `requirements.txt` and run Streamlit locally.
2. Obtain a SAM.gov public API key and confirm the connector returns expected notices for the selected date range.
3. Confirm whether the SAM.gov description endpoint returns usable text with the API key and whether attachment links are accessible.
4. Run Google News RSS searches and record their coverage gaps and duplicates.
5. Test AI enrichment with an OpenAI API key, checking unsupported claims and citation/evidence quality.
6. Test malformed dates, missing dates, API timeouts, empty results, and rate-limit responses.
7. Review all actual RFP specifications against approved product, legal, regulatory, and technical documentation before making any commercial recommendation.
