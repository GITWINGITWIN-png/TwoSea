# ข้อเสนอโครงงาน (Project Proposal)

**01204496 การประมวลผลสัญญาณดิจิทัลเชิงอัลกอริทึมสำหรับวิศวกรคอมพิวเตอร์**
(Algorithmic-Oriented Digital Signal Processing for Computer Engineers)

> ⚠️ **ต้องเติมก่อนแปลงเป็น PDF** — ลบกล่องนี้ทิ้งเมื่อเติมครบ
> ชื่อไฟล์ตอนส่ง: `Project Proposal_{ID6710503739}_{Kawinphop Junjuae}.pdf`

|                 |                                                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **ชื่อนิสิต**   | กวินภพ จันเจือ                                                                                                          |
| **รหัสนิสิต**   | 6710503739                                                                                                              |
| **ชื่อโครงงาน** | การวิเคราะห์ความสอดคล้องเชิงเวลา–ความถี่ระหว่างระดับน้ำทะเลอันดามันกับ climate index หลายตัว ด้วย Multiple Wavelet Coherence |

---

## 1. บทนำ (Introduction)

### 1.1 ที่มาและความสำคัญของปัญหา

สัญญาณที่สนใจคือ time series ของระดับน้ำทะเลรายเดือน จาก tide gauge ที่สถานี Ko Taphao Noi
จังหวัดภูเก็ต ฝั่งทะเลอันดามัน ซึ่งเป็น discrete-time signal ที่มีคาบหลายชั้นซ้อนกัน ตั้งแต่วงรอบ
ตามฤดูกาล 1 ปี ไปจนถึงความแปรปรวนหลายปีและหลายสิบปี

เนื่องจากองค์ประกอบเชิงความถี่เป็นแบบ non-stationary สัญญาณ El Niño ที่คาบ 2–7 ปี ปรากฏแรง
ในบางทศวรรษแล้วหายไปในบางทศวรรษ เครื่องมือมาตรฐานอย่าง DFT หรือ periodogram หาได้เพียง
spectrum เฉลี่ยของทั้งช่วงเวลา จึงตอบไม่ได้ว่า *สัญญาณแรงขึ้นตอนไหนและหายไปตอนไหน*
การวิเคราะห์จึงต้องขยับไปสู่ time–frequency plane และเนื่องจากระดับน้ำทะเลถูกขับด้วย
climate index หลายตัวพร้อมกัน การวัดทีละคู่จึงไม่พอ ต้องใช้เครื่องมือที่วัดความสัมพันธ์ของ
predictor variable หลายตัวพร้อมกันที่ทุกจุดบน plane นั้น คือ Multiple Wavelet Coherence (MWC)

ช่องว่างที่โครงงานนี้เข้าไปอยู่ — Song & Chen (2022) ใช้กรอบ Wavelet Coherence (WTC) ร่วมกับ
MWC หาชุด climate index ที่อธิบายระดับน้ำทะเลอเมริกาเหนือได้ดีที่สุด แต่ยังไม่เคยมีใครนำกรอบนี้
มาใช้กับทะเลอันดามัน ซึ่งเป็นส่วนหนึ่งของมหาสมุทรอินเดีย จึงมี Indian Ocean Dipole และมรสุม
เอเชียตะวันออกเฉียงใต้เป็นตัวขับที่ไม่อยู่ในชุดตัวแปรของงานต้นทางเลย

### 1.2 วัตถุประสงค์หลักของโครงงาน

1. เพื่อทดลองใช้ Wavelet Coherence และ Multiple Wavelet Coherence วิเคราะห์ความสัมพันธ์
   ระหว่างระดับน้ำทะเลอันดามันกับ climate index บนระนาบเวลา–ความถี่
2. เพื่อทดลองใช้ anti-alias filter และ decimation แปลงสัญญาณรายชั่วโมงเป็นรายเดือน
   แล้วตรวจสอบกับค่าอ้างอิงทางการของ PSMSL

### 1.3 ขอบเขตของโครงงาน (Scope)

ศึกษาทะเลเดียวคือทะเลอันดามัน สถานีเดียวคือ Ko Taphao Noi ซึ่งเป็นสถานีที่การทดสอบเบื้องต้น
ยืนยันแล้วว่ามีสัญญาณ ENSO จริงอย่างมีนัยสำคัญ และไม่มีการทรุดตัวของแผ่นดินมาปนในสัญญาณ

| สัญญาณ                              | Sampling rate | ความยาว          |
| ----------------------------------- | ------------- | ---------------- |
| ระดับน้ำทะเล PSMSL (Ko Taphao Noi)  | รายเดือน      | พ.ศ. 2483–2567   |
| ระดับน้ำทะเล UHSLC (Ko Taphao Noi)  | รายชั่วโมง    | 306,785 จุด      |
| Climate index 8 ตัว                 | รายเดือน      | ประมาณ 900 เดือน |

