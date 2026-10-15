# ทำซ้ำ wavelet coherence ของระดับน้ำทะเล — ด้วยข้อมูลไทย

> 📄 **รายงานฉบับสมบูรณ์: [`reports/final/report.pdf`](reports/final/report.pdf)** — ทะเลสองฝั่ง ฟังภูมิอากาศคนละแบบ

**โครงงานจบวิชา 01204496 Algorithmic-Oriented DSP for CE** · เดดไลน์ **2026-11-08** · นำเสนอสัปดาห์ที่ 15

ทำซ้ำ [Song & Chen (2022)](https://doi.org/10.2166/wcc.2022.180) ซึ่งใช้ **wavelet coherence (WTC)**
และ **multiple wavelet coherence (MWC)** หาว่าดัชนีภูมิอากาศชุดไหนอธิบายระดับน้ำทะเล
อเมริกาเหนือได้ — **แล้วเปลี่ยนบริบทมาเป็นอ่าวไทยกับทะเลอันดามัน**

## ทำไมคำตอบถึงยังไม่มีใครรู้

อ่าวไทยกับอันดามันไม่มี AMO/NAO ที่เป็นแอตแลนติกแบบอเมริกาเหนือ แต่มี **มรสุมเอเชีย
ตะวันออกเฉียงใต้ + IOD** ซึ่งไม่อยู่ในชุดของเขา และ **สองสถานีอยู่คนละมหาสมุทรกัน**

## เริ่มยังไง

```bash
uv sync
uv run python scripts/fetch_data.py     # โหลดข้อมูลดิบ 19 ไฟล์
uv run python scripts/check_data.py     # ตรวจว่าตัวเลขตรงกับ data/MANIFEST.md
```

## ✅ ด่านแรกผ่านแล้ว — premise test เสร็จ 2026-09-20

```bash
uv run python scripts/build_series.py                    # -> data/processed/series.npz
uv run --group reference python scripts/validate_wtc.py  # 🚦 ประตู G1
uv run --group dev python -m pytest                      # ทดสอบเชิงตัวเลขทั้งหมด
uv run python scripts/verify_decimation.py               # Q7: โซ่ anti-alias + decimation
uv run python scripts/run_wtc.py                         # Q1: WTC ดัชนีเดี่ยว + นัยสำคัญ + PASC/AWC
uv run python scripts/run_mwc_null.py                    # W5: threshold ของ MWC ต่อ (q, สถานี) · ~8 นาที
uv run python scripts/run_mwc.py                         # Q3–Q5: ค้นครบ 218 ชุด × 3 สถานี · ~7 นาที
uv run python scripts/null_control.py --nrep 1000        # Q6: null ของการค้นหาทั้งดุ้น · ~5 นาที
uv run python scripts/sensitivity.py --all               # W7: ทดสอบความไว 8 แบบ × 2 ทะเล · ~45 นาที
uv run python scripts/make_figures.py                    # รูปสุดท้ายของรายงาน -> figures/report/
uv run --group report python scripts/make_infographics.py  # แผนที่ + อินโฟกราฟิกของรายงาน (cartopy)
cd reports/final && latexmk -xelatex report.tex          # 📄 รายงานฉบับสมบูรณ์ -> report.pdf
uv run --group dev --group reference python scripts/run_notebooks.py  # รันโน้ตบุ๊กทุกเล่มซ้ำ
```

**ผลที่ได้**: WTC ที่เขียนเองต่างจาก `pycwt.wct` เพียง **1.4e-15 ทั้งระนาบ** (เกณฑ์คือ 0.05)
และทำซ้ำ p = 0.016 (อันดามัน) / 0.984 (อ่าวไทย) ได้ตรงเลขเป้า
กระบวนการทั้งหมดเดินซ้ำได้ใน `notebooks/01_data.ipynb` และ `notebooks/02_wtc.ipynb`

<details><summary>เกณฑ์เดิมของด่านนี้ (เก็บไว้อ้างอิง)</summary>

### ด่านแรก — premise test ให้จบภายใน 2026-09-16

**เขียน cross-wavelet spectrum + wavelet coherence ด้วยมือ** (ใช้ `pycwt.cwt` เป็นฐานได้
แต่ **ห้ามใช้ `pycwt.wct`**) รันระหว่าง **KO TAPHAO NOI รายเดือน** กับ **Niño3.4**
พร้อม AR(1) surrogate ของตัวเอง แล้วเทียบกับเลขเป้า

```bash
uv run --group reference python scripts/baseline_pycwt.py
```

```
เลขเป้าที่ต้องได้ใกล้เคียง (รันแล้วเมื่อ 2026-09-09, seed 7, surrogate 60 ชุด)

  KO TAPHAO NOI (อันดามัน)   coherence แถบ 2-7 ปี = 0.3583   p = 0.016   สัญญาณจริง
  KO LAK        (อ่าวไทย)    coherence แถบ 2-7 ปี = 0.1689   p = 0.984   ไม่มีเลย
```

**เกณฑ์ที่แปลว่าให้เลิก:** ถึง 2026-09-16 แล้วยังไม่มี coherence ที่เขียนเองรันได้ →
หนี้ทักษะสูงกว่าที่ประเมิน **ถอยไปทางเรียกไลบรารีแล้วเปลี่ยนที่ส่ง หรือหยุด — ไม่ใช่ดันต่อ**

</details>
· หรือถ้าโค้ดตัวเองให้ค่าต่างจาก `pycwt.wct` เกิน ~0.05 ในแถบ 2–7 ปี แล้วหาสาเหตุ
ไม่เจอในสัปดาห์นั้น → มีบั๊กที่ยังจับไม่ได้ **หยุด**

> ⚠️ **KO LAK ไม่มีสัญญาณ ENSO** อย่าเอามาใช้เป็นตัวทดสอบว่าโค้ดตัวเองถูกหรือผิด
> — จะได้ผลว่างแล้วสรุปผิดว่าโค้ดพัง

## ผลตั้งต้นที่รู้แล้ว — สองทะเลของไทยไม่เหมือนกันเลย

| | KO LAK (อ่าวไทย) | KO TAPHAO NOI (อันดามัน) |
| --- | ---: | ---: |
| แนวโน้ม | +1.70 mm/ปี (5.8% ของความแปรปรวน) | +2.62 mm/ปี (16.6%) |
| วงรอบปี+ครึ่งปี | 212 mm → **80.4%** ของที่เหลือ | 89 mm → 27.7% |
| corr กับ Niño3.4 | −0.106 (t ≈ −1.9) **ไม่มีนัยสำคัญ** | −0.275 (t ≈ −3.7) **มีนัยสำคัญ** |
| WTC แถบ 2–7 ปี | 0.169 · p = 0.984 | 0.358 · **p = 0.016** |

**อ่าวไทยถูกครอบงำด้วยมรสุม อันดามันเปิดรับ ENSO** — ตรงกับที่เปเปอร์ต้นทาง
เรียกว่า *"differences among places"* พอดี **นี่คือข้อค้นพบตั้งต้นของโปรเจกต์**

## เส้นแบ่งที่ทำให้ผ่านหรือตกวิชา

```
ต้องเขียนเอง                              เรียกไลบรารีได้
------------------------------------      --------------------
cross-wavelet spectrum                    pycwt.cwt
smoothing ในสเกลและเวลา                    numpy / scipy
wavelet coherence (สูตรเต็ม)               matplotlib
MWC หลายตัวแปร
AR(1) surrogate + significance
anti-alias filter + decimation

ห้ามเรียก: pycwt.wct , vectorwavelet::mwc
```

ถ้าเรียก `pycwt.wct()` แล้วจบ จะไม่เหลือทักษะของวิชาให้ตรวจเลย —
งานจะกลายเป็นการวิเคราะห์ภูมิอากาศที่บังเอิญใช้เครื่องมือของคนอื่น

## โครงไฟล์

```
data/raw/psmsl/      ระดับน้ำทะเล 3 สถานี รายเดือน+รายปี 1940-2024   <- commit ไว้ (เล็ก)
data/raw/indices/    ดัชนีภูมิอากาศ 7 ตัว                            <- commit ไว้
data/raw/uhslc/      รายชั่วโมง 306,785 จุด/สถานี                     <- gitignore (5 MB/ไฟล์)
data/MANIFEST.md     🔴 อ่านก่อนใช้ข้อมูล — มีกับดัก 3 ข้อที่ต้องรู้
scripts/loaders.py   ตัวอ่านไฟล์ทั้งสามรูปแบบ (ตรวจกับไฟล์จริงแล้ว)
scripts/fetch_data.py / check_data.py / baseline_pycwt.py
docs/feasibility.md  คำตัดสิน ✅ go + งบเวลา + premise test
docs/syllabus-map.md ทักษะของโปรเจกต์ ↔ สไลด์จริงใน ../midterm/
docs/source-paper.md เปเปอร์ต้นทาง + สิ่งที่ต้องอ่านเองก่อนเขียนโค้ด
```

## ที่มา

คัดและตัดสินด้วยไปป์ไลน์ใน `~/Projects/research_labs`
(`research-feed` → `project-feasibility`) เมื่อ 2026-09-09
ฉบับเต็มของการคัด: `vault/Feed/2026-09-09-c.md` · การตัดสิน: `docs/feasibility.md`
