# Enterprise Imaging Opportunity Radar – syngo Carbon MVP v0.2

A focused MBA prototype for identifying North American public-sector procurement notices and healthcare market signals that may be relevant to Siemens Healthineers syngo Carbon.

## What's new in v0.2

- Focused product matching based on the two user-supplied syngo Carbon brochures.
- Distinguishes active procurement, RFI/sources sought, early buying signals, competitive signals, and expired/historical notices.
- Detects and surfaces explicit response deadlines; expired procurement signals are not treated as open opportunities.
- Optional direct SAM.gov Get Opportunities Public API v2 integration.
- Broader public healthcare news discovery via Google News RSS.
- Optional OpenAI second-pass assessment grounded in the brochure profile and explicit qualification cautions.
- Includes the two supplied RFP/RFI examples as labelled evaluation cases, separate from live scan results.
- CSV export and product matching profile tab.

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
```

4. Install dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Optional API keys

### SAM.gov
The direct federal procurement connector uses the official Get Opportunities Public API v2 and requires a SAM.gov public API key. Create a key through your SAM.gov account details, then paste it into the app's sidebar. The application searches titles for enterprise imaging, PACS, radiology, medical imaging, image management, and cardiology, across solicitation, sources sought, combined synopsis/solicitation, and presolicitation types.

The SAM.gov API requires `postedFrom` and `postedTo` date parameters and limits the requested posting-date range to one year. This app uses the selected 7/14/30-day look-back. See the [official GSA API documentation](https://open.gsa.gov/api/get-opportunities-public-api/) for current API details.

### OpenAI
An OpenAI API key is optional. Without it, the app uses deterministic keyword screening. With it, each result receives an additional structured assessment using `gpt-4.1-mini`. Never commit API keys to source control. For deployment, use environment variables or the hosting provider's secrets manager.

## Reference cases included

1. **VA / SAM.gov – Radiology and Cardiology Foundational Enterprise Imaging System.** Notice posted November 16, 2026; response deadline December 9, 2026; solicitation 36C10B27R0003. The official SAM page is the source of record. A third-party indexed listing provides extra scope details, but its AI-generated summary must be checked against the original solicitation and attachments.
2. **New Jersey – RFI / Sources Sought for Cloud-Based Radiology and Cardiology Enterprise Imaging System.** Posted October 27, 2026; response deadline November 10, 2026. As of November 17, 2026, it is expired and should be treated as a historical test case, not an open RFP.

These examples appear under **RFP examples & evaluation cases** and are intentionally not injected into live scan results.

## Product capability profile

The starter profile is derived from the supplied Syngo Carbon Core VA23A data sheet and Syngo Carbon Elevator Flyer USA 2026. It emphasizes patient-centric and vendor-neutral image/data management, DICOM and non-DICOM data, VNA, scalability/modularity, multi-site/MPI, ILM, zero-footprint enterprise viewing, and interoperability. It also recognizes the brochure's AI-workflow positioning while preserving the fact that options/products may be separate or market-dependent.

The profile deliberately does **not** assume that brochure references prove a complete cloud-hosted solution, every cardiology-specific workflow, all third-party AI requirements, full nuclear medicine raw-data processing, very large migration capacity, particular uptime SLAs, regulatory clearances, or OEM eligibility.

## Important limitations

- Google News RSS is not exhaustive and is not a direct procurement database.
- SAM.gov search requires a public API key and covers federal opportunities, not every state/provincial/hospital procurement portal.
- Some SAM.gov descriptions or attachments may require separate retrieval or manual review.
- The app does not determine technical compliance, bid eligibility, customer intent, account ownership, or win probability.
- The scoring system is a screening heuristic. Human review of the original notice and approved product/technical materials is mandatory.

## Suggested deployment

Streamlit Community Cloud or another supported Streamlit host can run this app. Push `app.py`, `requirements.txt`, and supporting documentation to a repository. Store API keys in the host's secret manager, not in Git.
