# Multimodal Construction Intelligence Platform
**Skill Wallet Capstone Project 1**

A Streamlit prototype for visual site safety review, crack triage, construction planning estimates, and weather-aware site assistance. It has no database dependency and can run with Gemini AI or in explicitly labelled demonstration mode.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Gemini API key

- Paste a key into the sidebar for the current session, or
- Set `GEMINI_API_KEY` as an environment variable, or
- Add a Streamlit secret in `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-key-here"
```

Do not commit secrets to Git. The sidebar input is masked; API keys are not written to a database or file by this app.

## Deploy to Streamlit Community Cloud

1. Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. Create a Streamlit Community Cloud app pointing to `app.py`.
3. Add `GEMINI_API_KEY` under the app's Secrets settings if using Gemini.
4. Deploy. Without a key, demonstration mode remains available.

## Modules

1. **Site Safety & PPE Audit** — image upload, Gemini multimodal JSON response, PPE checklist, hazard severity/remedies, score and downloadable report.
2. **Crack Diagnostics** — visual defect triage, estimated width with uncertainty, potential causes, engineering follow-up recommendations, downloadable JSON.
3. **Planning & Valuation** — editable rate assumptions, tier multiplier, budget/CapEx/valuation, rough steel/cement planning quantities, milestone progress and Pollinations AI prompt URL.
4. **Daily Site Assistant** — weather-aware advisories and a multi-turn Gemini chat.

## Important engineering limitations

- This is a capstone prototype, not a certified safety, structural diagnosis, quantity-surveying, valuation, or engineering-design system.
- AI vision can miss obscured or out-of-frame hazards. Always verify on site with a competent person.
- OSHA applicability depends on jurisdiction and activity. IS 456 is a concrete design code, not a general PPE checklist; the app avoids treating it as one.
- Crack widths inferred from photos are not reliable measurements without a known scale. Structural defects require qualified assessment.
- Budget rates, market valuation, steel quantities and cement quantities are editable early-stage assumptions only. Validate against current local rates, BOQ, drawings, approvals, taxes and comparable transactions.
- Pollinations AI is a third-party service. The app opens a generated image URL; availability, output and terms are controlled by that provider.
- For production use, add authentication, rate limiting, observability, key-management controls, test coverage, and a formal review of data retention/privacy requirements.
