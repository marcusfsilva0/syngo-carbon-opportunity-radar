import os
import re
import json
import hashlib
from datetime import datetime, timedelta, timezone, date
from urllib.parse import quote_plus, urlparse

import feedparser
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Enterprise Imaging Opportunity Radar", page_icon="🎯", layout="wide")

# Product profile based on the two user-supplied Siemens Healthineers brochures.
# This taxonomy is a screening aid, not approved product positioning or a technical qualification.
PROFILE = {
    "portfolio": "syngo Carbon",
    "region": "North America",
    "documented_capabilities": [
        "patient-centric enterprise image and data management across DICOM and non-DICOM data",
        "vendor-neutral archive (VNA) foundation",
        "scalable and modular image and data management architecture",
        "multi-site archive using Master Patient Index (MPI) support",
        "information lifecycle management (ILM), storage pools, and long-term archiving",
        "zero-footprint HTML5 enterprise viewer for DICOM and non-DICOM clinical content",
        "diagnostic workspace combining reading, reporting, advanced visualization, and workflow tools",
        "DICOM and HL7 interfaces, plus FHIR and XDS/XDS-I connectivity described in the data sheet",
        "AI-result workflow integration; AI-Rad Companion described as an optional addition",
        "web-based access to enterprise imaging data and connected archives"
    ],
    "match_terms": {
        "enterprise image/data management": ["enterprise imaging", "enterprise image", "image and data management", "image management", "imaging platform"],
        "VNA / vendor neutrality": ["vendor neutral archive", "vendor-neutral archive", "vna", "vendor neutral", "archive consolidation"],
        "PACS / archive modernization": ["pacs", "archive replacement", "archive modernization", "pacs replacement", "pacs modernization"],
        "enterprise viewing": ["zero footprint", "zero-footprint", "enterprise viewer", "web viewer", "web-based viewer", "universal viewer"],
        "interoperability": ["dicom", "hl7", "fhir", "xds", "interoperability", "integration", "interface"],
        "data consolidation / multi-site": ["multi-site", "multi site", "consolidation", "data silos", "patient-centric", "patient centric", "multiple hospitals"],
        "data lifecycle / archive scale": ["information lifecycle", "long-term archive", "long term archive", "storage pool", "archive migration", "petabyte", "large data volumes"],
        "clinical workflow / AI": ["image to report", "imaging workflow", "radiology workflow", "ai result", "artificial intelligence", "worklist", "reporting workflow"]
    },
    "buying_signals": [
        "request for proposal", "rfp", "request for information", "rfi", "sources sought", "solicitation", "tender", "procurement", "bid",
        "pacs replacement", "pacs modernization", "enterprise imaging strategy", "vna procurement", "contract expiration",
        "technology refresh", "vendor selection", "system replacement", "platform replacement"
    ],
    "early_signals": [
        "digital transformation", "cloud migration", "data center modernization", "hospital merger", "health system acquisition",
        "new hospital", "imaging expansion", "it modernization", "interoperability initiative", "standardization", "consolidation",
        "capital investment", "enterprise architecture", "image exchange", "archive strategy"
    ],
    "competitors": ["GE HealthCare", "Philips", "Sectra", "Agfa", "Intelerad", "Fujifilm", "Change Healthcare"],
    "qualification_cautions": [
        "Cloud hosting/deployment architecture is not established by the brochures; cloud storage connectivity is not the same as a complete cloud-hosted solution.",
        "The brochures do not establish the complete cardiology-specific diagnostic workflow or every specialty application in a combined radiology/cardiology tender.",
        "AI-result workflow and optional AI-Rad Companion references do not prove that every requested third-party AI platform or hosted AI service is covered.",
        "Exact throughput, petabyte migration scale, uptime SLA, recovery objectives, and service-level commitments require technical validation.",
        "Regulatory clearances, OEM/principal-contractor eligibility, procurement terms, and bid compliance must be checked against the solicitation and regulatory records."
    ]
}

SEARCH_QUERIES = [
    '"enterprise imaging" hospital RFP OR procurement OR tender North America',
    'PACS replacement OR modernization hospital health system North America',
    '"vendor neutral archive" hospital RFP OR procurement OR implementation',
    'health system imaging consolidation OR enterprise imaging strategy',
    'hospital digital transformation imaging infrastructure modernization',
    'health system PACS contract award OR imaging platform vendor',
    '"radiology and cardiology" enterprise imaging RFI OR RFP'
]

