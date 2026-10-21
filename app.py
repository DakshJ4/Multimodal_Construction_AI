import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

try:
    from google import genai
    from google.genai import types
except Exception:
    genai = None
    types = None

APP_NAME = "Multimodal Construction Intelligence Platform"
MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
      :root { --ink:#14212b; --muted:#637381; --accent:#f59e0b; --teal:#0f766e; }
      html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
      h1,h2,h3 { font-family:'Space Grotesk',sans-serif; letter-spacing:-.03em; }
      .stApp { background:linear-gradient(180deg,#f7fafc 0%,#eef3f6 100%); }
      [data-testid="stSidebar"] { background:#14212b; }
      [data-testid="stSidebar"] * { color:#f3f7fa !important; }
      .hero { padding:1.35rem 1.6rem; border-radius:22px; color:#fff;
        background:linear-gradient(120deg,#14212b 0%,#244653 62%,#0f766e 100%);
        box-shadow:0 14px 36px rgba(20,33,43,.13); margin-bottom:1rem; }
      .hero-kicker { text-transform:uppercase; letter-spacing:.16em; font-size:.75rem; color:#fbbf24; font-weight:700; }
      .hero h1 { color:#fff; margin:.35rem 0 .45rem; font-size:2.15rem; }
      .hero p { color:#dbe7ec; margin:0; max-width:900px; }
      .pill { display:inline-block; border-radius:999px; padding:.25rem .7rem; font-size:.78rem; font-weight:700; }
      .pill-good { background:#d1fae5; color:#065f46; }
      .pill-warn { background:#fef3c7; color:#92400e; }
      .pill-bad { background:#fee2e2; color:#991b1b; }
      .pill-neutral { background:#dbeafe; color:#1e40af; }
      .small-muted { color:#637381; font-size:.88rem; }
      .section-card { background:#fff; border:1px solid #e5edf1; border-radius:16px; padding:1rem 1.15rem; }
      div[data-testid="stMetric"] { background:#fff; padding:1rem; border:1px solid #e5edf1; border-radius:14px; }
      .stButton>button, .stDownloadButton>button { border-radius:10px; font-weight:700; }
      .disclaimer { border-left:4px solid #f59e0b; padding:.7rem 1rem; background:#fffbeb; border-radius:8px; color:#78350f; }
    </style>
    """,
    unsafe_allow_html=True,
)

def pill(label: str, kind: str = "neutral") -> str:
    return f'<span class="pill pill-{kind}">{label}</span>'

def safe_json_from_text(text: str) -> Dict[str, Any]:
    """Parse JSON even when a model wraps it in a Markdown code fence."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise ValueError("The model did not return valid JSON.")
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("Expected a JSON object.")
    return parsed

def get_api_key() -> str:
    sidebar_key = st.session_state.get("gemini_api_key", "").strip()
    if sidebar_key:
        return sidebar_key
    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        return os.getenv("GEMINI_API_KEY", "").strip()

def gemini_json(prompt: str, image_bytes: bytes, mime_type: str) -> Dict[str, Any]:
    key = get_api_key()
    if not key or genai is None or types is None:
        raise RuntimeError("Gemini is not configured; demonstration mode is active.")
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    if not getattr(response, "text", None):
        raise ValueError("Gemini returned an empty response.")
    return safe_json_from_text(response.text)

def demo_safety(filename: str) -> Dict[str, Any]:
    return {
        "safety_score": 78,
        "overall_status": "Needs Improvement",
        "ppe_detection": [
            {"item": "Hard hat / helmet", "status": "Needs verification", "evidence": "Demo result: inspect each worker and confirm secure fit."},
            {"item": "High-visibility vest", "status": "Needs verification", "evidence": "Demo result: confirm reflective vest is worn and visible."},
            {"item": "Steel-toe safety boots", "status": "Not verifiable from image", "evidence": "Footwear protection often cannot be confirmed from distant photos."},
            {"item": "Safety harness / fall protection", "status": "Context dependent", "evidence": "Verify harness, lanyard, and suitable anchor when working at height."},
        ],
        "hazards": [
            {"hazard": "Unprotected edge or fall exposure", "severity": "High", "evidence": "Illustrative demo finding; confirm on site.", "corrective_remedy": "Install compliant guardrails or a verified fall-arrest system; restrict access until corrected."},
            {"hazard": "Housekeeping / trip exposure", "severity": "Medium", "evidence": "Illustrative demo finding; confirm on site.", "corrective_remedy": "Clear walkways, secure cables and materials, and maintain designated access routes."},
        ],
        "limitations": "Demonstration data only; no image inference was performed.",
        "source_image": filename,
    }

def demo_crack(filename: str) -> Dict[str, Any]:
    return {
        "defect_type": "Hairline",
        "estimated_crack_width_mm": 0.3,
        "confidence": "Illustrative only",
        "possible_root_causes": ["Drying shrinkage", "Thermal movement", "Surface plaster movement"],
        "recommended_engineering_repairs": [
            "Map and photograph the crack; install tell-tales or gauges if movement is suspected.",
            "For stable, non-structural hairline cracks, use a compatible crack filler or polymer-modified repair system after substrate preparation.",
            "Escalate active, widening, diagonal, or load-related cracks to a licensed structural engineer before repair."
        ],
        "urgency": "Routine inspection",
        "limitations": "Demonstration data only; width and defect type have not been measured from the uploaded image.",
        "source_image": filename,
    }

SAFETY_PROMPT = """You are a construction site safety observation assistant. Inspect the supplied photo and return ONLY valid JSON with this schema:
{
 "safety_score": integer 0-100,
 "overall_status": "Compliant"|"Needs Improvement"|"Unsafe"|"Unable to Determine",
 "ppe_detection": [{"item": string, "status": "Observed"|"Not Observed"|"Unclear"|"Not Applicable", "evidence": string}],
 "hazards": [{"hazard": string, "severity": "Low"|"Medium"|"High"|"Critical", "evidence": string, "corrective_remedy": string}],
 "limitations": string
}
Check helmets, high-visibility vests, steel-toe boots, and safety harnesses/fall protection where relevant. Only report what is visible; do not claim boots are verified when feet are obscured. Distinguish observed facts from uncertainty. Include practical remedies. Treat this as preliminary visual screening, not certification. OSHA and Indian requirements vary by activity and jurisdiction; do not claim that a photo alone proves compliance. IS 456 primarily concerns plain and reinforced concrete, not a general PPE code; do not misrepresent it as one. Avoid asserting a legal violation unless the image supports it. If image quality/context is insufficient, state that clearly. Use concise values."""

CRACK_PROMPT = """You are a preliminary concrete and building-surface defect triage assistant. Inspect the supplied photo and return ONLY valid JSON:
{
 "defect_type": "Hairline"|"Settlement"|"Structural Shear"|"Thermal Expansion"|"Spalling"|"Other/Unclear",
 "estimated_crack_width_mm": number|null,
 "confidence": "Low"|"Medium"|"High",
 "possible_root_causes": [string],
 "recommended_engineering_repairs": [string],
 "urgency": "Monitor"|"Routine inspection"|"Prompt engineer review"|"Immediate safety assessment",
 "red_flags": [string],
 "limitations": string
}
Do not imply exact width can reliably be measured without a scale/reference. Distinguish surface plaster cracks from possible structural cracks. Do not prescribe epoxy injection or re-grouting automatically; recommendations depend on diagnosis, crack activity, substrate, water ingress, and structural role. For wide/active cracks, displacement, exposed reinforcement, falling concrete, or sudden progression, recommend restricting access as appropriate and prompt review by a qualified structural engineer. This is triage, not a structural safety certification."""

def format_inr(value: float) -> str:
    if value >= 1e7:
        return f"₹{value / 1e7:.2f} Cr"
    if value >= 1e5:
        return f"₹{value / 1e5:.2f} L"
    return f"₹{value:,.0f}"

def render_download(data: Dict[str, Any], filename: str):
    st.download_button(
        "⬇️ Download JSON report",
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name=filename,
        mime="application/json",
        use_container_width=True,
    )

def display_safety_report(data: Dict[str, Any]):
    score = max(0, min(100, int(data.get("safety_score", 0) or 0)))
    status = str(data.get("overall_status", "Unable to Determine"))
    c1, c2, c3 = st.columns(3)
    c1.metric("Visual safety score", f"{score}/100")
    c2.metric("Hazards identified", len(data.get("hazards", [])))
    c3.metric("PPE checks", len(data.get("ppe_detection", [])))
    kind = "good" if status.lower() == "compliant" else "bad" if status.lower() == "unsafe" else "warn"
    st.markdown(f"**Overall status:** {pill(status, kind)}", unsafe_allow_html=True)
    st.progress(score / 100)
    st.subheader("PPE checklist")
    rows = data.get("ppe_detection", [])
    if rows:
        for item in rows:
            with st.container(border=True):
                st.markdown(f"**{item.get('item', 'PPE item')}**")
                state = str(item.get("status", "Unclear"))
                st.markdown(f"{pill(state, 'good' if state.lower() in ['observed','compliant'] else 'warn' if state.lower() in ['unclear','needs verification','not verifiable from image','context dependent'] else 'bad')}", unsafe_allow_html=True)
                st.caption(item.get("evidence", ""))
    else:
        st.info("No PPE checklist entries were returned.")
    st.subheader("Hazards & corrective actions")
    hazards = data.get("hazards", [])
    if not hazards:
        st.success("No hazards were returned. This is not proof that the site is safe.")
    for hazard in hazards:
        severity = str(hazard.get("severity", "Unknown"))
        k = "bad" if severity.lower() in ("critical", "high") else "warn" if severity.lower() == "medium" else "neutral"
        with st.expander(f"{severity.upper()} — {hazard.get('hazard', 'Hazard')}", expanded=severity.lower() in ("critical", "high")):
            st.markdown(f"{pill(severity, k)}", unsafe_allow_html=True)
            st.write("**Evidence:**", hazard.get("evidence", "Not provided"))
            st.write("**Corrective remedy:**", hazard.get("corrective_remedy", "Refer to the site safety lead."))
    if data.get("limitations"):
        st.caption("Limitations: " + str(data["limitations"]))

def main():
    with st.sidebar:
        st.markdown("## 🏗️ MCIP")
        st.caption("Skill Wallet Capstone · Project 1")
        st.markdown("---")
        st.markdown("### Gemini connection")
        st.text_input(
            "Google Gemini API key",
            type="password",
            key="gemini_api_key",
            help="Used only for this running session. For deployment, prefer Streamlit secrets.",
            placeholder="Paste API key (optional)",
        )
        api_ready = bool(get_api_key()) and genai is not None
        st.markdown(pill("Gemini connected" if api_ready else "Demonstration mode", "good" if api_ready else "warn"), unsafe_allow_html=True)
        st.caption("No key? The app still works with clearly labelled illustrative results.")
        st.markdown("---")
        st.markdown("### Architecture")
        st.markdown("1. Streamlit UI\n2. Gemini multimodal inference (optional)\n3. Python planning calculators\n4. JSON reports · no database")
        st.markdown("---")
        page = st.radio(
            "Feature navigation",
            ["Site Safety & PPE Audit", "Crack Diagnostics", "Planning & Valuation", "Daily Site Assistant"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.caption("Visual AI outputs are preliminary observations, not professional certification.")

    st.markdown(
        f"""<div class="hero">
        <div class="hero-kicker">Skill Wallet Capstone · Project 1</div>
        <h1>{APP_NAME}</h1>
        <p>Multimodal field intelligence for safer sites, faster defect triage, practical planning, and weather-aware decisions.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if page == "Site Safety & PPE Audit":
        st.header("🦺 Site Safety & PPE Audit")
        st.write("Upload a site photo to run a preliminary visual PPE and hazard review.")
        uploaded = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="safety_upload")
        if uploaded:
            st.image(uploaded, caption=uploaded.name, use_container_width=True)
            if st.button("Run safety audit", type="primary", use_container_width=True):
                with st.spinner("Reviewing the scene..."):
                    try:
                        if get_api_key() and genai is not None:
                            result = gemini_json(SAFETY_PROMPT, uploaded.getvalue(), uploaded.type or "image/jpeg")
                            result["source_image"] = uploaded.name
                            result["generated_at"] = datetime.now().isoformat(timespec="seconds")
                            result["mode"] = "Gemini AI"
                        else:
                            result = demo_safety(uploaded.name)
                            result["generated_at"] = datetime.now().isoformat(timespec="seconds")
                            result["mode"] = "Demonstration"
                        st.session_state["safety_result"] = result
                    except Exception as exc:
                        st.error(f"Audit could not be completed: {exc}")
                        st.info("Check the API key, network access, supported model availability, and image file. You can remove the key to use demonstration mode.")
        result = st.session_state.get("safety_result")
        if result:
            st.markdown(f"**Analysis mode:** {result.get('mode', 'Unknown')}")
            if result.get("mode") == "Demonstration":
                st.warning("These are illustrative sample findings, not an analysis of your photo.")
            display_safety_report(result)
            render_download(result, "site_safety_audit.json")
        st.markdown('<div class="disclaimer">Safety-critical decisions require an on-site competent person. A photo can miss hazards outside the frame, obscured PPE, site rules, and changing conditions.</div>', unsafe_allow_html=True)

    elif page == "Crack Diagnostics":
        st.header("🧱 Crack Diagnostics & Structural Integrity")
        st.write("Classify a visible defect and prepare a triage note for engineering review.")
        uploaded = st.file_uploader("Concrete / wall surface photo", type=["jpg", "jpeg", "png"], key="crack_upload")
        if uploaded:
            st.image(uploaded, caption=uploaded.name, use_container_width=True)
            if st.button("Analyze surface defect", type="primary", use_container_width=True):
                with st.spinner("Assessing visible defect features..."):
                    try:
                        if get_api_key() and genai is not None:
                            result = gemini_json(CRACK_PROMPT, uploaded.getvalue(), uploaded.type or "image/jpeg")
                            result["mode"] = "Gemini AI"
                        else:
                            result = demo_crack(uploaded.name)
                            result["mode"] = "Demonstration"
                        result["source_image"] = uploaded.name
                        result["generated_at"] = datetime.now().isoformat(timespec="seconds")
                        st.session_state["crack_result"] = result
                    except Exception as exc:
                        st.error(f"Defect analysis failed: {exc}")
        result = st.session_state.get("crack_result")
        if result:
            if result.get("mode") == "Demonstration":
                st.warning("Illustrative sample only. The uploaded photo was not analyzed in demonstration mode.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Defect category", str(result.get("defect_type", "Unclear")))
            width = result.get("estimated_crack_width_mm")
            c2.metric("Estimated width", f"{width} mm" if width is not None else "Not estimated")
            c3.metric("Urgency", str(result.get("urgency", "Unclear")))
            st.markdown("**Confidence:** " + str(result.get("confidence", "Not provided")))
            st.subheader("Possible root causes")
            for cause in result.get("possible_root_causes", []):
                st.markdown(f"- {cause}")
            st.subheader("Recommended engineering actions")
            for action in result.get("recommended_engineering_repairs", []):
                st.markdown(f"- {action}")
            flags = result.get("red_flags", [])
            if flags:
                st.error("Red flags: " + "; ".join(flags))
            if result.get("limitations"):
                st.caption("Limitations: " + str(result["limitations"]))
            render_download(result, "crack_diagnostics_report.json")
        st.markdown('<div class="disclaimer">Do not infer structural safety from a photo. If there is sudden crack growth, displacement, falling/spalled concrete, exposed reinforcement, or signs of distress, keep people clear and obtain prompt professional assessment.</div>', unsafe_allow_html=True)

    elif page == "Planning & Valuation":
        st.header("📐 Planning & Real Estate Valuation")
        st.write("A transparent concept estimator. Replace defaults with local BOQ, schedule-of-rates, and market evidence before making commitments.")
        left, right = st.columns([1, 1])
        with left:
            structure = st.selectbox("Structure type", ["Residential RCC", "Commercial RCC", "Industrial shed", "Low-rise masonry"])
            area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=2400, step=100)
            tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"], index=1)
            completion = st.slider("Physical completion (%)", 0, 100, 35, 5)
            st.caption("Illustrative base construction rates; edit assumptions to match project-specific estimates.")
            rates = {"Residential RCC": 2200, "Commercial RCC": 2800, "Industrial shed": 1500, "Low-rise masonry": 1750}
            tier_multiplier = {"Tier 1": 1.18, "Tier 2": 1.00, "Tier 3": 0.88}
            base_rate = st.number_input("Base build cost (₹/sq ft)", min_value=500, max_value=15000, value=rates[structure], step=50)
            contingency = st.slider("Contingency (%)", 0, 25, 10, 1)
            market_rate = st.number_input("Indicative market value (₹/sq ft)", min_value=500, max_value=50000, value=int(base_rate * tier_multiplier[tier] * 1.25), step=100)
        with right:
            effective_rate = base_rate * tier_multiplier[tier]
            base_budget = area * effective_rate
            total_budget = base_budget * (1 + contingency / 100)
            incurred = total_budget * completion / 100
            valuation = area * market_rate
            # Rule-of-thumb quantities are planning placeholders, not structural design quantities.
            steel_kg = area * (3.5 if structure in ["Residential RCC", "Commercial RCC"] else 2.0 if structure == "Industrial shed" else 1.2)
            cement_bags = area * (0.40 if structure in ["Residential RCC", "Commercial RCC"] else 0.22 if structure == "Industrial shed" else 0.30)
            st.subheader("Project snapshot")
            m1, m2 = st.columns(2)
            m1.metric("Estimated total budget", format_inr(total_budget))
            m2.metric("CapEx incurred", format_inr(incurred), f"{completion}% progress")
            m3, m4 = st.columns(2)
            m3.metric("Indicative asset valuation", format_inr(valuation))
            m4.metric("Budget remaining", format_inr(max(0, total_budget - incurred)))
            st.markdown("**Milestone progress**")
            st.progress(completion / 100)
            st.caption(f"{completion}% complete · {100-completion}% remaining")
            st.markdown("---")
            q1, q2 = st.columns(2)
            q1.metric("Indicative steel", f"{steel_kg/1000:,.2f} tonnes")
            q2.metric("Indicative cement", f"{cement_bags:,.0f} bags")
            st.caption("Material quantities are broad early-stage thumb rules, not a bill of quantities or design take-off.")
        plan = {
            "project": {"structure_type": structure, "built_up_sqft": area, "location_tier": tier, "completion_percent": completion},
            "assumptions": {"base_rate_inr_sqft": base_rate, "tier_multiplier": tier_multiplier[tier], "contingency_percent": contingency, "market_rate_inr_sqft": market_rate},
            "estimates": {"total_project_budget_inr": round(total_budget), "capex_incurred_inr": round(incurred), "budget_remaining_inr": round(max(0, total_budget-incurred)), "indicative_market_valuation_inr": round(valuation), "steel_kg_approx": round(steel_kg), "cement_bags_approx": round(cement_bags)},
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "disclaimer": "Concept estimates only; validate against current local rates, BOQ, engineering design, taxes, approvals, and comparable transactions."
        }
        render_download(plan, "construction_planning_estimate.json")
        st.subheader("Conceptual 3D rendering prompt")
        render_prompt = st.text_area("Describe the architectural concept", value=f"Photorealistic architectural visualization of a {structure.lower()} project, {area} sq ft built-up area, Indian {tier} city context, construction stage {completion}% complete, realistic climate-responsive design, professional architectural photography, no text or watermark.", height=100)
        if st.button("Generate rendering prompt URL", use_container_width=True):
            from urllib.parse import quote
            url = "https://image.pollinations.ai/prompt/" + quote(render_prompt, safe="")
            st.session_state["render_url"] = url
        if st.session_state.get("render_url"):
            st.link_button("Open conceptual render (Pollinations AI)", st.session_state["render_url"], use_container_width=True)
            st.caption("The image service is third-party and may be unavailable. Do not include confidential project details in prompts.")

    else:
        st.header("🌦️ Daily Site Assistant & Weather-Aware Advisory")
        weather = st.selectbox("Current / forecast condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
        alerts = {
            "Normal": ("Routine controls", "Continue toolbox talks, PPE checks, housekeeping, lifting-plan checks, and daily equipment inspections. Monitor updated forecasts.", "good"),
            "High Wind": ("Wind / lifting alert", "Pause crane and hoisting operations when site-specific manufacturer limits or the lift plan threshold is reached. Secure loose materials, inspect scaffolds, and restrict exposed-edge work. The site supervisor must apply actual wind-speed limits.", "bad"),
            "Heavy Rain": ("Rain / electrical / access alert", "Stop work in flooded or unstable areas; isolate and protect electrical equipment, use RCD/GFCI protection as applicable, inspect excavations and access routes, and reassess ground bearing before lifting. Protect fresh concrete and follow the approved curing/mix procedure.", "bad"),
            "Extreme Heat": ("Heat-stress alert", "Provide drinking water, shaded rest, acclimatization, work-rest cycles, and buddy monitoring. Schedule heavy work in cooler periods where possible. Follow the approved concrete placing and curing plan; prevent rapid moisture loss and avoid adding water outside the mix design.", "warn"),
        }
        title, advice, level = alerts[weather]
        st.markdown(f"### {title}")
        st.markdown(f'<div class="section-card">{pill("Priority advisory", level)}<p>{advice}</p></div>', unsafe_allow_html=True)
        st.caption("Use the site's emergency response plan and competent-person judgement; this advisory is not a substitute for site-specific limits.")

        st.subheader("Construction engineering assistant")
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        user_prompt = st.chat_input("Ask about sequencing, QA/QC, concrete, site safety, or planning…")
        if user_prompt:
            st.session_state["chat_history"].append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)
            answer = None
            key = get_api_key()
            if key and genai is not None:
                try:
                    client = genai.Client(api_key=key)
                    history = []
                    for msg in st.session_state["chat_history"][-12:]:
                        role = "user" if msg["role"] == "user" else "model"
                        history.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=history,
                        config=types.GenerateContentConfig(
                            system_instruction="You are a careful construction engineering assistant. Give practical, concise guidance, state assumptions, distinguish general guidance from code requirements, and advise a qualified engineer for structural design or safety-critical decisions. Do not fabricate code clauses or exact legal requirements.",
                            temperature=0.35,
                        ),
                    )
                    answer = response.text or "I couldn't generate a response. Please try again."
                except Exception as exc:
                    answer = f"Assistant unavailable: {exc}. Please check your API key/network, or ask again in demonstration mode."
            else:
                answer = (
                    "Demonstration mode is active, so I can't call Gemini. General starting point: define the activity and site constraints, "
                    "check the approved drawings/method statement and applicable local requirements, assign a competent person, document QA/QC "
                    "checks, and stop work if conditions are unsafe. Add a Gemini API key in the sidebar for a context-aware response."
                )
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)
        if st.button("Clear chat history"):
            st.session_state["chat_history"] = []
            st.rerun()

    st.markdown("---")
    st.caption("MCIP · Prototype capstone · No external database · Reports are generated locally in your session.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        st.error("The application encountered an unexpected error.")
        st.exception(exc)
