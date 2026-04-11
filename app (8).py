import streamlit as st
import pandas as pd
import numpy as np
import re
import json
import io
import zipfile
from datetime import datetime
from collections import defaultdict
import unicodedata

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TransQA Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
  --beige-50:  #faf8f4;
  --beige-100: #f3ede3;
  --beige-200: #e8ddd0;
  --beige-300: #d5c8b5;
  --mint-100:  #e6f4ef;
  --mint-200:  #c8e9dd;
  --mint-400:  #7dc9b0;
  --mint-600:  #3fa882;
  --mint-700:  #2e8a68;
  --slate-600: #475569;
  --slate-800: #1e293b;
  --pass-bg:   #e8f5e9; --pass-text: #1b5e20; --pass-border: #66bb6a;
  --minor-bg:  #fff8e1; --minor-text: #e65100; --minor-border: #ffca28;
  --major-bg:  #fff3e0; --major-text: #bf360c; --major-border: #ffa726;
  --crit-bg:   #fce4ec; --crit-text:  #880e4f; --crit-border:  #ef5350;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--beige-50);
  color: var(--slate-800);
}

/* Header */
.qa-header {
  background: linear-gradient(135deg, #2e8a68 0%, #3fa882 50%, #7dc9b0 100%);
  color: white;
  padding: 1.5rem 2rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 20px rgba(46,138,104,0.25);
}
.qa-header h1 {
  font-family: 'Playfair Display', serif;
  font-size: 1.9rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.5px;
}
.qa-header p { margin: 0; opacity: 0.85; font-size: 0.88rem; font-weight: 300; }

/* Stats bar */
.stats-bar {
  display: flex; gap: 10px; margin-bottom: 1.2rem; flex-wrap: wrap;
}
.stat-card {
  flex: 1; min-width: 100px;
  background: white;
  border-radius: 10px;
  padding: 0.8rem 1rem;
  text-align: center;
  border: 1.5px solid var(--beige-200);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform .15s;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-card .num { font-size: 1.8rem; font-weight: 700; line-height: 1; }
.stat-card .lbl { font-size: 0.72rem; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; margin-top: 4px; opacity: .7; }
.stat-total  { border-color: var(--mint-400); }
.stat-total  .num { color: var(--mint-700); }
.stat-pass   { border-color: var(--pass-border); }
.stat-pass   .num { color: var(--pass-text); }
.stat-minor  { border-color: var(--minor-border); }
.stat-minor  .num { color: var(--minor-text); }
.stat-major  { border-color: var(--major-border); }
.stat-major  .num { color: var(--major-text); }
.stat-crit   { border-color: var(--crit-border); }
.stat-crit   .num { color: var(--crit-text); }

/* QA Table rows */
.qa-row { padding: .55rem .9rem; border-radius: 6px; margin-bottom: 5px; font-size: .88rem; border-left: 4px solid transparent; }
.qa-row.pass   { background: var(--pass-bg);  border-color: var(--pass-border);  color: var(--pass-text); }
.qa-row.minor  { background: var(--minor-bg); border-color: var(--minor-border); color: var(--minor-text); }
.qa-row.major  { background: var(--major-bg); border-color: var(--major-border); color: var(--major-text); }
.qa-row.crit   { background: var(--crit-bg);  border-color: var(--crit-border);  color: var(--crit-text); }

/* Badge */
.badge { display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: .72rem; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
.badge-pass  { background: var(--pass-bg);  color: var(--pass-text);  border: 1px solid var(--pass-border); }
.badge-minor { background: var(--minor-bg); color: var(--minor-text); border: 1px solid var(--minor-border); }
.badge-major { background: var(--major-bg); color: var(--major-text); border: 1px solid var(--major-border); }
.badge-crit  { background: var(--crit-bg);  color: var(--crit-text);  border: 1px solid var(--crit-border); }

/* Panel cards */
.panel-card {
  background: white;
  border: 1.5px solid var(--beige-200);
  border-radius: 10px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.panel-title {
  font-family: 'Playfair Display', serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--mint-700);
  margin-bottom: .6rem;
  border-bottom: 1px solid var(--beige-200);
  padding-bottom: .4rem;
}
.file-badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--mint-100); color: var(--mint-700);
  border: 1px solid var(--mint-200); border-radius: 8px;
  padding: 4px 12px; font-size: .82rem; font-weight: 500;
  margin-bottom: .8rem;
}
.section-label {
  font-size: .78rem; font-weight: 600; letter-spacing: .06em;
  text-transform: uppercase; color: var(--slate-600); margin-bottom: .4rem;
}

/* Override Streamlit elements */
.stTabs [data-baseweb="tab-list"] {
  background: var(--beige-100);
  border-radius: 10px;
  padding: 4px;
  gap: 4px;
  border: 1px solid var(--beige-200);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 7px !important;
  font-weight: 500 !important;
  font-size: .88rem !important;
  padding: 6px 16px !important;
  color: var(--slate-600) !important;
}
.stTabs [aria-selected="true"] {
  background: white !important;
  color: var(--mint-700) !important;
  box-shadow: 0 1px 4px rgba(0,0,0,.08) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

.stButton>button {
  background: var(--mint-600) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: .88rem !important;
  padding: .45rem 1.2rem !important;
  transition: background .2s !important;
}
.stButton>button:hover { background: var(--mint-700) !important; }

.stTextInput>div>div>input, .stSelectbox>div>div, .stTextArea>div>div>textarea {
  border-color: var(--beige-300) !important;
  border-radius: 8px !important;
  font-size: .88rem !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
  border-color: var(--mint-400) !important;
  box-shadow: 0 0 0 3px rgba(125,201,176,.2) !important;
}

div[data-testid="stExpander"] {
  border: 1.5px solid var(--beige-200) !important;
  border-radius: 10px !important;
  background: white !important;
}
div[data-testid="metric-container"] { background: white; border-radius: 8px; padding: .5rem; }

.stDataFrame { border-radius: 8px; overflow: hidden; }
.stDataFrame th { background: var(--beige-100) !important; color: var(--slate-800) !important; }

.glossary-term {
  background: var(--beige-50); border: 1px solid var(--beige-200);
  border-radius: 8px; padding: .6rem .9rem; margin-bottom: 6px;
  display: flex; align-items: center; justify-content: space-between;
}
</style>
""", unsafe_allow_html=True)

# ─── State Init ────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "glossary": [],          # list of {term, translation, importance, notes}
        "history": [],           # list of {timestamp, filename, results, stats}
        "style_guide": {
            "punctuation": [
                {"symbol": ".", "name": "Full Stop", "enabled": True, "severity": "Minor"},
                {"symbol": ",", "name": "Comma", "enabled": True, "severity": "Minor"},
                {"symbol": "!", "name": "Exclamation", "enabled": True, "severity": "Minor"},
                {"symbol": "?", "name": "Question Mark", "enabled": True, "severity": "Minor"},
                {"symbol": ":", "name": "Colon", "enabled": True, "severity": "Minor"},
                {"symbol": ";", "name": "Semicolon", "enabled": True, "severity": "Minor"},
                {"symbol": "\"", "name": "Double Quote", "enabled": True, "severity": "Minor"},
                {"symbol": "'", "name": "Single Quote", "enabled": False, "severity": "Minor"},
                {"symbol": "-", "name": "Hyphen", "enabled": True, "severity": "Minor"},
                {"symbol": "—", "name": "Em Dash", "enabled": True, "severity": "Minor"},
                {"symbol": "...", "name": "Ellipsis", "enabled": True, "severity": "Minor"},
            ],
            "encoding": "UTF-8",
            "font": "",
            "tone": "Formal",
            "max_length_ratio": 1.5,
            "min_length_ratio": 0.5,
            "check_length": True,
            "check_encoding": True,
            "check_tone": False,
        },
        "qa_rules": {
            "placeholders": True,
            "glossary_check": True,
            "punctuation": True,
            "spelling_en": True,
            "spelling_th": True,
            "numbers": True,
            "extra_symbols": True,
            "length_check": True,
            "encoding_check": True,
            "style_guide": True,
        },
        "qa_results": [],
        "current_file": None,
        "source_col": None,
        "target_col": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── QA Engine ─────────────────────────────────────────────────────────────────
THAI_PATTERN = re.compile(r'[\u0e00-\u0e7f]')
PLACEHOLDER_PATTERN = re.compile(r'\{[^}]+\}|\[[^\]]+\]|%[sd\d]|<[^>]+>')
NUMBER_PATTERN = re.compile(r'\b\d[\d,\.]*\b')

COMMON_EN_MISSPELLINGS = {
    "teh": "the", "recieve": "receive", "occured": "occurred", "seperate": "separate",
    "definately": "definitely", "accomodate": "accommodate", "begining": "beginning",
    "beleive": "believe", "calender": "calendar", "collegue": "colleague",
    "concious": "conscious", "dissapear": "disappear", "enviroment": "environment",
    "experiance": "experience", "freind": "friend", "goverment": "government",
    "harrass": "harass", "independant": "independent", "lisence": "license",
    "maintanance": "maintenance", "millenium": "millennium", "necesary": "necessary",
    "occassion": "occasion", "persue": "pursue", "profesional": "professional",
    "publically": "publicly", "reccomend": "recommend", "refered": "referred",
    "relevent": "relevant", "remeber": "remember", "repitition": "repetition",
    "responsability": "responsibility", "rythm": "rhythm", "shedule": "schedule",
    "sieze": "seize", "succesful": "successful", "suprise": "surprise",
    "tommorrow": "tomorrow", "truely": "truly", "untill": "until", "wierd": "weird",
}

COMMON_TH_MISSPELLINGS = {
    "กรูณา": "กรุณา", "สวัสดิ์": "สวัสดี", "เรียบร้อ": "เรียบร้อย",
    "ประสงค์": "ประสงค์", "โดยเฉพราะ": "โดยเฉพาะ", "ผลิดภัณฑ์": "ผลิตภัณฑ์",
    "บริหาน": "บริหาร", "สำเหร็จ": "สำเร็จ", "เจตนาราย": "เจตนาร้าย",
    "ใด้": "ได้", "เนื่องจาก": "เนื่องจาก", "อนุมัติ": "อนุมัติ",
    "สิ่งแวดล้อม": "สิ่งแวดล้อม", "กฎหมาย": "กฎหมาย",
}

def get_placeholders(text):
    return set(PLACEHOLDER_PATTERN.findall(str(text)))

def get_numbers(text):
    return NUMBER_PATTERN.findall(str(text))

def check_spelling_en(text):
    issues = []
    words = re.findall(r'\b[a-zA-Z]+\b', str(text))
    for w in words:
        lw = w.lower()
        if lw in COMMON_EN_MISSPELLINGS:
            issues.append(f"'{w}' → '{COMMON_EN_MISSPELLINGS[lw]}'")
    return issues

def check_spelling_th(text):
    issues = []
    for wrong, correct in COMMON_TH_MISSPELLINGS.items():
        if wrong in str(text):
            issues.append(f"'{wrong}' → '{correct}'")
    return issues

def count_symbols(text):
    symbols = re.findall(r'[^\w\s\u0e00-\u0e7f]', str(text))
    return set(symbols)

def run_qa(df, src_col, tgt_col, rules, glossary, style):
    results = []
    sg = style

    for idx, row in df.iterrows():
        src = str(row[src_col]) if pd.notna(row[src_col]) else ""
        tgt = str(row[tgt_col]) if pd.notna(row[tgt_col]) else ""
        row_issues = []

        # 1. Placeholder check
        if rules.get("placeholders"):
            src_ph = get_placeholders(src)
            tgt_ph = get_placeholders(tgt)
            missing = src_ph - tgt_ph
            extra   = tgt_ph - src_ph
            if missing:
                row_issues.append({"rule": "Placeholder", "severity": "Critical",
                    "detail": f"Missing: {', '.join(missing)}"})
            if extra:
                row_issues.append({"rule": "Placeholder", "severity": "Major",
                    "detail": f"Extra placeholders: {', '.join(extra)}"})

        # 2. Number / specific data check
        if rules.get("numbers"):
            src_nums = get_numbers(src)
            tgt_nums = get_numbers(tgt)
            for n in src_nums:
                if n not in tgt_nums:
                    row_issues.append({"rule": "Numbers/Data", "severity": "Major",
                        "detail": f"Number '{n}' from source missing in target"})

        # 3. Extra symbols check
        if rules.get("extra_symbols"):
            src_sym = count_symbols(src)
            tgt_sym = count_symbols(tgt)
            extra_s = tgt_sym - src_sym - {'—', '–', ''', ''', '"', '"', '฿', '×'}
            if extra_s:
                row_issues.append({"rule": "Extra Symbols", "severity": "Minor",
                    "detail": f"Extra symbols in target: {' '.join(extra_s)}"})

        # 4. Spelling EN
        if rules.get("spelling_en"):
            sp_issues = check_spelling_en(tgt)
            for sp in sp_issues:
                row_issues.append({"rule": "Spelling EN", "severity": "Minor",
                    "detail": f"Possible misspelling: {sp}"})

        # 5. Spelling TH
        if rules.get("spelling_th") and THAI_PATTERN.search(tgt):
            sp_issues = check_spelling_th(tgt)
            for sp in sp_issues:
                row_issues.append({"rule": "Spelling TH", "severity": "Minor",
                    "detail": f"Possible misspelling: {sp}"})

        # 6. Glossary check
        if rules.get("glossary_check") and glossary:
            for g in glossary:
                term = g.get("term", "")
                trans = g.get("translation", "")
                imp   = g.get("importance", "Major")
                if term.lower() in src.lower() and trans and trans.lower() not in tgt.lower():
                    row_issues.append({"rule": "Glossary", "severity": imp,
                        "detail": f"Term '{term}' should be translated as '{trans}'"})

        # 7. Punctuation / Style guide
        if rules.get("punctuation") and sg:
            for p in sg.get("punctuation", []):
                if not p.get("enabled"):
                    continue
                sym = p["symbol"]
                sev = p.get("severity", "Minor")
                src_count = src.count(sym)
                tgt_count = tgt.count(sym)
                if src_count > 0 and tgt_count == 0:
                    row_issues.append({"rule": f"Punctuation '{sym}'", "severity": sev,
                        "detail": f"Source has {src_count}× '{sym}' but target has none"})

        # 8. Length check
        if rules.get("length_check") and sg.get("check_length"):
            if len(src) > 0:
                ratio = len(tgt) / len(src)
                max_r = sg.get("max_length_ratio", 1.5)
                min_r = sg.get("min_length_ratio", 0.5)
                if ratio > max_r:
                    row_issues.append({"rule": "Length", "severity": "Minor",
                        "detail": f"Target {ratio:.1f}× longer than source (max {max_r}×)"})
                elif ratio < min_r:
                    row_issues.append({"rule": "Length", "severity": "Minor",
                        "detail": f"Target {ratio:.1f}× shorter than source (min {min_r}×)"})

        # 9. Encoding check
        if rules.get("encoding_check") and sg.get("check_encoding"):
            try:
                tgt.encode(sg.get("encoding", "UTF-8"))
            except (UnicodeEncodeError, LookupError):
                row_issues.append({"rule": "Encoding", "severity": "Major",
                    "detail": f"Target contains characters incompatible with {sg.get('encoding','UTF-8')}"})

        # Determine row status
        if not row_issues:
            status = "Pass"
        else:
            sevs = [i["severity"] for i in row_issues]
            if "Critical" in sevs: status = "Critical"
            elif "Major"   in sevs: status = "Major"
            else:                   status = "Minor"

        results.append({
            "row": idx + 1,
            "source": src[:120] + ("…" if len(src) > 120 else ""),
            "target": tgt[:120] + ("…" if len(tgt) > 120 else ""),
            "status": status,
            "issues": row_issues,
        })

    return results

def calc_stats(results):
    total = len(results)
    counts = {"Pass": 0, "Minor": 0, "Major": 0, "Critical": 0}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    return total, counts

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="qa-header">
  <span style="font-size:2rem">✦</span>
  <div>
    <h1>TransQA Studio</h1>
    <p>Professional Translation Quality Assurance Platform</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab_qa, tab_glossary, tab_style, tab_history = st.tabs(
    ["🔍  QA Check", "📚  Glossary", "📐  Style Guide", "🕘  History"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — QA Check
# ══════════════════════════════════════════════════════════════════════════════
with tab_qa:
    col_left, col_right = st.columns([1, 2], gap="large")

    # ── Left: Upload + Settings ──
    with col_left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📂 Upload File</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Supported: CSV, XLSX, TXT",
            type=["csv", "xlsx", "xls", "txt"],
            key="qa_upload",
            label_visibility="collapsed",
        )

        if uploaded:
            st.session_state["current_file"] = uploaded.name
            st.markdown(f'<div class="file-badge">📄 {uploaded.name}</div>', unsafe_allow_html=True)

            # Load data
            try:
                if uploaded.name.endswith(".csv"):
                    df_raw = pd.read_csv(uploaded)
                elif uploaded.name.endswith((".xlsx", ".xls")):
                    df_raw = pd.read_excel(uploaded)
                else:
                    content = uploaded.read().decode("utf-8")
                    lines = content.strip().split("\n")
                    df_raw = pd.DataFrame({"source": lines})

                cols = list(df_raw.columns)

                st.markdown('<div class="section-label">Column Mapping</div>', unsafe_allow_html=True)
                if len(cols) >= 2:
                    src_default = next((c for c in cols if "source" in c.lower() or "src" in c.lower() or "en" in c.lower()), cols[0])
                    tgt_default = next((c for c in cols if "target" in c.lower() or "tgt" in c.lower() or "th" in c.lower()), cols[1])
                    src_idx = cols.index(src_default)
                    tgt_idx = cols.index(tgt_default)
                else:
                    src_idx, tgt_idx = 0, 0

                st.session_state["source_col"] = st.selectbox("Source column", cols, index=src_idx, key="src_sel")
                st.session_state["target_col"] = st.selectbox("Target column", cols, index=tgt_idx, key="tgt_sel")
                st.session_state["df_raw"] = df_raw

            except Exception as e:
                st.error(f"Error loading file: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── QA Rules ──
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">⚙️ QA Rules</div>', unsafe_allow_html=True)
        rules = st.session_state["qa_rules"]

        rules["placeholders"]    = st.toggle("Placeholder validation", rules["placeholders"])
        rules["numbers"]         = st.toggle("Numbers / Specific data", rules["numbers"])
        rules["extra_symbols"]   = st.toggle("Extra symbol detection", rules["extra_symbols"])
        rules["spelling_en"]     = st.toggle("Spelling check (English)", rules["spelling_en"])
        rules["spelling_th"]     = st.toggle("Spelling check (Thai)", rules["spelling_th"])
        rules["glossary_check"]  = st.toggle("Glossary consistency", rules["glossary_check"])
        rules["punctuation"]     = st.toggle("Punctuation / Style guide", rules["punctuation"])
        rules["length_check"]    = st.toggle("Length ratio check", rules["length_check"])
        rules["encoding_check"]  = st.toggle("Font & Encoding check", rules["encoding_check"])

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Run ──
        run_disabled = "df_raw" not in st.session_state
        if st.button("▶  Run QA Check", disabled=run_disabled, use_container_width=True):
            with st.spinner("Running QA checks…"):
                df = st.session_state["df_raw"]
                src_col = st.session_state["source_col"]
                tgt_col = st.session_state["target_col"]
                results = run_qa(df, src_col, tgt_col, rules,
                                 st.session_state["glossary"],
                                 st.session_state["style_guide"])
                st.session_state["qa_results"] = results

                # Save to history
                total, counts = calc_stats(results)
                st.session_state["history"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "filename": st.session_state.get("current_file", "—"),
                    "total": total,
                    "counts": counts,
                    "results": results,
                    "src_col": src_col,
                    "tgt_col": tgt_col,
                })
            st.success("QA check complete!")

    # ── Right: Results ──
    with col_right:
        results = st.session_state.get("qa_results", [])

        if results:
            total, counts = calc_stats(results)

            # Stats bar
            st.markdown(f"""
            <div class="stats-bar">
              <div class="stat-card stat-total"><div class="num">{total}</div><div class="lbl">Total</div></div>
              <div class="stat-card stat-pass"><div class="num">{counts.get('Pass',0)}</div><div class="lbl">Pass</div></div>
              <div class="stat-card stat-minor"><div class="num">{counts.get('Minor',0)}</div><div class="lbl">Minor</div></div>
              <div class="stat-card stat-major"><div class="num">{counts.get('Major',0)}</div><div class="lbl">Major</div></div>
              <div class="stat-card stat-crit"><div class="num">{counts.get('Critical',0)}</div><div class="lbl">Critical</div></div>
            </div>
            """, unsafe_allow_html=True)

            # Filter
            filter_sev = st.multiselect(
                "Filter by severity",
                ["Pass", "Minor", "Major", "Critical"],
                default=["Minor", "Major", "Critical"],
                key="filter_sev",
            )

            filtered = [r for r in results if r["status"] in filter_sev]

            # Progress bar
            pass_pct = counts.get("Pass", 0) / total if total else 0
            st.progress(pass_pct, text=f"Pass rate: {pass_pct*100:.1f}%")

            # Results table
            severity_map = {"Pass": "pass", "Minor": "minor", "Major": "major", "Critical": "crit"}
            badge_class  = {"Pass": "badge-pass", "Minor": "badge-minor", "Major": "badge-major", "Critical": "badge-crit"}

            for r in filtered:
                sc = severity_map[r["status"]]
                bc = badge_class[r["status"]]
                issues_html = ""
                if r["issues"]:
                    for iss in r["issues"]:
                        isc = severity_map.get(iss["severity"], "minor")
                        ibc = badge_class.get(iss["severity"], "badge-minor")
                        issues_html += f'<div style="margin-top:4px; font-size:.82rem; color:#444;">• <span class="badge {ibc}">{iss["rule"]}</span> {iss["detail"]}</div>'

                st.markdown(f"""
                <div class="qa-row {sc}">
                  <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; font-size:.82rem; opacity:.6;">Row {r['row']}</span>
                    <span class="badge {bc}">{r['status']}</span>
                  </div>
                  <div style="margin-top:5px; font-size:.83rem;">
                    <strong>SRC:</strong> {r['source']}<br>
                    <strong>TGT:</strong> {r['target']}
                  </div>
                  {issues_html}
                </div>
                """, unsafe_allow_html=True)

            # Export
            st.markdown("---")
            st.markdown('<div class="section-label">Export Results</div>', unsafe_allow_html=True)
            col_e1, col_e2 = st.columns(2)

            with col_e1:
                # Build export DataFrame
                export_rows = []
                for r in results:
                    for iss in (r["issues"] if r["issues"] else [{"rule": "—", "severity": "Pass", "detail": "No issues"}]):
                        export_rows.append({
                            "Row": r["row"],
                            "Source": r["source"],
                            "Target": r["target"],
                            "Status": r["status"],
                            "Rule": iss.get("rule", "—"),
                            "Severity": iss.get("severity", "Pass"),
                            "Detail": iss.get("detail", ""),
                        })
                export_df = pd.DataFrame(export_rows)
                csv_data = export_df.to_csv(index=False).encode("utf-8-sig")
                st.download_button("⬇ Download CSV", csv_data,
                    file_name=f"qa_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv", use_container_width=True)

            with col_e2:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    export_df.to_excel(writer, index=False, sheet_name="QA Results")
                xlsx_data = buf.getvalue()
                st.download_button("⬇ Download Excel", xlsx_data,
                    file_name=f"qa_results_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)

        else:
            st.markdown("""
            <div style="text-align:center; padding:4rem 2rem; color:#aaa;">
              <div style="font-size:3rem; margin-bottom:1rem;">✦</div>
              <div style="font-size:1.1rem; font-weight:500;">Upload a file and run QA Check</div>
              <div style="font-size:.88rem; margin-top:.5rem;">Results will appear here</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Glossary
# ══════════════════════════════════════════════════════════════════════════════
with tab_glossary:
    col_g1, col_g2 = st.columns([1, 1.4], gap="large")

    with col_g1:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">➕ Add Term</div>', unsafe_allow_html=True)

        g_term  = st.text_input("Source term", key="g_term", placeholder="e.g. Invoice")
        g_trans = st.text_input("Translation", key="g_trans", placeholder="e.g. ใบแจ้งหนี้")
        g_imp   = st.selectbox("Importance", ["Critical", "Major", "Minor"], key="g_imp")
        g_notes = st.text_area("Notes (optional)", key="g_notes", height=80, placeholder="Context, notes…")

        if st.button("Add to Glossary", use_container_width=True):
            if g_term.strip():
                st.session_state["glossary"].append({
                    "term": g_term.strip(),
                    "translation": g_trans.strip(),
                    "importance": g_imp,
                    "notes": g_notes.strip(),
                })
                st.success(f"Added: {g_term}")
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Import
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📥 Import Glossary</div>', unsafe_allow_html=True)
        gfile = st.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx"], key="g_import", label_visibility="collapsed")
        if gfile:
            try:
                if gfile.name.endswith(".csv"):
                    gdf = pd.read_csv(gfile)
                else:
                    gdf = pd.read_excel(gfile)
                gdf.columns = [c.lower().strip() for c in gdf.columns]
                added = 0
                for _, row2 in gdf.iterrows():
                    entry = {
                        "term": str(row2.get("term", row2.iloc[0]) if "term" in gdf.columns else row2.iloc[0]),
                        "translation": str(row2.get("translation", row2.iloc[1] if len(row2) > 1 else "")),
                        "importance": str(row2.get("importance", "Major")),
                        "notes": str(row2.get("notes", "")),
                    }
                    if entry["term"] and entry["term"] != "nan":
                        st.session_state["glossary"].append(entry)
                        added += 1
                st.success(f"Imported {added} terms")
                st.rerun()
            except Exception as e:
                st.error(f"Import error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_g2:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="panel-title">📚 Glossary — {len(st.session_state["glossary"])} terms</div>', unsafe_allow_html=True)

        if st.session_state["glossary"]:
            search_g = st.text_input("🔍 Search terms", key="g_search", placeholder="Filter…", label_visibility="collapsed")
            filtered_g = [g for g in st.session_state["glossary"]
                          if not search_g or search_g.lower() in g["term"].lower() or search_g.lower() in g["translation"].lower()]

            for i, g in enumerate(filtered_g):
                real_idx = st.session_state["glossary"].index(g)
                bc = badge_class if 'badge_class' in dir() else {"Critical":"badge-crit","Major":"badge-major","Minor":"badge-minor","Pass":"badge-pass"}
                imp_badge = {"Critical": "badge-crit", "Major": "badge-major", "Minor": "badge-minor"}.get(g["importance"], "badge-minor")
                with st.expander(f"**{g['term']}** → {g['translation']}", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        new_term  = st.text_input("Term", g["term"], key=f"gt_{real_idx}")
                        new_trans = st.text_input("Translation", g["translation"], key=f"gtr_{real_idx}")
                        new_imp   = st.selectbox("Importance", ["Critical", "Major", "Minor"],
                            index=["Critical","Major","Minor"].index(g["importance"]), key=f"gi_{real_idx}")
                        new_notes = st.text_input("Notes", g["notes"], key=f"gn_{real_idx}")
                        if st.button("💾 Save", key=f"gsv_{real_idx}"):
                            st.session_state["glossary"][real_idx] = {
                                "term": new_term, "translation": new_trans,
                                "importance": new_imp, "notes": new_notes,
                            }
                            st.rerun()
                    with c2:
                        if st.button("🗑 Delete", key=f"gd_{real_idx}"):
                            st.session_state["glossary"].pop(real_idx)
                            st.rerun()

            # Export glossary
            if st.session_state["glossary"]:
                gexp = pd.DataFrame(st.session_state["glossary"])
                gcsv = gexp.to_csv(index=False).encode("utf-8-sig")
                st.download_button("⬇ Export Glossary CSV", gcsv,
                    file_name="glossary.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("No glossary terms yet. Add terms on the left.")

        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Style Guide
# ══════════════════════════════════════════════════════════════════════════════
with tab_style:
    sg = st.session_state["style_guide"]

    col_s1, col_s2 = st.columns([1, 1], gap="large")

    with col_s1:
        # ── Project settings ──
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🔧 Project Settings</div>', unsafe_allow_html=True)

        sg["encoding"] = st.selectbox("Encoding", ["UTF-8", "UTF-16", "TIS-620", "ISO-8859-1", "Windows-1252"],
            index=["UTF-8","UTF-16","TIS-620","ISO-8859-1","Windows-1252"].index(sg.get("encoding","UTF-8")))
        sg["font"]  = st.text_input("Expected Font (optional)", sg.get("font",""), placeholder="e.g. Sarabun, TH Sarabun New")
        sg["tone"]  = st.selectbox("Tone", ["Formal", "Semi-Formal", "Casual", "Technical", "Legal"],
            index=["Formal","Semi-Formal","Casual","Technical","Legal"].index(sg.get("tone","Formal")))
        sg["check_encoding"] = st.toggle("Enable Encoding Check", sg.get("check_encoding", True))
        sg["check_length"]   = st.toggle("Enable Length Check", sg.get("check_length", True))
        if sg["check_length"]:
            cc1, cc2 = st.columns(2)
            with cc1: sg["max_length_ratio"] = st.number_input("Max length ratio", min_value=0.5, max_value=5.0, value=float(sg.get("max_length_ratio",1.5)), step=0.1)
            with cc2: sg["min_length_ratio"] = st.number_input("Min length ratio", min_value=0.1, max_value=2.0, value=float(sg.get("min_length_ratio",0.5)), step=0.1)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Add custom punctuation ──
        with st.expander("➕ Add Custom Punctuation / Symbol", expanded=False):
            new_sym_input = st.text_input("Symbol(s) — separate multiple with space", key="new_sym", placeholder='e.g.  ※  ·  〈〉')
            new_sym_name  = st.text_input("Name", key="new_sym_name", placeholder="e.g. Reference mark")
            new_sym_sev   = st.selectbox("Severity", ["Minor", "Major", "Critical"], key="new_sym_sev")
            if st.button("Add Symbol(s)", key="add_sym"):
                symbols_to_add = new_sym_input.strip().split()
                for sym in symbols_to_add:
                    if sym:
                        sg["punctuation"].append({"symbol": sym, "name": new_sym_name or sym, "enabled": True, "severity": new_sym_sev})
                st.success(f"Added {len(symbols_to_add)} symbol(s)")
                st.rerun()

    with col_s2:
        # ── Punctuation toggles ──
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">✍️ Punctuation Rules</div>', unsafe_allow_html=True)

        sev_colors = {"Minor": "#fff8e1", "Major": "#fff3e0", "Critical": "#fce4ec"}

        for i, p in enumerate(sg["punctuation"]):
            bg = sev_colors.get(p.get("severity","Minor"), "#fff8e1")
            with st.container():
                c1, c2, c3, c4 = st.columns([1.5, 3, 2.5, 1])
                with c1:
                    p["enabled"] = st.toggle("", p.get("enabled", True), key=f"pen_{i}", label_visibility="collapsed")
                with c2:
                    st.markdown(f'<span style="font-family:DM Mono,monospace; background:{bg}; padding:2px 8px; border-radius:5px; font-size:.9rem;">{p["symbol"]}</span> <span style="font-size:.82rem; color:#666;">{p["name"]}</span>', unsafe_allow_html=True)
                with c3:
                    p["severity"] = st.selectbox("", ["Minor","Major","Critical"],
                        index=["Minor","Major","Critical"].index(p.get("severity","Minor")),
                        key=f"psev_{i}", label_visibility="collapsed")
                with c4:
                    if st.button("✕", key=f"pdel_{i}"):
                        sg["punctuation"].pop(i)
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — History
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    history = st.session_state["history"]

    if not history:
        st.markdown("""
        <div style="text-align:center; padding:4rem; color:#aaa;">
          <div style="font-size:3rem">🕘</div>
          <div style="margin-top:1rem; font-size:1rem; font-weight:500;">No history yet</div>
          <div style="font-size:.85rem; margin-top:.3rem">Run a QA check to see it here</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary table
        hist_rows = []
        for h in reversed(history):
            c = h["counts"]
            hist_rows.append({
                "Time": h["timestamp"],
                "File": h["filename"],
                "Total": h["total"],
                "✅ Pass": c.get("Pass", 0),
                "🟡 Minor": c.get("Minor", 0),
                "🟠 Major": c.get("Major", 0),
                "🔴 Critical": c.get("Critical", 0),
                "Pass %": f"{c.get('Pass',0)/h['total']*100:.0f}%" if h["total"] else "—",
            })

        hist_df = pd.DataFrame(hist_rows)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        # Detail expand
        st.markdown("---")
        st.markdown('<div class="section-label">View session details</div>', unsafe_allow_html=True)
        for j, h in enumerate(reversed(history)):
            with st.expander(f"📄 {h['filename']}  ·  {h['timestamp']}  ·  {h['total']} rows", expanded=False):
                c = h["counts"]
                st.markdown(f"""
                <div class="stats-bar" style="margin-bottom:.5rem">
                  <div class="stat-card stat-pass"><div class="num">{c.get('Pass',0)}</div><div class="lbl">Pass</div></div>
                  <div class="stat-card stat-minor"><div class="num">{c.get('Minor',0)}</div><div class="lbl">Minor</div></div>
                  <div class="stat-card stat-major"><div class="num">{c.get('Major',0)}</div><div class="lbl">Major</div></div>
                  <div class="stat-card stat-crit"><div class="num">{c.get('Critical',0)}</div><div class="lbl">Critical</div></div>
                </div>
                """, unsafe_allow_html=True)

                # Re-export from history
                export_rows = []
                for r in h["results"]:
                    for iss in (r["issues"] if r["issues"] else [{"rule": "—", "severity": "Pass", "detail": "No issues"}]):
                        export_rows.append({
                            "Row": r["row"], "Source": r["source"], "Target": r["target"],
                            "Status": r["status"], "Rule": iss.get("rule","—"),
                            "Severity": iss.get("severity","Pass"), "Detail": iss.get("detail",""),
                        })
                export_df2 = pd.DataFrame(export_rows)
                csv2 = export_df2.to_csv(index=False).encode("utf-8-sig")
                st.download_button(f"⬇ Export this session",
                    csv2, file_name=f"qa_{h['timestamp'].replace(':','').replace(' ','_')}.csv",
                    mime="text/csv", key=f"hist_dl_{j}")

        # Clear history
        if st.button("🗑 Clear All History"):
            st.session_state["history"] = []
            st.rerun()
