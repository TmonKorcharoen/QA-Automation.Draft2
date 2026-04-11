import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime

st.set_page_config(
    page_title="TransQA Studio",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Sarabun', sans-serif !important;
    background-color: #f7f4ef !important;
    color: #1a1a1a !important;
}
.main .block-container {
    padding: 0 2.5rem 3rem 2.5rem !important;
    max-width: 1300px !important;
}

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

/* Section title */
.sec-title {
    font-size: 1.05rem; font-weight: 600; color: #2e7d32;
    margin: 1.4rem 0 0.8rem 0; padding-bottom: 0.4rem;
    border-bottom: 1px solid #e8e8e8;
}

/* File badge */
.file-info {
    background: #f1f8f1; border: 1px solid #c8e6c9; border-radius: 8px;
    padding: 0.5rem 1rem; font-size: 0.92rem; color: #2e7d32;
    display: inline-flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;
}

/* Stats row */
.stats-row { display: flex; gap: 12px; margin: 1.2rem 0; flex-wrap: wrap; }
.stat-box  {
    flex: 1; min-width: 90px; background: #fafafa;
    border: 1.5px solid #e0e0e0; border-radius: 10px;
    padding: 0.9rem 0.8rem; text-align: center;
}
.stat-box .s-num { font-size: 2rem; font-weight: 700; line-height: 1; }
.stat-box .s-lbl { font-size: 0.78rem; font-weight: 600; color: #888; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.stat-total .s-num { color: #2e7d32; }
.stat-pass  .s-num { color: #388e3c; } .stat-pass  { border-color: #a5d6a7; }
.stat-minor .s-num { color: #f57c00; } .stat-minor { border-color: #ffcc80; }
.stat-major .s-num { color: #e64a19; } .stat-major { border-color: #ffab91; }
.stat-crit  .s-num { color: #c62828; } .stat-crit  { border-color: #ef9a9a; }

/* QA Table — matching screenshot style */
.qa-table { width: 100%; border-collapse: collapse; margin-top: 0.8rem; font-size: 0.97rem; }
.qa-table thead tr { border-bottom: 2px solid #e0e0e0; }
.qa-table thead th {
    padding: 0.6rem 1rem 0.6rem 0; font-weight: 600;
    color: #333; text-align: left; font-size: 0.92rem;
}
.qa-table tbody tr { border-bottom: 1px solid #f0f0f0; }
.qa-table tbody tr:hover { background: #fafafa; }
.qa-table td { padding: 0.85rem 1rem 0.85rem 0; vertical-align: top; color: #222; line-height: 1.55; }
.td-num    { font-weight: 700; color: #555; width: 42px; }
.td-text   { max-width: 250px; word-break: break-word; }
.td-rule   { color: #555; white-space: nowrap; }
.sev-cell  { white-space: nowrap; font-weight: 600; font-size: 1rem; }
.sev-pass  { color: #388e3c; }
.sev-minor { color: #f57c00; }
.sev-major { color: #e64a19; }
.sev-crit  { color: #c62828; }
.td-detail { color: #444; font-size: 0.9rem; }

/* Buttons */
.stButton > button {
    background: #2e7d32 !important; color: white !important;
    border: none !important; border-radius: 7px !important;
    font-size: 0.95rem !important; font-weight: 500 !important;
    padding: 0.45rem 1.3rem !important;
    font-family: 'Sarabun', sans-serif !important;
}
.stButton > button:hover { background: #1b5e20 !important; }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stSelectbox > div > div {
    border-color: #ddd !important; border-radius: 7px !important;
    font-size: 0.95rem !important; font-family: 'Sarabun', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
    border-color: #43a047 !important;
    box-shadow: 0 0 0 2px rgba(67,160,71,0.15) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #e0e0e0 !important;
    background: transparent !important; gap: 0 !important; padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1rem !important; font-weight: 500 !important; color: #666 !important;
    padding: 0.65rem 1.5rem !important; border-radius: 0 !important;
    background: transparent !important; border-bottom: 3px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #2e7d32 !important; border-bottom: 3px solid #2e7d32 !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Expander */
div[data-testid="stExpander"] {
    border: 1px solid #e8e8e8 !important; border-radius: 8px !important; background: white !important;
}
</style>
""", unsafe_allow_html=True)

# ── State ────────────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "glossary": [],
        "history": [],
        "style_guide": {
            "punctuation": [
                {"symbol": ".",   "name": "Full Stop",     "enabled": True,  "severity": "Minor"},
                {"symbol": ",",   "name": "Comma",         "enabled": True,  "severity": "Minor"},
                {"symbol": "!",   "name": "Exclamation",   "enabled": True,  "severity": "Minor"},
                {"symbol": "?",   "name": "Question Mark", "enabled": True,  "severity": "Minor"},
                {"symbol": ":",   "name": "Colon",         "enabled": True,  "severity": "Minor"},
                {"symbol": ";",   "name": "Semicolon",     "enabled": True,  "severity": "Minor"},
                {"symbol": '"',   "name": "Double Quote",  "enabled": True,  "severity": "Minor"},
                {"symbol": "-",   "name": "Hyphen",        "enabled": True,  "severity": "Minor"},
                {"symbol": "—",   "name": "Em Dash",       "enabled": True,  "severity": "Minor"},
                {"symbol": "...", "name": "Ellipsis",      "enabled": True,  "severity": "Minor"},
            ],
            "encoding": "UTF-8", "font": "", "tone": "Formal",
            "max_length_ratio": 1.5, "min_length_ratio": 0.5,
            "check_length": True, "check_encoding": True,
        },
        "qa_rules": {
            "placeholders": True, "glossary_check": True, "punctuation": True,
            "spelling_en": True,  "spelling_th": True,    "numbers": True,
            "extra_symbols": True,"length_check": True,   "encoding_check": True,
        },
        "qa_results": [], "current_file": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── QA Engine ────────────────────────────────────────────────────────────────────
PH_PAT  = re.compile(r'\{[^}]+\}|\[[^\]]+\]|%[sd\d]|<[^>]+>')
NUM_PAT = re.compile(r'\b\d[\d,\.]*\b')
TH_PAT  = re.compile(r'[\u0e00-\u0e7f]')
EN_TYPOS = {
    "teh":"the","recieve":"receive","occured":"occurred","seperate":"separate",
    "definately":"definitely","accomodate":"accommodate","begining":"beginning",
    "beleive":"believe","freind":"friend","goverment":"government",
    "necesary":"necessary","occassion":"occasion","succesful":"successful",
    "suprise":"surprise","tommorrow":"tomorrow","untill":"until","wierd":"weird",
    "reccomend":"recommend","refered":"referred","relevent":"relevant",
}
TH_TYPOS = {
    "กรูณา":"กรุณา","ใด้":"ได้","โดยเฉพราะ":"โดยเฉพาะ",
    "ผลิดภัณฑ์":"ผลิตภัณฑ์","สำเหร็จ":"สำเร็จ","บริหาน":"บริหาร",
}
SEV_EMOJI = {"Pass":"✅","Minor":"🟡","Major":"🟠","Critical":"🔴"}
SEV_CLASS = {"Pass":"sev-pass","Minor":"sev-minor","Major":"sev-major","Critical":"sev-crit"}

def run_qa(df, src_col, tgt_col, rules, glossary, style):
    results = []
    for idx, row in df.iterrows():
        src = str(row[src_col]) if pd.notna(row[src_col]) else ""
        tgt = str(row[tgt_col]) if pd.notna(row[tgt_col]) else ""
        issues = []

        if rules.get("placeholders"):
            sp, tp = set(PH_PAT.findall(src)), set(PH_PAT.findall(tgt))
            for m in sp - tp:
                issues.append({"rule":"Placeholder","severity":"Critical","detail":f"หาย: {m}"})
            for m in tp - sp:
                issues.append({"rule":"Placeholder","severity":"Major","detail":f"เกิน: {m}"})

        if rules.get("numbers"):
            for n in NUM_PAT.findall(src):
                if n not in set(NUM_PAT.findall(tgt)):
                    issues.append({"rule":"Numbers","severity":"Major","detail":f"หายเลข: {n}"})

        if rules.get("extra_symbols"):
            skip = {'—','–',''',''','"','"','฿','×','·'}
            ssym = set(re.findall(r'[^\w\s\u0e00-\u0e7f]', src)) - skip
            tsym = set(re.findall(r'[^\w\s\u0e00-\u0e7f]', tgt)) - skip
            extra = tsym - ssym
            if extra:
                issues.append({"rule":"Extra Symbols","severity":"Minor","detail":f"สัญลักษณ์เพิ่ม: {' '.join(extra)}"})

        if rules.get("spelling_en"):
            for w in re.findall(r'\b[a-zA-Z]+\b', tgt):
                if w.lower() in EN_TYPOS:
                    issues.append({"rule":"Spelling EN","severity":"Minor","detail":f"'{w}' → '{EN_TYPOS[w.lower()]}'"})

        if rules.get("spelling_th") and TH_PAT.search(tgt):
            for wrong, correct in TH_TYPOS.items():
                if wrong in tgt:
                    issues.append({"rule":"Spelling TH","severity":"Minor","detail":f"'{wrong}' → '{correct}'"})

        if rules.get("glossary_check"):
            for g in glossary:
                term = g.get("term","").strip()
                trans = g.get("translation","").strip()
                imp = g.get("importance","Major")
                if not term:
                    continue
                if term.lower() in src.lower():
                    if not trans:
                        issues.append({"rule":"Glossary","severity":"Minor",
                            "detail":f"พบ '{term}' ใน source แต่ยังไม่ได้กำหนดคำแปลใน Glossary"})
                    elif trans.lower() not in tgt.lower():
                        issues.append({"rule":"Glossary","severity":imp,
                            "detail":f"'{term}' ควรแปลว่า '{trans}' (ไม่พบในคำแปล)"})

        if rules.get("punctuation"):
            for p in style.get("punctuation",[]):
                if not p.get("enabled"): continue
                sym, sev = p["symbol"], p.get("severity","Minor")
                if src.count(sym) > 0 and tgt.count(sym) == 0:
                    issues.append({"rule":f"เครื่องหมาย '{sym}'","severity":sev,"detail":f"ไม่มี '{sym}' ใน target"})

        if rules.get("length_check") and style.get("check_length") and len(src) > 0:
            ratio = len(tgt) / len(src)
            if ratio > style.get("max_length_ratio",1.5):
                issues.append({"rule":"Length","severity":"Minor","detail":f"ยาวกว่า source {ratio:.1f}×"})
            elif ratio < style.get("min_length_ratio",0.5):
                issues.append({"rule":"Length","severity":"Minor","detail":f"สั้นกว่า source {ratio:.1f}×"})

        if rules.get("encoding_check") and style.get("check_encoding"):
            try:
                tgt.encode(style.get("encoding","UTF-8"))
            except Exception:
                issues.append({"rule":"Encoding","severity":"Major","detail":f"ตัวอักษรไม่รองรับ {style.get('encoding','UTF-8')}"})

        sevs = [i["severity"] for i in issues]
        status = "Critical" if "Critical" in sevs else "Major" if "Major" in sevs else "Minor" if sevs else "Pass"
        results.append({"row":idx+1,"source":src,"target":tgt,"status":status,"issues":issues})
    return results

def calc_stats(results):
    counts = {"Pass":0,"Minor":0,"Major":0,"Critical":0}
    for r in results: counts[r["status"]] = counts.get(r["status"],0) + 1
    return len(results), counts

def build_export_df(results):
    rows = []
    for r in results:
        for iss in (r["issues"] if r["issues"] else [{"rule":"—","severity":"Pass","detail":"ไม่พบปัญหา"}]):
            rows.append({"#":r["row"],"Source":r["source"],"Target":r["target"],
                "Status":r["status"],"Rule":iss.get("rule","—"),
                "ระดับ":iss.get("severity","Pass"),"รายละเอียด":iss.get("detail","")})
    return pd.DataFrame(rows)

# ── Header ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="app-header-icon">🔍</div>
  <div>
    <div class="app-header-title">TransQA Studio</div>
    <div class="app-header-sub">ระบบตรวจสอบคุณภาพการแปล · Translation Quality Assurance</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────────
tab_qa, tab_glossary, tab_style, tab_history = st.tabs([
    "🔍  QA Check", "📚  Glossary", "📐  Style Guide", "🕘  History"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — QA CHECK
# ════════════════════════════════════════════════════════════════════════════════
with tab_qa:
    st.markdown('<div class="sec-title">📂 อัปโหลดไฟล์</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("รองรับ CSV, XLSX, TXT", type=["csv","xlsx","xls","txt"], key="qa_upload")

    if uploaded:
        st.session_state["current_file"] = uploaded.name
        st.markdown(f'<div class="file-info">📄 {uploaded.name}</div>', unsafe_allow_html=True)
        try:
            if uploaded.name.endswith(".csv"):
                df_raw = pd.read_csv(uploaded)
            elif uploaded.name.endswith((".xlsx",".xls")):
                df_raw = pd.read_excel(uploaded)
            else:
                lines = uploaded.read().decode("utf-8").strip().split("\n")
                df_raw = pd.DataFrame({"source": lines})
            st.session_state["df_raw"] = df_raw

            cols = list(df_raw.columns)
            uc1, uc2 = st.columns(2)
            with uc1:
                src_def = next((c for c in cols if any(k in c.lower() for k in ["source","src","en","ต้นฉบับ"])), cols[0])
                st.session_state["source_col"] = st.selectbox("คอลัมน์ Source", cols, index=cols.index(src_def))
            with uc2:
                tgt_def = next((c for c in cols if any(k in c.lower() for k in ["target","tgt","th","แปล"])), cols[min(1,len(cols)-1)])
                st.session_state["target_col"] = st.selectbox("คอลัมน์ Target", cols, index=cols.index(tgt_def))

            st.caption(f"ตัวอย่างข้อมูล ({len(df_raw)} แถว)")
            st.dataframe(df_raw.head(3), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"โหลดไฟล์ไม่ได้: {e}")

    st.markdown('<div class="sec-title">⚙️ กฎการตรวจสอบ</div>', unsafe_allow_html=True)
    rules = st.session_state["qa_rules"]
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        rules["placeholders"]   = st.toggle("Placeholder",        rules["placeholders"])
        rules["numbers"]        = st.toggle("ตัวเลข / ข้อมูลเฉพาะ", rules["numbers"])
        rules["extra_symbols"]  = st.toggle("สัญลักษณ์เกิน",       rules["extra_symbols"])
    with rc2:
        rules["spelling_en"]    = st.toggle("Spelling (EN)",       rules["spelling_en"])
        rules["spelling_th"]    = st.toggle("Spelling (TH)",       rules["spelling_th"])
        rules["glossary_check"] = st.toggle("Glossary",            rules["glossary_check"])
    with rc3:
        rules["punctuation"]    = st.toggle("เครื่องหมายวรรคตอน",  rules["punctuation"])
        rules["length_check"]   = st.toggle("ความยาว",              rules["length_check"])
        rules["encoding_check"] = st.toggle("Encoding / Font",     rules["encoding_check"])

    st.write("")
    # แสดงสถานะ glossary ก่อน run
    g_count = len(st.session_state["glossary"])
    if g_count > 0:
        st.caption(f"📚 Glossary พร้อมใช้งาน: **{g_count} คำ** — จะนำมาตรวจสอบเมื่อเปิด toggle Glossary")
    else:
        st.caption("📚 Glossary: ยังว่างอยู่ — เพิ่มคำใน Tab Glossary ก่อนรัน")

    if st.button("▶  รันการตรวจสอบ QA", disabled=("df_raw" not in st.session_state)):
        with st.spinner("กำลังตรวจสอบ…"):
            # snapshot ค่า rules และ glossary ณ ตอนที่กด run (ป้องกัน reference mutation)
            rules_snapshot    = dict(st.session_state["qa_rules"])
            glossary_snapshot = list(st.session_state["glossary"])
            style_snapshot    = dict(st.session_state["style_guide"])
            results = run_qa(
                st.session_state["df_raw"],
                st.session_state["source_col"],
                st.session_state["target_col"],
                rules_snapshot, glossary_snapshot, style_snapshot,
            )
            st.session_state["qa_results"] = results
            total, counts = calc_stats(results)
            st.session_state["history"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "filename": st.session_state.get("current_file","—"),
                "total": total, "counts": counts, "results": results,
            })
        st.success(f"ตรวจสอบเสร็จแล้ว — {total} แถว")

    # Results
    results = st.session_state.get("qa_results", [])
    if results:
        total, counts = calc_stats(results)

        st.markdown(f"""
        <div class="stats-row">
          <div class="stat-box stat-total"><div class="s-num">{total}</div><div class="s-lbl">ทั้งหมด</div></div>
          <div class="stat-box stat-pass" ><div class="s-num">{counts.get('Pass',0)}</div><div class="s-lbl">✅ Pass</div></div>
          <div class="stat-box stat-minor"><div class="s-num">{counts.get('Minor',0)}</div><div class="s-lbl">🟡 Minor</div></div>
          <div class="stat-box stat-major"><div class="s-num">{counts.get('Major',0)}</div><div class="s-lbl">🟠 Major</div></div>
          <div class="stat-box stat-crit" ><div class="s-num">{counts.get('Critical',0)}</div><div class="s-lbl">🔴 Critical</div></div>
        </div>
        """, unsafe_allow_html=True)

        pass_pct = counts.get("Pass",0) / total if total else 0
        st.progress(pass_pct, text=f"Pass rate: {pass_pct*100:.1f}%")

        st.markdown('<div class="sec-title">กรองตามระดับ</div>', unsafe_allow_html=True)
        filter_sev = st.multiselect("ระดับ", ["Critical","Major","Minor","Pass"],
            default=["Critical","Major","Minor"], label_visibility="collapsed")

        # Export buttons
        exp_df = build_export_df(results)
        ec1, ec2, _ = st.columns([1.2, 1.2, 4])
        with ec1:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                exp_df.to_excel(w, index=False, sheet_name="QA Results")
            st.download_button("⬇ Export Excel", buf.getvalue(),
                file_name=f"qa_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with ec2:
            st.download_button("⬇ Export CSV", exp_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"qa_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv", use_container_width=True)

        # Build flat rows (one row per issue — like screenshot)
        filtered = [r for r in results if r["status"] in filter_sev]
        flat_rows = []
        for r in filtered:
            if r["issues"]:
                for iss in r["issues"]:
                    flat_rows.append({
                        "row": r["row"], "source": r["source"], "target": r["target"],
                        "rule": iss["rule"], "severity": iss["severity"], "detail": iss["detail"],
                    })
            else:
                flat_rows.append({
                    "row": r["row"], "source": r["source"], "target": r["target"],
                    "rule": "—", "severity": "Pass", "detail": "ไม่พบปัญหา",
                })

        if flat_rows:
            rows_html = ""
            for fr in flat_rows:
                sc = SEV_CLASS.get(fr["severity"], "sev-minor")
                em = SEV_EMOJI.get(fr["severity"], "🟡")
                src_d = fr["source"][:120] + ("…" if len(fr["source"]) > 120 else "")
                tgt_d = fr["target"][:120] + ("…" if len(fr["target"]) > 120 else "")
                rows_html += f"""
                <tr>
                  <td class="td-num">{fr['row']}</td>
                  <td class="td-text">{src_d}</td>
                  <td class="td-text">{tgt_d}</td>
                  <td class="td-rule">{fr['rule']}</td>
                  <td class="sev-cell {sc}">{em} {fr['severity']}</td>
                  <td class="td-detail">{fr['detail']}</td>
                </tr>"""

            st.markdown(f"""
            <table class="qa-table">
              <thead><tr>
                <th>#</th><th>source</th><th>target</th>
                <th>Rule</th><th>ระดับ</th><th>รายละเอียด</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("ไม่มีผลลัพธ์ในระดับที่เลือก")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — GLOSSARY
# ════════════════════════════════════════════════════════════════════════════════
with tab_glossary:
    st.markdown('<div class="sec-title">➕ เพิ่มคำศัพท์</div>', unsafe_allow_html=True)
    ga, gb, gc, gd = st.columns([2,2,1.5,2])
    with ga: g_term  = st.text_input("คำ Source", key="g_term",  placeholder="เช่น Invoice")
    with gb: g_trans = st.text_input("คำแปล",     key="g_trans", placeholder="เช่น ใบแจ้งหนี้")
    with gc: g_imp   = st.selectbox("ระดับ", ["Critical","Major","Minor"], key="g_imp")
    with gd: g_notes = st.text_input("หมายเหตุ",  key="g_notes", placeholder="บริบท / หมายเหตุ")

    if st.button("เพิ่มคำศัพท์"):
        if g_term.strip():
            st.session_state["glossary"].append({
                "term":g_term.strip(),"translation":g_trans.strip(),
                "importance":g_imp,"notes":g_notes.strip()})
            st.success(f"เพิ่มแล้ว: {g_term}")
            st.rerun()

    st.markdown('<div class="sec-title">📥 นำเข้า Glossary (CSV / XLSX)</div>', unsafe_allow_html=True)
    gfile = st.file_uploader("คอลัมน์: term, translation, importance, notes", type=["csv","xlsx"], key="g_import")
    if gfile:
        try:
            gdf = pd.read_csv(gfile) if gfile.name.endswith(".csv") else pd.read_excel(gfile)
            gdf.columns = [c.lower().strip() for c in gdf.columns]
            added = 0
            for _, row2 in gdf.iterrows():
                entry = {
                    "term":        str(row2.get("term", row2.iloc[0])),
                    "translation": str(row2.get("translation", row2.iloc[1] if len(row2)>1 else "")),
                    "importance":  str(row2.get("importance","Major")),
                    "notes":       str(row2.get("notes","")),
                }
                if entry["term"] and entry["term"] != "nan":
                    st.session_state["glossary"].append(entry); added += 1
            st.success(f"นำเข้า {added} คำ"); st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown(f'<div class="sec-title">📚 รายการคำศัพท์ ({len(st.session_state["glossary"])} คำ)</div>', unsafe_allow_html=True)
    if st.session_state["glossary"]:
        search_g = st.text_input("🔍 ค้นหา", key="g_search", placeholder="กรองคำ…")
        filtered_g = [g for g in st.session_state["glossary"]
                      if not search_g or search_g.lower() in g["term"].lower() or search_g.lower() in g["translation"].lower()]
        for i, g in enumerate(filtered_g):
            real_idx = st.session_state["glossary"].index(g)
            with st.expander(f"{g['term']}  →  {g['translation']}", expanded=False):
                ec1, ec2 = st.columns([3,1])
                with ec1:
                    nt  = st.text_input("คำ Source", g["term"],       key=f"gt_{real_idx}")
                    ntr = st.text_input("คำแปล",     g["translation"], key=f"gtr_{real_idx}")
                    ni  = st.selectbox("ระดับ", ["Critical","Major","Minor"],
                        index=["Critical","Major","Minor"].index(g["importance"]), key=f"gi_{real_idx}")
                    nn  = st.text_input("หมายเหตุ",  g["notes"],       key=f"gn_{real_idx}")
                    if st.button("💾 บันทึก", key=f"gsv_{real_idx}"):
                        st.session_state["glossary"][real_idx] = {"term":nt,"translation":ntr,"importance":ni,"notes":nn}
                        st.rerun()
                with ec2:
                    st.write("")
                    if st.button("🗑 ลบ", key=f"gd_{real_idx}"):
                        st.session_state["glossary"].pop(real_idx); st.rerun()
        gexp = pd.DataFrame(st.session_state["glossary"])
        st.download_button("⬇ Export Glossary CSV", gexp.to_csv(index=False).encode("utf-8-sig"),
            file_name="glossary.csv", mime="text/csv")
    else:
        st.info("ยังไม่มีคำศัพท์ เพิ่มได้ด้านบน")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — STYLE GUIDE
# ════════════════════════════════════════════════════════════════════════════════
with tab_style:
    sg = st.session_state["style_guide"]
    st.markdown('<div class="sec-title">🔧 ตั้งค่าโปรเจกต์</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sg["encoding"] = st.selectbox("Encoding",
            ["UTF-8","UTF-16","TIS-620","ISO-8859-1","Windows-1252"],
            index=["UTF-8","UTF-16","TIS-620","ISO-8859-1","Windows-1252"].index(sg.get("encoding","UTF-8")))
        sg["font"] = st.text_input("Font (ถ้ากำหนด)", sg.get("font",""), placeholder="เช่น Sarabun")
    with sc2:
        sg["tone"] = st.selectbox("Tone", ["Formal","Semi-Formal","Casual","Technical","Legal"],
            index=["Formal","Semi-Formal","Casual","Technical","Legal"].index(sg.get("tone","Formal")))
        sg["check_encoding"] = st.toggle("เปิดการตรวจ Encoding", sg.get("check_encoding",True))
    with sc3:
        sg["check_length"] = st.toggle("เปิดการตรวจความยาว", sg.get("check_length",True))
        if sg["check_length"]:
            sg["max_length_ratio"] = st.number_input("สัดส่วนสูงสุด", 0.5, 5.0, float(sg.get("max_length_ratio",1.5)), 0.1)
            sg["min_length_ratio"] = st.number_input("สัดส่วนต่ำสุด", 0.1, 2.0, float(sg.get("min_length_ratio",0.5)), 0.1)

    st.markdown('<div class="sec-title">✍️ เครื่องหมายวรรคตอน</div>', unsafe_allow_html=True)
    sev_bg = {"Minor":"#fff8e1","Major":"#fff3e0","Critical":"#fce4ec"}
    for i, p in enumerate(sg["punctuation"]):
        c1, c2, c3, c4, c5 = st.columns([0.7,1.2,2.8,2,0.7])
        with c1:
            p["enabled"] = st.toggle("", p.get("enabled",True), key=f"pen_{i}", label_visibility="collapsed")
        with c2:
            bg = sev_bg.get(p.get("severity","Minor"),"#fff8e1")
            st.markdown(f'<span style="font-family:monospace;background:{bg};padding:3px 10px;border-radius:5px;font-size:1rem;">{p["symbol"]}</span>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<span style="font-size:0.93rem;color:#555;line-height:2.2;">{p["name"]}</span>', unsafe_allow_html=True)
        with c4:
            p["severity"] = st.selectbox("", ["Minor","Major","Critical"],
                index=["Minor","Major","Critical"].index(p.get("severity","Minor")),
                key=f"psev_{i}", label_visibility="collapsed")
        with c5:
            if st.button("✕", key=f"pdel_{i}"):
                sg["punctuation"].pop(i); st.rerun()

    with st.expander("➕ เพิ่มเครื่องหมายใหม่", expanded=False):
        ns1, ns2, ns3 = st.columns([2,2,1.5])
        with ns1: new_syms = st.text_input("สัญลักษณ์ (คั่นด้วย space)", key="new_sym", placeholder="เช่น ※ · 〈〉")
        with ns2: new_name = st.text_input("ชื่อ", key="new_sym_name", placeholder="เช่น Reference mark")
        with ns3: new_sev  = st.selectbox("ระดับ", ["Minor","Major","Critical"], key="new_sym_sev")
        if st.button("เพิ่ม", key="add_sym"):
            for sym in new_syms.strip().split():
                sg["punctuation"].append({"symbol":sym,"name":new_name or sym,"enabled":True,"severity":new_sev})
            st.success("เพิ่มแล้ว"); st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — HISTORY
# ════════════════════════════════════════════════════════════════════════════════
with tab_history:
    history = st.session_state["history"]
    if not history:
        st.info("ยังไม่มีประวัติการตรวจสอบ รัน QA Check ก่อนนะคะ")
    else:
        hist_rows = []
        for h in reversed(history):
            c = h["counts"]
            hist_rows.append({
                "เวลา": h["timestamp"], "ไฟล์": h["filename"], "ทั้งหมด": h["total"],
                "✅ Pass": c.get("Pass",0), "🟡 Minor": c.get("Minor",0),
                "🟠 Major": c.get("Major",0), "🔴 Critical": c.get("Critical",0),
                "Pass %": f"{c.get('Pass',0)/h['total']*100:.0f}%" if h["total"] else "—",
            })
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)

        st.markdown('<div class="sec-title">รายละเอียดแต่ละ Session</div>', unsafe_allow_html=True)
        for j, h in enumerate(reversed(history)):
            with st.expander(f"📄 {h['filename']}  ·  {h['timestamp']}  ·  {h['total']} แถว"):
                c = h["counts"]
                st.markdown(f"""
                <div class="stats-row">
                  <div class="stat-box stat-pass" ><div class="s-num">{c.get('Pass',0)}</div><div class="s-lbl">✅ Pass</div></div>
                  <div class="stat-box stat-minor"><div class="s-num">{c.get('Minor',0)}</div><div class="s-lbl">🟡 Minor</div></div>
                  <div class="stat-box stat-major"><div class="s-num">{c.get('Major',0)}</div><div class="s-lbl">🟠 Major</div></div>
                  <div class="stat-box stat-crit" ><div class="s-num">{c.get('Critical',0)}</div><div class="s-lbl">🔴 Critical</div></div>
                </div>
                """, unsafe_allow_html=True)
                rows2 = []
                for r in h["results"]:
                    for iss in (r["issues"] if r["issues"] else [{"rule":"—","severity":"Pass","detail":"ไม่พบปัญหา"}]):
                        rows2.append({"#":r["row"],"Source":r["source"],"Target":r["target"],
                            "Rule":iss.get("rule","—"),"ระดับ":iss.get("severity","Pass"),"รายละเอียด":iss.get("detail","")})
                df2 = pd.DataFrame(rows2)
                st.download_button("⬇ Export session นี้",
                    df2.to_csv(index=False).encode("utf-8-sig"),
                    file_name=f"qa_{h['timestamp'].replace(':','').replace(' ','_')}.csv",
                    mime="text/csv", key=f"hdl_{j}")

        if st.button("🗑 ล้างประวัติทั้งหมด"):
            st.session_state["history"] = []; st.rerun()