REFERENCE_CASES = [
    {
        "case_id": "VA-36C10B27R0003",
        "title": "Radiology and Cardiology Foundational Enterprise Imaging System",
        "organization": "U.S. Department of Veterans Affairs",
        "region": "New Jersey / U.S. federal procurement",
        "type": "Active procurement",
        "notice_type": "Combined Synopsis/Solicitation",
        "published": "2026-11-16",
        "deadline": "2026-12-09",
        "status": "Active as indexed on 2026-11-17",
        "solicitation_number": "36C10B27R0003",
        "notice_id": "0b48a6495bdb4fe5b3cb53e0b962a913",
        "url": "https://sam.gov/opp/0b48a6495bdb4fe5b3cb53e0b962a913/view",
        "source": "SAM.gov (official record); third-party listing used only to inspect indexed metadata",
        "summary": "Officially visible metadata identifies a VA combined synopsis/solicitation for a Radiology and Cardiology Foundational Enterprise Imaging System. The SAM.gov description itself says to see the attached solicitation. A third-party listing's AI-generated secondary summary (not authoritative solicitation text) reports a PACS diagnostic viewer, vendor neutral archive (VNA), radiology and cardiology worklists/assignment engine, voice-recognition integration, an AI platform hosted in VA Enterprise Cloud, migration of about 20 petabytes, and an estimated 12 million exams annually. Treat those details as hypotheses until checked against the official solicitation and attachments.",
        "expected_classification": "Active procurement",
        "expected_fit": "Strong potential thematic alignment; technical/bid qualification unresolved",
        "documented_matches": ["enterprise image/data management", "VNA / vendor neutrality", "PACS / archive modernization", "enterprise viewing", "interoperability"],
        "gaps": ["cardiology-specific requirements", "cloud hosting architecture", "AI platform scope", "scale/migration and SLA", "FDA 510(k)/OEM and bid eligibility"],
        "evaluation_note": "A strong positive detection test, but not proof that the solution meets every requirement or that Siemens should bid. Read the official solicitation and attachments."
    },
    {
        "case_id": "NJ-SW-121250",
        "title": "RFI for Cloud-Based Radiology and Cardiology Enterprise Imaging System - Sources Sought",
        "organization": "New Jersey public-sector authority (as described by RFPMart)",
        "region": "New Jersey, USA",
        "type": "Expired / historical procurement signal",
        "notice_type": "RFI / Sources Sought",
        "published": "2026-10-27",
        "deadline": "2026-11-10",
        "status": "Expired as of 2026-11-17",
        "solicitation_number": "SW-121250",
        "notice_id": "",
        "url": "https://www.rfpmart.com/1190069-usa-new-jersey-rfi-for-cloud-based-radiology-and-cardiology-enterprise-imaging-system-sources-sought-rfp.html",
        "source": "RFPMart (aggregator listing; verify against issuing authority)",
        "summary": "The RFPMart listing describes a cloud-based radiology and cardiology enterprise imaging system with advanced AI and third-party integration, expandable multispecialty diagnostic review/interpretation/reporting, zero-footprint web viewer, ad hoc query/retrieve with non-integrated systems, nuclear medicine raw-image storage/transfer/reprocessing/display and processing, research/AI data curation, national tumor-board review, redundant report archiving, and an inbound/outbound message-normalization broker. The listing labels this an RFI / Sources Sought, not a final RFP. Its November 10, 2026 response deadline has passed.",
        "expected_classification": "Expired / historical procurement signal",
        "expected_fit": "Partial thematic alignment; several requirements unverified",
        "documented_matches": ["enterprise image/data management", "enterprise viewing", "interoperability", "clinical workflow / AI"],
        "gaps": ["cloud hosting architecture", "cardiology-specific requirements", "nuclear medicine raw data processing", "research/AI data curation", "message broker/normalization"],
        "evaluation_note": "A date/status test and an early-market-engagement test. The system should not show this as an open RFP after its deadline."
    }
]


def clean_html(value):
    value = re.sub(r"<script.*?</script>|<style.*?</style>", " ", value or "", flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s[:19], fmt).date()
        except Exception:
            pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except Exception:
        return None


