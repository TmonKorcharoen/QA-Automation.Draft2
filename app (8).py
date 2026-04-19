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
    background-color: #f5f0e8 !important;
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
    border-bottom: 1px solid #ddd;
}

/* File badge */
.file-info {
    background: #edf5ed; border: 1px solid #c8e6c9; border-radius: 8px;
    padding: 0.5rem 1rem; font-size: 0.92rem; color: #2e7d32;
    display: inline-flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;
}

/* Stats row */
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

/* QA Table */
.qa-table { width: 100%; border-collapse: collapse; margin-top: 0.8rem; font-size: 0.97rem; }
.qa-table thead tr { border-bottom: 2px solid #ccc; }
.qa-table thead th {
    padding: 0.6rem 1rem 0.6rem 0; font-weight: 600;
    color: #333; text-align: left; font-size: 0.92rem;
    background: transparent;
}
.qa-table tbody tr { border-bottom: 1px solid #e8e0d5; }
.qa-table tbody tr:hover { background: #ede8df; }
.qa-table td { padding: 0.9rem 1rem 0.9rem 0; vertical-align: top; color: #222; line-height: 1.6; }
.td-num    { font-weight: 700; color: #555; width: 42px; white-space: nowrap; }
.td-text   { min-width: 200px; max-width: 280px; word-break: break-word; }
.td-rule   { color: #555; white-space: nowrap; }
.sev-cell  { white-space: nowrap; font-weight: 600; font-size: 1rem; }
.sev-pass  { color: #388e3c; }
.sev-minor { color: #f57c00; }
.sev-major { color: #e64a19; }
.sev-crit  { color: #c62828; }
.td-detail { color: #444; font-size: 0.9rem; min-width: 160px; }

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
    border-color: #ccc !important; border-radius: 7px !important;
    font-size: 0.95rem !important; font-family: 'Sarabun', sans-serif !important;
    background: #fffdf8 !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
    border-color: #43a047 !important;
    box-shadow: 0 0 0 2px rgba(67,160,71,0.15) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 2px solid #ccc !important;
    background: transparent !important; gap: 0 !important; padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-size: 1rem !important; font-weight: 500 !important; color: #777 !important;
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
    border: 1px solid #ddd !important; border-radius: 8px !important;
    background: #fffdf8 !important;
}

/* Dataframe */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Caption / info */
.stAlert { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── State ────────────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "glossary": [],
        "history": [],
        "style_guide": {
            "punctuation": [
                # ── ไวยากรณ์ภาษาอังกฤษ (grammar) — ปิด default เพราะภาษาไทยไม่ใช้
                {"symbol": ".",  "name": "จุด (Full Stop)",          "type": "grammar", "enabled": False, "severity": "Minor"},
                {"symbol": ",",  "name": "จุลภาค (Comma)",           "type": "grammar", "enabled": False, "severity": "Minor"},
                {"symbol": "!",  "name": "อัศเจรีย์ (Exclamation)",  "type": "grammar", "enabled": False, "severity": "Minor"},
                {"symbol": "?",  "name": "ปรัศนี (Question Mark)",   "type": "grammar", "enabled": False, "severity": "Minor"},
                {"symbol": ":",  "name": "ทวิภาค (Colon)",           "type": "grammar", "enabled": False, "severity": "Minor"},
                {"symbol": ";",  "name": "อัฒภาค (Semicolon)",       "type": "grammar", "enabled": False, "severity": "Minor"},
                {"symbol": "-",  "name": "ยัติภังค์ (Hyphen)",       "type": "grammar", "enabled": False, "severity": "Minor"},
                # ── อักขระพิเศษ (special) — เปิด default เพราะต้องคงไว้เสมอ
                {"symbol": "...", "name": "จุดไข่ปลา (Ellipsis)",    "type": "special", "enabled": True,  "severity": "Minor"},
                {"symbol": "—",  "name": "ยัติภังค์ยาว (Em Dash)",   "type": "special", "enabled": True,  "severity": "Minor"},
                {"symbol": '"',  "name": "อัญประกาศคู่",             "type": "special", "enabled": True,  "severity": "Minor"},
                {"symbol": "※",  "name": "เครื่องหมายอ้างอิง",      "type": "special", "enabled": False, "severity": "Minor"},
            ],
            "encoding": "UTF-8", "font": "", "tone": "Formal",
            "max_length_ratio": 1.5, "min_length_ratio": 0.5,
            "check_length": True, "check_encoding": True,
        },
        "qa_rules": {
            "placeholders": True, "glossary_check": True, "punctuation": True,
            "spelling_en": True,  "spelling_th": True,    "numbers": True,
            "extra_symbols": True,"length_check": True,   "encoding_check": True,
            "consistency_check": True,
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

# ปี พ.ศ. ↔ ค.ศ. ±543 — ถ้าเลขต่างกัน 543 ถือว่าตรงกัน
def numbers_match(src_nums, tgt_nums):
    """คืน set ของตัวเลขใน source ที่ไม่มีใน target (รวม offset พ.ศ./ค.ศ.)"""
    tgt_set = set(tgt_nums)
    missing = []
    for n in src_nums:
        try:
            nval = int(re.sub(r'[,\.]','', n))
            # ตรงกันเลย
            if n in tgt_set:
                continue
            # อาจแปลงปี พ.ศ. → ค.ศ. (ลบ 543) หรือกลับกัน
            offset_down = str(nval - 543)
            offset_up   = str(nval + 543)
            if offset_down in tgt_set or offset_up in tgt_set:
                continue
            # ไม่ตรงเลย
            missing.append(n)
        except Exception:
            if n not in tgt_set:
                missing.append(n)
    return missing

def run_qa(df, src_col, tgt_col, rules, glossary, style):
    results = []

    # ── Pre-pass: Consistency Check ───────────────────────────────────────────
    # สแกนทั้งไฟล์ก่อน เพื่อดูว่า term เดียวกันถูกแปลกี่รูปแบบ
    consistency_map = {}   # term_lower → { term, imp, expected, rows_found: {trans_used: [row_nums]} }
    if rules.get("glossary_check") and rules.get("consistency_check"):
        for g in glossary:
            if not g.get("enforce_consistency"):
                continue
            term = g.get("term","").strip()
            if not term:
                continue
            imp      = g.get("importance","Major")
            expected = g.get("translation","").strip()
            rows_found = {}  # trans_used (str) → [row_nums]

            for idx2, row2 in df.iterrows():
                src2 = str(row2[src_col]) if pd.notna(row2[src_col]) else ""
                tgt2 = str(row2[tgt_col]) if pd.notna(row2[tgt_col]) else ""
                if term.lower() not in src2.lower():
                    continue

                if expected and expected.lower() in tgt2.lower():
                    used = expected   # แปลถูก ใช้ expected เป็น key
                elif not expected:
                    # ไม่ได้กำหนด expected → ใช้ target ทั้งหมดเป็น key เพื่อตรวจว่าเหมือนกันไหม
                    used = tgt2.strip()
                else:
                    used = f"__other__: {tgt2[:60]}"  # แปลต่างออกไป

                rows_found.setdefault(used, []).append(idx2 + 1)

            consistency_map[term.lower()] = {
                "term": term, "imp": imp, "expected": expected,
                "rows_found": rows_found,
            }

    # สร้าง lookup row_num → [issues] จาก consistency_map
    consist_issues_by_row = {}
    for term_lower, cdata in consistency_map.items():
        rows_found = cdata["rows_found"]
        term       = cdata["term"]
        imp        = cdata["imp"]
        expected   = cdata["expected"]

        if not rows_found:
            continue

        unique_keys = list(rows_found.keys())

        if expected:
            # มี expected → ตรวจง่าย: แถวไหนไม่ใช้ expected → flagged
            wrong_rows = []
            for key, rnums in rows_found.items():
                if key != expected:
                    wrong_rows.extend(rnums)
            correct_rows = rows_found.get(expected, [])
            if wrong_rows:
                for rnum in wrong_rows:
                    consist_issues_by_row.setdefault(rnum, []).append({
                        "rule": "Consistency",
                        "severity": imp,
                        "detail": (
                            f"'{term}' ต้องแปลว่า '{expected}' เหมือนกันทุกแถว "
                            f"(แถวที่ถูก: {correct_rows if correct_rows else 'ไม่มี'})"
                        ),
                    })
        else:
            # ไม่มี expected → ตรวจว่าแปลเหมือนกันทั้งหมดไหม
            if len(unique_keys) > 1:
                # หา majority (ใช้บ่อยสุด = "ถูก")
                majority_key = max(unique_keys, key=lambda k: len(rows_found[k]))
                summary = "; ".join(
                    f'"{k[:40]}" (แถว {rows_found[k]})'
                    for k in unique_keys if k != majority_key
                )
                for key, rnums in rows_found.items():
                    if key == majority_key:
                        continue
                    for rnum in rnums:
                        consist_issues_by_row.setdefault(rnum, []).append({
                            "rule": "Consistency",
                            "severity": imp,
                            "detail": f"'{term}' ถูกแปลต่างกันในหลายแถว — แถวนี้ใช้: \"{key[:50]}\" ขณะที่แถวอื่นใช้: \"{majority_key[:50]}\"",
                        })

    for idx, row in df.iterrows():
        src = str(row[src_col]) if pd.notna(row[src_col]) else ""
        tgt = str(row[tgt_col]) if pd.notna(row[tgt_col]) else ""
        issues = []

        # เพิ่ม consistency issues ที่คำนวณไว้ล่วงหน้า
        for ci in consist_issues_by_row.get(idx + 1, []):
            issues.append(ci)

        # 1. Placeholder
        if rules.get("placeholders"):
            sp, tp = set(PH_PAT.findall(src)), set(PH_PAT.findall(tgt))
            for m in sp - tp:
                issues.append({"rule":"Placeholder","severity":"Critical",
                    "detail":f"ตัวแปร {m} หายไปจากคำแปล"})
            for m in tp - sp:
                issues.append({"rule":"Placeholder","severity":"Major",
                    "detail":f"มีตัวแปร {m} เกินมาในคำแปล"})

        # 2. ตัวเลข (รองรับ พ.ศ./ค.ศ.)
        if rules.get("numbers"):
            src_nums = NUM_PAT.findall(src)
            tgt_nums = NUM_PAT.findall(tgt)
            for n in numbers_match(src_nums, tgt_nums):
                issues.append({"rule":"ตัวเลข/ตัวเลข","severity":"Critical",
                    "detail":f"ตัวเลข หายไป: {n}"})

        # 3. สัญลักษณ์เกิน
        if rules.get("extra_symbols"):
            skip = {'—','–',''',''','"','"','฿','×','·','•'}
            ssym = set(re.findall(r'[^\w\s\u0e00-\u0e7f]', src)) - skip
            tsym = set(re.findall(r'[^\w\s\u0e00-\u0e7f]', tgt)) - skip
            extra = tsym - ssym
            if extra:
                issues.append({"rule":"สัญลักษณ์","severity":"Minor",
                    "detail":f"มีสัญลักษณ์เพิ่มมาในคำแปล: {' '.join(sorted(extra))}"})

        # 4. สะกดผิด (EN)
        if rules.get("spelling_en"):
            for w in re.findall(r'\b[a-zA-Z]+\b', tgt):
                if w.lower() in EN_TYPOS:
                    issues.append({"rule":"Spelling EN","severity":"Minor",
                        "detail":f"น่าจะสะกดผิด: '{w}' → '{EN_TYPOS[w.lower()]}'"})

        # 5. สะกดผิด (TH)
        if rules.get("spelling_th") and TH_PAT.search(tgt):
            for wrong, correct in TH_TYPOS.items():
                if wrong in tgt:
                    issues.append({"rule":"Spelling TH","severity":"Minor",
                        "detail":f"น่าจะสะกดผิด: '{wrong}' → '{correct}'"})

        # 6. Glossary — ตรวจว่าคำศัพท์ที่กำหนดไว้ถูกแปลถูกต้อง
        if rules.get("glossary_check") and glossary:
            for g in glossary:
                term  = g.get("term","").strip()
                trans = g.get("translation","").strip()
                imp   = g.get("importance","Major")
                if not term:
                    continue
                # ตรวจว่า term ปรากฏใน source ของแถวนี้
                if term.lower() in src.lower():
                    if not trans:
                        issues.append({"rule":"Glossary","severity":"Minor",
                            "detail":f"พบคำ '{term}' ใน source แต่ยังไม่ได้กำหนดคำแปลใน Glossary"})
                    elif trans.lower() not in tgt.lower():
                        issues.append({"rule":"Glossary","severity":imp,
                            "detail":f"'{term}' ควรแปลว่า '{trans}' แต่ไม่พบในคำแปล"})

        # 7. เครื่องหมายวรรคตอน
        if rules.get("punctuation"):
            tgt_is_thai = bool(TH_PAT.search(tgt))
            for p in style.get("punctuation",[]):
                if not p.get("enabled"):
                    continue
                sym  = p["symbol"]
                sev  = p.get("severity","Minor")
                ptype = p.get("type","special")  # "grammar" | "special"

                # เครื่องหมายไวยากรณ์ (. , ! ? : ; -) → ถ้า target เป็นภาษาไทย ข้ามได้
                # เพราะภาษาไทยไม่มีกฎบังคับใช้เครื่องหมายเหล่านี้
                if ptype == "grammar" and tgt_is_thai:
                    continue

                if src.count(sym) > 0 and tgt.count(sym) == 0:
                    issues.append({"rule":"เครื่องหมาย","severity":sev,
                        "detail":f"source มีเครื่องหมาย '{sym}' แต่ไม่พบในคำแปล"})

        # 8. ความยาว
        if rules.get("length_check") and style.get("check_length") and len(src) > 0:
            ratio = len(tgt) / len(src)
            if ratio > style.get("max_length_ratio",1.5):
                issues.append({"rule":"ความยาว","severity":"Minor",
                    "detail":f"คำแปลยาวกว่าต้นฉบับ {ratio:.1f} เท่า (เกินกว่า {style.get('max_length_ratio',1.5)} เท่า)"})
            elif ratio < style.get("min_length_ratio",0.5):
                issues.append({"rule":"ความยาว","severity":"Minor",
                    "detail":f"คำแปลสั้นกว่าต้นฉบับ {ratio:.1f} เท่า (ต่ำกว่า {style.get('min_length_ratio',0.5)} เท่า)"})

        # 9. Encoding
        if rules.get("encoding_check") and style.get("check_encoding"):
            try:
                tgt.encode(style.get("encoding","UTF-8"))
            except Exception:
                issues.append({"rule":"Encoding","severity":"Major",
                    "detail":f"คำแปลมีตัวอักษรที่ไม่รองรับใน {style.get('encoding','UTF-8')}"})

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
    <div class="app-header-sub">ระบบตรวจสอบคุณภาพงานแปล · Translation Quality Assurance</div>
  </div>
</div>
""", unsafe_allow_html=True)

tab_qa, tab_glossary, tab_style, tab_history = st.tabs([
    "🔍  ตรวจสอบ QA", "📚  Glossary", "📐  Style Guide", "🕘  ประวัติ"
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — QA CHECK
# ════════════════════════════════════════════════════════════════════════════════
with tab_qa:
    st.markdown('<div class="sec-title">📂 อัปโหลดไฟล์</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("รองรับไฟล์ CSV, XLSX, TXT", type=["csv","xlsx","xls","txt"], key="qa_upload")

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
                st.session_state["source_col"] = st.selectbox("เลือกคอลัมน์ต้นฉบับ (Source)", cols, index=cols.index(src_def))
            with uc2:
                tgt_def = next((c for c in cols if any(k in c.lower() for k in ["target","tgt","th","แปล"])), cols[min(1,len(cols)-1)])
                st.session_state["target_col"] = st.selectbox("เลือกคอลัมน์คำแปล (Target)", cols, index=cols.index(tgt_def))

            st.caption(f"ตัวอย่างข้อมูล 3 แถวแรก (ทั้งหมด {len(df_raw)} แถว)")
            st.dataframe(df_raw.head(3), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"ไม่สามารถโหลดไฟล์ได้: {e}")

    st.markdown('<div class="sec-title">⚙️ เลือกกฎที่ต้องการตรวจ</div>', unsafe_allow_html=True)
    rules = st.session_state["qa_rules"]
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        rules["placeholders"]       = st.toggle("ตรวจ Placeholder (ตัวแปร)",    rules["placeholders"])
        rules["numbers"]            = st.toggle("ตรวจตัวเลขและข้อมูลเฉพาะ",      rules["numbers"])
        rules["extra_symbols"]      = st.toggle("ตรวจสัญลักษณ์ที่เพิ่มขึ้น",     rules["extra_symbols"])
    with rc2:
        rules["spelling_en"]        = st.toggle("ตรวจสะกดคำภาษาอังกฤษ",          rules["spelling_en"])
        rules["spelling_th"]        = st.toggle("ตรวจสะกดคำภาษาไทย",             rules["spelling_th"])
        rules["glossary_check"]     = st.toggle("ตรวจตามรายการ Glossary",         rules["glossary_check"])
    with rc3:
        rules["punctuation"]        = st.toggle("ตรวจเครื่องหมายวรรคตอน",        rules["punctuation"])
        rules["length_check"]       = st.toggle("ตรวจความยาวของคำแปล",           rules["length_check"])
        rules["encoding_check"]     = st.toggle("ตรวจ Encoding และ Font",         rules["encoding_check"])
    rules["consistency_check"]  = st.toggle(
        "🔒 ตรวจความสม่ำเสมอของคำแปล (Consistency) — ตรวจว่าคำที่กำหนดใน Glossary ถูกแปลเหมือนกันทุกแถว",
        rules.get("consistency_check", True)
    )

    st.write("")
    g_count      = len(st.session_state["glossary"])
    g_consist_ct = sum(1 for g in st.session_state["glossary"] if g.get("enforce_consistency"))
    if g_count > 0:
        consist_note = f" · 🔒 {g_consist_ct} คำบังคับ Consistency" if g_consist_ct else ""
        st.caption(f"📚 Glossary พร้อมใช้งาน {g_count} คำ{consist_note} — เปิดสวิตช์ 'ตรวจตามรายการ Glossary' เพื่อเริ่มตรวจ")
    else:
        st.caption("📚 ยังไม่มี Glossary — ไปเพิ่มคำได้ที่แท็บ Glossary")

    if st.button("▶  เริ่มตรวจสอบ", disabled=("df_raw" not in st.session_state)):
        with st.spinner("กำลังตรวจสอบ กรุณารอสักครู่…"):
            rules_snap    = dict(st.session_state["qa_rules"])
            glossary_snap = [dict(g) for g in st.session_state["glossary"]]
            style_snap    = dict(st.session_state["style_guide"])

            results = run_qa(
                st.session_state["df_raw"],
                st.session_state["source_col"],
                st.session_state["target_col"],
                rules_snap, glossary_snap, style_snap,
            )
            st.session_state["qa_results"] = results
            total, counts = calc_stats(results)
            st.session_state["history"].append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "filename":  st.session_state.get("current_file","—"),
                "total": total, "counts": counts, "results": results,
            })
        st.success(f"ตรวจสอบเสร็จแล้ว พบ {total} แถว")

    # ── Results ──────────────────────────────────────────────────────────────────
    results = st.session_state.get("qa_results", [])
    if results:
        total, counts = calc_stats(results)

        st.markdown(f"""
        <style>
        .stats-row {{ display:flex; gap:10px; margin:1.2rem 0; flex-wrap:wrap; position:relative; }}
        .stat-box {{
          flex:1; min-width:90px; background:#fffdf8;
          border:1.5px solid #e0d8cc; border-radius:10px;
          padding:0.9rem 0.8rem; text-align:center;
          cursor:pointer; user-select:none;
          transition: transform .12s, box-shadow .12s;
          position: relative;
        }}
        .stat-box.no-click {{ cursor:default; }}
        .stat-box:not(.no-click):hover {{ transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,0.08); }}
        .stat-box:not(.no-click):hover .stat-hint {{ opacity:1; }}
        .stat-hint {{
          position:absolute; bottom:-6px; left:50%; transform:translateX(-50%);
          font-size:9px; color:#aaa; opacity:0; transition:opacity .15s;
          white-space:nowrap;
        }}
        .s-num {{ font-size:2rem; font-weight:700; line-height:1; }}
        .s-lbl {{ font-size:0.78rem; font-weight:600; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.05em; }}
        .stat-total .s-num {{ color:#2e7d32; }}
        .stat-pass  .s-num {{ color:#388e3c; }} .stat-pass  {{ border-color:#a5d6a7; }}
        .stat-minor .s-num {{ color:#f57c00; }} .stat-minor {{ border-color:#ffcc80; }}
        .stat-major .s-num {{ color:#e64a19; }} .stat-major {{ border-color:#ffab91; }}
        .stat-crit  .s-num {{ color:#c62828; }} .stat-crit  {{ border-color:#ef9a9a; }}

        /* Overlay — wrap ใน stats-row container */
        .stats-wrapper {{ position: relative; }}
        .sev-overlay {{
          display:none;
          position: absolute;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0,0,0,0.28);
          z-index: 100;
          border-radius: 12px;
          align-items: center;
          justify-content: center;
          min-height: 100px;
        }}
        .sev-overlay.open {{ display:flex; }}
        .sev-popup {{
          background:#fffdf8; border-radius:14px; padding:1.6rem 1.8rem;
          max-width:420px; width:90%; box-shadow:0 8px 32px rgba(0,0,0,0.18);
          position:relative; border:1.5px solid #e0d8cc;
          animation: popIn .15s ease;
        }}
        @keyframes popIn {{ from{{transform:scale(.94);opacity:0}} to{{transform:scale(1);opacity:1}} }}
        .sev-popup-close {{
          position:absolute; top:12px; right:14px;
          font-size:1.1rem; cursor:pointer; color:#aaa; background:none; border:none;
          line-height:1;
        }}
        .sev-popup-close:hover {{ color:#555; }}
        .sev-popup-title {{
          font-size:1.15rem; font-weight:700; margin:0 0 4px;
          display:flex; align-items:center; gap:8px;
        }}
        .sev-popup-sub {{
          font-size:0.82rem; font-weight:600; letter-spacing:.05em;
          text-transform:uppercase; margin:0 0 1rem; opacity:.6;
        }}
        .sev-popup-desc {{ font-size:0.95rem; color:#333; line-height:1.65; margin:0 0 1rem; }}
        .sev-popup-q {{
          font-size:0.88rem; background:#f5f0e8; border-radius:8px;
          padding:.6rem .9rem; color:#555; border-left:3px solid #ccc;
          margin:0 0 1rem;
        }}
        .sev-popup-q strong {{ color:#333; }}
        .sev-tags {{ display:flex; flex-wrap:wrap; gap:6px; }}
        .sev-tag {{
          font-size:0.78rem; padding:3px 10px; border-radius:20px;
          border:1px solid transparent;
        }}
        </style>

        <style>
        .stats-wrapper {{ position: relative; }}
        .stats-row {{ display:flex; gap:10px; margin:1.2rem 0 0 0; flex-wrap:wrap; }}
        .stat-box {{
          flex:1; min-width:90px; background:#fffdf8;
          border:1.5px solid #e0d8cc; border-radius:10px;
          padding:0.9rem 0.8rem; text-align:center;
          user-select:none; transition: transform .12s, box-shadow .12s;
          position: relative;
        }}
        .stat-box.clickable {{ cursor:pointer; }}
        .stat-box.clickable:hover {{ transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,0.08); }}
        .stat-box.clickable:hover .stat-hint {{ opacity:1; }}
        .stat-box.no-click {{ cursor:default; }}
        .stat-hint {{
          position:absolute; bottom:-5px; left:50%; transform:translateX(-50%);
          font-size:9px; color:#aaa; opacity:0; transition:opacity .15s; white-space:nowrap;
        }}
        .s-num {{ font-size:2rem; font-weight:700; line-height:1; }}
        .s-lbl {{ font-size:0.78rem; font-weight:600; color:#888; margin-top:4px; text-transform:uppercase; letter-spacing:0.05em; }}
        .stat-total .s-num {{ color:#2e7d32; }}
        .stat-pass  .s-num {{ color:#388e3c; }} .stat-pass  {{ border-color:#a5d6a7; }}
        .stat-minor .s-num {{ color:#f57c00; }} .stat-minor {{ border-color:#ffcc80; }}
        .stat-major .s-num {{ color:#e64a19; }} .stat-major {{ border-color:#ffab91; }}
        .stat-crit  .s-num {{ color:#c62828; }} .stat-crit  {{ border-color:#ef9a9a; }}

        .sev-popup-inline {{
          display: none;
          margin-top: 10px;
          background: #fffdf8;
          border-radius: 10px;
          padding: 1.2rem 1.4rem;
          border: 1.5px solid #e0d8cc;
          box-shadow: 0 4px 16px rgba(0,0,0,0.10);
          position: relative;
          animation: popIn .15s ease;
        }}
        .sev-popup-inline.open {{ display: block; }}
        @keyframes popIn {{ from{{transform:translateY(-6px);opacity:0}} to{{transform:translateY(0);opacity:1}} }}
        .sev-popup-close {{
          position:absolute; top:10px; right:12px;
          font-size:1rem; cursor:pointer; color:#aaa;
          background:none; border:none; line-height:1; padding:2px 6px;
        }}
        .sev-popup-close:hover {{ color:#555; }}
        .sev-popup-title {{
          font-size:1.1rem; font-weight:700; margin:0 0 2px;
          display:flex; align-items:center; gap:8px;
        }}
        .sev-popup-sub {{
          font-size:0.78rem; font-weight:600; letter-spacing:.06em;
          text-transform:uppercase; margin:0 0 0.8rem; opacity:.65;
        }}
        .sev-popup-desc {{ font-size:0.92rem; color:#333; line-height:1.65; margin:0 0 0.8rem; }}
        .sev-popup-q {{
          font-size:0.86rem; background:#f5f0e8; border-radius:7px;
          padding:.55rem .9rem; color:#555; border-left:3px solid #ccc; margin:0 0 0.8rem;
        }}
        .sev-popup-q strong {{ color:#333; }}
        .sev-tags {{ display:flex; flex-wrap:wrap; gap:6px; }}
        .sev-tag {{
          font-size:0.76rem; padding:3px 10px; border-radius:20px; border:1px solid transparent;
        }}
        </style>

        <div class="stats-wrapper">
          <div class="stats-row">
            <div class="stat-box stat-total no-click">
              <div class="s-num">{total}</div>
              <div class="s-lbl">ทั้งหมด</div>
            </div>
            <div class="stat-box stat-pass clickable" onclick="openPopup('pass')">
              <div class="s-num">{counts.get('Pass',0)}</div>
              <div class="s-lbl">✅ ผ่าน</div>
              <div class="stat-hint">คลิกดูรายละเอียด</div>
            </div>
            <div class="stat-box stat-minor clickable" onclick="openPopup('minor')">
              <div class="s-num">{counts.get('Minor',0)}</div>
              <div class="s-lbl">🟡 Minor</div>
              <div class="stat-hint">คลิกดูรายละเอียด</div>
            </div>
            <div class="stat-box stat-major clickable" onclick="openPopup('major')">
              <div class="s-num">{counts.get('Major',0)}</div>
              <div class="s-lbl">🟠 Major</div>
              <div class="stat-hint">คลิกดูรายละเอียด</div>
            </div>
            <div class="stat-box stat-crit clickable" onclick="openPopup('crit')">
              <div class="s-num">{counts.get('Critical',0)}</div>
              <div class="s-lbl">🔴 Critical</div>
              <div class="stat-hint">คลิกดูรายละเอียด</div>
            </div>
          </div>

          <!-- Inline popup แสดงใต้ stats bar -->
          <div class="sev-popup-inline" id="sevPopup">
            <button class="sev-popup-close" onclick="closePopup()">✕</button>
            <div class="sev-popup-title" id="popTitle"></div>
            <div class="sev-popup-sub"  id="popSub"></div>
            <div class="sev-popup-desc" id="popDesc"></div>
            <div class="sev-popup-q"    id="popQ"></div>
            <div class="sev-tags"       id="popTags"></div>
          </div>
        </div>

        <script>
        var popups = {{
          pass: {{
            title: "✅ Pass — ผ่านแล้ว",
            sub: "ไม่พบข้อผิดพลาด",
            color: "#388e3c",
            desc: "แถวที่ไม่พบข้อผิดพลาดใดๆ หรือมีข้อผิดพลาดเล็กน้อยมากจนยอมรับได้ตามเกณฑ์โปรเจกต์ที่กำหนด",
            q: "\"ยอมรับได้ตามเกณฑ์โปรเจกต์?\"",
            tags: ["ความหมายถูกต้อง", "ภาษาเป็นธรรมชาติ", "Glossary ตรงกัน"],
            tagColor: "#e8f5e9", tagText: "#1b5e20", tagBorder: "#a5d6a7"
          }},
          minor: {{
            title: "🟡 Minor — ข้อผิดพลาดเล็กน้อย",
            sub: "แก้ได้ในรอบถัดไป",
            color: "#f57c00",
            desc: "ความหมายยังถูกต้อง แต่คุณภาพภาษาไม่ดีพอ อาจดูไม่ professional หรือไม่สอดคล้องกับ style guide ของโปรเจกต์",
            q: "\"ความหมายถูก แต่ดูไม่ professional?\"",
            tags: ["สะกดผิด (typo)", "เครื่องหมายไม่สอดคล้อง", "ความยาวผิดสัดส่วน", "Inconsistency เล็กน้อย"],
            tagColor: "#fff8e1", tagText: "#e65100", tagBorder: "#ffcc80"
          }},
          major: {{
            title: "🟠 Major — ข้อผิดพลาดสำคัญ",
            sub: "ต้องแก้ก่อน publish",
            color: "#e64a19",
            desc: "ความหมายเปลี่ยนไปบางส่วน ผู้อ่านอาจเข้าใจผิดได้ แต่ยังไม่ถึงขั้นก่อความเสียหายร้ายแรง ต้องแก้ไขก่อนส่งงาน",
            q: "\"ผู้อ่านจะเข้าใจผิดไหม?\"",
            tags: ["Glossary ผิด (สำคัญ)", "ละเว้น clause สำคัญ", "โครงสร้างประโยคผิด", "ตัวเลขไม่ตรง"],
            tagColor: "#fff3e0", tagText: "#bf360c", tagBorder: "#ffab91"
          }},
          crit: {{
            title: "🔴 Critical — ข้อผิดพลาดร้ายแรง",
            sub: "ห้ามปล่อยผ่านเด็ดขาด",
            color: "#c62828",
            desc: "ข้อผิดพลาดที่ส่งผลกระทบร้ายแรง ความหมายเปลี่ยนไปจนตรงข้าม ข้อมูลสำคัญหาย หรืออาจก่อให้เกิดความเสียหายในเชิงกฎหมาย/ความปลอดภัย",
            q: "\"ถ้าปล่อยผ่าน จะเกิดความเสียหายไหม?\"",
            tags: ["ตัวแปรหาย {{DAMAGE}}", "ความหมายตรงข้าม", "ไม่ได้แปล", "ตัวเลขสำคัญหาย"],
            tagColor: "#fce4ec", tagText: "#880e4f", tagBorder: "#ef9a9a"
          }}
        }};
        var currentOpen = null;
        function openPopup(key) {{
          if (currentOpen === key) {{ closePopup(); return; }}
          currentOpen = key;
          var d = popups[key];
          document.getElementById('popTitle').innerHTML = d.title;
          document.getElementById('popTitle').style.color = d.color;
          document.getElementById('popSub').textContent  = d.sub;
          document.getElementById('popSub').style.color  = d.color;
          document.getElementById('popDesc').textContent = d.desc;
          document.getElementById('popQ').innerHTML = '<strong>ถามตัวเองว่า:</strong> ' + d.q;
          document.getElementById('popQ').style.borderColor = d.color;
          var tagsHtml = '';
          d.tags.forEach(function(t) {{
            tagsHtml += '<span class="sev-tag" style="background:' + d.tagColor + ';color:' + d.tagText + ';border-color:' + d.tagBorder + '">' + t + '</span>';
          }});
          document.getElementById('popTags').innerHTML = tagsHtml;
          var el = document.getElementById('sevPopup');
          el.classList.remove('open');
          void el.offsetWidth;
          el.classList.add('open');
        }}
        function closePopup() {{
          currentOpen = null;
          document.getElementById('sevPopup').classList.remove('open');
        }}
        document.addEventListener('keydown', function(e) {{
          if (e.key === 'Escape') closePopup();
        }});
        </script>
        """, unsafe_allow_html=True)


        pass_pct = counts.get("Pass",0) / total if total else 0
        st.progress(pass_pct, text=f"อัตราผ่าน: {pass_pct*100:.1f}%")

        st.markdown('<div class="sec-title">กรองตามระดับความรุนแรง</div>', unsafe_allow_html=True)
        filter_sev = st.multiselect(
            "ระดับ", ["Critical","Major","Minor","Pass"],
            default=["Critical","Major","Minor"],
            label_visibility="collapsed",
        )

        # Export
        exp_df = build_export_df(results)
        ec1, ec2, _ = st.columns([1.2, 1.2, 4])
        with ec1:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                exp_df.to_excel(w, index=False, sheet_name="QA Results")
            st.download_button("⬇ ดาวน์โหลด Excel", buf.getvalue(),
                file_name=f"qa_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with ec2:
            st.download_button("⬇ ดาวน์โหลด CSV", exp_df.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"qa_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv", use_container_width=True)

        # Build table rows — แสดงข้อความเต็ม ไม่ตัด
        filtered = [r for r in results if r["status"] in filter_sev]
        flat_rows = []
        for r in filtered:
            if r["issues"]:
                for iss in r["issues"]:
                    flat_rows.append({
                        "row": r["row"],
                        "source": r["source"],   # ← เต็ม ไม่ตัด
                        "target": r["target"],   # ← เต็ม ไม่ตัด
                        "rule": iss["rule"],
                        "severity": iss["severity"],
                        "detail": iss["detail"],
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
                # escape HTML entities to prevent injection, but keep full text
                src_safe = fr["source"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                tgt_safe = fr["target"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                rows_html += f"""
                <tr>
                  <td class="td-num">{fr['row']}</td>
                  <td class="td-text">{src_safe}</td>
                  <td class="td-text">{tgt_safe}</td>
                  <td class="td-rule">{fr['rule']}</td>
                  <td class="sev-cell {sc}">{em} {fr['severity']}</td>
                  <td class="td-detail">{fr['detail']}</td>
                </tr>"""

            st.markdown(f"""
            <table class="qa-table">
              <thead><tr>
                <th>#</th>
                <th>ต้นฉบับ (Source)</th>
                <th>คำแปล (Target)</th>
                <th>กฎที่ตรวจ</th>
                <th>ระดับ</th>
                <th>รายละเอียด</th>
              </tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("ไม่มีแถวที่ตรงกับระดับที่เลือก")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — GLOSSARY
# ════════════════════════════════════════════════════════════════════════════════
with tab_glossary:
    st.markdown('<div class="sec-title">➕ เพิ่มคำศัพท์ใหม่</div>', unsafe_allow_html=True)
    ga, gb, gc, gd = st.columns([2,2,1.5,2])
    with ga: g_term  = st.text_input("คำต้นฉบับ (Source)", key="g_term",  placeholder="เช่น Invoice")
    with gb: g_trans = st.text_input("คำแปลที่ถูกต้อง",    key="g_trans", placeholder="เช่น ใบแจ้งหนี้")
    with gc: g_imp   = st.selectbox("ระดับความสำคัญ", ["Critical","Major","Minor"], key="g_imp")
    with gd: g_notes = st.text_input("หมายเหตุ / บริบท",  key="g_notes", placeholder="บริบทการใช้งาน")

    g_consist = st.toggle(
        "🔒 บังคับแปลเหมือนกันทุกแถว (Consistency Check) — หากคำนี้ปรากฏในหลายแถว ต้องแปลออกมาเป็นคำเดียวกันเสมอ",
        value=False, key="g_consist"
    )

    if st.button("เพิ่มลงใน Glossary"):
        if g_term.strip():
            st.session_state["glossary"].append({
                "term": g_term.strip(), "translation": g_trans.strip(),
                "importance": g_imp, "notes": g_notes.strip(),
                "enforce_consistency": g_consist,
            })
            st.success(f"เพิ่มคำ '{g_term}' เรียบร้อยแล้ว")
            st.rerun()
        else:
            st.warning("กรุณาใส่คำต้นฉบับก่อน")

    st.markdown('<div class="sec-title">📥 นำเข้า Glossary จากไฟล์</div>', unsafe_allow_html=True)
    st.caption("ไฟล์ควรมีคอลัมน์: term, translation, importance, notes")
    gfile = st.file_uploader("เลือกไฟล์ CSV หรือ XLSX", type=["csv","xlsx"], key="g_import")
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
                    "enforce_consistency": str(row2.get("enforce_consistency","False")).strip().lower() in ("true","1","yes","ใช่"),
                }
                if entry["term"] and entry["term"] != "nan":
                    st.session_state["glossary"].append(entry); added += 1
            st.success(f"นำเข้าสำเร็จ {added} คำ")
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")

    st.markdown(f'<div class="sec-title">📚 รายการ Glossary ทั้งหมด ({len(st.session_state["glossary"])} คำ)</div>', unsafe_allow_html=True)
    if st.session_state["glossary"]:
        search_g = st.text_input("🔍 ค้นหาคำ", key="g_search", placeholder="พิมพ์เพื่อกรอง…")
        filtered_g = [g for g in st.session_state["glossary"]
                      if not search_g or search_g.lower() in g["term"].lower() or search_g.lower() in g["translation"].lower()]

        imp_label = {"Critical":"🔴 Critical","Major":"🟠 Major","Minor":"🟡 Minor"}
        for i, g in enumerate(filtered_g):
            real_idx = st.session_state["glossary"].index(g)
            badge = imp_label.get(g["importance"], g["importance"])
            lock  = "  🔒" if g.get("enforce_consistency") else ""
            with st.expander(f"{g['term']}  →  {g['translation']}  ({badge}){lock}", expanded=False):
                ec1, ec2 = st.columns([3,1])
                with ec1:
                    nt  = st.text_input("คำต้นฉบับ", g["term"],        key=f"gt_{real_idx}")
                    ntr = st.text_input("คำแปล",      g["translation"], key=f"gtr_{real_idx}")
                    ni  = st.selectbox("ระดับความสำคัญ", ["Critical","Major","Minor"],
                        index=["Critical","Major","Minor"].index(g["importance"]), key=f"gi_{real_idx}")
                    nn  = st.text_input("หมายเหตุ", g["notes"], key=f"gn_{real_idx}")
                    nc  = st.toggle("🔒 บังคับแปลเหมือนกันทุกแถว",
                        value=g.get("enforce_consistency", False), key=f"gc_{real_idx}")
                    if st.button("💾 บันทึกการแก้ไข", key=f"gsv_{real_idx}"):
                        st.session_state["glossary"][real_idx] = {
                            "term":nt,"translation":ntr,"importance":ni,
                            "notes":nn,"enforce_consistency":nc,
                        }
                        st.success("บันทึกเรียบร้อย"); st.rerun()
                with ec2:
                    st.write("")
                    st.write("")
                    if st.button("🗑 ลบ", key=f"gd_{real_idx}"):
                        st.session_state["glossary"].pop(real_idx); st.rerun()

        gexp = pd.DataFrame(st.session_state["glossary"])
        st.download_button("⬇ ดาวน์โหลด Glossary (CSV)",
            gexp.to_csv(index=False).encode("utf-8-sig"),
            file_name="glossary.csv", mime="text/csv")
    else:
        st.info("ยังไม่มีคำใน Glossary เพิ่มคำได้ด้านบนเลยค่ะ")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — STYLE GUIDE
# ════════════════════════════════════════════════════════════════════════════════
with tab_style:
    sg = st.session_state["style_guide"]
    st.markdown('<div class="sec-title">🔧 ตั้งค่าโปรเจกต์</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sg["encoding"] = st.selectbox("Encoding ที่ใช้",
            ["UTF-8","UTF-16","TIS-620","ISO-8859-1","Windows-1252"],
            index=["UTF-8","UTF-16","TIS-620","ISO-8859-1","Windows-1252"].index(sg.get("encoding","UTF-8")))
        sg["font"] = st.text_input("ชื่อ Font (ถ้ากำหนด)", sg.get("font",""), placeholder="เช่น Sarabun, TH Sarabun New")
    with sc2:
        sg["tone"] = st.selectbox("ระดับภาษา (Tone)", ["Formal","Semi-Formal","Casual","Technical","Legal"],
            index=["Formal","Semi-Formal","Casual","Technical","Legal"].index(sg.get("tone","Formal")))
        sg["check_encoding"] = st.toggle("เปิดใช้การตรวจ Encoding", sg.get("check_encoding",True))
    with sc3:
        sg["check_length"] = st.toggle("เปิดใช้การตรวจความยาว", sg.get("check_length",True))
        if sg["check_length"]:
            sg["max_length_ratio"] = st.number_input("คำแปลยาวได้สูงสุด (×)", 0.5, 5.0, float(sg.get("max_length_ratio",1.5)), 0.1)
            sg["min_length_ratio"] = st.number_input("คำแปลสั้นได้ต่ำสุด (×)", 0.1, 2.0, float(sg.get("min_length_ratio",0.5)), 0.1)

    st.markdown('<div class="sec-title">✍️ กฎเครื่องหมายวรรคตอน</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#edf5ed;border:1px solid #c8e6c9;border-radius:8px;padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.9rem;color:#2e7d32;line-height:1.6;">
    <strong>💡 ประเภทเครื่องหมาย</strong><br>
    <span style="background:#e3f2fd;color:#1565c0;padding:1px 7px;border-radius:4px;font-size:0.82rem;font-weight:600;">ไวยากรณ์</span>
    &nbsp;เครื่องหมายที่เป็นส่วนหนึ่งของไวยากรณ์ภาษาอังกฤษ เช่น <code>. , ! ?</code> — ภาษาไทยไม่ต้องใช้ <strong>ปิดไว้ by default</strong><br>
    <span style="background:#fce4ec;color:#880e4f;padding:1px 7px;border-radius:4px;font-size:0.82rem;font-weight:600;">อักขระพิเศษ</span>
    &nbsp;สัญลักษณ์ที่ต้องคงไว้ในคำแปล เช่น <code>... — "</code> — <strong>ตรวจเสมอไม่ว่า target จะเป็นภาษาใด</strong>
    </div>
    """, unsafe_allow_html=True)

    sev_bg   = {"Minor":"#fff8e1","Major":"#fff3e0","Critical":"#fce4ec"}
    type_badge = {
        "grammar": '<span style="background:#e3f2fd;color:#1565c0;padding:1px 7px;border-radius:4px;font-size:0.78rem;font-weight:600;white-space:nowrap;">ไวยากรณ์</span>',
        "special": '<span style="background:#fce4ec;color:#880e4f;padding:1px 7px;border-radius:4px;font-size:0.78rem;font-weight:600;white-space:nowrap;">อักขระพิเศษ</span>',
    }

    for i, p in enumerate(sg["punctuation"]):
        c1, c2, c3, c4, c5, c6 = st.columns([0.7, 1.0, 1.4, 2.8, 2.0, 0.7])
        with c1:
            p["enabled"] = st.toggle("", p.get("enabled", False), key=f"pen_{i}", label_visibility="collapsed")
        with c2:
            bg = sev_bg.get(p.get("severity","Minor"),"#fff8e1")
            st.markdown(f'<div style="padding-top:6px"><span style="font-family:monospace;background:{bg};padding:3px 10px;border-radius:5px;font-size:1rem;">{p["symbol"]}</span></div>', unsafe_allow_html=True)
        with c3:
            ptype = p.get("type","special")
            st.markdown(f'<div style="padding-top:9px">{type_badge.get(ptype,"")}</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="padding-top:10px;font-size:0.93rem;color:#444;">{p["name"]}</div>', unsafe_allow_html=True)
        with c5:
            p["severity"] = st.selectbox("", ["Minor","Major","Critical"],
                index=["Minor","Major","Critical"].index(p.get("severity","Minor")),
                key=f"psev_{i}", label_visibility="collapsed")
        with c6:
            st.markdown('<div style="padding-top:4px">', unsafe_allow_html=True)
            if st.button("✕", key=f"pdel_{i}"):
                sg["punctuation"].pop(i); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("➕ เพิ่มเครื่องหมายหรือสัญลักษณ์ใหม่", expanded=False):
        st.caption("สามารถเพิ่มได้มากกว่า 1 สัญลักษณ์พร้อมกัน โดยคั่นด้วยช่องว่าง")
        ns1, ns2, ns3, ns4 = st.columns([2, 2, 1.5, 1.5])
        with ns1: new_syms = st.text_input("สัญลักษณ์", key="new_sym", placeholder="เช่น ※ · 〈 〉")
        with ns2: new_name = st.text_input("ชื่อ/คำอธิบาย", key="new_sym_name", placeholder="เช่น เครื่องหมายอ้างอิง")
        with ns3: new_ptype = st.selectbox("ประเภท", ["special","grammar"],
            format_func=lambda x: "อักขระพิเศษ" if x=="special" else "ไวยากรณ์", key="new_sym_type")
        with ns4: new_sev = st.selectbox("ระดับ", ["Minor","Major","Critical"], key="new_sym_sev")
        if st.button("เพิ่มสัญลักษณ์", key="add_sym"):
            syms = [s for s in new_syms.strip().split() if s]
            if syms:
                for sym in syms:
                    sg["punctuation"].append({"symbol":sym,"name":new_name or sym,
                        "type":new_ptype,"enabled":True,"severity":new_sev})
                st.success(f"เพิ่ม {len(syms)} สัญลักษณ์เรียบร้อยแล้ว")
                st.rerun()
            else:
                st.warning("กรุณาใส่สัญลักษณ์ก่อน")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — HISTORY
# ════════════════════════════════════════════════════════════════════════════════
with tab_history:
    history = st.session_state["history"]
    if not history:
        st.info("ยังไม่มีประวัติการตรวจสอบ กลับไปที่แท็บ 'ตรวจสอบ QA' แล้วกด 'เริ่มตรวจสอบ' ได้เลยค่ะ")
    else:
        hist_rows = []
        for h in reversed(history):
            c = h["counts"]
            hist_rows.append({
                "เวลา": h["timestamp"], "ชื่อไฟล์": h["filename"], "จำนวนแถว": h["total"],
                "✅ ผ่าน": c.get("Pass",0), "🟡 Minor": c.get("Minor",0),
                "🟠 Major": c.get("Major",0), "🔴 Critical": c.get("Critical",0),
                "อัตราผ่าน": f"{c.get('Pass',0)/h['total']*100:.0f}%" if h["total"] else "—",
            })
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)

        st.markdown('<div class="sec-title">รายละเอียดแต่ละครั้ง</div>', unsafe_allow_html=True)
        for j, h in enumerate(reversed(history)):
            with st.expander(f"📄 {h['filename']}  ·  {h['timestamp']}  ·  {h['total']} แถว"):
                c = h["counts"]
                st.markdown(f"""
                <div class="stats-row">
                  <div class="stat-box stat-pass" ><div class="s-num">{c.get('Pass',0)}</div><div class="s-lbl">✅ ผ่าน</div></div>
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
                st.download_button("⬇ ดาวน์โหลด session นี้",
                    df2.to_csv(index=False).encode("utf-8-sig"),
                    file_name=f"qa_{h['timestamp'].replace(':','').replace(' ','_')}.csv",
                    mime="text/csv", key=f"hdl_{j}")

        st.write("")
        if st.button("🗑 ล้างประวัติทั้งหมด"):
            st.session_state["history"] = []; st.rerun()
