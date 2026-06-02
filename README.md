# 📄 Personal ATS — Resume Analyzer

Paste your resume + any Job Description → instant match score, gap analysis, and optimized resume sections powered by Claude AI.

---

## 🚀 Deploy on Streamlit Cloud (Free)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ats-resume-analyzer.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with GitHub
3. Click **New app**
4. Select your repo → Branch: `main` → File: `app.py`
5. Click **Deploy**

### Step 3 — Add your API Key (secrets)
In Streamlit Cloud dashboard:
1. Go to your app → **Settings** → **Secrets**
2. You don't need to add it here — the app asks for it in the sidebar at runtime ✅

---

## 💻 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔑 Get Anthropic API Key (Free)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up → API Keys → **Create Key**
3. Copy key (starts with `sk-ant-...`)
4. Paste it in the app sidebar

**Cost:** ~$0.002 per scan · $5 free credits = ~2500 scans

---

## ✨ What you get per scan
- Match score (0–100%)
- Matched vs missing skills
- Strengths & areas to improve
- Optimized Summary (copy-paste ready)
- Optimized Tech Skills (JD-ordered)
- Optimized Soft Skills (JD-mapped)
- 3 Project recommendations with resume bullets
- ATS optimization tips

---

## 📁 File structure
```
ats_app/
├── app.py                  # Main app
├── requirements.txt        # Dependencies
├── .streamlit/
│   └── config.toml         # UI theme
└── README.md
```