def google_news_rss(query, days):
    q = f"{query} when:{days}d"
    url = "https://news.google.com/rss/search?q=" + quote_plus(q) + "&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        published = ""
        if getattr(entry, "published_parsed", None):
            try:
                published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
        source_title = getattr(getattr(entry, "source", {}), "title", "Google News RSS")
        items.append({
            "title": getattr(entry, "title", "Untitled"),
            "url": getattr(entry, "link", ""),
            "source": source_title or "Google News RSS",
            "published": published,
            "deadline": "",
            "summary": clean_html(getattr(entry, "summary", "")),
            "notice_type": "",
            "procurement_status": "",
            "organization": "",
            "solicitation_number": "",
            "source_kind": "News search"
        })
    return items


def sam_gov_search(api_key, days):
    """Search official SAM.gov Get Opportunities Public API v2.
    User supplies their own public API key. SAM API date range is mandatory and max 1 year.
    """
    if not api_key:
        return [], "Add a SAM.gov public API key to enable direct federal opportunity search."
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=days)
    terms = ["enterprise imaging", "PACS", "radiology", "medical imaging", "image management", "cardiology"]
    ptypes = ["o", "r", "k", "p"]  # solicitation, sources sought, combined synopsis/solicitation, presolicitation
    found = []
    errors = []
    endpoint = "https://api.sam.gov/opportunities/v2/search"
    for term in terms:
        params = {
            "api_key": api_key,
            "postedFrom": start.strftime("%m/%d/%Y"),
            "postedTo": today.strftime("%m/%d/%Y"),
            "title": term,
            "limit": 100,
            "offset": 0,
        }
        params_list = list(params.items()) + [("ptype", t) for t in ptypes]
        try:
            response = requests.get(endpoint, params=params_list, timeout=25)
            response.raise_for_status()
            payload = response.json()
            records = payload.get("opportunitiesData", payload.get("data", [])) or []
            if isinstance(records, dict):
                records = records.get("opportunitiesData", [])
            for rec in records:
                deadline = rec.get("reponseDeadLine") or rec.get("responseDeadLine") or ""
                notice_id = rec.get("noticeId", "")
                ui_link = rec.get("uiLink") or (f"https://sam.gov/opp/{notice_id}/view" if notice_id else "")
                description = rec.get("description", "")
                summary = ""
                if description:
                    try:
                        desc_resp = requests.get(description, params={"api_key": api_key}, timeout=12)
                        if desc_resp.ok:
                            summary = clean_html(desc_resp.text)[:5000]
                    except Exception:
                        pass
                if not summary:
                    summary = "Official SAM.gov result. Open the original notice and attachments to review the description and requirements."
                found.append({
                    "title": rec.get("title", "Untitled SAM.gov opportunity"),
                    "url": ui_link,
                    "source": "SAM.gov Public Opportunities API",
                    "published": rec.get("postedDate", ""),
                    "deadline": deadline,
                    "summary": summary,
                    "notice_type": rec.get("type", ""),
                    "procurement_status": rec.get("active", ""),
                    "organization": rec.get("fullParentPathName", ""),
                    "solicitation_number": rec.get("solicitationNumber", ""),
                    "source_kind": "SAM.gov API",
                    "notice_id": notice_id
                })
        except Exception as exc:
            errors.append(f"{term}: {type(exc).__name__}")
    dedup, seen = [], set()
    for item in found:
        key = item.get("notice_id") or item.get("url") or item.get("title")
        if key not in seen:
            seen.add(key)
            dedup.append(item)
    message = f"SAM.gov API returned {len(dedup)} unique federal notices."
    if errors:
        message += " Some searches failed: " + "; ".join(errors[:3])
    return dedup, message


