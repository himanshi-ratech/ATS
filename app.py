import streamlit as st
import google.generativeai as genai
import json
import re

st.set_page_config(
    page_title="Personal ATS — Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stTextArea textarea { font-size: 13px; }
    .score-box {
        text-align: center; padding: 1.5rem;
        border-radius: 12px; margin-bottom: 1rem;
    }
    .score-high  { background: #d4edda; border: 1px solid #28a745; color: #155724; }
    .score-mid   { background: #fff3cd; border: 1px solid #ffc107; color: #856404; }
    .score-low   { background: #f8d7da; border: 1px solid #dc3545; color: #721c24; }
    .section-card {
        background: white; padding: 1.25rem 1.5rem;
        border-radius: 10px; border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .pill-green { background:#d4edda; color:#155724; padding:3px 10px; border-radius:20px; font-size:13px; margin:3px; display:inline-block; }
    .pill-red   { background:#f8d7da; color:#721c24; padding:3px 10px; border-radius:20px; font-size:13px; margin:3px; display:inline-block; }
    .pill-amber { background:#fff3cd; color:#856404; padding:3px 10px; border-radius:20px; font-size:13px; margin:3px; display:inline-block; }
    h3 { margin-top: 0 !important; }
    .stButton > button { font-size: 16px; padding: 0.6rem 1rem; }
</style>
""", unsafe_allow_html=True)


# ── Core Analysis Function ────────────────────────────────────────────────────
def analyze_resume(api_key: str, resume: str, jd: str) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are an expert ATS (Applicant Tracking System) and career coach. Analyze the resume against the job description below and return a detailed JSON response.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Return ONLY a valid JSON object (no markdown, no backticks, no explanation) with exactly this structure:

{{
  "match_score": <integer 0-100, overall resume-to-JD match percentage>,

  "matched_skills": [<list of skills/keywords from JD that ARE present in resume>],
  "missing_skills": [<list of required skills/keywords from JD that are NOT in resume>],
  "optional_missing": [<list of nice-to-have/preferred skills from JD not in resume>],

  "strengths": [<3-5 specific strengths of this resume for this JD>],
  "weaknesses": [<3-5 specific gaps or weaknesses of this resume for this JD>],

  "optimized_summary": "<2-3 sentence professional summary rewritten to target this JD, using keywords from it>",

  "optimized_tech_skills": [
    "<Category: skill1, skill2, skill3>",
    "<Category: skill1, skill2>"
  ],

  "optimized_soft_skills": [<5-7 relevant soft skills for this JD as plain strings>],

  "project_recommendations": [
    {{
      "title": "<project name>",
      "stack": "<tech stack to use>",
      "description": "<what to build and why it fits this JD>",
      "bullets": [
        "<resume bullet 1 with metrics>",
        "<resume bullet 2 with metrics>",
        "<resume bullet 3 with metrics>"
      ]
    }},
    {{
      "title": "<project name>",
      "stack": "<tech stack to use>",
      "description": "<what to build and why it fits this JD>",
      "bullets": [
        "<resume bullet 1 with metrics>",
        "<resume bullet 2 with metrics>",
        "<resume bullet 3 with metrics>"
      ]
    }}
  ],

  "ats_tips": [<5 specific actionable tips to improve ATS score for this exact JD>]
}}

Rules:
- match_score must be an integer, not a string
- All lists must have at least 1 item
- project_recommendations must have exactly 2 objects
- optimized_summary must reference specific skills/tools from the JD
- Each bullet in projects must contain a number or metric
- Return ONLY the JSON object — absolutely no text before or after it
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if model wraps in them anyway
    raw = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON_PARSE_ERROR: {e}\n\nRaw response:\n{raw}") from e


# ── Helper Functions ──────────────────────────────────────────────────────────
def score_color(score):
    if score >= 80: return "score-high"
    if score >= 60: return "score-mid"
    return "score-low"

def score_emoji(score):
    if score >= 80: return "🟢"
    if score >= 60: return "🟡"
    return "🔴"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Setup")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get your free key at aistudio.google.com/app/apikey"
    )
    st.markdown("---")
    st.markdown("### 📌 How to use")
    st.markdown("""
1. Enter your **Gemini API key**
2. Paste your **resume text**
3. Paste the **Job Description**
4. Click **Analyze Resume**
5. Copy optimized sections to your resume ✅
    """)
    st.markdown("---")
    st.markdown("### 💰 Cost")
    st.markdown("Gemini 1.5 Flash is **free** on the free tier  \nup to **15 requests/min**")
    st.markdown("[Get API Key →](https://aistudio.google.com/app/apikey)")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📄 Personal ATS — Resume Analyzer")
st.markdown("Paste your resume + any JD → get match score, gap analysis, and optimized resume sections instantly.")
st.markdown("---")

# ── Input ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 Your Resume")
    resume_text = st.text_area(
        "resume_input",
        height=340,
        placeholder="Paste your full resume text here...\n\nInclude: Summary, Skills, Experience, Projects, Education",
        label_visibility="collapsed"
    )
    st.caption(f"{'✅ ' + str(len(resume_text)) + ' characters' if resume_text.strip() else '⬆️ Paste your resume above'}")

with col2:
    st.markdown("### 💼 Job Description")
    jd_text = st.text_area(
        "jd_input",
        height=340,
        placeholder="Paste the full Job Description here...\n\nInclude: Responsibilities, Required skills, Qualifications",
        label_visibility="collapsed"
    )
    st.caption(f"{'✅ ' + str(len(jd_text)) + ' characters' if jd_text.strip() else '⬆️ Paste JD above'}")

st.markdown("---")
analyze_btn = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# ── Results ───────────────────────────────────────────────────────────────────
if analyze_btn:
    # Validation
    if not api_key.strip():
        st.error("❌ Enter your Gemini API key in the sidebar.")
        st.stop()
    if not resume_text.strip():
        st.error("❌ Please paste your resume text.")
        st.stop()
    if not jd_text.strip():
        st.error("❌ Please paste the Job Description.")
        st.stop()

    with st.spinner("🤖 Gemini is analyzing your resume against the JD..."):
        try:
            result = analyze_resume(api_key, resume_text, jd_text)
        except ValueError as e:
            st.error("❌ Failed to parse AI response. Please try again.")
            with st.expander("Debug info"):
                st.code(str(e))
            st.stop()
        except Exception as e:
            err_str = str(e).lower()
            if "api_key" in err_str or "invalid" in err_str or "permission" in err_str or "403" in err_str:
                st.error("❌ Invalid Gemini API key. Get yours at aistudio.google.com/app/apikey")
            elif "quota" in err_str or "429" in err_str:
                st.error("❌ API quota exceeded. Wait a minute and try again (free tier: 15 req/min).")
            elif "network" in err_str or "connection" in err_str:
                st.error("❌ Network error. Check your internet connection.")
            else:
                st.error(f"❌ Unexpected error: {e}")
            st.stop()

    # ── Safely read result fields ─────────────────────────────────────────────
    score   = int(result.get("match_score", 0))
    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])

    st.markdown("## 📊 Analysis Results")

    # Score cards
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="score-box {score_color(score)}">
            <div style="font-size:52px;font-weight:700;">{score}%</div>
            <div style="font-size:15px;font-weight:500;">Match Score {score_emoji(score)}</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="score-box score-high">
            <div style="font-size:52px;font-weight:700;">{len(matched)}</div>
            <div style="font-size:15px;font-weight:500;">Skills Matched ✓</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        box_cls = "score-low" if missing else "score-high"
        st.markdown(f"""
        <div class="score-box {box_cls}">
            <div style="font-size:52px;font-weight:700;">{len(missing)}</div>
            <div style="font-size:15px;font-weight:500;">Skills Missing ✗</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Skills gap
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("### ✅ Matched Skills")
        pills = "".join(f'<span class="pill-green">✓ {s}</span>' for s in matched)
        st.markdown(f'<div class="section-card">{pills or "<i>None detected</i>"}</div>', unsafe_allow_html=True)
    with g2:
        st.markdown("### ❌ Missing Skills")
        miss = "".join(f'<span class="pill-red">✗ {s}</span>' for s in missing)
        opt  = "".join(f'<span class="pill-amber">△ {s} (optional)</span>' for s in result.get("optional_missing", []))
        no_miss_msg = "<i>None — great match!</i>" if not miss and not opt else ""
        st.markdown(f'<div class="section-card">{miss}{opt}{no_miss_msg}</div>', unsafe_allow_html=True)

    # Strengths & weaknesses
    sw1, sw2 = st.columns(2)
    with sw1:
        st.markdown("### 💪 Strengths")
        html = "".join(f"<p>✅ {p}</p>" for p in result.get("strengths", []))
        st.markdown(f'<div class="section-card">{html or "<i>No data</i>"}</div>', unsafe_allow_html=True)
    with sw2:
        st.markdown("### ⚠️ Areas to Improve")
        html = "".join(f"<p>⚠️ {p}</p>" for p in result.get("weaknesses", []))
        st.markdown(f'<div class="section-card">{html or "<i>No data</i>"}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## ✍️ Optimized Resume Sections")
    st.markdown("*Copy these directly into your resume — tailored for this specific JD*")

    # Summary
    st.markdown("### 📝 Professional Summary")
    summary = result.get("optimized_summary", "")
    st.markdown(f'<div class="section-card"><p>{summary}</p></div>', unsafe_allow_html=True)
    st.code(summary, language=None)

    # Tech skills
    st.markdown("### 🛠️ Technical Skills")
    tech = result.get("optimized_tech_skills", [])
    if tech:
        st.markdown(f'<div class="section-card">{"".join(f"<p>• {s}</p>" for s in tech)}</div>', unsafe_allow_html=True)
        st.code("\n".join(f"• {s}" for s in tech), language=None)
    else:
        st.info("No technical skills data returned.")

    # Soft skills
    st.markdown("### 🤝 Soft Skills")
    soft = result.get("optimized_soft_skills", [])
    if soft:
        pills = "".join(f'<span class="pill-green">{s}</span>' for s in soft)
        st.markdown(f'<div class="section-card">{pills}</div>', unsafe_allow_html=True)
        st.code(" | ".join(soft), language=None)
    else:
        st.info("No soft skills data returned.")

    st.markdown("---")
    st.markdown("## 🚀 Project Recommendations")
    st.markdown("*Build these to strengthen your profile for this specific role:*")

    projects = result.get("project_recommendations", [])
    if projects:
        for i, proj in enumerate(projects, 1):
            title   = proj.get("title", f"Project {i}")
            stack   = proj.get("stack", "")
            desc    = proj.get("description", "")
            bullets = proj.get("bullets", [])
            with st.expander(f"📁 {i}. {title}  ·  {stack}"):
                st.markdown(f"**What to build:** {desc}")
                st.markdown("**Resume-ready bullets:**")
                for b in bullets:
                    st.markdown(f"- {b}")
                entry = f"**{title}** | {stack} | [GitHub](#)\n" + "\n".join(f"• {b}" for b in bullets)
                st.code(entry, language=None)
    else:
        st.info("No project recommendations returned.")

    st.markdown("---")
    st.markdown("### 💡 ATS Tips for this JD")
    tips = result.get("ats_tips", [])
    if tips:
        tips_html = "".join(f"<p>💡 {t}</p>" for t in tips)
        st.markdown(f'<div class="section-card">{tips_html}</div>', unsafe_allow_html=True)
    else:
        st.info("No ATS tips returned.")

    st.success("✅ Done! Copy any section above directly into your resume.")
