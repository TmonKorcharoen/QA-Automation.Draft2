import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(
    page_title="TransQA Studio",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Sarabun', sans-serif !important;
    background-color: #f5f0e8 !important;
    color: #1a1a1a !important;
}
.main .block-container {
    padding: 0 2.5rem 3rem 2.5rem !important;
    max-width: 1300px !important;
}

/* MQM Dashboard */
.mqm-container {
    background-color: white;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1.5px solid #e0d8cc;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.mqm-score { font-size: 3.2rem; font-weight: 800; margin: 0; line-height: 1.1; }
.mqm-label { font-size: 0.9rem; color: #666; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.mqm-meta { color: #888; font-size: 0.85rem; margin-top: 5px; }

/* Wide Header */
.app-header {
    background: linear-gradient(90deg, #2e7d32 0%, #43a047 100%);
    color: white;
    padding: 1.6rem 2.5rem;
    margin: 0 -2.5rem 2rem -2.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.app-header-icon  { font-size: 2rem; }
.app-header-title { font-size: 1.7rem; font-weight: 700; margin: 0; }
.app-header-sub   { font-size: 0.95rem; margin: 0; opacity: 0.85; font-weight: 400; }

.sec-title {
    font-size: 1.05rem; font-weight: 600; color: #2e7d32;
    margin: 1.4rem 0 0.8rem 0; padding-bottom: 0.4rem;
    border-bottom: 1px solid #ddd;
}

.stats-row { display: flex; gap: 12px; margin: 1.2rem 0; flex-wrap: wrap; }
.stat-box  {
    flex: 1; min-width: 90px; background: #fffdf8;
    border: 1.5px solid #e0d8cc; border-radius: 10px;
    padding: 0.9rem 0.8rem; text-align: center;
}
.stat-box .s-num { font-size: 2rem; font-weight: 700; line-height: 1; }
.stat-box .s-lbl { font-size: 0.78rem; font-weight: 600; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.stat-total .s-num { color: #2e7d32; }
.stat-pass  .s-num { color: #388e3c; } .stat-pass  { border-color: #a5d6a7; }
.stat-minor .s-num { color: #f57c00; } .stat-minor { border-color: #ffcc80; }
.stat-major .s-num { color: #e64a19; } .stat-major { border-color: #ffab91; }
.stat-crit  .s-num { color: #c62828; } .stat-crit  { border-color: #ef9a9a; }

.qa-table { width: 100%; border-collapse: collapse; margin-top: 0.8rem; font-size: 0.97rem; }
.qa-table thead tr { border-bottom: 2px solid #ccc; }
.qa-table thead th {
    padding: 0.6rem 1rem 0.6rem 0; font-weight: 600;
    color: #333; text-align: left; font-size: 0.92rem;
    background: transparent;
}
.qa-table tbody tr { border-bottom: 1px solid #e8e0d5; }
.qa-table td { padding: 0.9rem 1rem 0.9rem 0; vertical-align: top; color: #222; line-height: 1.6; }
.td-num    { font-weight: 700; color: #555; width: 42px; white-space: nowrap; }
.td-text   { min-width: 200px; max-width: 280px; word-break: break-word; }
.sev-pass  { color: #388e3c; }
.sev-minor { color: #f57c00; }
.sev-major { color: #e64a19; }
.sev-crit  { color: #c62828; }
</style>
""", unsafe_allow_html=True)

# ── State Initialization ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "glossary": [],
        "history": [],
        "style_guide": {
            "punctuation": [
                {"symbol": ".", "name": "จุด (Full Stop)", "type": "grammar", "enabled": False, "severity": "Minor"},
                {"symbol": "...", "name": "จุดไข่ปลา (Ellipsis)", "type": "special", "enabled": True, "severity": "Minor"},
                {"symbol": '"', "name": "อัญประกาศคู่", "type": "special", "enabled": True, "severity": "Minor"},
            ],
            "encoding": "UTF-8", "max_length_ratio": 1.5, "min_length_ratio": 0.5,
            "check_length": True, "check_encoding": True,
        },
        "qa_rules": {
            "placeholders": True, "glossary_check": True, "punctuation": True,
            "spelling_en": True, "spelling_th": True, "numbers": True,
            "extra_symbols": True, "length_check": True, "encoding_check": True,
            "consistency_check": True,
        },
        "qa_results": [], "current_file": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── MQM Engine ───────────────────────────────────────────────────────────────────
def calculate_mqm(minor, major, critical, source_texts):
    """
    MQM Scoring Logic: 100 - ((Penalty / Word Count) * 100)
    Weights: Minor=1, Major=5, Critical=10
    """
    combined_text = " ".join([str(t) for t in source_texts if pd.notna(t)])
    # Word count estimation (Space-based for EN/Technical)
    word_count = len(re.findall(r'\w+', combined_text))
    
    if word_count == 0: return 100.0, 0, 0
    
    penalty_total = (minor * 1) + (major * 5) + (critical * 10)
    score = 100 - ((penalty_total / word_count) * 100)
    return max(0, round(score, 2)), word_count, penalty_total

# ── QA Engine ────────────────────────────────────────────────────────────────────
PH_PAT = re.compile(r'\{[^}]+\}|\[[^\]]+\]|%[sd\d]|<[^>]+>')
NUM_PAT = re.compile(r'\b\d[\d,\.]*\b')
TH_PAT = re.compile(r'[\u0e00-\u0e7f]')

def numbers_match(src_nums, tgt_nums):
    tgt_set_norm = {re.sub(r'[,\.]', '', t) for t in tgt_nums}
    missing = []
    for n in src_nums:
        try:
            nval = int(re.sub(r'[,\.]', '', n))
            n_str = str(nval)
            if n_str in tgt_set_norm or str(nval-543) in tgt_set_norm or str(nval+543) in tgt_set_norm:
                continue
            missing.append(n)
        except:
            if n not in tgt_set_norm: missing.append(n)
    return missing

def run_qa(df, src_col, tgt_col, rules, glossary, style):
    results = []
    # Consistency check logic (Simplified from your snippet)
    consist_issues = {}
    if rules.get("consistency_check"):
        # Pre-scan for consistency can be added here
        pass

    for idx, row in df.iterrows():
        src, tgt = str(row[src_col]), str(row[tgt_col])
        issues = []
        
        # 1. Placeholders
        if rules.get("placeholders"):
            sp, tp = set(PH_PAT.findall(src)), set(PH_PAT.findall(tgt))
            if sp - tp: issues.append({"rule":"Placeholder","severity":"Critical","detail":f"ตัวแปร {sp-tp} หายไป"})

        # 2. Numbers
        if rules.get("numbers"):
            for n in numbers_match(NUM_PAT.findall(src), NUM_PAT.findall(tgt)):
                issues.append({"rule":"ตัวเลข","severity":"Critical","detail":f"เลข {n} ไม่พบในคำแปล"})

        # 3. Glossary
        if rules.get("glossary_check"):
            for g in glossary:
                if g['term'].lower() in src.lower() and g['translation'].lower() not in tgt.lower():
                    issues.append({"rule":"Glossary","severity":g.get("importance","Major"),"detail":f"ควรใช้ '{g['translation']}'"})

        sevs = [i["severity"] for i in issues]
        status = "Critical" if "Critical" in sevs else "Major" if "Major" in sevs else "Minor" if sevs else "Pass"
        results.append({"row":idx+1,"source":src,"target":tgt,"status":status,"issues":issues})
    return results

# ── UI Layout ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-header-icon">🔍</div>
  <div>
    <div class="app-header-title">TransQA Studio Professional</div>
    <div class="app-header-sub">ระบบตรวจสอบคุณภาพงานแปลระดับสากล (MQM Standard)</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab_qa, tab_glossary, tab_style = st.tabs(["🔍 ตรวจสอบ QA", "📚 Glossary", "📐 Style Guide"])

with tab_qa:
    uploaded = st.file_uploader("อัปโหลดไฟล์งานแปล", type=["csv","xlsx","txt"])
    if uploaded:
        df_raw = pd.read_excel(uploaded) if uploaded.name.endswith(".xlsx") else pd.read_csv(uploaded)
        st.session_state["df_raw"] = df_raw
        cols = list(df_raw.columns)
        c1, c2 = st.columns(2)
        src_col = c1.selectbox("Source Column", cols)
        tgt_col = c2.selectbox("Target Column", cols)

        if st.button("▶ เริ่มตรวจสอบ (Run QA + MQM Analysis)"):
            results = run_qa(df_raw, src_col, tgt_col, st.session_state["qa_rules"], st.session_state["glossary"], st.session_state["style_guide"])
            st.session_state["qa_results"] = results

    # Results Display
    if st.session_state.get("qa_results"):
        res = st.session_state["qa_results"]
        counts = {"Pass":0, "Minor":0, "Major":0, "Critical":0}
        for r in res: counts[r["status"]] += 1
        
        # MQM Calculation
        mqm_val, w_count, penalty = calculate_mqm(counts["Minor"], counts["Major"], counts["Critical"], [r["source"] for r in res])
        score_color = "#2e7d32" if mqm_val >= 98 else "#f57c00" if mqm_val >= 90 else "#d32f2f"

        # MQM Dashboard UI
        st.markdown(f"""
            <div class="mqm-container">
                <div class="mqm-label">MQM Quality Score</div>
                <div class="mqm-score" style="color: {score_color}">{mqm_val}%</div>
                <div class="mqm-meta">
                    Base on <b>{w_count:,}</b> source words | Total Penalty: <b>{penalty}</b> pts
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="stats-row">
                <div class="stat-box stat-pass"><div class="s-num">{counts['Pass']}</div><div class="s-lbl">✅ ผ่าน</div></div>
                <div class="stat-box stat-minor"><div class="s-num">{counts['Minor']}</div><div class="s-lbl">🟡 Minor</div></div>
                <div class="stat-box stat-major"><div class="s-num">{counts['Major']}</div><div class="s-lbl">🟠 Major</div></div>
                <div class="stat-box stat-crit"><div class="s-num">{counts['Critical']}</div><div class="s-lbl">🔴 Critical</div></div>
            </div>
        """, unsafe_allow_html=True)

with tab_glossary:
    st.info("เพิ่มรายการคำศัพท์เพื่อใช้ในการตรวจสอบความสม่ำเสมอ")
    ga, gb, gc = st.columns([3,3,2])
    term = ga.text_input("Source Term")
    trans = gb.text_input("Translation")
    imp = gc.selectbox("Severity", ["Critical","Major","Minor"])
    if st.button("Add to Glossary"):
        st.session_state["glossary"].append({"term":term, "translation":trans, "importance":imp})
        st.success(f"Added {term}")