def classify_and_match(item):
    combined = " ".join([
        str(item.get("title", "")), str(item.get("summary", "")),
        str(item.get("notice_type", "")), str(item.get("solicitation_number", ""))
    ]).lower()
    deadline = parse_date(item.get("deadline"))
    published = parse_date(item.get("published"))
    today = datetime.now(timezone.utc).date()

    procurement_words = ["rfp", "request for proposal", "tender", "procurement", "solicitation"]
    rfi_words = ["rfi", "request for information", "sources sought", "market research"]
    direct_terms = ["enterprise imaging", "pacs", "vendor neutral archive", "vna", "image management"]
    early_terms = ["digital transformation", "cloud migration", "modernization", "consolidation", "acquisition", "merger", "expansion", "interoperability", "capital investment"]
    competitor_hits = [name for name in PROFILE["competitors"] if name.lower() in combined]

    notice_type = (item.get("notice_type") or "").lower()
    procurement_intent = any(w in combined for w in procurement_words) or any(w in notice_type for w in ["solicitation", "tender"])
    rfi_intent = any(w in combined for w in rfi_words) or "sources sought" in notice_type
    expired = bool(deadline and deadline < today)

    if expired and (procurement_intent or rfi_intent):
        typ = "Expired / historical procurement signal"
    elif rfi_intent:
        typ = "RFI / sources sought"
    elif procurement_intent:
        typ = "Active procurement"
    elif competitor_hits:
        typ = "Competitive signal"
    elif any(w in combined for w in direct_terms):
        typ = "Emerging opportunity"
    elif any(w in combined for w in early_terms):
        typ = "Early buying signal"
    else:
        typ = "General market signal"

    matched = []
    for group, terms in PROFILE["match_terms"].items():
        hits = [term for term in terms if term in combined]
        if hits:
            matched.append({"capability": group, "evidence_terms": hits[:5]})

    buy_hits = [term for term in PROFILE["buying_signals"] if term.lower() in combined]
    early_hits = [term for term in PROFILE["early_signals"] if term.lower() in combined]
    match_groups = len(matched)
    # Transparent screening score. It is NOT probability of purchase, technical fit, or win probability.
    score = min(100, 10 + 7 * match_groups + 5 * min(len(buy_hits), 3) + 3 * min(len(early_hits), 3))
    if typ == "Active procurement": score = min(100, score + 10)
    if typ == "RFI / sources sought": score = min(100, score + 8)
    if typ == "Expired / historical procurement signal": score = min(score, 35)
    if typ == "Competitive signal": score = min(100, score + 5)

    gaps = []
    gap_map = [
        (["cloud", "hosted", "saas"], "Cloud hosting/deployment architecture requires validation; storage connectivity alone does not prove a complete cloud-hosted service."),
        (["cardiology", "echocardiography", "cath", "electrophysiology"], "Cardiology-specific workflow and diagnostic functionality must be validated; the supplied brochures do not substantiate the complete cardiology scope."),
        (["nuclear medicine", "nm raw", "raw image"], "Nuclear medicine raw-data handling and full processing requirements need technical validation."),
        (["petabyte", "million exams", "uptime", "rto", "rpo", "99.99"], "Exact scale, throughput, uptime and recovery commitments are not established by the brochures."),
        (["fda", "510(k)", "oem", "original equipment manufacturer", "prime contractor"], "Regulatory clearance, OEM/principal-contractor status and bid eligibility must be validated separately."),
        (["third-party ai", "third party ai", "ai platform", "ai assurance"], "The brochure describes AI-result workflow integration and optional AI-Rad Companion; requested platform scope and third-party coverage need validation."),
        (["message broker", "message normalization", "broker"], "An integrated message broker/normalization requirement is not explicitly established by the supplied brochures."),
        (["migration", "migrate", "historical images"], "Migration scope, tooling, sequencing and capacity require a technical assessment; do not infer fit from archive scalability alone.")
    ]
    for needles, message in gap_map:
        if any(n in combined for n in needles):
            gaps.append(message)

    rationale = []
    if matched:
        rationale.append("Potential matches to documented brochure themes: " + "; ".join(m["capability"] for m in matched))
    if buy_hits:
        rationale.append("Buying/procurement signals: " + ", ".join(buy_hits[:5]))
    if early_hits:
        rationale.append("Early-stage signals: " + ", ".join(early_hits[:4]))
    if not rationale:
        rationale.append("No strong documented syngo Carbon or buying-signal matches; manual review recommended.")

    return {
        **item,
        "type": typ,
        "deadline_parsed": deadline.isoformat() if deadline else "",
        "score": score,
        "fit_strength": "Strong potential thematic alignment" if match_groups >= 5 else ("Partial thematic alignment" if match_groups >= 2 else ("Limited thematic alignment" if match_groups == 1 else "Unclear from available evidence")),
        "matched_capabilities": matched,
        "rationale": " ".join(rationale),
        "qualification_gaps": gaps,
        "confidence": "Needs human validation"
    }