climate index 8 ตัว = 6 ตัวจากงานต้นทาง (Niño3.4, PDO, NAO, SOI, AMO, TPI) + 2 ตัวประจำภูมิภาค
(DMI ซึ่งเป็นดัชนี IOD และ WNPMI ซึ่งเป็นดัชนี monsoon)

**ข้อจำกัด**

1. ข้อมูลมี missing value 6.2% และปี ค.ศ. 2004 สูญหายทั้งปี (ปีสึนามิ) จึงต้องออกแบบวิธี
   gap filling และพก mask ไปตลอดสายการคำนวณ
2. ศึกษาสถานีเดียว จึงสรุปผลได้เฉพาะทะเลอันดามัน

**งานในอนาคต** — ขยายการวิเคราะห์ไปยังอ่าวไทย (สถานี Ko Lak) ซึ่งอยู่คนละมหาสมุทรกับทะเลอันดามัน
และมีวงรอบตามฤดูกาลจากมรสุมเป็นองค์ประกอบหลักของสัญญาณ เพื่อเปรียบเทียบว่าชุด climate index
ที่อธิบายระดับน้ำทะเลของสองทะเลแตกต่างกันหรือไม่

---

## 2. วิธีที่นำเสนอ (Proposed Method)

### 2.1 แผนภาพสายงาน

```
 [UHSLC hourly]              [PSMSL monthly]        [8 climate indices]
        |                            |                       |
        v                            |                       |
  FIR lowpass design                 |                       |
  + decimation                       |                       |
        |                            |                       |
        +---> compare vs official <--+                       |
              (validate filter chain) |                      |
                                      v                      v
          detrend + remove 1, 1/2-year harmonics · gap filling  (บทที่ 1)
                                            |
                                            v
                                   CWT (Morlet) -> W(s,t)
                                            |
                    +-----------------------+----------------------+
                    v                                              v
        cross-spectrum + smoothing                        AR(1) estimation
        -> WTC (2 variables)                              -> surrogates
        -> MWC (q variables)                              -> 95% threshold
                    |                                              |
                    +-----------------------+----------------------+
                                            v
                            mask COI -> count area -> PASC, AWC
                                            |
                                            v
        exhaustive search over index subsets (size 1-5) -> best set
```

### 2.2 ทฤษฎีและสมการหลัก

Cross-wavelet spectrum — ขยายแนวคิด cross-spectrum ให้มีความละเอียดเชิงเวลา
โดย $W_n^X(s)$ คือ Continuous Wavelet Transform (CWT) ของสัญญาณ $X$ ที่ scale $s$ เวลา $n$

Wavelet Coherence (WTC) — Grinsted et al. (2004) ตีความได้ว่าเป็น correlation coefficient
ที่ระบุตำแหน่งได้ทั้งในเวลาและความถี่

Multiple Wavelet Coherence (MWC) — Hu & Si (2016) ขยาย WTC จาก 2 ตัวแปรเป็น q ตัวแปร
โดยใช้เมทริกซ์ของ auto/cross-spectrum ที่ผ่าน smoothing แล้ว รูปสมการเทียบเท่ากับสัมประสิทธิ์
การตัดสินใจพหุของการถดถอยเชิงเส้นพหุ แต่คำนวณแยกที่ทุกจุดบนระนาบเวลา–ความถี่

$$
\rho_m^2(s,t)=\frac{\widetilde{W}^{\,Y,X}\;\left[\widetilde{W}^{\,X,X}\right]^{-1}\;\widetilde{W}^{\,Y,X*}}
{\widetilde{W}^{\,Y,Y}}
$$

Significance test — ประมาณ AR(1) จากข้อมูลจริงด้วย lag-1 autocorrelation (บทที่ 5)
แล้วสร้าง surrogate ส่งผ่านสายงานเดียวกัน เพื่อหา significance threshold ที่ percentile
ที่ 95 แยกตาม scale

$$z_n = a\,z_{n-1} + \varepsilon_n,\qquad \varepsilon_n \sim \mathcal{N}(0,\sigma^2)$$

ตัววัดผล — นับพื้นที่เฉพาะภายใน Cone of Influence (COI) บนแกน scale แบบ logarithmic

$$
\text{PASC}=100\times\frac{A_{\text{sig}}}{A_{\text{sig}}+A_{\text{insig}}}
\qquad
\text{AWC}=\overline{\rho^2}\;\Big|_{\text{significant region}}
$$

### 2.3 การแบ่งงาน — อะไรใช้ของเดิม อะไรสร้างเอง

