"""ตรวจว่าสไลด์และโน้ตไม่บิดเบือนตัวเลข: script.md ↔ claims.yaml ↔ data/facts.json ↔ manim/sq*.py

    uv run python tools/check_claims.py          # รันก่อน export ทุกครั้ง · exit 1 ถ้ามีปัญหา

สี่ชั้นที่ตรวจ:
1. ทุกประโยคที่พูด ทุกโน้ต "ถ้าถูกถาม:" (ไม่นับเวลา) และทุก "หัวข้อ:" บนจอ มีป้าย [Cnn] ที่มีอยู่จริง หรือ [F] (ประโยคเชื่อม ห้ามมีตัวเลข)
2. ตัวเลขทุกตัวในประโยค/หัวข้อต้องประกาศไว้ใน numbers ของ claim ที่อ้าง
3. ตัวเลขที่ประกาศต้องตรงกับค่าใน facts.json เมื่อจัดรูปแบบตามที่กำหนด (หรือเป็น lit พร้อมเหตุผล)
4. lint ไฟล์สไลด์: ข้อความที่ส่งเข้า thai("...") ห้ามมีตัวเลขพิมพ์เอง — ต้องมาจาก num()/F() ใน f-string
   และหน้า deck (deck/slides.md · deck/pages/*.md): ข้อความที่มองเห็นห้ามมีตัวเลข — ต้องอยู่ใน <Fact id="…" />

แล้วประมาณเวลาพูดสดต่อตอน (ไม่นับภาคผนวก SQ11) เทียบงบ BUDGET_MIN
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "context" / "script.md"
CLAIMS = ROOT / "context" / "claims.yaml"
FACTS = ROOT / "data" / "facts.json"

# ชื่อที่มีตัวเลขอยู่ในตัว — ไม่ใช่ตัวเลขที่ต้องตรวจ
NAMES = ["Niño3.4", "AR(1)", "K1", "P1", "K2", "M2", "S2", "O1", "Q1", "N2", "R²", "ω0"]
NUMBER = re.compile(r"(?<![A-Za-z\d.,])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?![A-Za-z\d])")
TAG = re.compile(r"\[(C\d+|F)\]")
SHOT = re.compile(r"^### (SQ\d+_S\d+)")
# ความเร็วพูดสด (ตัวอักษร/วินาที) — ช้ากว่าการอ่านบันทึกเสียง (13) · ปรับจากการซ้อมจริงใน context/rehearsal.md
THAI_CHARS_PER_SEC = 10.5
SECONDS_PER_CLICK = 1.5      # เวลาที่ภาพเคลื่อน/รอหลังคลิก
SECONDS_PER_GUESS = 8        # รอคนฟังทาย (ทาย ①②③)
BUDGET_MIN = 14              # งบเวลาพูด (ช่องนำเสนอ 15 นาที เผื่อ 1)
APPENDIX = "SQ11"
SLIDE_FILES = sorted((ROOT / "manim").glob("sq*.py"))
DECK_FILES = [ROOT / "deck" / "slides.md", *sorted((ROOT / "deck" / "pages").glob("*.md"))]


QA = "ถ้าถูกถาม: "


def narration(text):
    """[(หน้า, line_no, ข้อความ, tags)] จาก 'หัวข้อ:' ส่วน 'พูด:' และส่วน 'ถ้าถูกถาม:' ของทุกหน้า

    หัวข้อถูกเก็บเป็นข้อความที่ขึ้นต้นด้วย "หัวข้อ: " และโน้ตเผื่อโดนถามขึ้นต้นด้วย QA
    เพื่อให้ตรวจ claim/ตัวเลขเหมือนคำพูด แต่ไม่ถูกนับเป็นเวลาพูด
    """
    out, shot, speaking, prefix = [], None, False, ""
    for no, line in enumerate(text.splitlines(), 1):
        if m := SHOT.match(line):
            shot, speaking = m.group(1), False
        elif shot and line.startswith("หัวข้อ:"):
            tags = TAG.findall(line)
            out.append((shot, no, "หัวข้อ: " + TAG.sub("", line[7:]).strip(), tags))
            speaking = False
        elif line.startswith("พูด:"):
            speaking, prefix = True, ""
        elif shot and line.startswith(QA.strip()):
            speaking, prefix = True, QA
        elif speaking and line.startswith("- "):
            tags = TAG.findall(line)
            sentence = TAG.sub("", line[2:]).strip()
            out.append((shot, no, prefix + sentence, tags))
        elif speaking and line.strip() and not line.startswith("- "):
            speaking = False
    return out


def clicks_and_guesses(text):
    """{หน้า: (จำนวนคลิก, จำนวนจุดทาย)} จากส่วน 'ขั้น:'"""
    out, shot, in_steps = {}, None, False
    for line in text.splitlines():
        if m := SHOT.match(line):
            shot, in_steps = m.group(1), False
            out[shot] = (0, 0)
        elif shot and line.startswith("ขั้น:"):
            in_steps = True
        elif in_steps and re.match(r"^\d+\. ", line):
            c, g = out[shot]
            out[shot] = (c + 1, g + ("ทาย" in line))
        elif in_steps and line.strip() and not re.match(r"^\d+\. ", line):
            in_steps = False
    return out


THAI_CALL = re.compile(r"""thai\(\s*(f?)(["'])(.*?)\2""")


def lint_slide_files():
    """ข้อความใน thai("...") ห้ามมีตัวเลขพิมพ์เอง · ใน f-string ตัดส่วน {...} ออกก่อนตรวจ"""
    errors = []
    for path in SLIDE_FILES:
        for no, line in enumerate(path.read_text().splitlines(), 1):
            for is_f, _, literal in THAI_CALL.findall(line):
                text = re.sub(r"\{[^}]*\}", " ", literal) if is_f else literal
                if nums := numbers_in(text):
                    errors.append(f"{path.relative_to(ROOT)}:{no}: เลข {nums} พิมพ์เองใน thai() — ใช้ num()/F()")
    return errors


YAML_LINE = re.compile(r"^(\s+\S|[A-Za-z_][\w-]*:)")


def visible_text(md):
    """ข้อความที่คนดูเห็นบนหน้า deck: ตัด frontmatter · โน้ต (<!-- -->) · <Fact/> · ทุกแท็กพร้อม attribute ออก

    คืน [(line_no, ข้อความ)] — เลขบรรทัดเดิมไว้ชี้ตำแหน่ง
    """
    lines = md.splitlines()
    hide = [False] * len(lines)
    # frontmatter = บล็อกระหว่าง --- สองเส้นที่ทุกบรรทัดดูเป็น YAML (headmatter ต้นไฟล์ และ frontmatter ของแต่ละหน้า)
    seps = [i for i, line in enumerate(lines) if line.strip() == "---"]
    for a, b in zip(seps, seps[1:]):
        body = [line for line in lines[a + 1:b] if line.strip()]
        if body and all(YAML_LINE.match(line) for line in body):
            for i in range(a, b + 1):
                hide[i] = True
    text = "\n".join("" if h else line for line, h in zip(lines, hide))
    blank = lambda m: "\n" * m.group(0).count("\n")  # noqa: E731 — คงจำนวนบรรทัด
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)
    text = re.sub(r"<(style|script)\b.*?</\1>", blank, text, flags=re.S)  # CSS/JS ไม่ใช่ข้อความบนจอ
    text = re.sub(r"<Fact\b[^>]*/>", " ", text)
    text = re.sub(r"<Lit\b[^>]*/>", " ", text)
    # แท็ก: attribute ในเครื่องหมายคำพูดอาจมี > (เช่น :height="$clicks >= 1 ? 330 : 560") — ข้ามทั้งก้อนคำพูด
    text = re.sub(r"""<(?:[^>"']|"[^"]*"|'[^']*')*>""", blank, text, flags=re.S)
    return list(enumerate(text.splitlines(), 1))


LIT = re.compile(r'<Lit\s+v="([^"]+)"\s+c="(C\d+)"\s*/>')


def lint_deck_pages(claims):
    """หน้า deck: ตัวเลขที่มองเห็นต้องมาจาก <Fact id="…" /> หรือ <Lit v c /> ที่ claim c ประกาศเลข v ไว้จริง"""
    errors = []
    for path in DECK_FILES:
        if not path.exists():
            continue
        for no, line in enumerate(path.read_text().splitlines(), 1):
            for v, cid in LIT.findall(line):
                if v.replace(",", "") not in {str(k) for k in ((claims.get(cid) or {}).get("numbers") or {})}:
                    errors.append(f"{path.relative_to(ROOT)}:{no}: <Lit v=\"{v}\"> แต่ {cid} ไม่ได้ประกาศเลขนี้")
        for no, line in visible_text(path.read_text()):
            if nums := numbers_in(line):
                errors.append(f"{path.relative_to(ROOT)}:{no}: เลข {nums} พิมพ์เองบนหน้า deck — ใช้ <Fact id=\"…\" />")
    return errors


def numbers_in(sentence):
    for name in NAMES:
        sentence = sentence.replace(name, " ")
    return [n.replace(",", "") for n in NUMBER.findall(sentence)]


def render(spec, facts):
    """ค่า fact ตาม spec -> (ok, ข้อความอธิบาย) สำหรับตัวเลข key ที่ตรวจอยู่"""
    def check(key):
        if "lit" in spec:
            return True, f"lit: {spec['lit']}"
        name = spec["fact"]
        if name not in facts:
            return False, f"ไม่มี fact '{name}'"
        value = facts[name]["value"]
        if name == "robust.rows":
            value = [r["n_pass"] for r in value]
        if isinstance(value, dict):
            value = list(value.values())
        if "index" in spec:
            value = value[spec["index"]]
        if spec.get("below"):
            ok = all(v < float(key) for v in value)
            return ok, f"{name} = {value} (ทุกค่า < {key}?)"
        if spec.get("in"):
            vals = [round(v, spec.get("round", 0)) if isinstance(v, float) else v for v in value]
            ok = any(float(v) == float(key) for v in vals)
            return ok, f"{name} = {value}"
        v = abs(value) if spec.get("abs") else value
        if "round" in spec:
            text = f"{round(v, spec['round']):.0f}"
        else:
            text = spec.get("fmt", "{}").format(v)
        return text == key, f"{name} = {value} -> '{text}'"
    return check


def main():
    facts = json.loads(FACTS.read_text())
    claims = yaml.safe_load(CLAIMS.read_text())
    lines = narration(SCRIPT.read_text())
    errors, used = [], set()

    # ชั้น 3: ตัวเลขใน claims ตรงกับ facts
    for cid, c in claims.items():
        for name in c.get("facts", []):
            if name not in facts:
                errors.append(f"{cid}: facts อ้าง '{name}' ที่ไม่มีใน facts.json")
        for key, spec in (c.get("numbers") or {}).items():
            for s in spec if isinstance(spec, list) else [spec]:
                ok, why = render(s, facts)(str(key))
                if not ok:
                    errors.append(f"{cid}: เลข '{key}' ไม่ตรง fact — {why}")

    # ชั้น 1–2: ประโยคและหัวข้อในบท
    chars, cut_chars = {}, 0
    for shot, no, sentence, tags in lines:
        if not sentence.startswith(("หัวข้อ: ", QA)):
            chars[shot] = chars.get(shot, 0) + len(sentence)
            if "✂" in sentence and not shot.startswith(APPENDIX):
                cut_chars += len(sentence)
        where = f"script.md:{no} ({shot})"
        if not tags:
            errors.append(f"{where}: ไม่มีป้าย [Cnn] หรือ [F] — \"{sentence[:40]}…\"")
            continue
        nums = numbers_in(sentence)
        if tags == ["F"]:
            if nums:
                errors.append(f"{where}: ประโยค [F] มีตัวเลข {nums} — ต้องมี claim")
            continue
        declared = set()
        for t in tags:
            if t == "F":
                continue
            if t not in claims:
                errors.append(f"{where}: อ้าง {t} ที่ไม่มีใน claims.yaml")
                continue
            used.add(t)
            declared |= {str(k) for k in (claims[t].get("numbers") or {})}
        for n in nums:
            if n not in declared:
                errors.append(f"{where}: เลข '{n}' ไม่ได้ประกาศใน {tags} — \"{sentence[:50]}…\"")

    # ชั้น 4: ตัวเลขในไฟล์สไลด์
    errors += lint_slide_files()
    errors += lint_deck_pages(claims)

    # เวลาพูดสดต่อตอน
    steps = clicks_and_guesses(SCRIPT.read_text())
    per_seq = {}
    for shot, (n_click, n_guess) in steps.items():
        seq = shot[:4]
        if seq == APPENDIX:
            continue
        sec = chars.get(shot, 0) / THAI_CHARS_PER_SEC + n_click * SECONDS_PER_CLICK + n_guess * SECONDS_PER_GUESS
        pages, total = per_seq.get(seq, (0, 0.0))
        per_seq[seq] = (pages + 1, total + sec)
    total = sum(t for _, t in per_seq.values())
    print("เวลาพูดสดโดยประมาณ (" + f"{THAI_CHARS_PER_SEC} ตัวอักษร/วินาที):")
    for seq, (pages, sec) in per_seq.items():
        print(f"  {seq}  {pages:2d} หน้า  {sec / 60:4.1f} นาที")
    n_pages = sum(p for p, _ in per_seq.values())
    print(f"  รวม {n_pages} หน้าหลัก · {total / 60:.1f} นาที (งบ {BUDGET_MIN}) · ภาคผนวก "
          f"{sum(1 for s in steps if s.startswith(APPENDIX))} หน้า")
    lean = total - cut_chars / THAI_CHARS_PER_SEC
    print(f"  ถ้าตัดประโยค ✂ ทั้งหมด: {lean / 60:.1f} นาที")
    if lean / 60 > BUDGET_MIN:
        print(f"⚠️  แม้ตัด ✂ แล้วยังเกินงบ {lean / 60 - BUDGET_MIN:.1f} นาที — ต้องตัดเนื้อหา")
    elif total / 60 > BUDGET_MIN:
        print(f"⚠️  รวม ✂ เกินงบ {total / 60 - BUDGET_MIN:.1f} นาที — ตัดประโยค ✂ บางประโยคหลังซ้อมจับเวลา")

    unused = sorted(set(claims) - used, key=lambda s: int(s[1:]))
    print(f"ข้อความ {len(lines)} (หัวข้อ + ประโยค) · claims ใช้ {len(used)}/{len(claims)}")
    if unused:
        print("⚠️  claims ที่บทไม่ได้ใช้:", ", ".join(unused))
    if errors:
        print(f"\n❌ {len(errors)} ปัญหา")
        for e in errors:
            print("  -", e)
        return 1
    print("✅ หัวข้อ + โน้ต ↔ claims ↔ facts ตรงกันทุกตัวเลข · ไฟล์สไลด์ไม่มีเลขพิมพ์เอง")
    return 0


if __name__ == "__main__":
    sys.exit(main())
