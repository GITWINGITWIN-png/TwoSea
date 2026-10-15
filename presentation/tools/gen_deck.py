"""สร้าง deck/slides.md (Slidev) จากบท — หนึ่งหัวข้อ ### ใน context/script.md = หนึ่งหน้า

    uv run python tools/gen_deck.py            # เขียน deck/slides.md + คัดลอกรูปสำรอง + facts.json
    cd deck && npx slidev                       # ดูผล (http://localhost:3030)

แต่ละหน้าได้:
  frontmatter  layout page/cover/end · seq · section · page (เลขหน้า) · kinds (ป้ายชนิดภาพ) · id
  หัวข้อ       จาก "หัวข้อ:" — ตัวเลขทุกตัวแปลงเป็น <Fact/> (มาจาก facts.json) หรือ <Lit/> (claim ประกาศเป็น lit)
               ตามป้าย [Cnn] ของบรรทัดนั้น · เลขที่ claim ไม่ได้ประกาศ = หยุดพร้อมบอกบรรทัด (กฎ "ตัวเลขมาจาก facts เท่านั้น")
  เนื้อหน้า    deck/pages/<รหัสหน้า>.md ถ้ามี (ทำมือ) · ไม่มี = ภาพสำรองจาก shotlist (รูปรายงานในการ์ด หรือการ์ดข้อความ)
  โน้ต         ส่วน "พูด:" และ "ถ้าถูกถาม:" (ตัดป้าย claim ออกให้อ่านง่ายบน presenter view)
               ประโยคที่ claim เป็นการอนุมาน/งานเดียว ต่อท้ายด้วย (อนุมาน)/(งานเดียว) — ป้ายหลักฐานไม่ขึ้นจอ ผู้นำเสนอพูดเอง

ไฟล์หน้าทำมือ (deck/pages/<รหัสหน้า>.md) = เนื้อหน้าใต้หัวข้อเท่านั้น · บรรทัดแรกเขียน <!-- clicks: N --> ได้ถ้าหน้ามีคลิก
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check_claims import NAMES, NUMBER, TAG  # noqa: E402 — ใช้กติกาแยกตัวเลขชุดเดียวกับตัวตรวจ

SCRIPT = ROOT / "context" / "script.md"
CLAIMS = ROOT / "context" / "claims.yaml"
SHOTLIST = ROOT / "context" / "shotlist.yaml"
FACTS = ROOT / "data" / "facts.json"
REPORT_FIGS = ROOT / "00_input" / "report_figs"
DECK = ROOT / "deck"
PAGES = DECK / "pages"

KINDS = ("ข้อมูลจริง", "แผนภาพ", "เปรียบเทียบ")
# ระดับหลักฐานที่ต้องพูดเผื่อ → คำต่อท้ายประโยคในโน้ตผู้พูด (ผู้ใช้ 10-14: ไม่ขึ้นจอ)
HEDGE = {"inferred": "อนุมาน", "single": "งานเดียว"}
COVER = {
    "subtitle": "Time–Scale Relationships between Interannual Sea-Level Variability along the Thai Coasts and Climate Indices: An Analysis Using Wavelet Coherence and Multiple Wavelet Coherence",
    "course": "โครงงานรายวิชา 01204496 การประมวลผลสัญญาณดิจิทัลเชิงอัลกอริทึมสำหรับวิศวกรคอมพิวเตอร์ ภาควิชาวิศวกรรมคอมพิวเตอร์",
    "byline": "กวินภพ จันเจือ รหัสนิสิต 6710503739",
}
# ข้อความบนจอไม่ใช้ "·" (ผู้ใช้ 10-14) — รายการคั่นด้วยจุลภาค
CREDITS = [
    "ข้อมูล: PSMSL, UHSLC, NOAA PSL/CPC",
    "วิธี: Grinsted et al. 2004, Hu & Si 2016, Song & Chen 2022, Torrence & Compo 1998",
    "กลไก: Han & Webster 2002, Aparna et al. 2012, Brown et al. 2019, Anutaliya 2023, Liu et al. 2011",
    "เครื่องมือ: Slidev, Manim, Blender",
    "ผู้จัดทำ: กวินภพ จันเจือ รหัสนิสิต 6710503739",
]


# --- อ่านบท ----------------------------------------------------------------------------------------------

def parse_script(text):
    """[{id, seq, section, header, head, head_tags, card, steps, say, qa}] ตามลำดับในบท (ไม่รวมบล็อก comment ท้ายไฟล์)"""
    text = text.split("```tandem-comments")[0]
    pages, section, page, field = [], "", None, None
    for line in text.splitlines():
        if m := re.match(r"^## (SQ\d{2}) · (.+)$", line):
            section = re.sub(r"\s*·\s*องก์.*$", "", m.group(2)).strip()
            continue
        if m := re.match(r"^### (SQ\d{2})_(S\d{3}) · (.+)$", line):
            page = {"id": f"{m.group(1)}_{m.group(2)}", "seq": m.group(1), "section": section, "header": m.group(3),
                    "head": "", "head_tags": [], "page_tags": [], "card": "", "steps": [], "say": [], "qa": []}
            pages.append(page)
            field = None
            continue
        if page is None:
            continue
        if line.startswith("หัวข้อ:"):
            page["head_tags"] = TAG.findall(line)
            page["head"] = TAG.sub("", line[len("หัวข้อ:"):]).strip()
            field = None
        elif line.startswith("การ์ดสรุป:"):
            page["page_tags"] += [t for t in TAG.findall(line) if t != "F"]  # การ์ดสรุปติดป้าย claim ของตัวเองได้
            page["card"] = TAG.sub("", line[len("การ์ดสรุป:"):]).strip().strip('"')
        elif line.startswith("ขั้น:"):
            field = "steps"
        elif line.startswith("พูด:"):
            field = "say"
        elif line.startswith("ถ้าถูกถาม:"):
            field = "qa"
        elif field and line.startswith("- "):
            page[field].append(line[2:].strip())
            page["page_tags"] += [t for t in TAG.findall(line) if t != "F"]
        elif field == "steps" and re.match(r"^\d+\. ", line):
            page["steps"].append(line)
        elif line.strip() and not line.startswith(("- ", "ภาพ:", "→", "(")):
            field = None
    return pages


# --- ตัวเลข → component --------------------------------------------------------------------------------

def fact_text(value, spec):
    """จัดรูปแบบแบบเดียวกับ Fact.vue — ใช้ยืนยันว่า component จะแสดงเลขตรงกับที่บทเขียน"""
    if isinstance(value, dict):
        value = list(value.values())
    if "index" in spec:
        value = value[spec["index"]]
    x = abs(value) if spec.get("abs") else value
    if "round" in spec:
        step = 10 ** (-spec["round"])
        return f"{round(x / step) * step:,.0f}", {"round-to": step, "digits": 0}
    m = re.match(r"\{:\.(\d)f\}", spec.get("fmt", "{}"))
    digits = int(m.group(1)) if m else 0
    return f"{x:,.{digits}f}", {"digits": digits}


def numbers_to_components(text, tags, claims, facts, where):
    """แทนเลขทุกตัวในข้อความด้วย <Fact/> หรือ <Lit/> ตาม claim ที่บรรทัดนั้นอ้าง"""
    protected = {}
    for i, name in enumerate(NAMES + ["ω0"]):
        token = f"{chr(0xE100 + i)}"  # รหัสแทนที่ต้องไม่มีตัวเลข ไม่อย่างนั้น NUMBER จับได้
        if name in text:
            protected[token] = name
            text = text.replace(name, token)

    def swap(m):
        raw = m.group(1)
        key = raw.replace(",", "")
        for cid in tags:
            spec = ((claims.get(cid) or {}).get("numbers") or {}).get(key)
            if spec is None:
                continue
            spec = spec[0] if isinstance(spec, list) else spec
            if "fact" in spec and not spec.get("below") and not spec.get("in"):
                shown, props = fact_text(facts[spec["fact"]]["value"], spec)
                if shown != raw:
                    raise SystemExit(f"{where}: เลข '{raw}' แต่ fact {spec['fact']} จะแสดง '{shown}' — แก้ fmt ใน {cid}")
                extra = "".join(f' :{k}="{v}"' for k, v in props.items() if k != "digits")
                if "index" in spec:
                    v = facts[spec["fact"]]["value"]
                    n = len(v) if isinstance(v, (list, dict)) else 0
                    extra += f' :index="{spec["index"] % n if n else spec["index"]}"'  # ติดลบ → นับจากหน้า
                if spec.get("abs"):
                    extra += ' :absval="true"'
                return f'<Fact id="{spec["fact"]}" :digits="{props["digits"]}"{extra} />'
            return f'<Lit v="{raw}" c="{cid}" />'
        raise SystemExit(f"{where}: เลข '{raw}' ไม่ได้ประกาศใน {tags} — \"{m.string[:60]}\"")

    out = NUMBER.sub(swap, text)
    for token, name in protected.items():
        out = out.replace(token, name)
    return out


# --- ข้อมูลอนุกรมสำหรับกราฟ HTML/SVG ในหน้า deck -------------------------------------------------------------

def export_series():
    """deck/data/series.json จาก data/derived.npz — ค่าข้อมูลดิบให้ component วาด (ไม่ใช่ข้อความบนจอ จึงไม่ผ่าน <Fact/>)

    t = ปีทศนิยม · *_mm = ระดับน้ำรายเดือนตัดแนวโน้ม+ฤดูกาล (มม.) · *_mm_12m = ค่าเฉลี่ย 12 เดือนของมัน · neg_* = ดัชนีกลับเครื่องหมาย (SD)
    fir_* = ผลตอบสนองตัวกรอง (รอบ/วัน, dB) ย่อเหลือ ~1,000 จุด
    """
    d = np.load(ROOT / "data" / "derived.npz")
    clean = lambda a, nd: [None if not np.isfinite(v) else round(float(v), nd) for v in a]  # noqa: E731
    step = max(1, len(d["fir_w"]) // 1000)
    out = {
        "t": clean(d["t"], 4),
        "andaman_mm_12m": clean(d["andaman_mm_12m"], 1), "gulf_mm_12m": clean(d["gulf_mm_12m"], 1),
        "andaman_mm": clean(d["andaman_mm"], 1), "gulf_mm": clean(d["gulf_mm"], 1),
        "neg_nino34_12m": clean(d["neg_nino34_12m"], 3), "neg_dmi_12m": clean(d["neg_dmi_12m"], 3),
        "fir_w": clean(d["fir_w"][::step], 4), "fir_h_db": clean(d["fir_h_db"][::step], 2),
    }
    (DECK / "data" / "series.json").write_text(json.dumps(out, separators=(",", ":")))


# --- ประกอบหน้า -----------------------------------------------------------------------------------------

def clean_note(line, claims):
    """ตัดป้าย claim · ✂ → (ตัดได้) · ต่อท้าย (อนุมาน)/(งานเดียว) ตาม evidence ของ claim ในประโยค"""
    hedges = []
    for cid in TAG.findall(line):
        h = HEDGE.get((claims.get(cid) or {}).get("evidence"))
        if h and h not in hedges:
            hedges.append(h)
    text = TAG.sub("", line).replace("✂", "(ตัดได้)").strip()
    return text + "".join(f" ({h})" for h in hedges)


def notes_block(page, claims):
    parts = [clean_note(s, claims) for s in page["say"]]
    if page["qa"]:
        parts += ["", "ถ้าถูกถาม:"] + ["- " + clean_note(s, claims) for s in page["qa"]]
    body = "\n".join(parts).replace("-->", "→")
    return f"<!--\n{body}\n-->" if body.strip() else ""


def fallback_body(page, shot, claims, facts):
    """เนื้อหน้าสำรอง: รูปรายงานในการ์ด หรือการ์ดข้อความ (การ์ดสรุปของหน้า ถ้ามี)"""
    kind, _, value = shot["fallback"].partition(":")
    where = f"{page['id']} (ภาพสำรอง)"
    if kind == "fig":
        return f'<FigCard src="/figs/{value}.png" note="ภาพจากรายงาน" />', value
    text = page["card"] or value
    # การ์ดสรุปรวมหลายข้อของหน้า → ใช้ทุก claim ที่หน้านั้นอ้าง (หัวข้อก่อน แล้วตามด้วยคำพูด)
    text = numbers_to_components(text, page["head_tags"] + page["page_tags"], claims, facts, where)
    return f'<div class="card textcard">{text}</div>', None


def frontmatter(fields):
    return "---\n" + yaml.safe_dump(fields, allow_unicode=True, sort_keys=False, width=1000, default_flow_style=None).strip() + "\n---"


def build():
    claims = yaml.safe_load(CLAIMS.read_text())
    facts = json.loads(FACTS.read_text())
    shots = {s["id"]: s for s in yaml.safe_load(SHOTLIST.read_text())}
    pages = parse_script(SCRIPT.read_text())
    if missing := [p["id"] for p in pages if p["id"] not in shots]:
        raise SystemExit(f"shotlist ไม่มีหน้า {missing} — รัน tools/make_shotlist.py ก่อน")

    head = {
        "theme": "default", "title": "ความสัมพันธ์ระหว่างระดับน้ำทะเลชายฝั่งประเทศไทยกับดัชนีภูมิอากาศ", "canvasWidth": 1920, "aspectRatio": "16/9",
        "colorSchema": "light", "fonts": {"provider": "none", "sans": "Anuphan", "local": "Anuphan,Kanit"},
        "transition": "none", "routerMode": "hash", "exportFilename": "two-seas",
        "generatedBy": "tools/gen_deck.py จาก context/script.md — อย่าแก้มือ (หน้าทำมืออยู่ที่ deck/pages/)",
    }
    slides, figs, no = [], set(), 0
    # เลขตอนบนแถบ = ลำดับของตอนที่มีอยู่จริง (ตัดทั้งตอนแล้วเลขไม่กระโดด เช่น ตัด SQ09 → SQ10 แสดงเป็น 9) · รหัส SQxx ไม่เปลี่ยน
    order = list(dict.fromkeys(pg["seq"] for pg in pages if pg["seq"] != "SQ11"))
    for page in pages:
        pid, appendix = page["id"], page["seq"] == "SQ11"
        no += 1
        headline = numbers_to_components(page["head"], page["head_tags"], claims, facts, f"{pid} หัวข้อ")
        if appendix:
            headline = headline.replace("ภาคผนวก · ", "")
        fm = {"id": pid}
        hand = PAGES / f"{pid}.md"
        if hand.exists():
            body = hand.read_text().strip()
            figs |= set(re.findall(r'/figs/([\w-]+)\.png', body))  # รูปรายงานที่หน้าทำมืออ้าง → คัดลอกด้วย
            # บรรทัดว่างกลางบล็อก HTML ทำให้ Markdown ตัดบล็อกขาด → Vue ฟ้อง "missing end tag" — ตัดทิ้งก่อน <style>
            html, sep, rest = body.partition("<style")
            body = "\n".join(line for line in html.splitlines() if line.strip()) + ("\n\n" + sep + rest if sep else "")
            if m := re.match(r"<!--\s*clicks:\s*(\d+)\s*-->\s*", body):
                fm["clicks"] = int(m.group(1))
                body = body[m.end():]
        else:
            body, fig = fallback_body(page, shots[pid], claims, facts)
            if fig:
                figs.add(fig)

        if "ชื่อเรื่อง" in page["header"]:
            fm.update({"layout": "cover", **COVER})
            content = f"# {headline}\n\n::wave::\n\n<CoverWave />"  # slot wave ของ layout cover = เส้นคลื่นข้อมูลจริง
        elif "เครดิต" in page["header"]:
            fm.update({"layout": "end", "credits": CREDITS})
            content = f"# {headline}"
        else:
            kinds = [k for k in KINDS if k in page["header"]] if "การ์ด" not in page["header"] else []
            fm.update({"layout": "page", "seq": "ภาคผนวก" if appendix else str(order.index(page["seq"]) + 1),
                       "section": page["section"], "page": no,
                       "kinds": (["ภาคผนวก"] if appendix else []) + kinds})
            content = f"# {headline}\n\n{body}"
        slides.append(f"{frontmatter(fm)}\n\n{content}\n\n{notes_block(page, claims)}".rstrip())

    # หน้าแรกรวม headmatter ของทั้ง deck เข้ากับ frontmatter ของปก
    first_fm, first_rest = slides[0].split("\n---", 1)
    merged = {**head, **yaml.safe_load(first_fm.removeprefix("---\n"))}
    slides[0] = frontmatter(merged) + first_rest

    # headmatter ต้องอยู่บรรทัดแรกของไฟล์ — มีอะไรมาก่อน --- (แม้แต่ comment) Slidev จะอ่านหน้าแรกผิดแล้วทั้ง deck ว่าง
    (DECK / "slides.md").write_text("\n\n".join(slides) + "\n")
    out = DECK / "public" / "figs"
    out.mkdir(parents=True, exist_ok=True)
    for f in sorted(figs):
        shutil.copyfile(REPORT_FIGS / f"{f}.png", out / f"{f}.png")
    (DECK / "data").mkdir(exist_ok=True)
    shutil.copyfile(FACTS, DECK / "data" / "facts.json")
    export_series()
    hand = sum(1 for p in pages if (PAGES / f"{p['id']}.md").exists())
    print(f"deck/slides.md: {len(pages)} หน้า · ทำมือ {hand} · ภาพสำรอง {len(pages) - hand} · รูปรายงาน {len(figs)} ไฟล์")


if __name__ == "__main__":
    build()