ตรวจ API ของ `pycwt` เวอร์ชัน 0.4.0b1 แล้วพบว่าฝั่งสองตัวแปรมีให้เกือบครบ แต่ฝั่งหลายตัวแปร
ไม่มีอะไรเลย ตารางนี้คือการแบ่งงานที่ตามมา

| ขั้นตอน | มีให้ใช้แล้วหรือไม่ | แผน |
| --- | --- | --- |
| CWT (Morlet) + scales + COI | มี — `pycwt.cwt` | ใช้ของเขา |
| Smoothing operator (Torrence & Webster) | มี — `pycwt.Morlet().smooth()` | ใช้ของเขา |
| Cross-wavelet spectrum | มี — `pycwt.xwt` | ใช้ของเขา |
| Wavelet Coherence (2 ตัวแปร) | มี — `pycwt.wct` | ใช้เป็นตัวตรวจ · ตัวงานได้มาฟรีจาก MWC ที่ q = 1 |
| ประมาณค่า AR(1) | มี — `pycwt.ar1` | ใช้ของเขา |
| สร้าง AR(1) surrogate | มี — `pycwt.rednoise` | ใช้ของเขา |
| Significance threshold (2 ตัวแปร) | มี — `pycwt.wct_significance` (Monte Carlo 300 ชุด) | ใช้ของเขา |
| **MWC (q ตัวแปร)** | **ไม่มีในไลบรารีไพธอนใดเลย** — มีแต่โค้ด MATLAB ของ Hu & Si (2016) และแพ็กเกจ R ที่ไม่อัปเดตตั้งแต่ปี 2021 | **สร้างเอง (เลี่ยงไม่ได้)** |
| **Significance threshold ของ MWC** | ไม่มี — `wct_significance` รองรับแค่ 2 ตัวแปร | **สร้างเอง** |
| **PASC / AWC** | ไม่มีในไลบรารีใดเลย | **สร้างเอง** |
| Anti-alias FIR + decimation | `scipy.signal` มีบล็อกพื้นฐานให้ | **ออกแบบสเปกเอง** (เนื้อบทที่ 3–4) |

เหตุผลที่ยังคุ้มจะให้ WTC มาจากโค้ดของตัวเอง — MWC ที่ q = 1 ยุบกลับเป็น WTC พอดีตามนิยาม
ดังนั้นเมื่อเขียน MWC เสร็จ ซึ่งเป็นงานที่เลี่ยงไม่ได้อยู่แล้วเพราะไม่มีไลบรารีไหนทำไว้ ก็ได้ WTC
มาโดยไม่ต้องเขียนเพิ่มแม้แต่บรรทัดเดียว การเรียก `pycwt.wct` มาใช้แทนจึงประหยัดเวลาแทบไม่ได้
และการมีทั้งสองทางกลับกลายเป็นเกณฑ์ตรวจความถูกต้องที่แข็งแรงที่สุดของโครงงาน (ดูหัวข้อ 4)

ลำดับการตัดงานถ้าเวลาไม่พอ โดยข้อบนสุดคือส่วนที่ตัดไม่ได้

1. MWC · significance ของ MWC · PASC/AWC — เป็นแกนของโครงงาน
2. โซ่ anti-alias filter และ decimation — เป็นเนื้อบทที่ 3–4 ที่ต้องแสดง
3. การค้นครบทุกชุดขนาด 1–5 — ถ้าไม่ทัน ลดเป็นการเพิ่มดัชนีทีละตัวแบบ greedy ตามที่งานต้นทางทำ
4. การทดสอบด้วย synthetic index — เป็นส่วนเสริม ตัดออกได้เป็นอย่างแรก

### 2.4 เครื่องมือที่ใช้

| ประเภท                | รายการ                                          |
| --------------------- | ----------------------------------------------- |
| ภาษาและสภาพแวดล้อม    | Python 3.12+ จัดการด้วย `uv`                    |
| Library ที่ใช้ได้     | `numpy`, `scipy`, `matplotlib`, `pytest`        |
| Library ที่ใช้เป็นฐาน | `pycwt` — รายละเอียดการแบ่งงานอยู่ในหัวข้อ 2.3  |
| ฮาร์ดแวร์             | คอมพิวเตอร์ส่วนตัว                              |
| แหล่งข้อมูล           | PSMSL, UHSLC, NOAA Physical Sciences Laboratory |

---

## 3. ผลลัพธ์ที่คาดหวัง (Expected Outcomes)

1. ภาพ time–frequency plane ของ Wavelet Coherence ระหว่างระดับน้ำทะเลที่ Ko Taphao Noi
   กับ climate index แต่ละตัว พร้อมเส้น contour ของบริเวณที่มีนัยสำคัญ
