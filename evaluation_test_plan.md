# Evaluation test plan – v0.2

Use the labelled examples in the app as a fixed test set. Record actual outcomes after running the application; do not fill in imagined results.

| Test | Input / expected result | What to inspect | Observed result | Change made |
|---|---|---|---|---|
| VA active solicitation | SAM.gov notice 0b48a6495bdb4fe5b3cb53e0b962a913; posted Nov 16, 2026; deadline Dec 9, 2026. Expected: Active procurement. | Can the agent retrieve it from SAM.gov API? Does it capture deadline, notice type, solicitation number and original URL? | | |
| New Jersey RFI | RFPMart item SW-121250; posted Oct 27, 2026; deadline Nov 10, 2026. Expected on Nov 17: Expired / historical procurement signal, not active RFP. | Does it distinguish RFI/Sources Sought from a solicitation? Does it prevent an expired item from being shown as open? | | |
| Relevant enterprise imaging RFP | An RFP for PACS/VNA/enterprise imaging should have high screening relevance. | Which brochure themes matched? Did it distinguish evidence from inference? | | |
| Irrelevant hospital RFP | Unrelated hospital equipment/service tender should not rank as a syngo Carbon prospect. | False positive caused by generic words such as hospital, technology, or procurement. | | |
| Early buying signal | Hospital announces imaging archive consolidation or PACS modernization, with no published RFP. Expected: Early buying signal / Emerging opportunity. | Does the system detect signals without requiring the literal term “enterprise imaging”? | | |
| Competitor contract award | A competitor is selected for an imaging platform. Expected: Competitive signal, not a new direct opportunity. | Does it distinguish competitive intelligence from a prospect? | | |
| Generic AI news | AI news without imaging or procurement evidence should rank low or as a general market signal. | Does the system overreact to generic AI wording? | | |
| Duplicate syndication | Same announcement appears from multiple publishers. Expected: duplicate suppression where URLs/notice IDs are identical. | Do duplicates inflate signal count? | | |
| Missing/ambiguous deadline | Notice has no parseable response date. Expected: “Not identified” and manual check, not assumed open. | Does the app avoid inventing a deadline or open status? | | |
| Unsupported product inference | Cloud, cardiology, large-scale migration, nuclear medicine raw data, AI platform, SLA, or regulatory/OEM requirements appear. | Does the system surface capability gaps rather than claim compliance from generic brochure language? | | |

## Product grounding checklist

The brochure profile can support screening for: patient-centric image/data management; DICOM and non-DICOM content; vendor-neutral archive; scalable/modular and multi-site architecture; zero-footprint enterprise viewing; DICOM/HL7, FHIR and XDS/XDS-I connectivity; information lifecycle management; diagnostic workspace and AI-result workflow positioning.

Do not treat the brochures alone as evidence of: a complete cloud-hosted SaaS implementation; every cardiology specialty application; all third-party AI integrations; full raw nuclear medicine processing; message-broker normalization; 20 PB migration capacity; a 12-million-exam annual throughput; uptime/RTO/RPO commitments; FDA clearance for each component; or OEM/principal-contractor eligibility.

## Evaluation note prompts

- What percentage of relevant examples were correctly detected and classified?
- What false positives and false negatives occurred?
- Did the deadline/status logic work correctly?
- Did the AI confuse a third-party summary with official solicitation language?
- Did it overstate the product match? Which specific requirement exposed the overstatement?
- What source, query, rule, scoring factor, prompt or UI behavior did you change as a result?
- Where could a salesperson still be misled, and what safeguard would you build next?
