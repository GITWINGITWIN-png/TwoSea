# เปเปอร์ต้นทาง

**Song, C. & Chen, X. (2022)** — *Multivariate analysis of multiscale periodicity in
North American annual mean sea level based on wavelet coherence and multiple wavelet coherence*
**Journal of Water and Climate Change** · [DOI 10.2166/wcc.2022.180](https://doi.org/10.2166/wcc.2022.180)
🟢 **diamond OA — อ่านฟรี ไม่ต้องผ่าน KU** · OpenAlex `W4296138289` · cited 8

## เขาทำอะไร

วัดความสัมพันธ์ระหว่าง **ระดับน้ำทะเลเฉลี่ยรายปี (AMSL)** กับดัชนีภูมิอากาศ **หลายตัวพร้อมกัน**
ด้วย **wavelet coherence (WTC)** และ **multiple wavelet coherence (MWC)**
วัดผลด้วยสองตัวเลข: **PASC** (สัดส่วนพื้นที่ในระนาบเวลา-คาบที่มีนัยสำคัญ) และ **AWC** (coherence เฉลี่ย)

**ผลบนข้อมูลอเมริกาเหนือ**
- 6 ดัชนีมีความสัมพันธ์อย่างมีนัยสำคัญ · **Niño3.4** เด่น (PASC **14.03%**, AWC **0.79**) · AMO อ่อนสุด
- รวมดัชนีเข้าด้วยกันค่าพุ่งขึ้น: ชุด 5 ดัชนีให้ PASC **95.87%**, AWC **0.965**
  (⚠️ ตัวเลขนี้มาจาก abstract แต่ตัวเนื้อหา §3.2.4 บอกว่า 95.87% คือ *ค่าต่ำสุด* ไม่ใช่ค่าเฉลี่ย — ดู [`source-paper-detail.md`](source-paper-detail.md) §6 ข้อ ก)
- ข้อสรุป: **ดัชนีตัวเดียวอธิบายไม่พอ ต้องใช้ 3–5 ตัว แล้วแต่ภูมิภาค**

## สิ่งที่ทำซ้ำโดยเปลี่ยนบริบท

| | ต้นทาง | โปรเจกต์นี้ |
| --- | --- | --- |
| ระดับน้ำ | tide gauge อเมริกาเหนือ | **PSMSL ไทย 3 สถานี · 2 ทะเล** |
| ดัชนี | Niño3.4, PDO, NAO, SOI, AMO, **TPI** (ยืนยันจากตัวเปเปอร์แล้ว) | Niño3.4, SOI, **DMI/IOD**, PDO, AMO, NAO, WHWP |
| ความละเอียด | รายปี | **รายเดือน** (ดัน Nyquist จาก 2 ปี เป็น 2 เดือน) |

**เหตุผลเชิงกายภาพว่าทำไมผลควรต่าง:** อ่าวไทยกับอันดามันไม่มี AMO/NAO ที่เป็นแอตแลนติก
แต่มี **มรสุมเอเชียตะวันออกเฉียงใต้ + IOD** ซึ่งไม่อยู่ในชุดของเขา และ**สองสถานีอยู่
คนละมหาสมุทรกัน**

## ✅ อ่าน method section แล้ว — 2026-09-09

รายละเอียดเต็มอยู่ที่ **[`source-paper-detail.md`](source-paper-detail.md)** (วิธีการทีละสมการ +
ผลลัพธ์ทีละตัวเลข + อ่านเชิงวิจารณ์) สรุปสถานะคำถามสี่ข้อที่ค้างไว้:

| # | คำถาม | สถานะ |
| --- | --- | --- |
| 1 | สูตร smoothing operator | ✅ Torrence & Webster (1999) — Gaussian ในเวลา + boxcar ยาว 0.6s ในสเกล · **เปเปอร์พิมพ์ป้ายสมการผิด** ดู detail §3.2 |
| 2 | นิยาม PASC | 🟡 มีสูตร แต่ไม่บอกว่าตัด COI ยังไง / นับพื้นที่ linear หรือ log — ต้องเลือกเอง |
| 3 | ดัชนี 6 ตัวคือตัวไหน | ✅ Niño3.4, PDO, NAO, SOI, AMO, TPI — **ไม่มี IOD และไม่มี WHWP** สองตัวนั้นเป็นของที่เราเพิ่มเอง |
| 4 | วิธีทำ significance | ❌ **เปเปอร์ไม่บอกเลย** — ไม่มีจำนวน surrogate ไม่มีวิธี fit AR(1) ไม่มี threshold ของ MWC ต้องออกแบบเองและประกาศให้ชัดในรายงาน |

## งานที่อ้างถึงเปเปอร์นี้ (ทั้ง 8 ชิ้น) — หลักฐานว่ารูปนี้ตีพิมพ์ได้

6 ใน 8 คือการยกกรอบ WTC/MWC ไปใช้กับภูมิภาค/ตัวแปรใหม่ แล้วตีพิมพ์ได้:
ฝนกับ large-scale circulation (2024) · ecological drought (2025) · GNSS PWV (2023) ·
คุณภาพอากาศกลางคืนที่ราบ Indo-Gangetic (2023) · คุณภาพอากาศ Naples (2023) ·
atmospheric aerosol ในจีน (2024) · chlorophyll-a ทะเลญี่ปุ่น (2025)

**ไม่มีชิ้นไหนเป็นระดับน้ำทะเลในเอเชียตะวันออกเฉียงใต้**

## Implementation ที่มีอยู่

| | ภาษา | สถานะ | ครอบคลุม |
| --- | --- | --- | --- |
| [`regeirk/pycwt`](https://github.com/regeirk/pycwt) | Python | ★351 · push 2025-10 · **0.5.0b0 (beta)** | `cwt`, `xwt`, `wct`, `wct_significance` — **ไม่มี MWC** |
| [`toygur/vectorwavelet`](https://github.com/toygur/vectorwavelet) | R | ★14 · push **2021-01** | `mwc`, `qmwc`, `vwc` |

🔴 **MWC ไม่มีใน Python** — ถ้าทำงานใน Python ต้องเขียนเอง ซึ่งคือ multivariate
cross-spectral analysis = เนื้อวิชาพอดี **ข้อจำกัดทางวิศวกรรมกับข้อกำหนดของวิชาชี้ทางเดียวกัน**