2. กราฟเปรียบเทียบก่อน–หลัง anti-alias filter แสดงว่าถ้าทำ decimation โดยไม่กรองก่อน
   องค์ประกอบ tide จะเกิด aliasing พับกลับมาปนอย่างไร
3. ตาราง PASC และ AWC ของ climate index ทั้ง 8 ตัว และกราฟแสดงว่า PASC เปลี่ยนอย่างไร
   เมื่อเพิ่มจำนวน index จาก 1 ถึง 5 ตัว พร้อมเส้นเปรียบเทียบกับ synthetic index ที่สร้างจาก
   AR(1) ล้วน เพื่อแยกว่าค่าที่เพิ่มขึ้นเป็นสัญญาณจริงเท่าใด
4. ข้อค้นพบว่าต้องใช้ climate index กี่ตัวและชุดใดจึงอธิบายระดับน้ำทะเลอันดามันได้ดีที่สุด
   และดัชนีประจำภูมิภาค (DMI, WNPMI) เพิ่มอำนาจการอธิบายเหนือชุด 6 ตัวของงานต้นทางหรือไม่

---

## 4. เกณฑ์การประเมิน (Evaluation Criteria)

| ด้าน        | เกณฑ์                     | วิธีวัดและเป้าหมาย                                                                                                            |
| ----------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| ความถูกต้อง | MWC ที่เขียนเอง           | เมื่อกำหนด q = 1 ค่า MWC ต้องยุบกลับเป็น WTC ตามนิยาม — เทียบกับ `pycwt.wct` ต้องต่างไม่เกิน 0.05 ในย่านคาบ 2–7 ปี             |
| ความถูกต้อง | Filter chain + decimation | นำข้อมูลรายชั่วโมงผ่าน chain ที่ออกแบบเอง เทียบกับค่าเฉลี่ยรายเดือนทางการของ PSMSL — รายงาน RMSE พร้อมอธิบายที่มาของผลต่างที่เหลือ |
| ความถูกต้อง | Stopband attenuation      | ป้อนสัญญาณทดสอบที่มีความถี่สูงกว่า Nyquist ใหม่ แล้ววัด attenuation — ต้องไม่ปรากฏใน spectrum ของสัญญาณที่ decimate แล้ว        |
| ความถูกต้อง | การทำซ้ำผลอ้างอิง         | ทำซ้ำค่าที่วัดไว้ล่วงหน้าด้วย library คือ $p \approx 0.016$ ที่ Ko Taphao Noi ในย่านคาบ 2–7 ปี                                 |
| คุณภาพผล    | อำนาจการอธิบาย            | ค่า PASC และ AWC ของแต่ละชุด index · index ที่เพิ่มแล้วทำให้ PASC สูงขึ้นอย่างน้อย 5 percentage point จึงถือว่าสำคัญ           |
| คุณภาพผล    | False positive rate       | สร้าง synthetic index จาก AR(1) ล้วน ส่งผ่านสายงานเดียวกัน — ค่า PASC ที่ได้คือ *false-positive floor* ที่ผลจริงต้องสูงกว่าจึงมีความหมาย |
| คุณภาพผล    | Robustness ของข้อสรุป     | ทำ sensitivity test โดยเปลี่ยนวิธี gap filling ตัดปีสึนามิออก และตัด index ที่จำกัดหน้าต่างเวลาออก                              |
| คุณภาพผล    | ความสอดคล้องเชิงกายภาพ    | ปีที่พบ significant coherence ต้องตรงกับปีที่เกิด El Niño และ La Niña ที่บันทึกไว้                                              |

---

## เอกสารอ้างอิง

1. Song, C. & Chen, X. (2022). Multivariate analysis of multiscale periodicity in North American
   annual mean sea level based on wavelet coherence and multiple wavelet coherence.
   *Journal of Water and Climate Change*, **13**(9), 3435–3457.
2. Grinsted, A., Moore, J. C. & Jevrejeva, S. (2004). Application of the cross wavelet transform
   and wavelet coherence to geophysical time series. *Nonlinear Processes in Geophysics*, **11**, 561–566.
3. Hu, W. & Si, B. C. (2016). Technical note: Multiple wavelet coherence for untangling
   scale-specific and localized multivariate relationships in geosciences.
   *Hydrology and Earth System Sciences*, **20**, 3183–3191.
4. Torrence, C. & Compo, G. P. (1998). A practical guide to wavelet analysis.
   *Bulletin of the American Meteorological Society*, **79**(1), 61–78.
5. Torrence, C. & Webster, P. (1999). Interdecadal changes in the ENSO–monsoon system.
   *Journal of Climate*, **12**, 2679–2690.
