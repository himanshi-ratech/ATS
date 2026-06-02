import streamlit as st
import anthropic
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


def call_claude(api_key: str, resume: str, jd: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and career coach specializing in data science roles.

Analyze the resume against the job description and return ONLY a valid JSON object — no preamble, no markdown fences.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Return exactly this JSON structure:
{{
  "match_score": <integer 0-100>,
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "optional_missing": ["skill1"],
  "strengths": ["point1", "point2", "point3"],
  "weaknesses": ["point1", "point2", "point3"],
  "optimized_summary": "<2-3 sentence summary tailored exactly to this JD>",
  "optimized_tech_skills": ["<Category> — <skill1>, <skill2>"],
  "optimized_soft_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "project_recommendations": [
    {{
      "title": "<Project title>",
      "stack": "<Tech stack>",
      "description": "<1 line what to build>",
      "bullets": ["<bullet 1 with metric>", "<bullet 2>", "<bullet 3>"]
    }}
  ],
  "ats_tips": ["tip1", "tip2", "tip3"]
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


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
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your free key at console.anthropic.com"
    )
    st.markdown("---")
    st.markdown("### 📌 How to use")
    st.markdown("""
1. Enter your **Anthropic API key**
2. Paste your **resume text**
3. Paste the **Job Description**
4. Click **Analyze Resume**
5. Copy optimized sections to your resume ✅
    """)
    st.markdown("---")
    st.markdown("### 💰 Cost")
    st.markdown("1 scan ≈ **\\$0.002**  \n\\$5 free credits = **~2500 scans**")
    st.markdown("[Get API Key →](https://console.anthropic.com)", unsafe_allow_html=False)

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
    if not api_key.strip():
        st.error("❌ Enter your Anthropic API key in the sidebar.")
        st.stop()
    if not resume_text.strip():
        st.error("❌ Please paste your resume text.")
        st.stop()
    if not jd_text.strip():
        st.error("❌ Please paste the Job Description.")
        st.stop()

    with st.spinner("🤖 Claude is analyzing your resume against the JD..."):
        try:
            result = call_claude(api_key, resume_text, jd_text)
        except json.JSONDecodeError:
            st.error("❌ Parsing error — please try again.")
            st.stop()
        except anthropic.AuthenticationError:
            st.error("❌ Invalid API key. Check at console.anthropic.com")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.stop()

    score   = result.get("match_score", 0)
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
        miss  = "".join(f'<span class="pill-red">✗ {s}</span>' for s in missing)
        opt   = "".join(f'<span class="pill-amber">△ {s} (optional)</span>' for s in result.get("optional_missing", []))
        st.markdown(f'<div class="section-card">{miss}{opt or ("<i>None — great match!</i>" if not miss else "")}</div>', unsafe_allow_html=True)

    # Strengths & weaknesses
    sw1, sw2 = st.columns(2)
    with sw1:
        st.markdown("### 💪 Strengths")
        html = "".join(f"<p>✅ {p}</p>" for p in result.get("strengths", []))
        st.markdown(f'<div class="section-card">{html}</div>', unsafe_allow_html=True)
    with sw2:
        st.markdown("### ⚠️ Areas to Improve")
        html = "".join(f"<p>⚠️ {p}</p>" for p in result.get("weaknesses", []))
        st.markdown(f'<div class="section-card">{html}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## ✍️ Optimized Resume Sections")
    st.markdown("*Copy these directly into your resume — tailored for this specific JD*")

    # Summary
    st.markdown("### 📝 Summary")
    summary = result.get("optimized_summary", "")
    st.markdown(f'<div class="section-card"><p>{summary}</p></div>', unsafe_allow_html=True)
    st.code(summary, language=None)

    # Tech skills
    st.markdown("### 🛠️ Technical Skills")
    tech = result.get("optimized_tech_skills", [])
    st.markdown(f'<div class="section-card">{"".join(f"<p>• {s}</p>" for s in tech)}</div>', unsafe_allow_html=True)
    st.code("\n".join(f"• {s}" for s in tech), language=None)

    # Soft skills
    st.markdown("### 🤝 Soft Skills")
    soft = result.get("optimized_soft_skills", [])
    pills = "".join(f'<span class="pill-green">{s}</span>' for s in soft)
    st.markdown(f'<div class="section-card">{pills}</div>', unsafe_allow_html=True)
    st.code(" | ".join(soft), language=None)

    st.markdown("---")
    st.markdown("## 🚀 Project Recommendations")
    st.markdown("*Build these to strengthen your profile for this specific role:*")

    for i, proj in enumerate(result.get("project_recommendations", []), 1):
        with st.expander(f"📁 {i}. {proj.get('title','')}  ·  {proj.get('stack','')}"):
            st.markdown(f"**What to build:** {proj.get('description','')}")
            st.markdown("**Resume-ready bullets:**")
            for b in proj.get("bullets", []):
                st.markdown(f"- {b}")
            entry = f"**{proj['title']}** | {proj['stack']} | [GitHub](#)\n" + "\n".join(f"• {b}" for b in proj.get("bullets",[]))
            st.code(entry, language=None)

    st.markdown("---")
    st.markdown("### 💡 ATS Tips for this JD")
    tips = "".join(f"<p>💡 {t}</p>" for t in result.get("ats_tips", []))
    st.markdown(f'<div class="section-card">{tips}</div>', unsafe_allow_html=True)

    st.success("✅ Done! Copy any section above directly into your resume.")