def ai_enrich(items, api_key):
    if not api_key or not items:
        return items, "Keyword screening is active. Add an OpenAI API key for a second-pass AI assessment."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        profile_text = "\n".join("- " + x for x in PROFILE["documented_capabilities"])
        caution_text = "\n".join("- " + x for x in PROFILE["qualification_cautions"])
        for item in items:
            prompt = f"""You are a cautious enterprise imaging market-intelligence analyst. Evaluate whether this public item could be relevant to Siemens Healthineers syngo Carbon.

Use ONLY this product profile, which is based on the user's supplied brochures. Do not add product capabilities from general knowledge:
{profile_text}

Known qualification cautions:
{caution_text}

Classify as exactly one of: Active procurement, RFI / sources sought, Early buying signal, Emerging opportunity, Competitive signal, Expired / historical procurement signal, General market signal.
Return valid JSON with keys: classification, organization, relevance_score (0-100 screening score, not win probability), potential_syngo_carbon_alignment, supporting_evidence (quote or precise paraphrase only from supplied item), gaps_to_validate (array), recommended_human_next_step, procurement_deadline, deadline_status, uncertainty.
Never invent customer intent, product capability, cloud deployment, cardiology functions, migration capacity, regulatory clearance, OEM status, RFP status, deadline, installed base, or account ownership. If the supplied source summary is third-party or AI-generated, say that.

ITEM:
Title: {item.get('title','')}
Source: {item.get('source','')}
Published: {item.get('published','')}
Deadline: {item.get('deadline','')}
Notice type: {item.get('notice_type','')}
Organization: {item.get('organization','')}
Summary: {item.get('summary','')}
URL: {item.get('url','')}
Current date: {datetime.now(timezone.utc).date().isoformat()}
"""
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            data = json.loads(response.choices[0].message.content)
            item["ai"] = data
            item["score"] = max(0, min(100, int(data.get("relevance_score", item["score"]))))
            item["confidence"] = "AI assessed; verify supporting evidence"
            item["ai_alignment"] = data.get("potential_syngo_carbon_alignment", "")
            item["ai_gaps"] = data.get("gaps_to_validate", [])
            item["ai_next_step"] = data.get("recommended_human_next_step", "")
        return items, "AI-assisted second-pass assessment enabled. Verify each result against the original source and product requirements."
    except Exception as exc:
        return items, f"AI enrichment unavailable ({type(exc).__name__}); showing keyword-based screening instead."


