# โปรเจกต์นี้ใช้ทักษะบทไหนของวิชา 01204496

จับคู่กับ **สไลด์จริงใน `../midterm/`** และโน้ตของตัวเองใน `../midterm-notes/`
ไม่ใช่กับเค้าโครงรายวิชาลอย ๆ

| ขั้นของไปป์ไลน์ | บท | สไลด์/โน้ตที่ตรง |
| --- | --- | --- |
| อ่านข้อมูลที่มีค่าหาย 2.6–6.2% · สัญญาณสุ่ม · AR(1) surrogate | **บทที่ 1–2** | `CH01-01 Discrete-Time Signal Fundamentals` · `02 การชักตัวอย่างและสัญญาณสุ่ม.md` |
| **anti-alias LPF + decimation** รายชั่วโมง → รายเดือน → รายปี **เทียบกับค่าทางการของ PSMSL** | **บทที่ 3** | `CH03-01 Down and Up Sampling` · `08 Down และ Up Sampling.md` (มีรูป `ch08-04-antialias`) |
| cross-spectrum · coherence · PASC/AWC | **บทที่ 2** | `CH02-03 Periodogram and Correlogram` · `07 Periodogram และ Correlogram.md` (Bartlett/Welch/Blackman-Tukey/หน้าต่าง/trade-off) |
| **การแยกหลายสเกลแบบ octave-band** | **บทที่ 3** | `CH03-02 Filterbank` · `09 Filter Bank และ QMF.md` |
| AR(1) fitting สำหรับ null hypothesis | **บทที่ 5** | (หลังกลางภาค — parametric estimation) |
| MWC = ขยาย coherence เป็นหลายตัวแปร | **บทที่ 2 ต่อยอด** | ไม่มีในสไลด์โดยตรง — เป็นส่วนที่ต้องสร้างเอง |

## 🔴 ข้อที่เคยเป็นความเสี่ยงใหญ่สุด และถูกลบทิ้งแล้ว

รายงาน feasibility ฉบับแรกเตือนว่า **"ซิลลาบัสไม่มีคำว่า wavelet"** จึงเป็นเครื่องมือ
ที่อยู่*ข้าง ๆ* เนื้อวิชา ไม่ใช่*อยู่ใน*เนื้อวิชา

**ตรวจสไลด์จริงแล้วพบว่าไม่จริง** — `midterm-notes/scripts/ch09_filterbank.py` สร้างรูป
`ch09-05-wavelet-tree.png` จากสไลด์ พร้อมคำบรรยายว่า

> *"Repeating the split on the LOW band only → wavelet / octave-band decomposition —
> fine frequency detail at low frequencies, fine time detail at high frequencies"*

และมี `ch09-06-image-wavelet.png` (Haar 2D) จากสไลด์หน้า 12–13 อีกด้วย

**สรุป: วิชาสอน wavelet จริง ในฐานะ dyadic filter-bank tree ใน `CH03-02 Filterbank`**
โปรเจกต์นี้ใช้ **CWT (ต่อเนื่อง)** ซึ่งคนละตัวกับ DWT tree ที่สอน แต่**สะพานเชื่อมถูกสอน
ไว้แล้วในวิชา** และการอธิบายความต่างระหว่างสองอันในรายงานคือเนื้อหาที่ตรงบทเรียนโดยตรง

## เส้นแบ่งที่ทำให้โปรเจกต์นี้ผ่านหรือตกแกน "ตรงเป้า"

```
เขียนเอง (ต้องทำ)                          เรียกไลบรารีได้ (ไม่ผิด)
--------------------------------------    ------------------------------
cross-wavelet spectrum                     pycwt.cwt   (ตัว CWT พื้นฐาน)
smoothing ในสเกลและเวลา                     numpy / scipy
wavelet coherence (สูตรเต็ม)                matplotlib
MWC หลายตัวแปร                             pandas
AR(1) surrogate + significance
anti-alias filter + decimation

⛔ ห้ามเรียก: pycwt.wct , vectorwavelet::mwc  <- นี่คือสิ่งที่ต้องพิสูจน์ว่าเขียนเองได้
```

ถ้าเรียก `pycwt.wct()` แล้วจบ **จะไม่เหลือทักษะของวิชาให้ตรวจเลย** — งานจะกลายเป็น
การวิเคราะห์ภูมิอากาศที่บังเอิญใช้เครื่องมือของคนอื่น (ดู `feasibility.md` §L6)