def deduplicate(items):
    unique, seen = [], set()
    for item in items:
        key = item.get("notice_id") or item.get("url") or hashlib.md5(item.get("title", "").encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


st.title("🎯 Enterprise Imaging Opportunity Radar")
st.caption("North America · syngo Carbon · Public information only")
st.info("Prototype for market sensing, not lead qualification or a bid/no-bid system. It identifies signals; it does not establish technical compliance or customer intent.")

with st.sidebar:
    st.header("Search settings")
    days = st.selectbox("Look-back period", [7, 14, 30], index=0)
    max_items = st.slider("Maximum findings", 10, 100, 50, 10)
    st.divider()
    st.subheader("Data connections")
    sam_key = st.text_input("SAM.gov public API key (optional)", type="password", value=os.getenv("SAM_GOV_API_KEY", ""))
    openai_key = st.text_input("OpenAI API key (optional)", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    st.caption("SAM.gov API key is required for direct federal notice search. Google News RSS is used for broader public news discovery.")
    st.divider()
    run = st.button("Run opportunity scan", type="primary", use_container_width=True)
    st.caption("Screening score is not purchase probability, product qualification, or win probability. Always verify source, date, status, deadline and requirements.")

if "results" not in st.session_state:
    st.session_state.results = []
if "scan_message" not in st.session_state:
    st.session_state.scan_message = "Run a scan to retrieve current public signals."

if run:
    raw = []
    messages = []
    progress = st.progress(0, text="Searching public sources…")
    sam_items, sam_msg = sam_gov_search(sam_key, days)
    raw.extend(sam_items)
    messages.append(sam_msg)
    progress.progress(0.2, text="Searching selected healthcare news queries…")
    for i, query in enumerate(SEARCH_QUERIES):
        try:
            raw.extend(google_news_rss(query, days))
        except Exception as exc:
            messages.append(f"RSS query issue ({type(exc).__name__}).")
        progress.progress(0.2 + 0.7 * (i + 1) / len(SEARCH_QUERIES), text=f"Searching news query {i+1} of {len(SEARCH_QUERIES)}…")
    unique = deduplicate(raw)
    analyzed = [classify_and_match(item) for item in unique]
    analyzed.sort(key=lambda x: (x["score"], x.get("published", "")), reverse=True)
    analyzed = analyzed[:max_items]
    analyzed, ai_msg = ai_enrich(analyzed, openai_key)
    messages.append(ai_msg)
    st.session_state.results = analyzed
    st.session_state.scan_message = f"Collected {len(unique)} unique public results; displaying {len(analyzed)}. " + " ".join(messages)
    progress.progress(1.0, text="Scan complete.")

items = st.session_state.results
st.caption(st.session_state.scan_message)

results_tab, examples_tab, profile_tab = st.tabs(["Live scan results", "RFP examples & evaluation cases", "Syngo Carbon matching profile"])

with results_tab:
    if items:
        active = sum(x["type"] == "Active procurement" for x in items)
        rfi = sum(x["type"] == "RFI / sources sought" for x in items)
        early = sum(x["type"] in ["Early buying signal", "Emerging opportunity"] for x in items)
        expired = sum(x["type"] == "Expired / historical procurement signal" for x in items)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Signals found", len(items))
        c2.metric("Active procurement", active)
        c3.metric("RFI / sources sought", rfi)
        c4.metric("Early / emerging", early)
        c5.metric("Expired references", expired)

        df = pd.DataFrame(items)
        f1, f2, f3 = st.columns([1.4, 1, 1.5])
        with f1:
            selected_types = st.multiselect("Filter by signal type", sorted(df["type"].unique()), default=sorted(df["type"].unique()))
        with f2:
            min_score = st.slider("Minimum screening score", 0, 100, 0, 5)
        with f3:
            search_text = st.text_input("Search organization / topic")

        filtered = [x for x in items if x["type"] in selected_types and x["score"] >= min_score and search_text.lower() in (x.get("title", "") + " " + x.get("summary", "") + " " + x.get("organization", "")).lower()]
        for item in filtered:
            with st.container(border=True):
                top = st.columns([5, 1, 1.6])
                top[0].markdown(f"**{item['title']}**")
                top[1].metric("Screening score", item["score"])
                top[2].write(f"**{item['type']}**")
                st.caption(f"{item.get('organization') or item.get('source')} · Published: {item.get('published') or 'Not parsed'} · Deadline: {item.get('deadline') or 'Not identified'} · {item.get('confidence')}")
                if item.get("summary"):
                    st.write(item["summary"][:1200])
                st.write("**Potential syngo Carbon alignment:**", item.get("ai_alignment") or item["fit_strength"])
                if item.get("matched_capabilities"):
                    st.write("**Brochure themes detected:**", ", ".join(x["capability"] for x in item["matched_capabilities"]))
                st.write("**Screening rationale:**", item["rationale"])
                gaps = item.get("ai_gaps") or item.get("qualification_gaps") or []
                if gaps:
                    st.warning("**Gaps / unknowns to validate:** " + " | ".join(str(g) for g in gaps))
                if item.get("ai_next_step"):
                    st.write("**Recommended human next step:**", item["ai_next_step"])
                else:
                    st.write("**Recommended human next step:** Open the original notice, confirm active status and deadline, and compare mandatory requirements against approved product/technical documentation.")
                if item.get("url"):
                    st.markdown(f"[Open original source]({item['url']})")

        export = pd.DataFrame([{
            "title": x.get("title"), "organization": x.get("organization"), "type": x.get("type"),
            "screening_score": x.get("score"), "fit_strength": x.get("fit_strength"),
            "published": x.get("published"), "deadline": x.get("deadline"), "notice_type": x.get("notice_type"),
            "source": x.get("source"), "url": x.get("url"), "summary": x.get("summary"),
            "matched_capabilities": json.dumps(x.get("matched_capabilities", [])),
            "qualification_gaps": json.dumps(x.get("qualification_gaps", [])),
            "ai_assessment": json.dumps(x.get("ai", {}), ensure_ascii=False)
        } for x in filtered])
        st.download_button("Download filtered findings as CSV", export.to_csv(index=False).encode("utf-8"), "syngo_carbon_opportunity_radar.csv", "text/csv")
    else:
        st.subheader("How to use the prototype")
        st.markdown("""
        1. Add a SAM.gov public API key in the sidebar for direct federal opportunity search (optional but recommended).
        2. Optionally add an OpenAI API key for a second-pass assessment grounded in the brochure profile.
        3. Select **Run opportunity scan**.
        4. Review the findings, open the original source, validate deadline/status and review the technical requirements.
        5. Export the findings to CSV for further evaluation.
        """)
        st.warning("No live findings are displayed until you run a scan. A scan without a SAM.gov key will use Google News RSS only and will not search the complete federal notice database.")

with examples_tab:
    st.subheader("Reference RFP/RFI examples supplied for evaluation")
    st.write("These are a small labelled test set, not live scan results. The agent should find, classify and match similar notices correctly.")
    for case in REFERENCE_CASES:
        with st.container(border=True):
            left, right = st.columns([4, 1.5])
            left.markdown(f"**{case['title']}**")
            left.caption(f"{case['organization']} · {case['region']} · {case['notice_type']}")
            left.write(case["summary"])
            left.write(f"**Expected classification:** {case['expected_classification']}")
            left.write(f"**Expected alignment:** {case['expected_fit']}")
            left.write(f"**Documented match themes:** {', '.join(case['documented_matches'])}")
            left.warning("**Qualification gaps:** " + "; ".join(case["gaps"]))
            left.caption(case["evaluation_note"])
            right.metric("Published", case["published"])
            right.metric("Response deadline", case["deadline"])
            right.write(f"**Status:** {case['status']}")
            right.write(f"**Notice / solicitation:** {case['solicitation_number']}")
            right.markdown(f"[Open source record]({case['url']})")
    st.download_button("Download labelled evaluation cases (JSON)", json.dumps(REFERENCE_CASES, indent=2).encode("utf-8"), "syngo_carbon_reference_cases.json", "application/json")

with profile_tab:
    st.subheader("Product capability profile used for matching")
    st.caption("Derived from the supplied Syngo Carbon Core VA23A data sheet and Syngo Carbon Elevator Flyer USA 2026. Validate against current approved product positioning before external use.")
    for capability in PROFILE["documented_capabilities"]:
        st.markdown(f"- {capability}")
    st.divider()
    st.subheader("Qualification cautions the agent is instructed to preserve")
    for caution in PROFILE["qualification_cautions"]:
        st.warning(caution)
    st.caption("The data sheet notes that Syngo Carbon comprises separate products/options and that some products may not be commercially available in all markets. The app therefore avoids assuming every platform capability is included in every configuration.")

with st.expander("Methodology, data sources and responsible use"):
    st.markdown("""
    **Sources.** Optional direct integration with the SAM.gov Get Opportunities Public API v2 (requires the user's own SAM.gov public API key) plus Google News RSS queries for broader public healthcare news discovery. Search coverage is not comprehensive and may miss state, provincial, hospital, and paid procurement portals.

    **Classification.** The application distinguishes active solicitations, RFIs/sources sought, early buying signals, competitive signals, and expired/historical procurement signals. When an explicit response deadline is parsed and has passed, the notice is labelled expired/historical rather than active.

    **Portfolio matching.** Matching is grounded in a curated profile derived from the user-supplied product brochures: patient-centric and vendor-neutral IDM/VNA; DICOM and non-DICOM data management; scalable/modular architecture; zero-footprint enterprise viewer; interoperability; and workflow/AI-result integration. Keyword overlap indicates a reason to investigate, not proof of technical compliance.

    **Scoring.** The score is a transparent screening heuristic based on matched brochure themes and buying signals. It is not a forecast of purchase, a technical fit score, or a win probability. Optional LLM analysis is a second opinion and can still be wrong.

    **Human checks.** Open the original issuing-authority notice, verify whether it is still active, check every amendment and attachment, confirm response deadline and eligibility, and validate every mandatory requirement with current approved product, regulatory, and technical documentation. Do not use a third-party AI summary as the authoritative solicitation.

    **Privacy/security.** API keys are entered at runtime and should never be committed to a repository. Do not enter confidential customer details or internal Siemens information into this public-information prototype.
    """)
