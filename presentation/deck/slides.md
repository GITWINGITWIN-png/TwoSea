---
theme: default
title: ความสัมพันธ์ระหว่างระดับน้ำทะเลชายฝั่งประเทศไทยกับดัชนีภูมิอากาศ
canvasWidth: 1920
aspectRatio: 16/9
colorSchema: light
fonts: {provider: none, sans: Anuphan, local: 'Anuphan,Kanit'}
transition: none
routerMode: hash
exportFilename: two-seas
generatedBy: tools/gen_deck.py จาก context/script.md — อย่าแก้มือ (หน้าทำมืออยู่ที่ deck/pages/)
id: SQ01_S030
layout: cover
subtitle: 'Time–Scale Relationships between Interannual Sea-Level Variability along the Thai Coasts and Climate Indices: An Analysis Using Wavelet Coherence and Multiple Wavelet Coherence'
course: โครงงานรายวิชา 01204496 การประมวลผลสัญญาณดิจิทัลเชิงอัลกอริทึมสำหรับวิศวกรคอมพิวเตอร์ ภาควิชาวิศวกรรมคอมพิวเตอร์
byline: กวินภพ จันเจือ รหัสนิสิต 6710503739
---

# ความสัมพันธ์เชิงเวลา–คาบระหว่างความผันแปรระหว่างปีของระดับน้ำทะเลชายฝั่งประเทศไทยกับดัชนีภูมิอากาศด้วย Wavelet Coherence และ Multiple Wavelet Coherence

::wave::

<CoverWave />

<!--
สวัสดีครับ ผมนายกวินภพ จันเจือ ขอนำเสนอผลงานการวิเคราะห์ความสัมพันธ์ระหว่างระดับน้ำทะเลไทยกับดัชนีภูมิอากาศ ด้วย wavelet coherence เพื่อตอบว่าระดับน้ำระหว่างปีของสองฝั่งทะเลไทยตอบสนองต่อปรากฏการณ์ภูมิอากาศตัวไหน และต่างกันหรือไม่
-->

---
id: SQ01_S010
clicks: 2
layout: page
seq: '1'
section: บทนำ
page: 2
kinds: [แผนภาพ]
---

# พื้นที่ศึกษา: มาตรวัดระดับน้ำสองฝั่งคาบสมุทร ห่างกันประมาณ <Fact id="stations.distance_km" :digits="0" :round-to="10" /> กม.

<!--
  แผนที่จริงพร้อมความลึกทะเล (Natural Earth bathymetry): tools/make_basemap.py → /plots/map_s01.png (ใกล้) · /plots/map_s01w.png (ไกล)
  ขั้น 0 คาบสมุทร + ทะเลสองฝั่งตามความลึก · 1 สองสถานี + ป้ายชื่อ + ช่วงข้อมูล · 2 ถอยออกกว้าง เส้นวัดระยะดูสั้นนิดเดียว
  ตำแหน่งสถานีจาก stations.ktn_latlon / stations.klk_latlon · ระยะจาก stations.distance_km (C02)
-->
<div class="card s11-card">
  <div class="s11-maps">
    <div class="s11-near" :class="{ off: $clicks >= 2 }">
      <img src="/plots/map_s01.png" class="s11-img" />
      <svg viewBox="0 0 1040 800" width="1040" height="800" class="s11-svg">
        <g class="s11-st" :class="{ on: $clicks >= 1 }">
          <line :x1="near.ktn.x" :y1="near.ktn.y" :x2="near.klk.x" :y2="near.klk.y" stroke="#12303D" stroke-width="3" stroke-dasharray="10 8" />
          <circle :cx="near.ktn.x" :cy="near.ktn.y" r="13" fill="#2F74C0" stroke="#FFFFFF" stroke-width="4" />
          <circle :cx="near.klk.x" :cy="near.klk.y" r="13" fill="#D9822B" stroke="#FFFFFF" stroke-width="4" />
        </g>
      </svg>
      <div class="s11-sea andaman" :style="near.at(9.6, 95.2)">ทะเลอันดามัน<small>ลึก ต่อกับมหาสมุทรอินเดีย</small></div>
      <div class="s11-sea gulf" :style="near.at(9.0, 102.4)">อ่าวไทย<small>ตื้นทั้งแอ่ง</small></div>
      <div class="s11-tag andaman" :class="{ on: $clicks >= 1 }" :style="near.at(7.4, 96.6)">เกาะตะเภาน้อย ภูเก็ต</div>
      <div class="s11-tag gulf" :class="{ on: $clicks >= 1 }" :style="near.at(12.55, 101.9)">เกาะหลัก ประจวบคีรีขันธ์</div>
    </div>
    <div class="s11-far" :class="{ on: $clicks >= 2 }">
      <img src="/plots/map_s01w.png" class="s11-img" />
      <svg viewBox="0 0 1493 800" width="1493" height="800" class="s11-svg">
        <line :x1="far.ktn.x" :y1="far.ktn.y" :x2="far.klk.x" :y2="far.klk.y" stroke="#12303D" stroke-width="5" stroke-linecap="round" />
        <circle :cx="far.ktn.x" :cy="far.ktn.y" r="8" fill="#2F74C0" stroke="#FFFFFF" stroke-width="3" />
        <circle :cx="far.klk.x" :cy="far.klk.y" r="8" fill="#D9822B" stroke="#FFFFFF" stroke-width="3" />
        <circle :cx="(far.ktn.x + far.klk.x) / 2" :cy="(far.ktn.y + far.klk.y) / 2" r="46" fill="none" stroke="#12303D" stroke-width="3" stroke-dasharray="8 7" />
      </svg>
      <div class="s11-ocean" :style="far.at(-12, 80)">มหาสมุทรอินเดีย</div>
      <div class="s11-ocean" :style="far.at(14, 143)">แปซิฟิก</div>
    </div>
  </div>
  <div class="s11-side">
    <div class="s11-key"><div class="s11-ramp"><i style="background:#EAF4FA"></i><i style="background:#D6E8F3"></i><i style="background:#BCD6EA"></i><i style="background:#9DC1E0"></i></div><span>สีน้ำ: ตื้น → ลึก</span></div>
    <div class="s11-info" :class="{ on: $clicks >= 1 }">
      <div class="s11-row"><i class="dot andaman"></i><div><b>ภูเก็ต (อันดามัน)</b><br>มาตรวัดเกาะตะเภาน้อย</div></div>
      <div class="s11-row"><i class="dot gulf"></i><div><b>ประจวบฯ (อ่าวไทย)</b><br>มาตรวัดเกาะหลัก</div></div>
      <div class="s11-span">ค่ารายเดือน <Fact id="series.start_year" plain />–<Fact id="series.end_year" plain /></div>
    </div>
    <div class="pill diag s11-pill">แผนที่จริง สีน้ำตามความลึก</div>
  </div>
</div>
<script setup>
// พิกัดภูมิศาสตร์ → พิกเซลของรูปพื้น (PlateCarree · ต้องตรงกับ MAPS ใน tools/make_basemap.py)
const proj = (lon0, lon1, lat0, lat1, w, h) => {
  const p = (lat, lon) => ({ x: (lon - lon0) / (lon1 - lon0) * w, y: (lat1 - lat) / (lat1 - lat0) * h })
  return { p, at: (lat, lon) => { const q = p(lat, lon); return { left: `${q.x}px`, top: `${q.y}px` } } }
}
const N = proj(92, 105, 4, 14, 1040, 800)
const F = proj(40, 180, -38, 37, 1493, 800)
const KTN = [7.833, 98.433], KLK = [11.8, 99.817]     // stations.ktn_latlon · stations.klk_latlon
const near = { at: N.at, ktn: N.p(...KTN), klk: N.p(...KLK) }
const far = { at: F.at, ktn: F.p(...KTN), klk: F.p(...KLK) }
</script>

<style>
/* แผนที่ซ้าย (สูงเต็มการ์ด) + คำอธิบายขวา · คลิก 2 แผนที่ใกล้จางออก แผนที่ไกลจางเข้า (เหมือนกล้องถอย) */
.s11-card { position: relative; flex: 1 1 auto; min-height: 0; padding: 0; overflow: hidden; background: #EAF4FA; display: flex; }
.s11-maps { position: relative; width: 1260px; flex: none; overflow: hidden; }
.s11-near, .s11-far { position: absolute; left: 0; top: 0; transform-origin: 0 0; transition: opacity 0.9s, transform 0.9s; }
.s11-near { width: 1040px; height: 800px; transform: scale(1.045); }
.s11-near.off { opacity: 0; transform: scale(0.7); }
.s11-far { width: 1493px; height: 800px; opacity: 0; transform: scale(1.3); }
.s11-far.on { opacity: 1; transform: scale(1.045); }
.s11-img, .s11-svg { position: absolute; left: 0; top: 0; }
/* ขอบขวาของแผนที่จางเข้าพื้นการ์ด ไม่ให้แผ่นดินขาดเป็นเส้นตรง */
.s11-maps::after { content: ''; position: absolute; right: 0; top: 0; width: 80px; height: 100%; background: linear-gradient(90deg, rgba(234,244,250,0), #EAF4FA); }
.s11-sea { position: absolute; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center;
  font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 36px; white-space: nowrap; }
.s11-sea small { font-family: 'Anuphan', sans-serif; font-weight: 400; font-size: 22px; color: var(--ink-2); }
.s11-sea.andaman { color: var(--andaman); }
.s11-sea.gulf { color: #A85A12; }
.s11-st, .s11-tag, .s11-info { opacity: 0; transition: opacity 0.6s; }
.s11-st.on, .s11-tag.on, .s11-info.on { opacity: 1; }
.s11-tag { position: absolute; transform: translate(-50%, -50%); padding: 4px 14px; border-radius: 10px; background: rgba(255,255,255,0.92);
  font-size: 22px; font-weight: 600; white-space: nowrap; }
.s11-tag.andaman { color: var(--andaman); }
.s11-tag.gulf { color: #A85A12; }
.s11-dist { position: absolute; transform: translate(-50%, -50%); font-size: 30px; white-space: nowrap; }
.s11-ocean { position: absolute; transform: translate(-50%, -50%); font-size: 26px; color: var(--ink-2); white-space: nowrap; }
.s11-side { flex: 1; display: flex; flex-direction: column; gap: 34px; padding: 40px 36px 0 20px; }
.s11-key { display: flex; flex-direction: column; gap: 8px; font-size: 22px; color: var(--ink-2); }
.s11-ramp { display: flex; }
.s11-ramp i { width: 60px; height: 22px; }
.s11-info { display: flex; flex-direction: column; gap: 22px; }
.s11-row { display: flex; gap: 16px; align-items: flex-start; font-size: 24px; line-height: 1.4; color: var(--ink-2); }
.s11-row b { color: var(--ink); }
.s11-row .dot { flex: none; width: 22px; height: 22px; border-radius: 50%; margin-top: 6px; border: 3px solid #fff; box-shadow: 0 0 0 1px #C9D6DC; }
.s11-row .dot.andaman { background: var(--andaman); }
.s11-row .dot.gulf { background: var(--gulf); }
.s11-span { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 30px; color: var(--ink); }
.s11-pill { align-self: flex-start; font-size: 20px; }
</style>

<!--
ข้อมูลของเรามาจากมาตรวัดระดับน้ำสองสถานี เกาะตะเภาน้อยที่ภูเก็ตฝั่งอันดามัน กับเกาะหลักที่ประจวบคีรีขันธ์ฝั่งอ่าวไทย
(ตัดได้) ใช้ค่ารายเดือนตั้งแต่ปี 1951 ถึง 2023
สองสถานีอยู่คนละฝั่งของคาบสมุทร ห่างกันเพียงราว 470 กิโลเมตร

ถ้าถูกถาม:
- "ห่างนิดเดียว" หมายถึงราว 470 กิโลเมตรเป็นเส้นตรงข้ามคาบสมุทร เทียบกับดัชนีภูมิอากาศที่วัดในที่ไกลออกไปหลายพันกิโลเมตร
- รายงานหน้าผลอ่าวไทยเขียนว่าไม่ถึง 450 กิโลเมตร ซึ่งผิด ระยะจากพิกัดในตารางข้อมูลของรายงานเองคือราว 470 กิโลเมตร
-->

---
id: SQ01_S020
layout: page
seq: '1'
section: บทนำ
page: 3
kinds: [ข้อมูลจริง]
---

# ช่วง ค.ศ. <Lit v="1997" c="C72" />–<Lit v="98" c="C72" /> ระดับน้ำทะเลอันดามันลดลงผิดปกติ ขณะที่อ่าวไทยไม่ลดลงตาม

<!--
  ขั้น 1 (ตอนเข้าหน้า) กราฟอันดามัน + ป้ายเหตุการณ์ · คลิก 1 กราฟอ่าวไทย · คลิก 2 ข้อความโยงกลับไปคำถามของหัวข้อ
  (หัวข้อเต็ม "… — เพราะอะไร" มาจาก gen_deck จึงขึ้นพร้อมหน้า — คลิก 2 ทำหน้าที่เป็นจังหวะ "เพราะอะไร")
  สองกราฟใช้ช่วงแกนเดียวกันทุกแกน (y-left ±250) เพื่อให้เทียบขนาดได้ตรง ๆ · แกนตั้งมีตัวเลขและชื่อแกน (ผู้ใช้ 10-15: ทุกกราฟต้องมีชื่อแกน x และ y)
-->
<div class="s1-row">
  <div class="card s1-card">
    <div class="s1-head"><i class="s1-dot" style="background: var(--andaman)"></i><b class="andaman">อันดามัน</b><span>ภูเก็ต ระดับน้ำค่าเฉลี่ย <Lit v="12" c="C20" /> เดือน</span></div>
    <div class="s1-chart">
      <SeriesChart :width="780" :height="600"
        :series="[{ key: 'andaman_mm_12m', kind: 'line', color: 'var(--andaman)', width: 5 }]"
        :x-range="[1996, 2000]" :y-left="[-250, 250]" :ticks-left="[-200, 0, 200]" :ticks-x="[1996, 1997, 1998, 1999]"
        y-label="ระดับน้ำ (มม.)" x-label="ปี"
        :band="[1997.5, 1998.5]" />
      <div class="bubble s1-event">
        <Lit v="1997" c="C01" />–<Lit v="98" c="C01" /><br>−<Fact id="event.phuket_drop_cm" /> ซม.<br><Fact id="event.phuket_drop_months" /> เดือน
        <small>(รายงานภาคสนาม)</small>
      </div>
    </div>
  </div>
  <div class="card s1-card">
    <div class="s1-head"><i class="s1-dot" style="background: var(--gulf)"></i><b class="gulf">อ่าวไทย</b><span>ประจวบคีรีขันธ์ สเกลเดียวกัน</span></div>
    <div class="s1-chart">
      <SeriesChart :width="780" :height="600"
        :series="[{ key: 'gulf_mm_12m', kind: 'line', color: 'var(--gulf)', width: 5 }]"
        :x-range="[1996, 2000]" :y-left="[-250, 250]" :ticks-left="[-200, 0, 200]" :ticks-x="[1996, 1997, 1998, 1999]"
        y-label="ระดับน้ำ (มม.)" x-label="ปี"
        :band="[1997.5, 1998.5]" />
    </div>
  </div>
</div>

<style>
.s1-row { display: flex; gap: 36px; flex: 1 1 auto; min-height: 0; }
.s1-card { flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; gap: 12px; padding: 24px 27px; }
.s1-head { display: flex; align-items: center; gap: 15px; font-size: 24px; color: var(--ink-2); }
.s1-head b { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 36px; }
.s1-dot { width: 21px; height: 21px; border-radius: 50%; display: inline-block; }
.s1-chart { position: relative; }
.s1-event { position: absolute; right: 0; top: 52px; font-size: 27px; line-height: 1.35; white-space: nowrap; }
.s1-event small { display: block; font-size: 20px; opacity: 0.8; }
.s1-ask { align-self: flex-start; font-size: 27px; margin-top: 18px; }
</style>

<!--
ปี 1997 ถึง 98 ทะเลหน้าภูเก็ตต่ำกว่าปกติราว 29 เซนติเมตร นาน 7 เดือน
แต่ช่วงเดียวกัน ฝั่งอ่าวไทยระดับน้ำไม่ได้ร่วงลงแบบเดียวกัน
แม้สองสถานีจะห่างกันแค่ราว 470 กิโลเมตร ระดับน้ำกลับต่างกันอย่างเห็นได้ชัด สาเหตุมาจากอะไร
นี่คือคำถามที่เราจะตอบด้วยการประมวลผลสัญญาณ

ถ้าถูกถาม:
- ตัวเลข 29 เซนติเมตรเป็นรายงานภาคสนาม ส่วนกราฟเป็นค่าเฉลี่ย 12 เดือนจากมาตรวัด ซึ่งปี 1997 ถึง 98 ร่วงราว 210 มิลลิเมตร จึงตื้นกว่า
-->

---
id: SQ02_S010
layout: page
seq: '2'
section: ข้อมูลและคำถามการวิจัย
page: 4
kinds: [ข้อมูลจริง]
---

# ข้อมูล: ระดับน้ำทะเลรายเดือนสองสถานี <Fact id="series.n_months" :digits="0" /> เดือน และดัชนีภูมิอากาศ <Fact id="indices.n" :digits="0" /> ตัว

<div class="card s21-card s21-split">
  <div class="s21-top">
    <div class="s21-legend">
      <span><i class="s21-sw and"></i>ภูเก็ต (อันดามัน)</span>
      <span><i class="s21-sw gul"></i>ประจวบฯ (อ่าวไทย)</span>
      <span class="muted">ระดับน้ำรายเดือน ตัดแนวโน้มระยะยาวของระดับน้ำและฤดูกาลแล้ว (มม.) จำนวน <Fact id="series.n_months" /> เดือน</span>
    </div>
    <div class="s21-wave">
      <SeriesChart :width="1680" :height="330" :y-left="[-350, 350]" :ticks-left="[-200, 0, 200]"
        :ticks-x="[1960, 1980, 2000, 2020]" y-label="ระดับน้ำ (มม.)" x-label="ปี"
        :series="[
          { key: 'gulf_mm', kind: 'line', color: 'var(--gulf)', width: 2 },
          { key: 'andaman_mm', kind: 'line', color: 'var(--andaman)', width: 2 },
        ]" />
    </div>
  </div>
  <div class="s21-bottom">
    <img class="s21-map" src="/figs/map01_indices.png" alt="">
    <div class="s21-xlabel">ดัชนีภูมิอากาศ <Fact id="indices.n" /> ตัว วัดในที่ไกลออกไปหลายพันกิโลเมตร</div>
    <div class="s21-chips">
      <span class="s21-chip key">Niño3.4</span><span class="s21-chip key">SOI</span><span class="s21-chip key">DMI</span>
      <span class="s21-chip">WNPMI</span><span class="s21-chip">PDO</span><span class="s21-chip">TPI</span>
      <span class="s21-chip">AMO</span><span class="s21-chip">NAO</span>
    </div>
  </div>
</div>

<style>
.s21-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 12px; overflow: hidden; }
.s21-legend { display: flex; gap: 30px; align-items: center; font-size: 22px; }
.s21-legend span { display: flex; align-items: center; gap: 10px; }
.s21-sw { display: inline-block; width: 33px; height: 4px; border-radius: 2px; }
.s21-sw.and { background: var(--andaman); } .s21-sw.gul { background: var(--gulf); }
/* คลื่นหดด้วยการเปลี่ยนความสูงกราฟจริง (ไม่ใช้ scale — scale บี้ตัวเลขแกน) */
.s21-wave { overflow: hidden; }
.s21-bottom { position: relative; flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 15px; padding-top: 6px; border-top: 1.5px solid #E6EEF1; }
.s21-map { position: absolute; right: 0; top: 9px; height: calc(100% - 9px); width: 1000px; object-fit: contain; object-position: right top; }
.s21-chips { max-width: 700px; }
.s21-xlabel { font-size: 24px; }
.s21-chips { display: flex; flex-wrap: wrap; gap: 15px; }
.s21-chip { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 36px; padding: 6px 27px; border-radius: 999px;
  background: var(--bg); color: var(--ink-2); }
.s21-chip.key { background: var(--ink); color: #FFFFFF; }
</style>

<!--
เส้นคลื่นที่อยู่ใต้ทุกหน้าตั้งแต่ต้นคือข้อมูลจริง คือระดับน้ำรายเดือนของสองสถานี รวม 865 เดือน นี่คือสัญญาณแรกของเรา
สัญญาณชุดที่สองคือดัชนีภูมิอากาศ 8 ตัว ที่วัดมหาสมุทรและบรรยากาศในที่ไกลออกไปหลายพันกิโลเมตร
ตัวสำคัญคือเอลนีโญที่วัดด้วย Niño3.4 และ SOI กับไดโพลมหาสมุทรอินเดียที่วัดด้วย DMI

ถ้าถูกถาม:
- เอลนีโญเป็นช่วงหนึ่งของ ENSO คือการแกว่งของอุณหภูมิผิวน้ำและความกดอากาศในแปซิฟิกเขตร้อน เป็นจังหวะราว 2 ถึง 7 ปี
- ปีเอลนีโญแปซิฟิกตะวันออกอุ่นผิดปกติ Niño3.4 จึงเป็นบวก และ SOI ซึ่งเป็นผลต่างความกดอากาศตาฮิติลบดาร์วินเป็นลบ
- IOD คือรูปแบบคล้ายกันในมหาสมุทรอินเดีย ปี IOD บวกฝั่งตะวันตกใกล้แอฟริกาอุ่น ส่วนนอกสุมาตราเย็นลง
-->

---
id: SQ02_S040
clicks: 1
layout: page
seq: '2'
section: ข้อมูลและคำถามการวิจัย
page: 5
kinds: []
---

# คำถามการวิจัย: สองสัญญาณสัมพันธ์กันที่คาบใด ช่วงเวลาใด และเกินระดับสัญญาณรบกวนหรือไม่

<!--
  ขั้น 1 (ตอนเข้าหน้า) การ์ดงานต้นแบบ · คลิก 1 การ์ด "ของเรา" · แถบคำถามสามข้อตัดออก (ซ้ำหัวข้อ · ผู้ใช้ 10-14)
  ตัวเลข: 82 · 2022 = C09 (Lit) · 2 สถานี = C03 (Lit) · 8 ดัชนี = indices.n (C05)
-->
<div class="s2-row">
  <div class="card s2-card">
    <div class="s2-tag">งานต้นแบบ</div>
    <div class="s2-title">Song &amp; Chen (<Lit v="2022" c="C09" />)</div>
    <div class="s2-stats">
      <div><span class="s2-big"><Lit v="82" c="C09" /></span><span class="s2-cap">สถานีวัดระดับน้ำ<br>อเมริกาเหนือ</span></div>
      <div><span class="s2-big s2-word">WTC<br>+ MWC</span><span class="s2-cap">วิธี wavelet coherence<br>ทีละดัชนี และหลายดัชนี</span></div>
    </div>
  </div>
  <svg v-click="1" class="s2-arrow" viewBox="0 0 60 60" width="60" height="60"><path d="M10 30 H46 M32 14 L48 30 L32 46" fill="none" stroke="var(--ink-3)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" /></svg>
  <div v-click="1" class="card s2-card s2-ours">
    <div class="s2-tag">ของเรา</div>
    <div class="s2-title">ทะเลไทย ใช้วิธีเดียวกัน</div>
    <div class="s2-stats">
      <div><span class="s2-big"><Lit v="2" c="C03" /></span><span class="s2-cap">สถานี<br><b class="andaman">อันดามัน</b> และ <b class="gulf">อ่าวไทย</b></span></div>
      <div><span class="s2-big"><Fact id="indices.n" /></span><span class="s2-cap">ดัชนีภูมิอากาศ<br>รวม DMI และ WNPMI ที่เพิ่ม</span></div>
    </div>
  </div>
</div>

<style>
.s2-row { display: flex; align-items: stretch; gap: 24px; margin-top: 60px; }
.s2-card { flex: 1 1 0; min-width: 0; padding: 42px 48px; display: flex; flex-direction: column; gap: 18px; }
.s2-tag { font-size: 24px; font-weight: 600; color: var(--ink-3); letter-spacing: 0.04em; }
.s2-title { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 48px; line-height: 1.3; }
.s2-stats { display: flex; gap: 42px; margin-top: 12px; }
.s2-stats > div { display: flex; flex-direction: column; gap: 6px; }
.s2-big { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 132px; line-height: 1.05; color: var(--ink); }
.s2-big.s2-word { font-size: 78px; line-height: 1.15; min-height: 138px; display: flex; align-items: center; }
.s2-cap { white-space: nowrap; font-size: 27px; line-height: 1.4; color: var(--ink-2); }
.s2-ours { border: 3px solid var(--ink); }
.s2-arrow { flex: none; align-self: center; }
.s2-sum { display: flex; align-items: center; gap: 48px; margin-top: 48px; padding: 36px 48px; background: var(--ink); color: #fff; }
.s2-sumhead { font-size: 30px; line-height: 1.4; white-space: nowrap; }
.s2-qs { display: flex; gap: 24px; flex: 1; counter-reset: q; }
.s2-q { flex: 1; display: flex; align-items: center; gap: 15px; background: #fff; color: var(--ink); border-radius: 21px;
  padding: 21px 27px; font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 38px; white-space: nowrap; }
.s2-q i::before { counter-increment: q; content: counter(q); }
.s2-q i { font-style: normal; display: inline-flex; align-items: center; justify-content: center; width: 48px; height: 48px;
  border-radius: 50%; background: var(--ink); color: #fff; font-size: 27px; flex: none; }
</style>

<!--
งานต้นแบบที่เราทำซ้ำคือ Song และ Chen ปี 2022 ที่ใช้วิธีนี้กับมาตรวัด 82 สถานีในอเมริกาเหนือ (งานเดียว)
เราใช้วิธีเดียวกันกับมาตรวัดของไทย และเพิ่มดัชนีของภูมิภาคเราอีกสองตัว คือ DMI และ WNPMI
ในภาษาสัญญาณ คำถามคือ ระดับน้ำกับดัชนีสัมพันธ์กันที่จังหวะเท่าไร เมื่อไร และสองฝั่งต่างกันหรือไม่

ถ้าถูกถาม:
- ที่เพิ่มสองตัว เพราะงานต้นแบบใช้ 6 ดัชนีที่ไม่มีตัวไหนวัดมหาสมุทรอินเดียหรือมรสุมเอเชียโดยตรง แต่ทะเลไทยอยู่ระหว่างสองระบบนี้ จึงเพิ่ม DMI ที่วัดมหาสมุทรอินเดีย และ WNPMI ที่วัดมรสุมแปซิฟิกตะวันตกเฉียงเหนือ
- ส่วนคำถามว่าดัชนีภูมิภาคช่วยเพิ่มอำนาจอธิบายไหม ผลยังไม่แน่น ผ่านแค่ 4 จาก 8 แบบทดสอบ
-->

---
id: SQ03_S005
clicks: 2
layout: page
seq: '3'
section: การเตรียมข้อมูล
page: 6
kinds: [แผนภาพ]
---

# ภาพรวมขั้นตอนการประมวลผลสัญญาณ

<!--
  ขั้น 1 (ตอนเข้าหน้า) ช่อง 1-3 · คลิก 1 ช่อง 4-5 · คลิก 2 ช่อง 6-7 — ทุกช่องเลื่อนขึ้นทีละช่องแบบเดียวกัน
  ภาพในช่อง = ครอปจากรูปรายงานใน deck/public/figs (ครอปด้วย CSS ไม่แก้ไฟล์รูป) · ชื่อขั้นอยู่ใต้ภาพ · ไม่มีป้ายบท
  คำอธิบายใต้ชื่อขั้น = เนื้อความจากบทพูดของหน้านี้ (ไม่มีตัวเลข)
-->
<div class="s3-flow">
  <div class="card s3-box s3-d0 s3-in" :class="{ on: true }" style="--d: 0.0s">
    <div class="s3-vis"><div class="s3-crop" style="aspect-ratio: 351/295"><img src="/figs/w2-hourly-sample.png" style="width: 407.41%; left: -29.91%; top: -15.25%" alt="" /></div></div>
    <div class="s3-name">รายชั่วโมง</div>
    <div class="s3-desc">ระดับน้ำจริงทุกชั่วโมง น้ำขึ้นน้ำลงเด่นชัด</div>
  </div>
  <svg class="s3-arrow s3-in" :class="{ on: true }" style="--d: 0.3s" viewBox="0 0 40 40" width="40" height="40"><path d="M6 20 H30 M21 10 L31 20 L21 30" fill="none" stroke="var(--ink-3)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" /></svg>
  <div class="card s3-box s3-d1 s3-in" :class="{ on: true }" style="--d: 0.6s">
    <div class="s3-vis"><div class="s3-crop" style="aspect-ratio: 500/420"><img src="/figs/w2-filter-response.png" style="width: 312.00%; left: -5.00%; top: -3.57%" alt="" /></div></div>
    <div class="s3-name">FIR + ลดอัตรา</div>
    <div class="s3-desc">กรองน้ำขึ้นน้ำลงออกก่อน แล้วค่อยลดอัตราสุ่ม</div>
  </div>
  <svg class="s3-arrow s3-in" :class="{ on: true }" style="--d: 0.9s" viewBox="0 0 40 40" width="40" height="40"><path d="M6 20 H30 M21 10 L31 20 L21 30" fill="none" stroke="var(--ink-3)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" /></svg>
  <div class="card s3-box s3-d2 s3-in" :class="{ on: true }" style="--d: 1.2s">
    <div class="s3-vis"><div class="s3-crop" style="aspect-ratio: 1430/940"><img src="/figs/w1-detrend-deseason.png" style="width: 100.00%; left: 0.00%; top: -2.13%" alt="" /></div></div>
    <div class="s3-name">เตรียมสัญญาณ</div>
    <div class="s3-desc">ตัดแนวโน้มระยะยาวของระดับน้ำกับฤดูกาล เหลือสัญญาณระหว่างปี</div>
  </div>
  <svg class="s3-arrow s3-in" :class="{ on: $clicks >= 1 }" style="--d: 0.0s" viewBox="0 0 40 40" width="40" height="40"><path d="M6 20 H30 M21 10 L31 20 L21 30" fill="none" stroke="var(--ink-3)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" /></svg>
  <div class="card s3-box s3-d3 s3-in" :class="{ on: $clicks >= 1 }" style="--d: 0.3s">
    <div class="s3-vis"><div class="s3-crop" style="aspect-ratio: 1110/710"><img src="/figs/w1-power-spectra.png" style="width: 128.83%; left: -8.56%; top: -5.63%" alt="" /></div></div>
    <div class="s3-name">CWT</div>
    <div class="s3-desc">ภาพเวลา × คาบ ว่าจังหวะไหนแรงเมื่อไร</div>
  </div>
  <svg class="s3-arrow s3-in" :class="{ on: $clicks >= 1 }" style="--d: 0.6s" viewBox="0 0 40 40" width="40" height="40"><path d="M6 20 H30 M21 10 L31 20 L21 30" fill="none" stroke="var(--ink-3)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" /></svg>
  <div class="card s3-box s3-d4 s3-in" :class="{ on: $clicks >= 1 }" style="--d: 0.9s">
    <div class="s3-vis"><div class="s3-crop" style="aspect-ratio: 445/375"><img src="/figs/fig03_wtc_maps.png" style="width: 414.61%; left: -26.97%; top: -30.67%" alt="" /></div></div>
    <div class="s3-name">WTC / MWC</div>
    <div class="s3-desc">ระดับน้ำกับดัชนีขยับพร้อมกันที่ไหน</div>
  </div>
  <svg class="s3-arrow s3-in" :class="{ on: $clicks >= 2 }" style="--d: 0.0s" viewBox="0 0 40 40" width="40" height="40"><path d="M6 20 H30 M21 10 L31 20 L21 30" fill="none" stroke="var(--ink-3)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" /></svg>
  <div class="card s3-box s3-d5 s3-in" :class="{ on: $clicks >= 2 }" style="--d: 0.3s">
    <div class="s3-vis"><div class="s3-crop" style="aspect-ratio: 500/305"><img src="/figs/w4-q1-pasc-null.png" style="width: 338.00%; left: -11.00%; top: -14.75%" alt="" /></div></div>
    <div class="s3-name">เทียบ noise</div>
    <div class="s3-desc">ผลต้องชนะ noise ที่สุ่มขึ้นมา</div>
  </div>
  <svg class="s3-arrow s3-in" :class="{ on: $clicks >= 2 }" style="--d: 0.6s" viewBox="0 0 40 40" width="40" height="40"><path d="M6 20 H30 M21 10 L31 20 L21 30" fill="none" stroke="var(--ink-3)" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" /></svg>
  <div class="card s3-box s3-d6 s3-in" :class="{ on: $clicks >= 2 }" style="--d: 0.9s">
    <div class="s3-vis"><div class="s3-crop" style="aspect-ratio: 340/315"><img src="/figs/fig12_phase.png" style="width: 550.29%; left: -11.76%; top: -89.52%" alt="" /></div></div>
    <div class="s3-name">ตรวจทิศ</div>
    <div class="s3-desc">ทิศของความสัมพันธ์ตรงกับกลไกหรือไม่</div>
  </div>
</div>

<style>
.s3-flow { display: flex; align-items: stretch; gap: 8px; margin-top: 84px; }
.s3-box { flex: 1 1 0; min-width: 0; padding: 21px 12px 27px; display: flex; flex-direction: column; align-items: center; gap: 15px; }
.s3-arrow { flex: none; width: 34px; height: 34px; align-self: center; }
.s3-vis { width: 100%; height: 220px; display: flex; align-items: center; justify-content: center; }
.s3-crop { position: relative; width: 100%; max-height: 100%; overflow: hidden; border-radius: 9px; background: #fff; }
.s3-crop img { position: absolute; max-width: none; display: block; }
.s3-name { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 30px; line-height: 1.3; text-align: center; }
.s3-desc { font-size: 21px; line-height: 1.45; color: var(--ink-2); text-align: center; padding: 0 6px; }
/* ทุกช่องเข้าแบบเดียวกัน (ผู้ใช้ 10-14): เลื่อนขึ้น + จางเข้า ทีละช่องในกลุ่มของคลิกนั้น · --d = ลำดับในกลุ่ม */
@keyframes s3-up { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
.s3-in { opacity: 0; }
.s3-in.on { animation: s3-up 0.5s ease var(--d) both; }
</style>

<!--
ขั้นแรก กรองน้ำขึ้นน้ำลงออกก่อนลดอัตรา แล้วลบแนวโน้มกับฤดูกาล ให้เหลือแต่สัญญาณระหว่างปี
จากนั้นแปลงเป็นภาพเวลาคูณคาบด้วย CWT แล้ววัดด้วย coherence ว่าระดับน้ำกับดัชนีขยับพร้อมกันที่ไหน
สุดท้ายเทียบกับ noise ที่สุ่มขึ้น 1,000 คู่ และใช้มุมเฟสตรวจทิศ

ถ้าถูกถาม:
- การวิเคราะห์หลักใช้ค่ารายเดือนของ PSMSL ส่วนสายกรองและลดอัตราจากรายชั่วโมงใช้สร้างค่ารายเดือนเองเพื่อเทียบกับค่าทางการ
-->

---
id: SQ03_S010
clicks: 1
layout: page
seq: '3'
section: การเตรียมข้อมูล
page: 7
kinds: [ข้อมูลจริง]
---

# องค์ประกอบของสัญญาณระดับน้ำทะเล และความผันแปรระหว่างปีที่ใช้ศึกษา

<!--
  รูปจาก tools/make_method_figs.py (แต่ละชั้นแยกรูป กว้าง 1400 px ขอบซ้ายเท่ากัน · แกน y หน่วย มม. ทุกชั้น):
  layer_hourly.png = UHSLC รายชั่วโมงจริง 7 วัน (เกาะตะเภาน้อย)
  layer_season / layer_inter / layer_trend.png = PSMSL รายเดือนจริงของสถานีเดียวกัน แยกด้วย fit แนวโน้ม + ฮาร์มอนิกของโครงงาน
  ระหว่างปี = ค่าเฉลี่ย 12 เดือนของส่วนที่เหลือ · แถบเทาในรูป = เดือนที่ PSMSL ไม่มีค่า (ไม่เติม)
  ขั้น 0 เส้นรายชั่วโมง · คลิก 1 สามชั้นช้าที่ซ้อนอยู่ใต้มัน · กรอบเน้นทั้งแถวระหว่างปี (เดิมกรอบลอยทับตัวเลขปี)
-->
<div class="card s31-card">
  <div class="s31-row">
    <div class="s31-lab"><b>น้ำขึ้นน้ำลง</b><span>ขึ้นลงทุกไม่กี่ชั่วโมง</span><small>รายชั่วโมงจริง หนึ่งสัปดาห์</small></div>
    <img src="/plots/layer_hourly.png" class="s31-img" />
  </div>
  <div class="s31-stack" :class="{ on: $clicks >= 1 }">
    <div class="s31-row">
      <div class="s31-lab"><b>ฤดูกาล</b><span>ปีละรอบ</span></div>
      <img src="/plots/layer_season.png" class="s31-img" />
    </div>
    <div class="s31-row key">
      <div class="s31-lab"><b>ระหว่างปี</b><span>ราว <Lit v="2" c="C07" />–<Lit v="7" c="C07" /> ปี <em>← ที่เราต้องการ</em></span><small>ค่าเฉลี่ยเคลื่อนที่หนึ่งปี</small><small>แถบเทา = ไม่มีข้อมูล</small></div>
      <img src="/plots/layer_inter.png" class="s31-img" />
    </div>
    <div class="s31-row">
      <div class="s31-lab"><b>แนวโน้มระยะยาว</b><span>ของระดับน้ำ</span><small>เส้นตรงที่ fit กับทั้งช่วง</small></div>
      <img src="/plots/layer_trend.png" class="s31-img" />
    </div>
  </div>
</div>

<style>
.s31-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 10px; padding: 18px 30px; }
.s31-row { display: flex; align-items: center; gap: 16px; }
.s31-stack { display: flex; flex-direction: column; gap: 10px; opacity: 0; transform: translateY(16px); transition: opacity 0.6s, transform 0.6s; }
.s31-stack.on { opacity: 1; transform: none; }
/* กรอบเน้นล้อมทั้งแถว (ป้าย + รูป) — ไม่ทับข้อความใด */
.s31-row.key { margin: 0 -14px; padding: 2px 12px; border: 3px solid var(--andaman); border-radius: 14px; }
.s31-lab { width: 260px; flex: none; display: flex; flex-direction: column; gap: 0; font-size: 22px; color: var(--ink-2); line-height: 1.3; }
.s31-lab b { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 28px; color: var(--ink); }
.s31-lab small { font-size: 20px; color: var(--ink-3); }
.s31-row.key .s31-lab b { color: var(--andaman); }
.s31-lab em { font-style: normal; font-weight: 600; color: var(--andaman); }
.s31-img { width: 1400px; display: block; }
</style>

<!--
สัญญาณระดับน้ำคือหลายจังหวะซ้อนกัน น้ำขึ้นน้ำลง ฤดูกาล การแกว่งหลายปี และแนวโน้มระยะยาวของระดับน้ำ
เราต้องการแค่ชั้นระหว่างปี เพราะเอลนีโญแกว่งเป็นจังหวะราว 2 ถึง 7 ปี

ถ้าถูกถาม:
- มาตรวัดบันทึกความสูงของน้ำทุกชั่วโมง สถานีเดียวมีกว่าสามแสนจุด
- แถบเทาคือช่วงที่ข้อมูลรายเดือนทางการไม่มีค่า ช่วงปี 2013 ถึง 2014 แท่นวัดถูกพายุทำลาย ส่วนช่วงอื่นไม่มีเอกสารบอกสาเหตุ
-->

---
id: SQ03_S020
clicks: 2
layout: page
seq: '3'
section: การเตรียมข้อมูล
page: 8
kinds: [ข้อมูลจริง, แผนภาพ]
---

# การสุ่มวันละครั้งให้ความถี่ Nyquist เพียง <Lit v="0.5" c="C63" /> รอบต่อวัน ต่ำกว่าความถี่น้ำขึ้นน้ำลง

<!--
  บน = แผนภาพเต็มความกว้างการ์ด (ผู้ใช้ 10-15: ตัดกรอบดำ "จุดที่ต่อกันได้เป็นคลื่นช้าที่ไม่มีอยู่จริง" แล้วขยายกราฟแทนที่)
-->
<div class="s32-col">
  <div class="card s32-top">
    <div class="s32-cap">ระดับน้ำรายชั่วโมง (น้ำขึ้นน้ำลง)</div>
    <svg class="s32-svg" viewBox="0 0 1690 350" width="1690" height="350">
      <line v-for="d in [0, 5, 10, 15, 20, 25, 30]" :key="'g' + d" :x1="X(d)" y1="14" :x2="X(d)" y2="332" stroke="#E3ECF0" stroke-width="2" />
      <line x1="20" y1="332" x2="1670" y2="332" stroke="#3B5866" stroke-width="3" />
      <line x1="20" y1="14" x2="20" y2="332" stroke="#3B5866" stroke-width="3" />
      <line v-for="d in [0, 5, 10, 15, 20, 25, 30]" :key="'t' + d" :x1="X(d)" y1="332" :x2="X(d)" y2="344" stroke="#3B5866" stroke-width="3" />
      <polyline class="s32-tide" pathLength="1" :points="tidePts" fill="none" stroke="#12303D" stroke-width="2" stroke-linejoin="round" />
      <polyline class="s32-slow" :class="{ on: $clicks >= 1 }" :points="dotPts" fill="none" stroke="#C0392B" stroke-width="4" stroke-dasharray="14 9" stroke-linecap="round" />
      <g :class="{ on: $clicks >= 1 }" class="s32-dots">
        <circle v-for="(p, i) in dots" :key="i" class="s32-dot" :style="{ animationDelay: (i * 0.06) + 's' }" :cx="p[0]" :cy="p[1]" r="7.5" fill="#C0392B" stroke="#fff" stroke-width="2.5" />
      </g>
    </svg>
    <div class="s32-x s32-x0">เริ่ม</div>
    <div class="s32-x s32-xm">เวลา (วัน)</div>
    <div class="s32-y">ระดับน้ำ</div>
    <div class="s32-x s32-x1">หนึ่งเดือนต่อมา</div>
    <div class="s32-leg" :class="{ on: $clicks >= 1 }"><i></i> จุดแดง = ค่าที่สุ่มได้ (เวลาเดียวกันของทุกวัน)</div>
  </div>
  <div v-click="2" class="card s32-bot">
    <div class="s32-cap">สเปกตรัมของระดับน้ำรายชั่วโมงจริงหนึ่งปี (แปลงฟูริเยร์ด้วย FFT)</div>
    <img src="/plots/spectrum_hourly.png" class="s32-spec" />
    <div class="s32-n">Nyquist ของการสุ่มวันละครั้ง</div>
    <div class="s32-catch">ส่วนที่จับได้</div>
    <div class="s32-g" style="left: 820px; top: 66px">K1 O1 P1<br><span>วันละรอบ</span></div>
    <div class="s32-g" style="left: 1450px; top: 66px">M2 S2 K2<br><span>วันละสองรอบ</span></div>
    <div class="s32-ax">ความถี่ (รอบต่อวัน)</div>
  </div>
</div>
<script setup>
// รูปร่างเท่านั้น (แผนภาพ): น้ำขึ้นน้ำลงแบบวันละรอบ = K1 + O1 (คาบเป็นวัน) · สัมประสิทธิ์ไม่ใช่ข้อมูลจริง
const X = (d) => 20 + d * (1650 / 30)
const Y = (v) => 172 - v * 100
const tide = (t) => Math.cos((2 * Math.PI * t) / 0.99727) + 0.55 * Math.cos((2 * Math.PI * t) / 1.0758)
const pts = []
for (let h = 0; h <= 30 * 24; h++) pts.push(`${X(h / 24).toFixed(1)},${Y(tide(h / 24)).toFixed(1)}`)
const tidePts = pts.join(' ')
const dots = []
for (let d = 0; d <= 30; d++) dots.push([X(d), Y(tide(d))])
const dotPts = dots.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ')
</script>

<style>
/* บน = โดเมนเวลา (แผนภาพ: เส้นน้ำขึ้นน้ำลงรายชั่วโมง → จุดสุ่มวันละครั้ง → เส้นช้าปลอม)
   ล่าง = โดเมนความถี่ (ข้อมูลจริง: สเปกตรัม FFT ของระดับน้ำรายชั่วโมงหนึ่งปี + Nyquist) */
.s32-col { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 20px; }
.s32-top { position: relative; flex: 0 0 450px; padding: 0; overflow: hidden; }
.s32-bot { position: relative; flex: 0 0 370px; padding: 0; overflow: hidden; }
.s32-svg { position: absolute; left: 30px; top: 74px; }
.s32-svg2 { position: absolute; left: 20px; top: 20px; }
.s32-cap { position: absolute; left: 34px; top: 14px; font-size: 26px; font-weight: 600; color: var(--ink-2); }
.s32-x { position: absolute; top: 420px; font-size: 24px; color: var(--ink-2); }
.s32-x0 { left: 34px; }
.s32-xm { left: 800px; }
.s32-y { position: absolute; left: 34px; top: 48px; font-size: 22px; color: var(--ink-2); font-weight: 600; }
.s32-x1 { right: 30px; }
.s32-leg { position: absolute; left: 820px; top: 14px; font-size: 22px; color: #C0392B; font-weight: 600; opacity: 0; transition: opacity 0.4s; }
.s32-leg.on { opacity: 1; }
.s32-leg i { display: inline-block; width: 16px; height: 16px; border-radius: 50%; background: #C0392B; margin-right: 6px; vertical-align: -1px; }
.s32-tide { stroke-dasharray: 1; stroke-dashoffset: 1; animation: s32-draw 3.2s ease-out forwards; }
@keyframes s32-draw { to { stroke-dashoffset: 0; } }
.s32-dot { opacity: 0; transform-box: fill-box; transform-origin: center; }
.s32-dots.on .s32-dot { animation: s32-pop 0.35s ease-out forwards; }
@keyframes s32-pop { 0% { opacity: 0; transform: scale(0.2); } 70% { opacity: 1; transform: scale(1.5); } 100% { opacity: 1; transform: scale(1); } }
.s32-slow { opacity: 0; }
.s32-slow.on { animation: s32-line 0.6s ease-out 2.3s forwards; }
@keyframes s32-line { to { opacity: 1; } }
/* แผงความถี่: รูปสเปกตรัมจริงจาก tools/make_method_figs.py spectrum() · แกน x ในรูป 0–2.5 รอบต่อวัน อยู่ที่ x 120–1576 px ของรูป
   รูปวางที่ left 40 → ตำแหน่งบนการ์ด = 160 + f × 582 (0.5 → 451 · 1 → 742 · 2 → 1324) */
.s32-spec { position: absolute; left: 40px; top: 58px; width: 1600px; }
.s32-bot .s32-cap { left: 34px; top: 12px; }
.s32-n { position: absolute; left: 470px; top: 72px; font-size: 22px; font-weight: 600; color: var(--andaman); white-space: nowrap; }
.s32-catch { position: absolute; left: 305px; top: 112px; transform: translateX(-50%); font-size: 26px; font-weight: 600; color: var(--andaman); white-space: nowrap; }
.s32-g { position: absolute; transform: translateX(-50%); text-align: center; font-size: 24px; font-weight: 600; color: #C0392B; line-height: 1.25; white-space: nowrap; }
.s32-g span { font-size: 22px; font-weight: 400; color: var(--ink-2); }
.s32-ax { position: absolute; right: 30px; top: 336px; font-size: 22px; color: var(--ink-2); font-weight: 600; }
</style>

<!--
ถ้าเราเก็บค่าแค่วันละครั้ง ก็เหมือนจับได้วันละจุด แต่น้ำขึ้นน้ำลงขึ้นลงวันละหนึ่งถึงสองรอบ จุดที่จับได้จึงตามมันไม่ทัน
ในภาษาความถี่ สุ่มวันละครั้งเห็นได้แค่ถึง Nyquist คือ 0.5 รอบต่อวัน
สเปกตรัมจากการแปลงฟูริเยร์ของข้อมูลรายชั่วโมงจริงหนึ่งปีแสดงยอดของน้ำขึ้นน้ำลงที่ราว 1 และ 2 รอบต่อวัน อยู่นอกส่วนที่จับได้ทั้งหมด

ถ้าถูกถาม:
- K1 O1 P1 กับ M2 S2 K2 คือชื่อองค์ประกอบของน้ำขึ้นน้ำลง กลุ่มแรกขึ้นลงราววันละ 1 รอบ กลุ่มที่สองราววันละ 2 รอบ
- ตัวอักษรบอกที่มาของแรงดึงดูด O1 มาจากดวงจันทร์ P1 มาจากดวงอาทิตย์ K1 มาจากทั้งสองร่วมกัน ส่วน M2 คือองค์ประกอบหลักจากดวงจันทร์ S2 จากดวงอาทิตย์ และ K2 จากทั้งสองร่วมกัน
- ถ้าไม่กรองก่อน จุดที่จับไม่ทันจะเรียงตัวเป็นคลื่นช้าปลอม K1 กับ P1 กลายเป็นคลื่นคาบ 365.2 วัน ปลอมตัวเป็นวงรอบฤดูกาลพอดี
-->

---
id: SQ03_S040
clicks: 2
layout: page
seq: '3'
section: การเตรียมข้อมูล
page: 9
kinds: [ข้อมูลจริง]
---

# ตัวกรอง FIR ออกแบบด้วยสูตร Kaiser <Fact id="fir.taps" :digits="0" /> taps ลดทอนน้ำขึ้นน้ำลง <Fact id="fir.tide_suppression_min_db" :digits="0" />–<Fact id="fir.tide_suppression_max_db" :digits="0" /> dB

<div class="s34-wrap">
  <div class="card s34-spec">
    <div class="s34-h">สเปกของตัวกรอง</div>
    <div>แถบหยุดเริ่มที่ Nyquist ของผลรายวัน <b><Lit v="0.5" c="C63" /></b> รอบต่อวัน</div>
    <div>ลดทอนในแถบหยุด <b><Fact id="fir.spec_db" :digits="0" /> dB</b></div>
    <div class="s34-arrow">↓</div>
    <div class="s34-box">สูตร Kaiser</div>
    <div class="s34-arrow">↓</div>
    <div class="s34-big"><span>β = <Fact id="fir.beta" :digits="4" /></span><span><Fact id="fir.taps" :digits="0" /> taps</span></div>
  </div>
  <div class="card s34-chart">
    <div class="s34-legend"><span><i class="s34-sw resp"></i>ผลตอบสนองที่วัดได้ (dB)</span><span v-click="1"><i class="s34-sw spec"></i>สเปก</span><span v-click="2"><i class="s34-sw tide"></i>น้ำขึ้นน้ำลงแต่ละองค์ประกอบ</span></div>
    <SeriesChart :width="1060" :height="560" x-key="fir_w" :x-range="[0, 2.5]" :ticks-x="[0, 0.5, 1, 1.5, 2, 2.5]"
      :y-left="[-125, 5]" :ticks-left="[-120, -70, 0]" y-label="ผลตอบสนอง (dB)" x-label="ความถี่ (รอบต่อวัน)" :zero="false"
      :series="[{ key: 'fir_h_db', kind: 'line', color: 'var(--andaman)', width: 3, at: 1 }]"
      :hlines="[{ y: -70, color: '#C0392B', dash: true, at: 1 }]"
      :points="[
        { x: 0.8932, y: -76.56, color: '#C0392B', at: 2 }, { x: 0.9295, y: -85.43, color: '#C0392B', at: 2 },
        { x: 0.9973, y: -78.84, color: '#C0392B', at: 2 }, { x: 1.0027, y: -79.90, color: '#C0392B', at: 2 },
        { x: 1.8960, y: -85.38, color: '#C0392B', at: 2 }, { x: 1.9323, y: -98.89, color: '#C0392B', at: 2 },
        { x: 2.0, y: -87.18, color: '#C0392B', at: 2 }, { x: 2.0055, y: -88.41, color: '#C0392B', at: 2 },
      ]" />
    <div v-click="1" class="bubble s34-measured">วัดจริงได้ <Fact id="fir.measured_db" :digits="2" /> dB</div>
  </div>
</div>

<style>
.s34-wrap { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 520px 1fr; gap: 30px; }
.s34-spec { display: flex; flex-direction: column; gap: 12px; font-size: 24px; }
.s34-h { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 30px; }
.s34-arrow { font-size: 30px; color: var(--ink-3); text-align: center; line-height: 1; }
.s34-box { align-self: center; background: var(--bg); border-radius: 18px; padding: 9px 30px; font-weight: 600; }
.s34-big { display: flex; flex-direction: column; align-items: center; gap: 2px; font-family: 'Kanit', sans-serif;
  font-weight: 500; font-size: 48px; line-height: 1.25; color: var(--ink); }
.s34-chart { position: relative; display: flex; flex-direction: column; gap: 6px; }
.s34-legend { display: flex; gap: 30px; font-size: 22px; color: var(--ink-2); }
.s34-legend span { display: flex; align-items: center; gap: 10px; }
.s34-sw { display: inline-block; width: 30px; height: 4px; border-radius: 2px; }
.s34-sw.resp { background: var(--andaman); }
.s34-sw.spec { background: repeating-linear-gradient(90deg, #C0392B 0 10px, transparent 10px 16px); }
.s34-sw.tide { width: 16px; height: 16px; border-radius: 50%; background: #C0392B; }
.s34-measured { position: absolute; left: 330px; top: 250px; }
.s34-tides { position: absolute; right: 40px; bottom: 60px; }
</style>

<!--
เราจึงออกแบบ FIR จากสเปก 70 เดซิเบลด้วยสูตร Kaiser ได้ความยาว 261 taps
ผลคือกดน้ำขึ้นน้ำลงทุกองค์ประกอบลง 77 ถึง 99 เดซิเบล ก่อนลดอัตรา

ถ้าถูกถาม:
- stopband เริ่มที่ Nyquist ของผลรายวันคือ 0.5 รอบต่อวัน
- สูตรของ Kaiser ให้ β เท่ากับ 6.7553 และวัดจริงได้ 70.07 เดซิเบล
- ตรวจทั้งสายแล้ว ค่ารายวันจากตัวกรองของเราต่างจากค่ารายวันของ UHSLC เพียง RMS 3.0 มิลลิเมตร
- และค่ารายเดือนต่างจาก PSMSL แค่ราว 1.1 ถึง 1.2 มิลลิเมตร ในช่วงที่ข้อมูลทางการนิ่ง
-->

---
id: SQ03_S060
clicks: 1
layout: page
seq: '3'
section: การเตรียมข้อมูล
page: 10
kinds: [ข้อมูลจริง]
---

# การกำจัดแนวโน้มระยะยาวและวงรอบฤดูกาลออกจากระดับน้ำทะเล

<!--
  รูปจาก tools/make_method_figs.py (PSMSL รายเดือนดิบของเกาะหลัก · fit ด้วยเมทริกซ์ออกแบบของโครงงาน wtc.preprocess._design)
  ขั้น 0 เส้นดิบ + เส้น fit (แนวโน้ม + ฤดูกาล) ทับ · คลิก 1 ลบออก → residual + การ์ดสรุป
-->
<div class="card s36-card">
  <div class="s36-head"><span class="s36-chip gulf">อ่าวไทย เกาะหลัก</span><span><i class="sw raw"></i>ระดับน้ำรายเดือนจริง</span><span><i class="sw fit"></i>แนวโน้มระยะยาว + ฤดูกาล ที่ fit ได้</span></div>
  <img src="/plots/prep_raw.png" class="s36-img" />
  <div class="s36-step" :class="{ on: $clicks >= 1 }">
    <div class="s36-minus">ลบเส้นเข้มออก ↓ เหลือ</div>
    <img src="/plots/prep_resid.png" class="s36-img" />
  </div>
</div>

<style>
.s36-card { position: relative; flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 6px; padding: 20px 36px; }
.s36-head { display: flex; align-items: center; gap: 34px; font-size: 22px; color: var(--ink-2); }
.s36-head span { display: flex; align-items: center; gap: 10px; }
.s36-chip { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 26px; padding: 2px 18px; border-radius: 999px; }
.s36-chip.gulf { background: #FBE6CF; color: #A85A12; }
.sw { display: inline-block; width: 34px; height: 5px; border-radius: 3px; }
.sw.raw { background: var(--gulf); }
.sw.fit { background: var(--ink); }
.s36-img { width: 1600px; height: 282px; display: block; }
.s36-step { opacity: 0; transition: opacity 0.6s; }
.s36-step.on { opacity: 1; }
.s36-minus { font-size: 24px; font-weight: 600; color: var(--ink); margin-left: 90px; }
.s36-sum { position: absolute; right: 36px; bottom: 18px; font-size: 26px; opacity: 0; transition: opacity 0.5s 0.4s; }
.s36-sum.on { opacity: 1; }
</style>

<!--
จากนั้น fit แนวโน้มเชิงเส้นระยะยาวของระดับน้ำกับฮาร์มอนิกรายปีและครึ่งปีแล้วลบออก เหลือแต่สัญญาณระหว่างปีที่จะเข้าเวฟเล็ต

ถ้าถูกถาม:
- fit เฉพาะเดือนที่มีข้อมูลจริง ช่องว่างไม่เกิน 3 เดือนเติมด้วยเส้นตรง ช่องว่างยาวเติมศูนย์และจดไว้ใน mask จุดที่มีของเติมเกิน 50 เปอร์เซ็นต์จะไม่ถูกนับ
- ต้องเติมเพราะ CWT ต้องการอนุกรมต่อเนื่องที่ห่างเท่ากัน และสัญญาณคาบ 2 ถึง 7 ปีแทบไม่เปลี่ยนในไม่กี่เดือน เส้นตรงจึงเดาได้ใกล้ ส่วนช่องยาวถ้าลากเส้นตรงจะสร้างสัญญาณปลอม จึงเติมศูนย์ซึ่งเท่ากับค่าเฉลี่ยแทน
- ข้อสรุปไม่ขึ้นกับวิธีเติม แบบทดสอบที่ลากเส้นตรงทุกช่องว่างก็ยังผ่าน
-->

---
id: SQ04_S020
layout: page
seq: '4'
section: ข้อจำกัดของสหสัมพันธ์
page: 11
kinds: [ข้อมูลจริง]
---

# สหสัมพันธ์ทั้งอนุกรมมีค่าเพียง <Fact id="corr.andaman.neg_nino34" :digits="2" /> และ <Fact id="corr.andaman.neg_dmi" :digits="2" /> เนื่องจากความสัมพันธ์ไม่คงที่ตามเวลา

<div class="card chart-card">
  <div class="legend">
    <span><i class="sw area"></i>ระดับน้ำอันดามัน ค่าเฉลี่ย <Lit v="12" c="C20" /> เดือน (มม.)</span>
    <span><i class="sw line nino"></i>−Niño3.4 (SD)</span>
    <span><i class="sw line dmi"></i>−DMI (SD)</span>
  </div>
  <SeriesChart :width="1680" :height="560"
    :series="[
      { key: 'andaman_mm_12m', kind: 'area', color: 'var(--andaman)' },
      { key: 'neg_dmi_12m', kind: 'line', axis: 'right', color: 'var(--dmi)', width: 2.4 },
      { key: 'neg_nino34_12m', kind: 'line', axis: 'right', color: 'var(--nino)' },
    ]"
    :y-left="[-250, 250]" :y-right="[-2.5, 2.5]" :ticks-left="[-200, 0, 200]" :ticks-right="[-2, 0, 2]"
    :band="[1997.5, 1998.5]" y-label="ระดับน้ำ (มม.)" y-label-right="ดัชนี (SD)" x-label="ปี" />
  <div class="bubble event">ปี <Lit v="1997" c="C20" />–<Lit v="98" c="C20" /> ระดับน้ำร่วงราว <Fact id="event.andaman_9798_min_mm" absval :round-to="10" /> มม. พร้อมเอลนีโญและ IOD บวก</div>
  <div class="r-values">
    <div><span class="r"><Fact id="corr.andaman.neg_nino34" :digits="2" /></span><span>r กับ −Niño3.4 ทั้งอนุกรม</span></div>
    <div><span class="r dmi"><Fact id="corr.andaman.neg_dmi" :digits="2" /></span><span>r กับ −DMI ทั้งอนุกรม</span></div>
  </div>
</div>

<style>
.chart-card { position: relative; flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 6px; }
.legend { display: flex; gap: 33px; font-size: 22px; color: var(--ink-2); }
.legend span { display: flex; align-items: center; gap: 12px; }
.sw { display: inline-block; }
.sw.area { width: 24px; height: 24px; border-radius: 6px; background: var(--andaman); opacity: 0.6; }
.sw.line { width: 33px; height: 4px; border-radius: 2px; }
.sw.nino { background: var(--nino); }
.sw.dmi { background: var(--dmi); }
.bubble.event { position: absolute; left: 1150px; top: 470px; max-width: 480px; }
.r-values { position: absolute; right: 170px; top: 18px; display: flex; gap: 42px; background: var(--card);
  padding: 12px 24px; border-radius: 21px; box-shadow: var(--shadow); }
.r-values > div { display: flex; flex-direction: column; align-items: flex-start; font-size: 20px; color: var(--ink-2); }
.r-values .r { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 60px; line-height: 1.1; color: var(--nino); }
.r-values .r.dmi { color: var(--dmi); }
.bubble.summary { align-self: flex-start; font-size: 27px; }
</style>

<!--
ปี 1997 ถึง 98 ค่าเฉลี่ย 12 เดือนของระดับน้ำร่วงราว 210 มิลลิเมตร ตรงกับปีเอลนีโญและ IOD บวก
แต่ถ้าคำนวณสหสัมพันธ์ทั้งอนุกรม จะได้แค่ 0.30 กับเอลนีโญ และ 0.10 กับ IOD
เพราะความสัมพันธ์นี้เปิดเฉพาะช่วงที่มีเหตุการณ์ แล้วปิดไปในปีปกติ
สหสัมพันธ์ที่เฉลี่ยทั้ง 72 ปีจึงมองไม่เห็นมัน เราต้องการเครื่องมือที่บอกได้ว่าเกิดเมื่อไร และที่จังหวะไหน
-->

---
id: SQ05_S020
clicks: 1
layout: page
seq: '5'
section: การแปลงเวฟเล็ตแบบต่อเนื่อง
page: 12
kinds: [แผนภาพ]
---

# การแปลงเวฟเล็ตแบบต่อเนื่องด้วย Morlet ω0 = <Fact id="cwt.morlet_w0" :digits="0" /> ที่ <Fact id="cwt.scales_per_octave" :digits="0" /> สเกลต่อ octave

<div class="card s52-card">
  <ManimClip page="SQ05_S020" :steps="2" :width="1680" :height="600" />
  <div class="s52-cap">สัญญาณ = ระดับน้ำอันดามัน (ค่าเฉลี่ย <Lit v="12" c="C20" /> เดือน) ทุกแถวของระนาบคำนวณจริงด้วย Morlet ω0 = <Fact id="cwt.morlet_w0" /></div>
</div>

<style>
.s52-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; align-items: center; gap: 6px; padding-top: 12px; }
.s52-cap { align-self: flex-start; font-size: 22px; color: var(--ink-2); }
</style>

<!--
CWT เลื่อน Morlet wavelet ซึ่งเป็นคลื่นสั้น ๆ ในซองรูประฆัง ไปตามเวลา ทุกขนาด 12 สเกลต่อ octave
แต่ละสเกลได้หนึ่งแถว รวมกันเป็นภาพสองมิติ แกนนอนคือเวลา แกนตั้งคือคาบ

ถ้าถูกถาม:
- CWT คือ filter bank ที่ละเอียดขึ้น filter bank แยกแถบต่ำซ้ำได้แถบแบบ octave ส่วน CWT แบ่งละเอียดกว่า
- ที่เลือก Morlet เพราะเป็นคลื่นเชิงซ้อน จึงให้ทั้งขนาดและเฟสที่เราต้องใช้ตอนท้าย และที่ ω0 เท่ากับ 6 สเกลแทบเท่ากับคาบ อ่านแกนเป็นปีได้ตรง ๆ
-->

---
id: SQ05_S030
clicks: 1
layout: page
seq: '5'
section: การแปลงเวฟเล็ตแบบต่อเนื่อง
page: 13
kinds: [ข้อมูลจริง]
---

# ระนาบกำลังเวฟเล็ตและกรวยอิทธิพล (COI)

<!--
  ระนาบกำลังเวฟเล็ตของอันดามัน: tools/make_method_figs.py → power_plain.png / power_coi.png
  (CWT ของโครงงานเอง wtc.transform.cwt บนอนุกรมที่สายประมวลผลป้อนจริง · สีเป็น log2 ของกำลัง เปรียบเทียบภายในภาพเดียว)
  ขั้น 0 ระนาบ · คลิก 1 กรวยอิทธิพล (รูปที่มีเส้นประ + ขอบจาง) · ไม่เทียบดนตรี ไม่มีการ์ดสรุป (ผู้ใช้ 10-14)
-->
<div class="card s53-card">
  <div class="s53-head">
    <span class="s53-chip andaman">ระดับน้ำอันดามัน</span>
    <span class="s53-ramp"><i></i>สีเข้ม = จังหวะนั้นแรง</span>
    <span>แกนนอน = เวลา&emsp;แกนตั้ง = คาบ</span>
  </div>
  <div class="s53-plane">
    <img src="/plots/power_plain.png" class="s53-img" />
    <img src="/plots/power_coi.png" class="s53-img over" :class="{ on: $clicks >= 1 }" />
    <div class="s53-coi" :class="{ on: $clicks >= 1 }"><b>เส้นประ = กรวยอิทธิพล (COI)</b><br>นอกกรวย คลื่นยื่นออกนอกข้อมูล → เชื่อไม่ได้</div>
  </div>
</div>

<style>
.s53-card { position: relative; flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 8px; padding: 18px 36px; }
.s53-head { display: flex; align-items: center; gap: 34px; font-size: 22px; color: var(--ink-2); }
.s53-head span { display: flex; align-items: center; gap: 10px; }
.s53-chip { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 26px; padding: 2px 18px; border-radius: 999px; }
.s53-chip.andaman { background: #DCE9F7; color: var(--andaman); }
.s53-ramp i { width: 110px; height: 18px; border-radius: 4px; border: 1px solid #C9D6DC;
  background: linear-gradient(90deg, #FFFFFF, #CFE3F3, #7FB0DD, #2F74C0, #1B4B80); }
.s53-plane { position: relative; width: 1600px; height: 527px; }
.s53-img { position: absolute; left: 0; top: 0; width: 1600px; height: 527px; }
.s53-img.over { opacity: 0; transition: opacity 0.8s; }
.s53-img.over.on { opacity: 1; }
.s53-coi { position: absolute; left: 110px; bottom: 70px; padding: 10px 18px; border-radius: 12px; background: rgba(255,255,255,0.93);
  font-size: 22px; line-height: 1.4; color: var(--ink-2); opacity: 0; transition: opacity 0.5s 0.5s; }
.s53-coi b { color: var(--ink); }
.s53-coi.on { opacity: 1; }
</style>

<!--
ระนาบนี้บอกว่าจังหวะคาบไหนแรงขึ้นในช่วงเวลาไหน
ส่วนขอบซ้ายขวาเชื่อไม่ได้ เพราะคลื่นยื่นออกนอกข้อมูล จึงตัดด้วยเส้นประที่เรียกว่ากรวยอิทธิพล
-->

---
id: SQ06_S020
clicks: 1
layout: page
seq: '6'
section: Wavelet coherence
page: 14
kinds: [แผนภาพ]
---

# Wavelet coherence: ความสัมพันธ์ของสองสัญญาณบนระนาบเวลา–คาบพร้อมมุมเฟส

<!--
  อธิบาย WTC ภาษาธรรมดา: คลิก 0 = สูตร (HTML/CSS ล้วน ไม่ใช้ KaTeX) + แผนภาพ เวลา × คาบ (ก้อนเดียว · ผู้ใช้ 10-15 ตัดจุดเล็กสองจุดที่ไม่มีคำอธิบาย) · คลิก 1 = นิยามเฟส θ (ไม่มีการ์ดลูกศร — ความหมายลูกศรอยู่ในคำอธิบายของหน้า SQ06_S030 · ผู้ใช้ 10-15)
-->
<div class="s62-top">
  <div class="card s62-formula">
    <div class="s62-eq">
      <span class="s62-lhs">R²(s, τ) =</span>
      <span class="s62-frac">
        <span class="s62-num">|<span class="s62-S">S(s⁻¹ W<sub>XY</sub>)</span>|²</span>
        <span class="s62-bar"></span>
        <span class="s62-den"><span class="s62-S">S(s⁻¹ |W<sub>X</sub>|²)</span>&thinsp;<span class="s62-S">S(s⁻¹ |W<sub>Y</sub>|²)</span></span>
      </span>
    </div>
    <div class="s62-call"><b>S</b> = ปรับเรียบในเวลาและสเกล — ถ้าไม่ปรับเรียบ ค่าจะเป็น <Lit v="1" c="C30" /> เสมอ</div>
    <ul class="s62-list">
      <li><b>W<sub>X</sub>, W<sub>Y</sub></b> = CWT ของระดับน้ำและของดัชนี</li>
      <li><b>W<sub>XY</sub></b> = ผลคูณไขว้ (ขยับพร้อมกันตรงไหน)</li>
      <li><b>R²</b> อยู่ระหว่าง <Lit v="0" c="C30" /> ถึง <Lit v="1" c="C30" /> — ใกล้ <Lit v="1" c="C30" /> = ขยับพร้อมกันมาก</li>
    </ul>
  </div>
  <div class="card s62-plane">
    <div class="s62-pbox">
      <span class="s62-ay">คาบ ↑</span>
      <svg viewBox="0 0 600 300" class="s62-svg">
        <defs>
          <radialGradient id="s62g" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#1B4B80" stop-opacity="0.95" />
            <stop offset="45%" stop-color="#2F74C0" stop-opacity="0.65" />
            <stop offset="100%" stop-color="#7FB0DD" stop-opacity="0" />
          </radialGradient>
        </defs>
        <rect x="0" y="0" width="600" height="300" fill="#fff" stroke="#C9D6DC" stroke-width="2" />
        <g stroke="#E3ECEF" stroke-width="2">
          <line x1="100" y1="0" x2="100" y2="300" /><line x1="200" y1="0" x2="200" y2="300" /><line x1="300" y1="0" x2="300" y2="300" />
          <line x1="400" y1="0" x2="400" y2="300" /><line x1="500" y1="0" x2="500" y2="300" />
          <line x1="0" y1="60" x2="600" y2="60" /><line x1="0" y1="120" x2="600" y2="120" /><line x1="0" y1="180" x2="600" y2="180" /><line x1="0" y1="240" x2="600" y2="240" />
        </g>
        <ellipse cx="370" cy="110" rx="170" ry="70" fill="url(#s62g)" />
      </svg>
      <span class="s62-ax">เวลา →</span>
    </div>
    <div class="s62-cap">ได้ค่าทุกจุดของเวลาและคาบ<br>ผลคือภาพ เวลา × คาบ แบบหน้าถัดไป</div>
  </div>
</div>
<div class="card s62-phase" :class="{ on: $clicks >= 1 }">
  <div class="s62-def">θ = มุมของ <span class="s62-S">S(s⁻¹ W<sub>XY</sub>)</span></div>
  <div class="s62-defsub">= เฟสระดับน้ำ − เฟสดัชนี<br>บอกว่าสองสัญญาณไปทางเดียวกันหรือสวนทาง และสัญญาณใดนำ</div>
</div>

<style>
.s62-top { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 1fr 700px; gap: 24px; }
.s62-formula { padding: 30px 40px; display: flex; flex-direction: column; justify-content: center; gap: 26px; }
.s62-eq { display: flex; align-items: center; gap: 22px; font-size: 56px; font-family: 'Kanit', sans-serif; font-weight: 400; color: var(--ink); padding: 8px 0; }
.s62-frac { display: inline-flex; flex-direction: column; align-items: center; }
.s62-num, .s62-den { padding: 4px 8px; white-space: nowrap; }
.s62-bar { align-self: stretch; height: 3px; background: var(--ink); border-radius: 2px; }
.s62-S { background: #DCE9F7; border-radius: 10px; padding: 0 8px; }
.s62-eq sub, .s62-def sub { font-size: 0.6em; }
.s62-eq sup, .s62-def sup { font-size: 0.6em; }
.s62-call { font-size: 30px; color: var(--ink); background: #EEF4FB; border-left: 6px solid var(--andaman); border-radius: 8px; padding: 8px 18px; }
.s62-list { margin: 0; padding: 0; list-style: none; font-size: 30px; line-height: 1.5; color: var(--ink-2); }
.s62-list b { color: var(--ink); }
.s62-list sub { font-size: 0.65em; }
.s62-plane { padding: 18px 30px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
.s62-pbox { display: grid; grid-template-columns: auto 600px; grid-template-rows: 300px auto; column-gap: 8px; }
.s62-svg { width: 600px; height: 300px; }
.s62-ay { writing-mode: vertical-rl; transform: rotate(180deg); font-size: 22px; color: var(--ink-3); text-align: center; }
.s62-ax { grid-column: 2; font-size: 22px; color: var(--ink-3); text-align: right; }
.s62-cap { font-size: 24px; line-height: 1.4; color: var(--ink-2); text-align: center; }
.s62-phase { display: flex; align-items: center; gap: 48px; padding: 30px 40px; margin-top: 24px; opacity: 0; transition: opacity 0.5s; }
.s62-phase.on { opacity: 1; }
.s62-def { font-family: "Kanit", sans-serif; font-size: 48px; line-height: 1.3; color: var(--ink); white-space: nowrap; }
.s62-defsub { font-size: 30px; line-height: 1.45; color: var(--ink-2); }
</style>

<!--
wavelet coherence วัดว่าระดับน้ำกับดัชนีขยับพร้อมกันแค่ไหน ได้ค่า 0 ถึง 1 ทุกจุดของเวลาและคาบ
และได้มุมเฟส 0 องศาคือไปด้วยกัน 180 องศาคือสวนทาง

ถ้าถูกถาม:
- ตัวปรับเรียบ S ในทิศเวลาและสเกลทำหน้าที่แทนการเฉลี่ยแบบ Welch
- coherence แบบ Welch ต้องเฉลี่ยหลายท่อน ถ้าใช้ท่อนเดียว ตัวเศษกับตัวส่วนมาจาก DFT ชุดเดียวกัน coherence จึงได้ 1 เสมอ
- มุมเฟส θ คือเฟสของระดับน้ำลบเฟสของดัชนี
-->

---
id: SQ06_S030
layout: page
seq: '6'
section: Wavelet coherence
page: 15
kinds: [ข้อมูลจริง]
---

# ทะเลอันดามันมี coherence ต่อเนื่องที่คาบ <Lit v="2" c="C31" />–<Lit v="5" c="C31" /> ปี ส่วนอ่าวไทยกระจายเป็นจุด

<!--
  ระนาบ WTC จริง สไตล์ D — รูปสร้างด้วย tools/make_wtc_fig.py (ข้อมูล wtc_q1.npz ของโครงงาน DSP · อ่านอย่างเดียว)
  ไม่มีคลิก ไม่มีแอนิเมชัน (ผู้ใช้ 10-14) — ทั้งสองแผงขึ้นพร้อมกัน
  วงรีวางตามพิกัดรูป 1700×330 ย่อเหลือสูง 300: แกน x 1951–2023 กินช่วง 5.5%–99.5% ของความกว้าง
-->
<div class="card s63-card">
  <div class="s63-legend">
    <span class="s63-ramp"><i></i>สีเข้ม = ขยับพร้อมกันมาก</span>
    <span><i class="s63-sw line"></i>เส้นทึบ = เกินระดับ noise</span>
    <span><b class="s63-arr">→</b> ไปด้วยกัน&emsp;<b class="s63-arr">←</b> สวนทาง</span>
    <span><i class="s63-sw coi"></i>พื้นจาง = นอกกรวย (เชื่อไม่ได้)</span>
  </div>
  <div class="s63-panel">
    <div class="s63-head"><span class="s63-chip andaman">อันดามัน × Niño3.4</span><span class="s63-note">ก้อนใหญ่ที่เกิน noise ลูกศรส่วนใหญ่ชี้ซ้าย = สวนทางกับ Niño3.4</span></div>
    <div class="s63-imgbox">
      <img src="/plots/wtc_andaman.png" class="s63-img" />
      <svg class="s63-ring" viewBox="0 0 1545 300" width="1545" height="300"><ellipse cx="1075" cy="118" rx="215" ry="48" fill="none" stroke="#12303D" stroke-width="4" stroke-dasharray="12 8" /></svg>
    </div>
  </div>
  <div class="s63-panel">
    <div class="s63-head"><span class="s63-chip gulf">อ่าวไทย × Niño3.4</span><span class="s63-note">มีแต่จุดเล็กกระจาย แบบที่ noise สร้างได้เอง</span></div>
    <div class="s63-imgbox"><img src="/plots/wtc_gulf.png" class="s63-img" /></div>
  </div>
</div>

<style>
.s63-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 10px; padding: 18px 40px; }
.s63-legend { display: flex; gap: 40px; align-items: center; font-size: 22px; color: var(--ink-2); }
.s63-legend span { display: flex; align-items: center; gap: 10px; }
.s63-ramp i { width: 120px; height: 18px; border-radius: 4px; background: linear-gradient(90deg, #FFFFFF, #CFE3F3, #7FB0DD, #2F74C0, #1B4B80); border: 1px solid #C9D6DC; }
.s63-sw { display: inline-block; }
.s63-sw.line { width: 34px; height: 5px; border-radius: 3px; background: var(--ink); }
.s63-sw.coi { width: 34px; height: 18px; border-radius: 4px; background: #F1F4F6; border: 2px dashed var(--ink-2); }
.s63-arr { font-size: 28px; color: #0B1A22; }
.s63-panel { display: flex; flex-direction: column; gap: 4px; }
.s63-head { display: flex; align-items: baseline; gap: 22px; }
.s63-chip { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 26px; padding: 2px 18px; border-radius: 999px; }
.s63-chip.andaman { background: #DCE9F7; color: var(--andaman); }
.s63-chip.gulf { background: #FBE6CF; color: #A85A12; }
.s63-note { font-size: 24px; color: var(--ink); }
.s63-imgbox { position: relative; width: 1545px; height: 300px; }
.s63-img { width: 1545px; height: 300px; display: block; }
.s63-ring { position: absolute; left: 0; top: 0; }
</style>

<!--
นี่คือผลจริง แถวบนคืออันดามัน มีก้อนใหญ่ช่วงปลายทศวรรษ 1990 ถึง 2010 ที่คาบ 2 ถึง 5 ปี
แถวล่างคืออ่าวไทย มีแต่จุดเล็ก ๆ กระจาย แบบที่ noise สร้างได้เอง
-->

---
id: SQ06_S040
clicks: 1
layout: page
seq: '6'
section: Wavelet coherence
page: 16
kinds: [แผนภาพ]
---

# Multiple wavelet coherence: ความสัมพันธ์กับหลายดัชนีพร้อมกัน ครบ <Lit v="218" c="C69" /> ชุด

<!--
  ขั้น 1 (ตอนเข้าหน้า) แผนภาพหลายดัชนี → ระดับน้ำ + สูตรพร้อมความหมายของแต่ละพจน์ (ผู้ใช้ 10-15 ตัดป้าย "ใช้ดัชนีเดียว → ลดรูปเป็น WTC") · คลิก 1 การ์ด 218 ชุด + การ์ดสรุป
-->
<div class="s64-top">
  <div class="card s64-diagram">
    <div class="s64-flow">
      <svg class="s64-arrows" viewBox="0 0 640 344" preserveAspectRatio="none">
        <defs>
          <marker id="s64-head" markerUnits="userSpaceOnUse" markerWidth="22" markerHeight="22" refX="20" refY="11" orient="auto">
            <path d="M0,0 L22,11 L0,22 z" fill="#1F6FB2" />
          </marker>
        </defs>
        <line x1="0" y1="28" x2="630" y2="172" stroke="#1F6FB2" stroke-width="4" marker-end="url(#s64-head)" />
        <line x1="0" y1="100" x2="630" y2="172" stroke="#1F6FB2" stroke-width="4" marker-end="url(#s64-head)" />
        <line x1="0" y1="172" x2="630" y2="172" stroke="#1F6FB2" stroke-width="4" marker-end="url(#s64-head)" />
        <line x1="0" y1="244" x2="630" y2="172" stroke="#1F6FB2" stroke-width="4" marker-end="url(#s64-head)" />
        <line x1="0" y1="316" x2="630" y2="172" stroke="#1F6FB2" stroke-width="4" marker-end="url(#s64-head)" stroke-dasharray="10 8" />
      </svg>
      <div class="s64-chips">
        <span>Niño3.4</span><span>SOI</span><span>DMI</span><span>WNPMI</span><span class="s64-more">…</span>
      </div>
      <div class="s64-target">ระดับน้ำ</div>
    </div>
    <div class="s64-cap"><b>WTC</b> = ดัชนีทีละตัว&emsp;&emsp;<b>MWC</b> = หลายดัชนีพร้อมกัน</div>
  </div>
  <div class="s64-side">
    <div class="card s64-formula">
      <div class="s64-fhead">สมการของ MWC</div>
      <div class="s64-eq">ρ²(s, τ) = W̃<sub>YX</sub> W̃<sub>XX</sub>⁻¹ W̃<sub>YX</sub><sup>H</sup> ⁄ W̃<sub>YY</sub></div>
      <ul class="s64-list">
        <li><b>W̃<sub>YY</sub></b> = กำลังของระดับน้ำ</li>
        <li><b>W̃<sub>YX</sub></b> = cross-wavelet ระดับน้ำกับแต่ละดัชนี</li>
        <li><b>W̃<sub>XX</sub></b> = เมทริกซ์ระหว่างดัชนีด้วยกัน</li>
        <li><b>~</b> = ผ่านการปรับเรียบ S แบบเดียวกับ WTC</li>
      </ul>
      <div class="s64-fnote">ขยายจาก WTC เป็นเมทริกซ์ของหลายดัชนี (Hu &amp; Si)</div>
    </div>
  </div>
</div>
<div class="s64-bottom" :class="$clicks >= 1 ? 's64-on' : ''">
  <div class="card s64-count">
    <div class="s64-big"><Lit v="218" c="C69" /> ชุด</div>
    <div class="s64-bigcap">ทุกชุดย่อยของ <Fact id="indices.n" /> ดัชนี<br>ขนาด <Lit v="1" c="C69" /> ถึง <Lit v="5" c="C69" /> ตัว</div>
  </div>
  <div class="bubble s64-bubble">coherence บอกว่าสัญญาณขยับพร้อมกัน เมื่อไร ที่คาบไหน และทิศไหน</div>
</div>

<style>
.s64-top { display: flex; gap: 30px; }
.s64-diagram { flex: 1.5 1 0; min-width: 0; padding: 24px 36px 20px; display: flex; flex-direction: column; gap: 14px; }
.s64-flow { position: relative; height: 344px; }
.s64-arrows { position: absolute; left: 230px; top: 0; width: 640px; height: 344px; }
.s64-chips { position: absolute; left: 0; top: 0; width: 220px; height: 344px; display: flex; flex-direction: column; gap: 16px; }
.s64-chips span { height: 56px; box-sizing: border-box; display: flex; align-items: center; justify-content: center;
  font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 30px; border-radius: 999px;
  background: color-mix(in srgb, var(--andaman) 14%, white); color: var(--andaman); }
.s64-chips .s64-more { background: transparent; color: var(--ink-3); border: 3px dashed var(--ink-3); }
.s64-target { position: absolute; left: 880px; top: 92px; width: 160px; height: 160px; box-sizing: border-box; border-radius: 24px;
  background: var(--andaman); color: white; display: flex; align-items: center; justify-content: center; text-align: center;
  font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 34px; line-height: 1.2; }
.s64-cap { font-size: 26px; color: var(--ink-2); text-align: center; }
.s64-cap b { font-family: 'Kanit', sans-serif; font-weight: 500; color: var(--andaman); }
.s64-side { flex: 0.9 1 0; min-width: 0; display: flex; flex-direction: column; gap: 24px; }
.s64-formula { padding: 24px 30px; display: flex; flex-direction: column; gap: 16px; flex: 1; justify-content: center; }
.s64-fhead { font-size: 24px; color: var(--ink-3); }
.s64-eq { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 36px; line-height: 1.6; color: var(--ink); }
.s64-eq sub, .s64-eq sup { font-size: 22px; }
.s64-fnote { font-size: 22px; line-height: 1.45; color: var(--ink-3); }
.s64-list { margin: 0; padding: 0; list-style: none; font-size: 26px; line-height: 1.55; color: var(--ink-2); }
.s64-list b { font-family: 'Kanit', sans-serif; font-weight: 500; color: var(--ink); }
.s64-list sub { font-size: 0.65em; }
.s64-bottom { display: flex; gap: 30px; margin-top: 36px; min-height: 270px; align-items: stretch; opacity: 0; transition: opacity 0.5s; }
.s64-bottom.s64-on { opacity: 1; }
.s64-count { flex: 0 0 860px; padding: 21px 36px; display: flex; align-items: center; gap: 30px; border-top: 12px solid var(--andaman); }
.s64-big { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 130px; line-height: 1; color: var(--andaman); white-space: nowrap; }
.s64-bigcap { font-size: 28px; line-height: 1.5; color: var(--ink-2); }
.s64-bubble { flex: 1 1 0; display: flex; align-items: center; font-size: 44px; line-height: 1.5; padding: 24px 42px; }
</style>

<!--
multiple wavelet coherence ขยายไปใช้หลายดัชนีพร้อมกัน ถ้าใช้ดัชนีเดียวก็ลดรูปเป็น WTC พอดี
เราค้นครบ 218 ชุด คือชุดขนาด 1 ถึง 5 จาก 8 ดัชนี

ถ้าถูกถาม:
- MWC เป็นของ Hu และ Si ปี 2016 ที่งานต้นแบบใช้
- ชุดที่ต่อจากชุดเดิมใช้ Cholesky ของชุดเดิมต่อได้ จึงค้นได้เร็วขึ้นราว 27 เท่า
-->

---
id: SQ07_S010
clicks: 1
layout: page
seq: '7'
section: การทดสอบนัยสำคัญ
page: 17
kinds: [แผนภาพ]
---

# การทดสอบนัยสำคัญด้วยการจำลองกระบวนการ AR(1) จำนวน <Fact id="null.n_pairs" :digits="0" /> คู่

<!--
  รูปจาก tools/make_method_figs.py: noise_pair.png (AR(1) สองตัว สัมประสิทธิ์เท่าอันดามันและ SOI จริง · wtc.significance.ar1_surrogate)
  noise_wtc.png (WTC ของคู่นั้นด้วยโค้ดของโครงงาน) · noise_thr.png (เกณฑ์ 95% ตามคาบ จาก wtc_q1.npz threshold ของคู่อันดามัน × SOI)
  ขั้น 0 คู่ noise + ระนาบที่ก็มีก้อน · คลิก 1 ทำ 1,000 คู่ → เกณฑ์ตามคาบ
-->
<div class="card s71-card">
  <div class="s71-pair">
    <div class="s71-plab"><b>noise สองตัว</b><span>สุ่มแบบ AR(1) เลียนแบบข้อมูลจริง<br>แต่ไม่เกี่ยวกันเลย</span></div>
    <img src="/plots/noise_pair.png" class="s71-pimg" />
  </div>
  <div class="s71-row">
    <div class="s71-box">
      <div class="s71-cap">WTC ของ noise คู่นี้ — <b>ก็มีก้อนสีเข้ม</b></div>
      <img src="/plots/noise_wtc.png" class="s71-wtc" />
    </div>
    <div class="s71-box s71-thr" :class="{ on: $clicks >= 1 }">
      <div class="s71-cap">ทำซ้ำ <Fact id="null.n_pairs" /> คู่ → ที่แต่ละคาบ<br>เก็บค่าที่ noise ทำได้ <Lit v="95" c="C36" />% เป็น<b class="red">เกณฑ์</b></div>
      <img src="/plots/noise_thr.png" class="s71-timg" />
      <div class="s71-note">ของจริงต้องสูงกว่าเส้นนี้ ถึงนับว่าไม่ใช่ noise</div>
    </div>
  </div>
</div>

<style>
.s71-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 10px; padding: 18px 36px; }
.s71-pair { display: flex; align-items: center; gap: 16px; }
.s71-plab { width: 330px; flex: none; display: flex; flex-direction: column; gap: 4px; font-size: 20px; color: var(--ink-2); line-height: 1.35; }
.s71-plab b { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 28px; color: var(--ink); }
.s71-pimg { width: 1330px; height: auto; }
.s71-row { display: flex; gap: 30px; align-items: flex-start; }
.s71-box { display: flex; flex-direction: column; gap: 6px; }
.s71-cap { font-size: 24px; color: var(--ink); line-height: 1.35; }
.s71-cap b { color: var(--andaman); }
.s71-cap b.red { color: #C0392B; }
.s71-wtc { width: 1100px; height: 400px; }
.s71-timg { width: 560px; height: 400px; }
.s71-thr { opacity: 0; transform: translateY(14px); transition: opacity 0.6s, transform 0.6s; }
.s71-thr.on { opacity: 1; transform: none; }
.s71-note { font-size: 22px; color: var(--ink-2); }
</style>

<!--
สัญญาณสุ่มสองตัวที่ไม่เกี่ยวกันก็สร้างก้อน coherence ได้ เราจึงสุ่ม AR(1) ที่มีสัมประสิทธิ์เท่ากับข้อมูลจริง 1,000 คู่
quantile 95 เปอร์เซ็นต์ของ noise คือเกณฑ์ บริเวณที่เกินคือที่ล้อมด้วยเส้นขาว
-->

---
id: SQ07_S020
clicks: 2
layout: page
seq: '7'
section: การทดสอบนัยสำคัญ
page: 18
kinds: [ข้อมูลจริง]
---

# ผลดัชนีเดี่ยว: อันดามันเกินระดับสัญญาณรบกวนสี่ดัชนี อ่าวไทยไม่เกินทั้ง <Fact id="indices.n" :digits="0" /> ดัชนี

<div class="card s7-card">
  <div class="s7-head">
    <div class="s7-def"><b>PASC</b> = เปอร์เซ็นต์ของพื้นที่ในระนาบเวลา–คาบที่เกินระดับ noise</div>
    <div class="s7-legend"><span><i class="sw andaman-bg"></i>อันดามัน</span><span><i class="sw gulf-bg"></i>อ่าวไทย</span></div>
  </div>
  <div class="s7-plot">
    <svg width="1680" height="620" viewBox="0 0 1680 620">
      <line x1="90" x2="1660" y1="540.0" y2="540.0" stroke="#DCE6EA" stroke-width="2"/><line x1="90" x2="1660" y1="380.0" y2="380.0" stroke="#DCE6EA" stroke-width="2"/><line x1="90" x2="1660" y1="220.0" y2="220.0" stroke="#DCE6EA" stroke-width="2"/><line x1="90" x2="1660" y1="60.0" y2="60.0" stroke="#DCE6EA" stroke-width="2"/>
      <line x1="90" x2="1660" y1="540" y2="540" stroke="var(--ink-3)" stroke-width="2.5"/>
      <g v-click="1" class="s7-grow"><rect x="110.1" y="83.64" width="74" height="456.36" rx="6" fill="var(--andaman)"/><rect x="306.4" y="105.64" width="74" height="434.36" rx="6" fill="var(--andaman)"/><rect x="502.6" y="113.12" width="74" height="426.88" rx="6" fill="var(--andaman)"/><rect x="698.9" y="218.84" width="74" height="321.16" rx="6" fill="var(--andaman)"/><rect x="895.1" y="279.65" width="74" height="260.35" rx="6" fill="var(--andaman)"/><rect x="1091.4" y="318.74" width="74" height="221.26" rx="6" fill="var(--andaman)"/><rect x="1287.6" y="378.54" width="74" height="161.46" rx="6" fill="var(--andaman)"/><rect x="1483.9" y="442.08" width="74" height="97.92" rx="6" fill="var(--andaman)"/></g>
      <g v-click="2" class="s7-grow"><rect x="192.1" y="399.37" width="74" height="140.63" rx="6" fill="var(--gulf)"/><rect x="388.4" y="389.99" width="74" height="150.01" rx="6" fill="var(--gulf)"/><rect x="584.6" y="385.16" width="74" height="154.84" rx="6" fill="var(--gulf)"/><rect x="780.9" y="460.77" width="74" height="79.23" rx="6" fill="var(--gulf)"/><rect x="977.1" y="335.72" width="74" height="204.28" rx="6" fill="var(--gulf)"/><rect x="1173.4" y="430.57" width="74" height="109.43" rx="6" fill="var(--gulf)"/><rect x="1369.6" y="333.25" width="74" height="206.75" rx="6" fill="var(--gulf)"/><rect x="1565.9" y="432.93" width="74" height="107.07" rx="6" fill="var(--gulf)"/></g>
      <line x1="90" x2="1660" y1="257.72" y2="257.72" stroke="var(--ink)" stroke-width="3.5" stroke-dasharray="16 10"/>
    </svg>
    <span class="s7-axis-title" style="left:0;top:0">PASC (%)</span>
    <span class="s7-axis-title s7-xtitle">ดัชนีภูมิอากาศ</span>
    <span v-for="t in [{n:0,y:540.0},{n:5,y:380.0},{n:10,y:220.0},{n:15,y:60.0}]" :key="t.n" class="s7-tick" :style="{ top: (t.y - 15) + 'px' }">{{ t.n }}</span>
    <span class="s7-name" style="left:90.0px;width:196.2px">SOI</span><span class="s7-name" style="left:286.2px;width:196.2px">DMI</span><span class="s7-name" style="left:482.5px;width:196.2px">WNPMI</span><span class="s7-name" style="left:678.8px;width:196.2px">Niño3.4</span><span class="s7-name" style="left:875.0px;width:196.2px">AMO</span><span class="s7-name" style="left:1071.2px;width:196.2px">TPI</span><span class="s7-name" style="left:1267.5px;width:196.2px">NAO</span><span class="s7-name" style="left:1463.8px;width:196.2px">PDO</span>
    <div v-click="1"><span class="s7-val andaman" style="left:102.1px;top:49.6px"><Fact id="pasc.andaman.plane.soi" :digits="1" /></span><span class="s7-val andaman" style="left:298.4px;top:71.6px"><Fact id="pasc.andaman.plane.dmi" :digits="1" /></span><span class="s7-val andaman" style="left:494.6px;top:79.1px"><Fact id="pasc.andaman.plane.wnpmi" :digits="1" /></span><span class="s7-val andaman" style="left:690.9px;top:184.8px"><Fact id="pasc.andaman.plane.nino34" :digits="1" /></span><span class="s7-val andaman" style="left:887.1px;top:245.7px"><Fact id="pasc.andaman.plane.amo" :digits="1" /></span><span class="s7-val andaman" style="left:1083.4px;top:284.7px"><Fact id="pasc.andaman.plane.tpi" :digits="1" /></span><span class="s7-val andaman" style="left:1279.6px;top:344.5px"><Fact id="pasc.andaman.plane.nao" :digits="1" /></span><span class="s7-val andaman" style="left:1475.9px;top:408.1px"><Fact id="pasc.andaman.plane.pdo" :digits="1" /></span></div>
    <div v-click="2"><span class="s7-val gulf" style="left:184.1px;top:365.4px"><Fact id="pasc.gulf.plane.soi" :digits="1" /></span><span class="s7-val gulf" style="left:380.4px;top:356.0px"><Fact id="pasc.gulf.plane.dmi" :digits="1" /></span><span class="s7-val gulf" style="left:576.6px;top:351.2px"><Fact id="pasc.gulf.plane.wnpmi" :digits="1" /></span><span class="s7-val gulf" style="left:772.9px;top:426.8px"><Fact id="pasc.gulf.plane.nino34" :digits="1" /></span><span class="s7-val gulf" style="left:969.1px;top:301.7px"><Fact id="pasc.gulf.plane.amo" :digits="1" /></span><span class="s7-val gulf" style="left:1165.4px;top:396.6px"><Fact id="pasc.gulf.plane.tpi" :digits="1" /></span><span class="s7-val gulf" style="left:1361.6px;top:299.3px"><Fact id="pasc.gulf.plane.nao" :digits="1" /></span><span class="s7-val gulf" style="left:1557.9px;top:398.9px"><Fact id="pasc.gulf.plane.pdo" :digits="1" /></span></div>
    <div class="bubble s7-noise">เส้นประ = ระดับ noise (ราว <Fact id="noise.pasc_p95_plane" :digits="0" />%) — แท่งที่สูงกว่าเส้นคือเกิน noise</div>
  </div>
</div>

<style>
.s7-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 6px; }
.s7-head { display: flex; justify-content: space-between; align-items: center; gap: 36px; }
.s7-def { font-size: 26px; color: var(--ink); line-height: 1.4; }
.s7-def b { font-family: 'Kanit', sans-serif; font-weight: 500; }
.s7-legend { display: flex; gap: 33px; font-size: 24px; color: var(--ink-2); white-space: nowrap; }
.s7-legend span { display: flex; align-items: center; gap: 12px; }
.sw { display: inline-block; width: 26px; height: 26px; border-radius: 7px; }
.sw.andaman-bg { background: var(--andaman); }
.sw.gulf-bg { background: var(--gulf); }
.s7-plot { position: relative; width: 1680px; height: 650px; }
.s7-xtitle { left: 90px; right: 20px; top: 596px; text-align: center; font-weight: 600; color: var(--ink-2); }
.s7-plot > svg { position: absolute; left: 0; top: 0; }
.s7-grow { transform-box: fill-box; transform-origin: 50% 100%; transition: transform .6s ease-out, opacity .3s; }
.s7-grow.slidev-vclick-hidden { transform: scaleY(0); opacity: 0; }
.s7-val { position: absolute; width: 90px; text-align: center; font-size: 26px; font-weight: 600; line-height: 1.2;
  background: var(--card); border-radius: 8px; }
.s7-name { position: absolute; top: 552px; text-align: center; font-size: 26px; color: var(--ink); }
.s7-tick { position: absolute; left: 0; width: 70px; text-align: right; font-size: 22px; color: var(--ink-3); line-height: 30px; }
.s7-axis-title { position: absolute; font-size: 22px; color: var(--ink-3); }
.s7-noise { position: absolute; right: 20px; top: 126px; white-space: nowrap; font-size: 24px; }
/* ก้านชี้ลงถึงเส้นประ (เส้นอยู่ที่ y ≈ 258 · ป้ายสูง ≈ 54 → ก้านยาว ≈ 70) */
.s7-noise::before { content: ''; position: absolute; left: 80px; top: 100%; width: 3px; height: 66px; background: var(--ink); }
.s7-noise::after { content: ''; position: absolute; left: 74px; top: calc(100% + 64px); border: 7.5px solid transparent;
  border-top: 10px solid var(--ink); border-bottom: 0; }
</style>

<!--
เราสรุปทั้งระนาบด้วย PASC คือเปอร์เซ็นต์ของพื้นที่ที่เกินเกณฑ์ ซึ่ง noise เองขึ้นไปได้ถึงราว 9 เปอร์เซ็นต์
อันดามันกับ SOI ได้ 14.3 DMI 13.6 WNPMI 13.3 และ Niño3.4 10.0 เปอร์เซ็นต์ เกินระดับ noise ทั้งสี่ตัว
ส่วนอ่าวไทย ไม่มีดัชนีไหนเกิน noise เลย ทั้ง 8 ดัชนี

ถ้าถูกถาม:
- จุดข้างเคียงสัมพันธ์กันผ่านการปรับเรียบ noise จึงเกินเป็นก้อน PASC ของ noise เฉลี่ยราว 5 เปอร์เซ็นต์ และขึ้นไปได้ถึงราว 9 เปอร์เซ็นต์
- ถ้าดูเฉพาะแถบ 2 ถึง 7 ปี noise ขึ้นไปได้ถึงราว 13 ถึง 15 เปอร์เซ็นต์
- อ่าวไทยไม่เกิน noise ในทั้ง 8 แบบทดสอบ
-->

---
id: SQ07_S040
clicks: 2
layout: page
seq: '7'
section: การทดสอบนัยสำคัญ
page: 19
kinds: [ข้อมูลจริง]
---

# เกณฑ์นัยสำคัญของ MWC ต้องปรับตามจำนวนดัชนี และการรวมดัชนีไม่เพิ่มอำนาจอธิบาย

<div class="card s74-card">
  <div class="s74-def"><b>ดัชนีปลอม</b> = สัญญาณสุ่มที่ไม่เกี่ยวกับทะเลเลย — ใช้ตรวจว่าวิธีหลอกเราได้ไหม</div>
  <div class="s74-body">
    <div class="s74-plot">
      <svg width="1150" height="600" viewBox="0 0 1150 600">
        <line x1="90" x2="1130" y1="520" y2="520" stroke="var(--ink-3)" stroke-width="2.5"/><line x1="90" x2="1130" y1="280" y2="280" stroke="#DCE6EA" stroke-width="2"/><line x1="90" x2="1130" y1="40" y2="40" stroke="#DCE6EA" stroke-width="2"/>
        <g class="s74-draw">
          <!-- ดัชนีจริง เกณฑ์เดิม (mwc.andaman.real_unadjusted) -->
          <polyline points="150,475.4 370,351.3 590,196.2 810,86.9 1030,47.3" fill="none" stroke="var(--andaman)" stroke-width="5" stroke-dasharray="16 10" stroke-linejoin="round"/>
          <circle cx="150" cy="475.4" r="8" fill="var(--andaman)"/><circle cx="370" cy="351.3" r="8" fill="var(--andaman)"/><circle cx="590" cy="196.2" r="8" fill="var(--andaman)"/><circle cx="810" cy="86.9" r="8" fill="var(--andaman)"/><circle cx="1030" cy="47.3" r="8" fill="var(--andaman)"/>
          <polyline points="150,497.0 370,396.9 590,232.8 810,105.0 1030,53.4" fill="none" stroke="#C0392B" stroke-width="5" stroke-dasharray="16 10" stroke-linejoin="round"/>
          <circle cx="150" cy="497.0" r="9" fill="#C0392B"/><circle cx="370" cy="396.9" r="9" fill="#C0392B"/><circle cx="590" cy="232.8" r="9" fill="#C0392B"/><circle cx="810" cy="105.0" r="9" fill="#C0392B"/><circle cx="1030" cy="53.4" r="9" fill="#C0392B"/>
        </g>
        <g v-click="2" class="s74-fade">
          <!-- ดัชนีจริง ปรับเกณฑ์แล้ว (mwc.andaman.real_adjusted) -->
          <polyline points="150,475.4 370,471.8 590,473.2 810,475.2 1030,477.6" fill="none" stroke="var(--andaman)" stroke-width="6" stroke-linejoin="round"/>
          <circle cx="150" cy="475.4" r="8" fill="var(--andaman)"/><circle cx="370" cy="471.8" r="8" fill="var(--andaman)"/><circle cx="590" cy="473.2" r="8" fill="var(--andaman)"/><circle cx="810" cy="475.2" r="8" fill="var(--andaman)"/><circle cx="1030" cy="477.6" r="8" fill="var(--andaman)"/>
          <polyline points="150,497.0 370,497.1 590,497.4 810,498.0 1030,498.1" fill="none" stroke="#C0392B" stroke-width="6" stroke-linejoin="round"/>
          <circle cx="150" cy="497.0" r="9" fill="#C0392B"/><circle cx="370" cy="497.1" r="9" fill="#C0392B"/><circle cx="590" cy="497.4" r="9" fill="#C0392B"/><circle cx="810" cy="498.0" r="9" fill="#C0392B"/><circle cx="1030" cy="498.1" r="9" fill="#C0392B"/>
        </g>
      </svg>
      <span class="s74-axis-title" style="left:0;top:0">PASC (%)</span>
      <span v-for="t in [{n:0,y:520},{n:50,y:280},{n:100,y:40}]" :key="t.n" class="s74-tick" :style="{ top: (t.y - 15) + 'px' }">{{ t.n }}</span>
      <span v-for="q in [1,2,3,4,5]" :key="q" class="s74-q" :style="{ left: (150 + (q - 1) * 220 - 25) + 'px' }">{{ q }}</span>
      <span class="s74-axis-title" style="left:430px;top:568px;font-size:24px;color:var(--ink)">จำนวนดัชนีที่รวมกัน</span>
      <span class="s74-val" style="left:52px;top:476px"><Fact id="mwc.andaman.fake_unadjusted" :index="0" :digits="1" /></span>
      <span class="s74-val real" style="left:62px;top:430px"><Fact id="mwc.andaman.real_unadjusted" :index="0" :digits="1" /></span>
      <span class="s74-val real" style="left:960px;top:-6px"><Fact id="mwc.andaman.real_unadjusted" :index="4" :digits="1" /></span>
      <span class="s74-val" style="left:1048px;top:36px"><Fact id="mwc.andaman.fake_unadjusted" :index="4" :digits="1" /></span>
      <div class="s74-key" style="left:110px;top:40px">
        <div><i class="sw dash fake"></i><b class="fake">ดัชนีปลอม</b> เกณฑ์เดิม</div>
        <div><i class="sw dash real"></i><b class="real">ดัชนีจริง</b> เกณฑ์เดิม</div>
        <div class="s74-note">ยิ่งรวมยิ่งดูดีทั้งคู่ แยกของจริงกับ noise ไม่ออก</div>
      </div>
      <div v-click="2" class="s74-key s74-fade" style="left:400px;top:352px">
        <div><i class="sw solid real"></i><b class="real">ดัชนีจริง</b> ปรับเกณฑ์แล้ว ราว <Fact id="mwc.andaman.real_adjusted" :index="4" :digits="0" />–<Fact id="mwc.andaman.real_adjusted" :index="1" :digits="0" />%</div>
        <div><i class="sw solid fake"></i><b class="fake">ดัชนีปลอม</b> ปรับเกณฑ์แล้ว ต่ำกว่า <Lit v="5" c="C44" />%</div>
      </div>
    </div>
    <div class="s74-side">
      <div v-click="1" class="s74-panel">
        <div class="s74-title">เกณฑ์ต้องสูงขึ้นตามจำนวนดัชนี</div>
        <div class="s74-ytitle">เกณฑ์ ρ² ของ noise</div>
        <div class="s74-splot">
          <svg width="450" height="330" viewBox="0 0 450 330">
            <line x1="10" x2="440" y1="300" y2="300" stroke="var(--ink-3)" stroke-width="2.5"/>
            <rect x="20" y="146.4" width="76" height="153.6" fill="var(--diag-bg)"/><rect x="105" y="99.9" width="76" height="200.1" fill="var(--diag-bg)"/><rect x="190" y="73.3" width="76" height="226.7" fill="var(--diag-bg)"/><rect x="275" y="58.3" width="76" height="241.7" fill="var(--diag-bg)"/><rect x="360" y="49.8" width="76" height="250.2" fill="var(--diag-bg)"/>
            <path d="M20,146.4 L96,146.4 L105,146.4 L105,99.9 L181,99.9 L190,99.9 L190,73.3 L266,73.3 L275,73.3 L275,58.3 L351,58.3 L360,58.3 L360,49.8 L436,49.8" fill="none" stroke="var(--ink)" stroke-width="4" stroke-linejoin="round"/>
          </svg>
          <span v-for="(t, i) in [82, 36, 10, -5, -14]" :key="i" class="s74-sv" :style="{ left: (13 + i * 85) + 'px', top: t + 'px' }"><Fact id="mwc.threshold_mid" :index="i" :digits="2" /></span>
          <span v-for="q in [1,2,3,4,5]" :key="q" class="s74-sq" :style="{ left: (13 + (q - 1) * 85) + 'px' }">{{ q }}</span>
        </div>
        <div class="s74-cap">จำนวนดัชนีที่รวมกัน</div>
      </div>
    </div>
  </div>
</div>

<style>
.s74-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 8px; }
.s74-def { font-size: 26px; color: var(--ink); line-height: 1.4; }
.s74-def b { color: #C0392B; font-family: 'Kanit', sans-serif; font-weight: 500; }
.s74-body { flex: 1 1 auto; display: flex; align-items: center; justify-content: center; gap: 60px; min-height: 0; }
.s74-plot { position: relative; width: 1150px; height: 610px; flex: none; }
.s74-plot > svg { position: absolute; left: 0; top: 0; }
.s74-draw { animation: s74-wipe 1.4s ease-out backwards; }
@keyframes s74-wipe { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
.s74-fade { transition: opacity .4s; }
.s74-fade.slidev-vclick-hidden { opacity: 0; }
.s74-tick { position: absolute; left: 0; width: 70px; text-align: right; font-size: 22px; color: var(--ink-3); line-height: 30px; }
.s74-q { position: absolute; top: 528px; width: 50px; text-align: center; font-size: 26px; color: var(--ink); }
.s74-axis-title { position: absolute; font-size: 22px; color: var(--ink-3); white-space: nowrap; }
.s74-val { position: absolute; width: 80px; text-align: center; font-size: 28px; font-weight: 600; color: #C0392B; line-height: 1.2; }
.s74-lab { position: absolute; font-size: 24px; font-weight: 600; color: #C0392B; line-height: 1.35; }
.s74-val.real { color: var(--andaman); }
.s74-key { position: absolute; display: flex; flex-direction: column; gap: 2px; font-size: 24px; color: var(--ink-2); line-height: 1.4;
  background: rgba(255,255,255,0.92); padding: 4px 10px; border-radius: 10px; }
.s74-key b { font-weight: 600; }
.s74-key b.fake { color: #C0392B; }
.s74-key b.real { color: var(--andaman); }
.s74-key .sw { display: inline-block; width: 44px; height: 0; margin-right: 10px; vertical-align: 6px; }
.s74-key .sw.dash { border-top: 5px dashed; }
.s74-key .sw.solid { border-top: 6px solid; }
.s74-key .sw.fake { border-color: #C0392B; }
.s74-key .sw.real { border-color: var(--andaman); }
.s74-note { font-size: 22px; color: var(--ink-3); }
.s74-side { width: 450px; flex: none; display: flex; flex-direction: column; justify-content: center; gap: 18px; }  /* ไม่มีกล่องดำ +0.6 จุด (ผู้ใช้ 10-15) */
.s74-panel { display: flex; flex-direction: column; gap: 6px; }
.s74-title { font-size: 26px; font-weight: 600; color: var(--ink); }
.s74-splot { position: relative; width: 450px; height: 330px; margin-top: 14px; }
.s74-splot > svg { position: absolute; left: 0; top: 0; }
.s74-sv { position: absolute; width: 90px; text-align: center; font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 26px; color: var(--ink); }
.s74-sq { position: absolute; top: 304px; width: 90px; text-align: center; font-size: 24px; color: var(--ink); }
.s74-cap { font-size: 21px; color: var(--ink-2); font-weight: 600; text-align: center; }
.s74-ytitle { font-size: 21px; color: var(--ink-2); font-weight: 600; margin-bottom: -4px; }
</style>

<!--
ถ้ารวมหลายดัชนีโดยใช้เกณฑ์เดิม แม้ดัชนีปลอมที่สุ่มขึ้นมาและไม่เกี่ยวกับทะเลเลย ก็ได้ PASC จาก 4.8 ไปถึง 97.2 เปอร์เซ็นต์
ดัชนีจริงก็ไต่ขึ้นแบบเดียวกัน จาก 9.3 ไปถึง 98.5 เปอร์เซ็นต์ จึงแยกของจริงกับของปลอมไม่ออก
เพราะ noise หลายตัวรวมกันก็อธิบายอะไรได้มากขึ้นโดยบังเอิญ เกณฑ์จึงต้องสูงขึ้นตามจำนวนดัชนี จาก 0.59 ไปถึง 0.96
พอปรับเกณฑ์แล้ว ดัชนีปลอมผ่านไม่ถึง 5 เปอร์เซ็นต์ ส่วนดัชนีจริงราบอยู่ราว 9 ถึง 10 เปอร์เซ็นต์ เหนือดัชนีปลอม คือมีสัญญาณจริง แต่ไม่ได้เพิ่มขึ้นเมื่อรวม
การรวมดัชนีจริงเพิ่มได้สูงสุดแค่ 0.6 จุด การรวมหลายดัชนีจึงไม่ได้ผลมากขึ้น

ถ้าถูกถาม:
- งานต้นแบบพบว่ายิ่งรวมดัชนีมาก PASC ยิ่งสูง จาก 14 ไปถึง 96 เปอร์เซ็นต์ ไต่ขึ้นแบบเดียวกับดัชนีปลอม (งานเดียว)
- เราแยกไม่ได้ว่างานต้นแบบใช้เกณฑ์แบบไหน จึงเป็นข้อสังเกต ไม่ใช่ข้อกล่าวหา
- การเลือกชุดที่ดีที่สุดจาก 218 ชุดต้องเทียบทั้งตระกูล ถ้าดู p ทีละชุด มีถึง 136 ชุดที่ต่ำกว่า 0.05 แต่เทียบกับค่าสูงสุดของการค้นหาภายใต้ noise เหลือผ่านแค่ 4 ถึง 5 ชุด
-->

---
id: SQ08_S020
clicks: 2
layout: page
seq: '8'
section: กลไกทางกายภาพ
page: 20
kinds: [แผนภาพ]
---

# กลไกฝั่งอันดามัน: ลมเหนือเส้นศูนย์สูตร → คลื่นเคลวิน → ระดับน้ำภูเก็ตลดลง

<!--
  แผนที่พื้นจากแนวชายฝั่งจริง: tools/make_basemap.py → /plots/map_s82.png (1600×800 · lon 80–132 · lat −10–16 · PlateCarree)
  ลูกศร/ป้ายทุกตัวกำหนดเป็นพิกัดภูมิศาสตร์ในบล็อก script ท้ายไฟล์ แล้วแปลงเป็นพิกเซลด้วย px() — ไม่วางพิกเซลด้วยมือ
  ขั้น 0 เอลนีโญ → ผ่านอากาศ → ลมตะวันออกนอกสุมาตรา–ชวา · 1 คลื่นเคลวินวิ่งไปตะวันออกตามศูนย์สูตร ·
  2 ชนสุมาตราแล้วเลี้ยวขึ้นเหนือเลียบชายฝั่งถึงภูเก็ต · ไม่มีกรอบ r ของแบบจำลอง (ผู้ใช้ 10-15 ตัด · ค่า r อยู่ใน ถ้าถูกถาม) · อ่าวไทยจางและไม่มีลูกศรเข้า (หน้าถัดไป)
-->
<div class="card s82-card">
  <div class="s82-box">
    <img src="/plots/map_s82.png" class="s82-map" />
    <svg class="s82-svg" viewBox="0 0 1600 800" width="1600" height="800">
      <defs>
        <marker id="s82-hk" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#12303D" /></marker>
        <marker id="s82-hg" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#6B7B85" /></marker>
        <marker id="s82-hb" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3.6" markerHeight="3.6" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#2F74C0" /></marker>
      </defs>
      <ellipse :cx="andaman.x" :cy="andaman.y" rx="100" ry="155" fill="#2F74C0" fill-opacity="0.12" />
      <ellipse :cx="gulf.x" :cy="gulf.y" rx="70" ry="110" fill="#D9822B" fill-opacity="0.12" />
      <path :d="airArc" class="s82-air" :class="{ dim: $clicks >= 1 }" fill="none" stroke="#6B7B85" stroke-width="5" stroke-dasharray="3 12" stroke-linecap="round" marker-end="url(#s82-hg)" />
      <g fill="none" stroke="#12303D" stroke-width="9" stroke-linecap="round">
        <line v-for="(w, i) in winds" :key="i" :x1="w.x1" :y1="w.y" :x2="w.x2" :y2="w.y" marker-end="url(#s82-hk)" />
      </g>
      <g class="s82-kelvin" :class="{ on: $clicks >= 1 }" :style="{ '--from': kelvinFrom + 'px' }">
        <ellipse :cx="kelvin.x" :cy="kelvin.y" :rx="kelvin.rx" ry="17" fill="#1B4A86" fill-opacity="0.9" />
        <ellipse :cx="kelvin.x" :cy="kelvin.y" :rx="kelvin.rx * 0.6" ry="7" fill="#0E2E57" />
      </g>
      <g class="s82-turn" :class="{ on: $clicks >= 2 }">
        <path :d="coastPath" pathLength="1" class="s82-turn-line" fill="none" stroke="#2F74C0" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" />
        <path :d="coastHead" class="s82-turn-head" fill="none" stroke="#2F74C0" stroke-width="12" stroke-linecap="round" marker-end="url(#s82-hb)" />
      </g>
      <circle :cx="phuket.x" :cy="phuket.y" r="12" fill="#2F74C0" class="s82-pulse" :class="{ on: $clicks >= 2 }" />
      <circle :cx="phuket.x" :cy="phuket.y" r="10" fill="#2F74C0" stroke="#FFFFFF" stroke-width="4" />
    </svg>
    <div class="s82-lab big andaman" :style="at(12.6, 90.6)">ทะเลอันดามัน</div>
    <div class="s82-lab big gulf" :style="at(11.0, 102.0)">อ่าวไทย</div>
    <div class="s82-lab" :style="at(8.9, 97.0)">ภูเก็ต</div>
    <div class="s82-lab" :style="at(-1.0, 100.6)">สุมาตรา</div>
    <div class="s82-lab" :style="at(-6.9, 108.2)">ชวา</div>
    <div class="s82-lab" :style="at(1.6, 112.6)">บอร์เนียว</div>
    <div class="s82-lab muted" :style="at(6.0, 87.0)">มหาสมุทรอินเดีย</div>
    <div class="s82-lab muted" :style="at(-1.0, 85.0)">ศูนย์สูตร</div>
    <div class="s82-lab big" :style="at(9.6, 128.0)">แปซิฟิก</div>
    <div class="s82-nino" :style="at(3.6, 126.6)">เอลนีโญ</div>
    <div class="bubble s82-air-label" :style="at(13.2, 114.2)">ผลของเอลนีโญมาทางลม<br><small>เปลี่ยนการไหลเวียนของอากาศ ไม่ได้ส่งน้ำทะเลมาเอง</small></div>
    <div class="s82-lab strong s82-wind-lab" :style="at(-7.6, 88.6)">ลมตะวันออกผิดปกติ<small>พัดไปทางตะวันตก ←</small></div>
    <div class="s82-kel-label" :class="{ show: $clicks >= 1 }" :style="at(3.2, 83.2)"><div class="k1">คลื่นเคลวิน</div><div class="k2">ดูดน้ำขึ้น → ผิวน้ำต่ำ</div><div class="k3">เคลื่อนไปทางตะวันออก →</div></div>
    <div class="bubble s82-phuket-label" :class="{ show: $clicks >= 2 }" :style="at(6.9, 99.5)">ระดับน้ำภูเก็ตลด</div>
    <div class="pill diag s82-schem">แผนที่จริง ลูกศรเป็นแผนภาพ</div>
  </div>
</div>
<script setup>
// พิกัดภูมิศาสตร์ → พิกเซลของรูปพื้น map_s82.png (PlateCarree · ต้องตรงกับ MAPS["s82"] ใน tools/make_basemap.py)
const LON0 = 80, LON1 = 132, LAT0 = -10, LAT1 = 16, W = 1600, H = 800
const px = (lat, lon) => ({ x: (lon - LON0) / (LON1 - LON0) * W, y: (LAT1 - lat) / (LAT1 - LAT0) * H })
const at = (lat, lon) => { const p = px(lat, lon); return { left: `${p.x}px`, top: `${p.y}px` } }
// เส้นโค้งเรียบผ่านจุด (Catmull-Rom → Bézier)
const smooth = (pts) => {
  const p = pts.map(([la, lo]) => px(la, lo))
  let d = `M${p[0].x},${p[0].y}`
  for (let i = 0; i !== p.length - 1; i++) {  // ไม่ใช้เครื่องหมายน้อยกว่า: markdown อ่านเป็นแท็ก HTML
    const a = p[i - 1] ?? p[i], b = p[i], c = p[i + 1], e = p[i + 2] ?? c
    d += ` C${b.x + (c.x - a.x) / 6},${b.y + (c.y - a.y) / 6} ${c.x - (e.x - b.x) / 6},${c.y - (e.y - b.y) / 6} ${c.x},${c.y}`
  }
  return d
}
const phuket = px(7.83, 98.42)                       // เกาะตะเภาน้อย (stations.ktn_latlon)
const andaman = px(10.8, 95.6)                       // ทะเลอันดามัน ≈ 92–98.5°E · 5.5–16°N
const gulf = px(9.8, 101.9)                          // อ่าวไทย ≈ 99.5–104°E · 6–13.5°N
const airArc = smooth([[4.0, 125.4], [10.0, 116.0], [6.5, 104.0], [-2.6, 97.6]])   // จบเหนือทะเลหน้าสุมาตรา ตรงลมลูกแรก
// ลมผิดปกติพัดไปทางตะวันตก (ลมตะวันออก) นอกฝั่งสุมาตรา–ชวา
const winds = [[-3.2, 97.0, 87.5], [-6.0, 101.5, 91.0], [-9.3, 112.0, 101.0]]
  .map(([la, from, to]) => ({ y: px(la, from).y, x1: px(la, from).x, x2: px(la, to).x }))
// แอ่งน้ำต่ำพักที่ศูนย์สูตรหน้าสุมาตรา (ปลายตะวันออก ≈ 98°E) · วิ่งมาจาก 85°E
const kelvin = { ...px(0, 93.6), rx: (4.4 / (LON1 - LON0)) * W }
const kelvinFrom = px(0, 85).x - px(0, 93.6).x
// คลื่นเคลวินชายฝั่ง: เลียบฝั่งตะวันตกของสุมาตราขึ้นเหนือ อ้อมปลายเกาะ แล้วเข้าอันดามันถึงภูเก็ต
const coast = [[0.2, 98.4], [1.8, 97.4], [3.6, 96.1], [5.3, 95.0], [6.4, 95.6], [7.3, 97.2], [7.75, 98.05]]
const coastPath = smooth(coast)
const coastHead = smooth(coast.slice(-2))
</script>

<style>
/* ขั้น 0 = เอลนีโญ → อากาศ → ลมตะวันออก · 1 = คลื่นเคลวินวิ่งไปตะวันออก · 2 = เลี้ยวขึ้นเหนือ ภูเก็ตน้ำลด · 3 = ฟองหลักฐาน
   ห้ามเว้นบรรทัดว่างในบล็อก HTML ด้านบน */
/* พื้นการ์ด = สีทะเลของแผนที่ → ไม่มีกรอบขาวรอบรูป (ผู้ใช้ 10-14) · แผนที่ขยายให้สูงเต็มการ์ด */
.s82-card { position: relative; flex: 1 1 auto; min-height: 0; padding: 0; overflow: hidden; background: #EEF5F9; }
.s82-box { position: absolute; left: 50%; top: 0; width: 1600px; height: 800px; transform: translateX(-50%) scale(1.045); transform-origin: 50% 0; }
.s82-map, .s82-svg { position: absolute; left: 0; top: 0; width: 1600px; height: 800px; display: block; }
/* ขอบซ้าย/ขวาของแผนที่จางเข้าสีทะเล ไม่ให้แผ่นดินขาดเป็นเส้นตรง */
.s82-box::before { content: ''; position: absolute; inset: 0; z-index: 1; pointer-events: none;
  background: linear-gradient(90deg, #EEF5F9, rgba(238,245,249,0) 70px, rgba(238,245,249,0) calc(100% - 70px), #EEF5F9); }
.s82-lab { position: absolute; z-index: 2; transform: translate(-50%, -50%); white-space: nowrap; font-size: 24px; color: var(--ink-2); }
.s82-lab.big { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 36px; color: var(--ink); }
.s82-lab.andaman { color: var(--andaman); }
.s82-lab.gulf { color: #A85A12; opacity: 0.45; }
.s82-lab.muted { color: var(--ink-3); font-size: 22px; }
.s82-lab.strong { font-weight: 600; color: var(--ink); font-size: 26px; }
.s82-nino { position: absolute; transform: translate(-50%, -50%); padding: 8px 26px; background: #FFFFFF; border: 4px solid var(--ink);
  border-radius: 14px; font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 34px; color: var(--ink); white-space: nowrap; }
.s82-air-label { position: absolute; transform: translate(-50%, -50%); font-size: 24px; white-space: nowrap; text-align: center; line-height: 1.35; }
.s82-air-label small { font-size: 20px; opacity: 0.85; }
.s82-air { transition: opacity 0.6s; }
.s82-air.dim { opacity: 0.35; }
.s82-kelvin { opacity: 0; transform: translateX(var(--from)); }
.s82-kelvin.on { opacity: 1; animation: s82-travel 2.4s ease-in-out forwards; }
@keyframes s82-travel { from { transform: translateX(var(--from)); } to { transform: translateX(0); } }
.s82-kel-label { position: absolute; transform: translate(0, -50%); opacity: 0; transition: opacity 0.5s 0.6s; }
.s82-kel-label.show { opacity: 1; }
.s82-kel-label .k1 { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 32px; color: #1B4A86; line-height: 1.2; }
.s82-kel-label .k2 { font-size: 24px; color: var(--ink-2); }
/* ทิศ (ผู้ใช้ 10-14): ลมพัดไปตะวันตก แต่คลื่นเคลวินที่ศูนย์สูตรเคลื่อนได้ทางเดียวคือไปตะวันออก — บอกบนแผนที่ให้ชัด */
.s82-kel-label .k3 { font-size: 24px; font-weight: 600; color: #1B4A86; }
.s82-wind-lab { display: flex; flex-direction: column; align-items: center; line-height: 1.25; }
.s82-wind-lab small { font-size: 22px; font-weight: 400; color: var(--ink-2); }
.s82-turn-line { stroke-dasharray: 1; stroke-dashoffset: 1; }
.s82-turn.on .s82-turn-line { stroke-dashoffset: 0; transition: stroke-dashoffset 1.6s ease-in-out; }
.s82-turn-head { opacity: 0; }
.s82-turn.on .s82-turn-head { opacity: 1; transition: opacity 0.3s 1.5s; }
.s82-pulse { opacity: 0; transform-box: fill-box; transform-origin: 50% 50%; }
.s82-pulse.on { animation: s82-ping 1.6s ease-out infinite 1.4s; }
@keyframes s82-ping { 0% { opacity: 0.9; transform: scale(1); } 100% { opacity: 0; transform: scale(3.4); } }
.s82-phuket-label { position: absolute; transform: translate(0, -50%); font-size: 26px; background: var(--andaman); white-space: nowrap; opacity: 0; transition: opacity 0.5s 1.4s; }
.s82-phuket-label.show { opacity: 1; }
.s82-schem { position: absolute; left: 70px; top: 36px; font-size: 20px; }
</style>

<!--
ผลทาง DSP นี้มีคำอธิบายทางกายภาพรองรับ ปีเอลนีโญการไหลเวียนของอากาศย้าย เกิดลมตะวันออกผิดปกตินอกชวาและสุมาตรา เป็นลมแบบเดียวกับที่ทำให้เกิด IOD บวก
สัญญาณเอลนีโญจึงมาถึงอันดามันทางอากาศ ไม่ได้มาทางทะเล
ลมนี้สร้างคลื่นเคลวินที่ดูดน้ำขึ้นจากข้างล่าง ผิวน้ำจึงต่ำลงตลอดทางที่มันวิ่งไปตามศูนย์สูตร
พอชนสุมาตรา คลื่นเลี้ยวขึ้นเหนือเลียบชายฝั่งเข้าอันดามัน ระดับน้ำภูเก็ตจึงลด

ถ้าถูกถาม:
- ในแบบจำลอง ลมที่ศูนย์สูตรอย่างเดียวอธิบายระดับน้ำขอบตะวันออกของอ่าวเบงกอลได้ที่ r 0.95 ส่วนลมท้องถิ่นได้แค่ 0.28
- เวลาเดินทางจากสุมาตราถึงภูเก็ตน่าจะไม่ถึงสองสัปดาห์ ที่ความละเอียดรายเดือนจึงไม่เห็นความหน่วงจากการเดินทาง (อนุมาน)
- ลมตะวันออกคือลมที่พัดจากตะวันออกไปตะวันตก มันดันน้ำผิวหน้าออกจากฝั่งสุมาตรา ส่วนคลื่นเคลวินไม่ใช่น้ำที่ไหลกลับ แต่เป็นรูปแบบของผิวน้ำต่ำที่เคลื่อนที่ไป และที่ศูนย์สูตรคลื่นนี้เคลื่อนได้ทางเดียวคือไปทางตะวันออก
- ค่า r ไม่ได้คำนวณในโครงงานนี้ มาจากแบบจำลองมหาสมุทรของ Han and Webster ที่รันโดยใส่ลมเฉพาะบางส่วน แล้ววัดสหสัมพันธ์ว่าระดับน้ำที่ได้ตรงกับผลของแบบจำลองที่ใส่ลมครบแค่ไหน
-->

---
id: SQ08_S030
clicks: 3
layout: page
seq: '8'
section: กลไกทางกายภาพ
page: 21
kinds: [ข้อมูลจริง, แผนภาพ]
---

# การไม่ปรากฏความสัมพันธ์ในอ่าวไทย: แอ่งตื้น ฤดูกาลเด่น และอยู่นอกเส้นทางคลื่น

<div class="card s3-card" :class="{ sea: $clicks >= 3 }">
  <div class="s3-stage s3-a" :class="{ gone: $clicks >= 2 }">
    <svg viewBox="0 0 1678 610" width="1678" height="610" class="s3-svg">
      <defs>
        <clipPath id="s3-basin"><path d="M868,150 L905,230 L950,300 L1520,300 L1560,235 L1590,150 Z" /></clipPath>
        <marker id="s3-wh" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#12303D" /></marker>
        <marker id="s3-dim" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,10 L5,0 L10,10 Z" fill="#3B5866" /></marker>
      </defs>
      <rect x="0" y="190" width="800" height="420" fill="#2F74C0" fill-opacity="0.28" />
      <g clip-path="url(#s3-basin)">
        <g class="s3-water" :class="{ run: $clicks >= 1 }">
          <rect x="840" y="190" width="780" height="200" fill="#D9822B" fill-opacity="0.34" />
          <line x1="840" y1="190" x2="1620" y2="190" stroke="#D9822B" stroke-width="5" />
        </g>
      </g>
      <path d="M0,610 L0,548 C200,548 380,542 520,472 C620,422 690,332 745,228 L772,150 L868,150 L905,230 L950,300 L1520,300 L1560,235 L1590,150 L1678,150 L1678,610 Z" fill="#CFC9BC" />
      <path d="M0,548 C200,548 380,542 520,472 C620,422 690,332 745,228 L772,150 L868,150 L905,230 L950,300 L1520,300 L1560,235 L1590,150 L1678,150" fill="none" stroke="#8C8576" stroke-width="4" stroke-linejoin="round" />
      <line x1="0" y1="190" x2="752" y2="190" stroke="#2F74C0" stroke-width="5" />
      <line x1="330" y1="200" x2="330" y2="538" stroke="#3B5866" stroke-width="3" marker-start="url(#s3-dim)" marker-end="url(#s3-dim)" />
      <text x="350" y="380" class="s3-t2">ลึก</text>
      <text x="10" y="150" class="s3-t2">← เปิดสู่มหาสมุทรอินเดีย</text>
      <text x="40" y="250" class="s3-big andaman">ทะเลอันดามัน</text>
      <text x="690" y="118" class="s3-t3">คาบสมุทร</text>
      <g class="s3-wind" :class="{ run: $clicks >= 1 }">
        <g class="w-r" fill="none" stroke="#12303D" stroke-width="7" stroke-linecap="round">
          <line x1="1010" y1="70" x2="1430" y2="70" marker-end="url(#s3-wh)" />
          <line x1="1060" y1="105" x2="1380" y2="105" marker-end="url(#s3-wh)" />
        </g>
        <g class="w-l" fill="none" stroke="#12303D" stroke-width="7" stroke-linecap="round">
          <line x1="1430" y1="70" x2="1010" y2="70" marker-end="url(#s3-wh)" />
          <line x1="1380" y1="105" x2="1060" y2="105" marker-end="url(#s3-wh)" />
        </g>
      </g>
      <line x1="1250" y1="198" x2="1250" y2="296" stroke="#12303D" stroke-width="3" marker-start="url(#s3-dim)" marker-end="url(#s3-dim)" />
    </svg>
    <div class="s3-pill-gulf">อ่าวไทย แอ่งตื้น</div>
    <div class="s3-depth" :class="{ off: $clicks >= 1 }"><span class="cap">ลึกเฉลี่ย</span> <span class="num">≈ <Fact id="gulf.depth_m" /> ม.</span></div>
    <div class="s3-wind-label" :class="{ show: $clicks >= 1 }">ลมท้องถิ่นเปลี่ยนทิศ</div>
    <div class="bubble s3-exag">ความลึกขยายเกินจริง</div>
    <div class="bubble s3-cap" :class="{ show: $clicks >= 1 }">ลมเปลี่ยนทิศ → น้ำเอียงตามทันที → กลับคืนทันที</div>
  </div>
  <div class="s3-stage s3-c" :class="{ show: $clicks === 2 }">
    <div class="s3-c-title">ฤดูกาลกลบทุกอย่าง</div>
    <div class="s3-c-scale">ความสูงของการแกว่ง สเกลเดียวกัน</div>
    <div class="s3-c-row">
      <div class="s3-c-lab">วงรอบฤดูกาลที่เราวัดได้</div>
      <div class="s3-c-track"><div class="s3-c-bar season"></div><span class="s3-c-val gulf-t">±<Fact id="season.amp_gulf_mm" :digits="0" /> มม.</span></div>
      <div class="s3-c-note">มรสุมดันน้ำเข้าแอ่ง ดาวเทียม GRACE วัดได้ราว <Fact id="gulf.season_grace_mm" /> มม.</div>
    </div>
    <div class="s3-c-row">
      <div class="s3-c-lab">สัญญาณเอลนีโญ</div>
      <div class="s3-c-track"><div class="s3-c-bar enso"></div><div class="s3-c-bar enso-range"></div><span class="s3-c-val">±<Fact id="gulf.enso_mm" :index="0" />–<Fact id="gulf.enso_mm" :index="1" /> มม.</span></div>
      <div class="s3-c-note">ชายฝั่งตะวันออกของมาเลเซีย ใกล้ ๆ กัน (ค่าเฉลี่ยรายปี)</div>
    </div>
    <div class="s3-c-share"><span class="num"><Fact id="season.share_gulf" :digits="0" />%</span><span class="cap">ของความแปรปรวนในอ่าวไทยคือฤดูกาล</span></div>
  </div>
  <div class="s3-stage s3-b" :class="{ show: $clicks >= 3 }">
    <div class="s3-mapbox">
      <img src="/plots/map_s83.png" class="s3-map" />
      <svg viewBox="0 0 832 608" width="832" height="608" class="s3-mapsvg">
        <defs>
          <marker id="s3-mb" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="3.6" markerHeight="3.6" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#2F74C0" /></marker>
          <marker id="s3-mg" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#6B7B85" /></marker>
          <marker id="s3-mk" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#12303D" /></marker>
        </defs>
        <ellipse :cx="m.andaman.x" :cy="m.andaman.y" rx="80" ry="150" fill="#2F74C0" fill-opacity="0.13" />
        <ellipse :cx="m.gulf.x" :cy="m.gulf.y" rx="70" ry="110" fill="#D9822B" fill-opacity="0.2" />
        <path :d="m.wave" fill="none" stroke="#2F74C0" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#s3-mb)" />
        <path :d="m.blocked" fill="none" stroke="#6B7B85" stroke-width="5" stroke-dasharray="3 10" stroke-linecap="round" marker-end="url(#s3-mg)" />
        <circle :cx="m.cross.x" :cy="m.cross.y" r="17" fill="#FFFFFF" stroke="#6B7B85" stroke-width="3.5" />
        <path :d="`M${m.cross.x - 8},${m.cross.y - 8} L${m.cross.x + 8},${m.cross.y + 8} M${m.cross.x + 8},${m.cross.y - 8} L${m.cross.x - 8},${m.cross.y + 8}`" stroke="#44515C" stroke-width="4.5" stroke-linecap="round" />
        <path :d="m.pacific" fill="none" stroke="#12303D" stroke-width="6" stroke-linecap="round" marker-end="url(#s3-mk)" />
        <circle :cx="m.phuket.x" :cy="m.phuket.y" r="9" fill="#2F74C0" stroke="#FFFFFF" stroke-width="3.5" />
        <circle :cx="m.kolak.x" :cy="m.kolak.y" r="9" fill="#D9822B" stroke="#FFFFFF" stroke-width="3.5" />
      </svg>
      <div class="s3-ml andaman big" :style="m.at(11.8, 95.0)">ทะเล<br>อันดามัน</div>
      <div class="s3-ml gulf big" :style="m.at(9.4, 102.0)">อ่าวไทย</div>
      <div class="s3-ml" :style="m.at(9.0, 113.0)">ทะเลจีนใต้</div>
      <div class="s3-ml chip" :style="m.at(15.0, 114.3)">จากแปซิฟิก</div>
      <div class="s3-ml chip" :style="m.at(0.6, 106.6)">ช่องแคบมะละกา (ตื้น)</div>
      <div class="s3-ml muted" :style="m.at(-0.9, 95.4)">ศูนย์สูตร</div>
    </div>
    <div class="s3-side">
      <div class="pill diag s3-real">แผนที่จริง ลูกศรเป็นแผนภาพ</div>
      <div class="s3-key"><i class="k-blue"></i><div><b>คลื่นจากศูนย์สูตร</b><br>เลียบสุมาตราเข้าอันดามัน ไม่เข้าอ่าว</div></div>
      <div class="s3-key"><i class="k-grey"></i><div><b>ช่องแคบมะละกาตื้นเกินไป</b><br>ส่งคลื่นจากอันดามันเข้าอ่าวไม่ได้</div></div>
      <div class="s3-key"><i class="k-ink"></i><div><b>สัญญาณทางทะเลจากแปซิฟิก</b><br>เข้าทะเลจีนใต้ทางช่องแคบลูซอน</div></div>
    </div>
  </div>
</div>
<div class="s3-chips">
  <span class="s3-chip" :class="{ on: $clicks >= 0 }">แอ่งตื้น</span>
  <span class="s3-chip" :class="{ on: $clicks >= 1 }">ไม่มีความจำ</span>
  <span class="s3-chip" :class="{ on: $clicks >= 2 }">ฤดูกาลกลบ</span>
  <span class="s3-chip" :class="{ on: $clicks >= 3 }">อยู่นอกเส้นทางคลื่น</span>
</div>
<script setup>
// แผนที่พื้น /plots/map_s83.png จาก tools/make_basemap.py (PlateCarree · lon 92–118 · lat −3–16 · 832×608)
const LON0 = 92, LON1 = 118, LAT0 = -3, LAT1 = 16, W = 832, H = 608
const px = (lat, lon) => ({ x: (lon - LON0) / (LON1 - LON0) * W, y: (LAT1 - lat) / (LAT1 - LAT0) * H })
const smooth = (pts) => {
  const p = pts.map(([la, lo]) => px(la, lo))
  let d = `M${p[0].x},${p[0].y}`
  for (let i = 0; i !== p.length - 1; i++) {
    const a = p[i - 1] ?? p[i], b = p[i], c = p[i + 1], e = p[i + 2] ?? c
    d += ` C${b.x + (c.x - a.x) / 6},${b.y + (c.y - a.y) / 6} ${c.x - (e.x - b.x) / 6},${c.y - (e.y - b.y) / 6} ${c.x},${c.y}`
  }
  return d
}
const m = {
  at: (lat, lon) => { const q = px(lat, lon); return { left: `${q.x}px`, top: `${q.y}px` } },
  andaman: px(11.0, 95.8), gulf: px(9.8, 101.9),
  phuket: px(7.833, 98.433), kolak: px(11.8, 99.817),      // stations.ktn_latlon · stations.klk_latlon
  // คลื่นเคลวินจากศูนย์สูตร → เลียบฝั่งตะวันตกสุมาตรา → อันดามัน → ภูเก็ต
  wave: smooth([[0, 92.4], [0, 96.6], [0.4, 98.3], [1.8, 97.4], [3.6, 96.1], [5.3, 95.0], [6.4, 95.6], [7.3, 97.2], [7.7, 98.0]]),
  // ทางที่ไปไม่ได้: ลงช่องแคบมะละกา (ตื้น) อ้อมปลายคาบสมุทรเข้าอ่าว
  blocked: smooth([[6.2, 98.9], [4.2, 99.9], [2.6, 101.4], [1.2, 103.6], [3.4, 104.9], [7.0, 103.4], [8.6, 102.4]]),
  cross: px(2.6, 101.4),
  // สัญญาณจากแปซิฟิกเข้าทะเลจีนใต้ทางช่องแคบลูซอน (ลูซอนอยู่นอกขอบขวาของแผนที่ · ลูกศรเข้ามาจากขอบ)
  pacific: smooth([[15.6, 118.0], [14.2, 115.0], [12.0, 112.6]]),
}
</script>

<style>
/* ขั้น 1 = ภาพตัดขวาง · ขั้น 2 = ลมเปลี่ยนทิศ น้ำเอียงตามแล้วกลับ (วนซ้ำ) + r · ขั้น 3 = ฤดูกาลกลบ (แท่งสเกลเดียวกัน) · ขั้น 4 = แผนที่ย่อ
   ห้ามเว้นบรรทัดว่างในบล็อก HTML ด้านบน (markdown จะมองเป็นโค้ด) */
.s3-card { position: relative; flex: 1 1 auto; min-height: 0; padding: 0; overflow: hidden; transition: background 0.5s; }
/* ฉากแผนที่: พื้นการ์ด = สีทะเลของแผนที่ → ไม่มีกรอบขาวรอบรูป (ผู้ใช้ 10-14) */
.s3-card.sea { background: #EEF5F9; }
.s3-stage { position: absolute; left: 36px; top: 20px; width: 1678px; height: 610px; transition: opacity 0.5s; }
.s3-a.gone { opacity: 0; }
.s3-c { opacity: 0; }
.s3-c.show { opacity: 1; }
.s3-b { opacity: 0; }
.s3-b.show { opacity: 1; }
.s3-svg { display: block; }
.s3-big { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 40px; fill: var(--ink); }
.s3-big.andaman { fill: var(--andaman); }
.s3-big.gulf-d { fill: #A85A12; }
.s3-t2 { font-family: 'Anuphan', sans-serif; font-size: 24px; fill: var(--ink-2); }
.s3-t2.andaman { fill: var(--andaman); font-weight: 600; }
.s3-t3 { font-family: 'Anuphan', sans-serif; font-size: 22px; fill: var(--ink-2); }

/* น้ำอ่าวไทยเอียงตามลม แล้วกลับราบ (ไม่มีความจำ) */
.s3-water { transform-box: fill-box; transform-origin: 50% 50%; }
.s3-water.run { animation: s3-tilt 9s ease-in-out infinite; }
@keyframes s3-tilt {
  0% { transform: skewY(0deg); } 7% { transform: skewY(-4deg); } 36% { transform: skewY(-4deg); }
  46% { transform: skewY(4deg); } 74% { transform: skewY(4deg); } 84% { transform: skewY(0deg); } 100% { transform: skewY(0deg); }
}
.s3-wind .w-r, .s3-wind .w-l { opacity: 0; }
.s3-wind.run .w-r { animation: s3-wr 9s ease-in-out infinite; }
.s3-wind.run .w-l { animation: s3-wl 9s ease-in-out infinite; }
@keyframes s3-wr { 0% { opacity: 0; } 4% { opacity: 1; } 36% { opacity: 1; } 40% { opacity: 0; } 100% { opacity: 0; } }
@keyframes s3-wl { 0%, 42% { opacity: 0; } 46% { opacity: 1; } 74% { opacity: 1; } 78% { opacity: 0; } 100% { opacity: 0; } }

.s3-pill-gulf { position: absolute; left: 1440px; top: 28px; background: #FBE6CF; color: #8A4A0A; border: 3px solid var(--gulf);
  border-radius: 999px; padding: 4px 22px; font-size: 26px; font-weight: 600; }
.s3-depth { position: absolute; left: 1010px; top: 318px; width: 480px; text-align: center; color: var(--ink); }
.s3-depth .cap { font-size: 26px; color: var(--ink-2); }
.s3-depth .num { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 62px; line-height: 1.2; }
.s3-depth { transition: opacity 0.4s; }
.s3-depth.off { opacity: 0; }

/* ฉากฤดูกาล: 1 มม. = 4 px · ฤดูกาล 213 มม. = 852 px · เอลนีโญ 30–50 มม. = 120–200 px */
.s3-c-title { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 44px; color: var(--ink); margin: 16px 0 0 10px; }
.s3-c-scale { font-size: 24px; color: var(--ink-3); margin: 0 0 40px 10px; }
.s3-c-row { display: grid; grid-template-columns: 330px 1fr; column-gap: 24px; row-gap: 4px; align-items: center; margin: 0 0 56px 10px; }
.s3-c-lab { font-size: 28px; font-weight: 600; color: var(--ink); }
.s3-c-track { position: relative; height: 72px; display: flex; align-items: center; gap: 18px; }
.s3-c-bar { height: 64px; border-radius: 8px; flex: none; }
.s3-c-bar.season { width: 852px; background: var(--gulf); }
.s3-c-bar.enso { width: 120px; background: var(--nino); }
.s3-c-bar.enso-range { width: 80px; margin-left: -18px; background: var(--nino); opacity: 0.35; border-radius: 0 8px 8px 0; }
.s3-c-val { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 40px; color: var(--ink); }
.s3-c-val.gulf-t { color: #A85A12; }
.s3-c-note { grid-column: 2; font-size: 24px; color: var(--ink-2); }
.s3-c-share { margin: 6px 0 0 10px; display: flex; align-items: baseline; gap: 24px; }
.s3-c-share .num { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 84px; line-height: 1.05; color: #A85A12; }
.s3-c-share .cap { font-size: 24px; color: var(--ink-2); }
.s3-wind-label { position: absolute; left: 1010px; top: 12px; font-size: 24px; color: var(--ink); font-weight: 600; opacity: 0; transition: opacity 0.4s; }
.s3-wind-label.show { opacity: 1; }
.s3-exag { position: absolute; left: 960px; top: 536px; font-size: 24px; padding: 8px 22px; }
.s3-cap { position: absolute; left: 960px; top: 450px; width: 690px; font-size: 26px; opacity: 0; transition: opacity 0.4s; }
.s3-cap.show { opacity: 1; }

/* แผนที่ขยายให้สูงเต็มการ์ด ชิดขอบซ้าย (การ์ดสูง ≈ 760 = 608 × 1.25) — ไม่มีขอบรูปลอยกลางการ์ด */
.s3-mapbox { position: absolute; left: -36px; top: -20px; width: 832px; height: 608px; transform: scale(1.25); transform-origin: 0 0; }
.s3-map, .s3-mapsvg { position: absolute; left: 0; top: 0; width: 832px; height: 608px; }
/* ขอบขวาของแผนที่จางเข้าสีทะเล ไม่ให้แผ่นดินขาดเป็นเส้นตรง */
.s3-mapbox::after { content: ''; position: absolute; right: 0; top: 0; width: 70px; height: 100%; background: linear-gradient(90deg, rgba(238,245,249,0), #EEF5F9); }
.s3-ml { position: absolute; transform: translate(-50%, -50%); white-space: nowrap; font-size: 22px; color: var(--ink-2); text-align: center; line-height: 1.15; }
.s3-ml.big { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 28px; }
.s3-ml.andaman { color: var(--andaman); }
.s3-ml.gulf { color: #A85A12; }
.s3-ml.muted { color: var(--ink-3); font-size: 20px; }
.s3-ml.chip { background: rgba(255, 255, 255, 0.88); border-radius: 8px; padding: 1px 10px; font-size: 20px; color: var(--ink); }
.s3-side { position: absolute; left: 1050px; top: 30px; width: 610px; display: flex; flex-direction: column; gap: 26px; }
.s3-real { align-self: flex-start; font-size: 20px; }
.s3-key { display: flex; align-items: flex-start; gap: 20px; font-size: 26px; line-height: 1.4; color: var(--ink-2); }
.s3-key b { color: var(--ink); }
.s3-key i { flex: none; width: 64px; height: 8px; border-radius: 4px; margin-top: 18px; }
.s3-key .k-blue { background: #2F74C0; }
.s3-key .k-grey { height: 6px; background: repeating-linear-gradient(90deg, #6B7B85 0 4px, transparent 4px 13px); }
.s3-key .k-ink { background: #12303D; }
.s3-msg { align-self: flex-start; font-size: 28px; padding: 16px 28px; margin-top: 6px; }

.s3-chips { display: flex; gap: 18px; flex: 0 0 auto; }
.s3-chip { font-size: 26px; padding: 6px 28px; border-radius: 999px; background: #FFFFFF; color: var(--ink-3); border: 2px solid #D4E0E5; transition: all 0.4s; }
.s3-chip.on { background: var(--ink); color: #FFFFFF; border-color: var(--ink); }
</style>

<!--
ส่วนอ่าวไทยเป็นแอ่งตื้น ลึกเฉลี่ยราว 40 เมตร
ระดับน้ำทั้งแอ่งเอียงตามลมท้องถิ่นแทบทันที และกลับคืนทันทีที่ลมเปลี่ยน แอ่งนี้จึงไม่มีความจำ ไม่สะสมสัญญาณระหว่างปี
และฤดูกาลกลบทุกอย่าง มรสุมดันน้ำเข้าแอ่งเป็นวงรอบปีละราว 200 มิลลิเมตร ตรงกับที่เราวัดได้ 213 มิลลิเมตร คิดเป็น 81 เปอร์เซ็นต์ของความแปรปรวน
(ตัดได้) ส่วนสัญญาณเอลนีโญที่ชายฝั่งตะวันออกของมาเลเซียใกล้ ๆ กันมีแค่ราว 30 ถึง 50 มิลลิเมตร เล็กพอ ๆ กับที่ฤดูกาลแกว่งเองปีต่อปี (งานเดียว)
และอ่าวไทยอยู่นอกเส้นทางของคลื่นจากศูนย์สูตร ช่องแคบมะละกาก็ตื้นเกินจะส่งคลื่นจากอันดามันเข้ามา

ถ้าถูกถาม:
- ระดับน้ำทั้งแอ่งตามลมท้องถิ่นด้วยสหสัมพันธ์ถึง 0.84 โดยไม่มีความหน่วง ตามงานของ Anutaliya
- หน่วยงานไทยอธิบายน้ำทะเลหนุนในอ่าวไทยว่าเป็นเหตุการณ์ปลายปีจากน้ำเกิด มรสุม และน้ำท่า ไม่เคยโยงกับ ENSO (งานเดียว)
- 213 มิลลิเมตรคือแอมพลิจูดของคลื่นคาบหนึ่งปีที่ fit กับระดับน้ำรายเดือนของเกาะหลัก ระดับน้ำขึ้นลงจากค่าเฉลี่ยราวบวกลบ 213 มิลลิเมตรในหนึ่งปี
-->

---
id: SQ08_S050
clicks: 2
layout: page
seq: '8'
section: กลไกทางกายภาพ
page: 22
kinds: [ข้อมูลจริง]
---

# ทิศและความล่าช้าของเฟสสอดคล้องกับกลไกทั้งสี่ดัชนี

<!--
  ภาษาธรรมดาแทนหน้าปัด: แถบอธิบาย 3 คำ + ตารางทิศและความสัมพันธ์ + การ์ด "ตัวอย่างการคำนวณความสัมพันธ์" (ผู้ใช้ 10-15 เปลี่ยนชื่อ)
  (ผู้ใช้ 10-15: ตัดคอลัมน์ "ตรงกับกลไก" · "จังหวะ" → "ความสัมพันธ์" · ไม่ใช้ "~" · มีภาพอธิบายที่มาของ 3 เดือน)
  คลิก 0 = แถบ + ชื่อดัชนี · 1 = ทิศที่วัดได้ · 2 = คอลัมน์ความสัมพันธ์ + การ์ดอธิบาย
  การ์ดอธิบาย: สูตรเดียวกับ scripts/make_infographics.py fig12_phase (C96)
    มุมเฟสห่างจากทิศหลักกี่องศา ÷ 360 × คาบกลาง (เดือน) = ความล่าช้า · คลื่นในภาพวาดจากคาบและความล่าช้าจริงใน facts.json
  ช่องที่ยังไม่เปิดใช้ opacity 0 เพื่อให้ตารางไม่ขยับ
-->
<div class="s85-strip">
  <div class="s85-tile" v-for="t in tiles" :key="t.name">
    <svg viewBox="0 0 220 100" class="s85-svg">
      <line x1="0" y1="50" x2="220" y2="50" class="s85-base" />
      <path :d="t.sea" class="s85-sea" />
      <path :d="t.idx" class="s85-idx" />
    </svg>
    <div class="s85-txt"><b>{{ t.name }}</b><span>{{ t.cap }}</span></div>
  </div>
</div>
<div class="s85-main">
  <div class="card s85-card">
    <div class="s85-row s85-head"><span>ดัชนี</span><span>เมื่อดัชนีขึ้น ระดับน้ำภูเก็ต…</span><span>ความสัมพันธ์</span></div>
    <div class="s85-row">
      <span class="s85-name" style="color: var(--nino)">Niño3.4</span>
      <span class="s85-guess" :class="{ on: $clicks >= 1 }">ลง (สวนทาง)</span>
      <span class="s85-lag" :class="{ on: $clicks >= 2 }">ระดับน้ำตามหลัง <b><Fact id="phase.nino34.lag_months" :absval="true" :digits="0" /> เดือน</b></span>
    </div>
    <div class="s85-row">
      <span class="s85-name" style="color: var(--andaman)">SOI</span>
      <span class="s85-guess" :class="{ on: $clicks >= 1 }">ขึ้น (ไปด้วยกัน)</span>
      <span class="s85-lag" :class="{ on: $clicks >= 2 }">ระดับน้ำตามหลัง <b><Fact id="phase.soi.lag_months" :absval="true" :digits="0" /> เดือน</b></span>
    </div>
    <div class="s85-row">
      <span class="s85-name" style="color: var(--dmi)">DMI</span>
      <span class="s85-guess" :class="{ on: $clicks >= 1 }">ลง (สวนทาง)</span>
      <span class="s85-lag" :class="{ on: $clicks >= 2 }">ระดับน้ำลดก่อน DMI สูงสุด <b><Fact id="phase.dmi.lag_months" :digits="0" /> เดือน</b></span>
    </div>
    <div class="s85-row">
      <span class="s85-name">WNPMI</span>
      <span class="s85-guess" :class="{ on: $clicks >= 1 }">ขึ้น (ไปด้วยกัน)</span>
      <span class="s85-lag" :class="{ on: $clicks >= 2 }">ระดับน้ำนำ <b><Fact id="phase.wnpmi.lag_months" :digits="0" /> เดือน</b><small>น่าจะเป็นผลตามของเอลนีโญ</small></span>
    </div>
  </div>
  <div class="card s85-why" :class="{ on: $clicks >= 2 }">
    <div class="s85-why-h">ตัวอย่างการคำนวณความสัมพันธ์ <em class="s85-sub">Niño3.4</em></div>
    <div class="s85-plot">
      <span class="s85-ytitle">ค่าสัมพัทธ์</span>
      <svg :viewBox="`0 0 ${W} ${H}`" :width="W" :height="H">
        <line :x1="X(T0)" :x2="X(T1)" :y1="Y(0)" :y2="Y(0)" class="s85-base" />
        <line :x1="X(T0)" :x2="X(T0)" :y1="Y(1.25)" :y2="Y(-1.25)" class="s85-axis" />
        <line :x1="X(T0)" :x2="X(T1)" :y1="Y(-1.25)" :y2="Y(-1.25)" class="s85-axis" />
        <g v-for="t in ticks" :key="t">
          <line :x1="X(t)" :x2="X(t)" :y1="Y(-1.25)" :y2="Y(-1.25) + 8" class="s85-axis" />
          <text :x="X(t)" :y="Y(-1.25) + 32" class="s85-tick">{{ t }}</text>
        </g>
        <!-- เส้นแนวตั้งที่ยอด Niño3.4 และที่ระดับน้ำต่ำสุด + วงเล็บความล่าช้า -->
        <line :x1="X(0)" :x2="X(0)" :y1="Y(1)" :y2="Y(1.5)" class="s85-mark" />
        <line :x1="X(lag)" :x2="X(lag)" :y1="Y(-1)" :y2="Y(1.5)" class="s85-mark" />
        <line :x1="X(0)" :x2="X(lag)" :y1="Y(1.5)" :y2="Y(1.5)" class="s85-brace" />
        <path :d="idxPath" class="s85-idx" />
        <path :d="seaPath" class="s85-sea" />
        <circle :cx="X(0)" :cy="Y(1)" r="7" fill="var(--ink-3)" />
        <circle :cx="X(lag)" :cy="Y(-1)" r="7" fill="var(--andaman)" />
      </svg>
      <span class="s85-gap" :style="{ left: (X(lag / 2)) + 'px', top: (Y(1.5) - 38) + 'px' }"><Fact id="phase.nino34.lag_months" :absval="true" :digits="1" /> เดือน</span>
      <span class="s85-pt" :style="{ left: (X(0) - 14) + 'px', top: (Y(1.5) - 14) + 'px', transform: 'translateX(-100%)' }">Niño3.4 สูงสุด</span>
      <span class="s85-pt sea" :style="{ left: (X(lag) + 10) + 'px', top: (Y(-1) - 56) + 'px' }">ระดับน้ำต่ำสุด</span>
      <span class="s85-xtitle">เวลา (เดือน)</span>
    </div>
    <div class="s85-key"><span><i class="dash"></i>Niño3.4</span><span><i class="solid"></i>ระดับน้ำภูเก็ต (สวนทางกับ Niño3.4)</span></div>
    <ol class="s85-steps">
      <li>มุมเฟส <b><Fact id="phase.nino34.theta" :digits="0" />°</b> ใกล้สวนทาง (<Lit v="180" c="C96" />°) ห่างไป <b><Fact id="phase.nino34.offset_deg" :absval="true" :digits="0" />°</b></li>
      <li><Fact id="phase.nino34.offset_deg" :absval="true" :digits="0" />° ÷ <Lit v="360" c="C96" />° × คาบ <Fact id="phase.nino34.period_months" :digits="0" /> เดือน = <b><Fact id="phase.nino34.lag_months" :absval="true" :digits="1" /> เดือน</b></li>
      <li>ปัดเป็นจำนวนเต็มได้ <b><Fact id="phase.nino34.lag_months" :absval="true" :digits="0" /> เดือน</b></li>
    </ol>
  </div>
</div>
<script setup>
import facts from './data/facts.json'   // path เทียบกับ deck/slides.md (หน้าถูกรวมเข้าไฟล์นั้น)
// เส้นจิ๋วของแต่ละกล่องคำอธิบาย: คลื่นไซน์ x = 0..220 · ดัชนี = เส้นประเทา · ระดับน้ำ = เส้นทึบสีอันดามัน
const wave = (phase, sign, amp = 34) => {
  const pts = []
  for (let x = 0; x <= 220; x += 4) pts.push(`${pts.length ? 'L' : 'M'}${x},${(50 - sign * amp * Math.sin((x / 220) * 4 * Math.PI - phase)).toFixed(1)}`)
  return pts.join(' ')
}
const tiles = [
  { name: 'ไปด้วยกัน', cap: 'ดัชนีขึ้น ระดับน้ำขึ้น', idx: wave(0, 1, 18), sea: wave(0, 1) },  // ดัชนีเล็กกว่า ไม่ให้ทับเส้นระดับน้ำจนมองไม่เห็น
  { name: 'สวนทาง', cap: 'ดัชนีขึ้น ระดับน้ำลง', idx: wave(0, 1), sea: wave(0, -1) },
  { name: 'ตามหลัง', cap: 'ระดับน้ำเปลี่ยนช้ากว่าดัชนีไม่กี่เดือน', idx: wave(0, 1), sea: wave(1.3, 1) },
]
// การ์ดอธิบาย: คลื่นคาบจริง (เดือน) · Niño3.4 ยอดที่ t = 0 · ระดับน้ำสวนทางและตามหลังเท่าความล่าช้าจริง
const P = facts['phase.nino34.period_months'].value
const lag = Math.abs(facts['phase.nino34.lag_months'].value)
const W = 640, H = 320, T0 = -9, T1 = 15          // ซูมรอบยอด ให้ช่วง 2.5 เดือนกว้างพอเห็น
const ticks = [-6, 0, 6, 12]
const X = (t) => 50 + (t - T0) / (T1 - T0) * (W - 70)
const Y = (v) => 160 - v * 80
const path = (f) => {
  let d = ''
  for (let t = T0; t <= T1 + 1e-9; t += 0.25) d += `${d ? 'L' : 'M'}${X(t).toFixed(1)},${Y(f(t)).toFixed(1)} `
  return d
}
const idxPath = path((t) => Math.cos((2 * Math.PI * t) / P))
const seaPath = path((t) => -Math.cos((2 * Math.PI * (t - lag)) / P))
</script>

<style>
.s85-strip { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.s85-tile { display: flex; align-items: center; gap: 22px; background: #fff; border-radius: var(--radius); box-shadow: var(--shadow); padding: 14px 24px; }
.s85-svg { width: 220px; flex: none; }
.s85-base { stroke: #DCE7EB; stroke-width: 2; }
.s85-idx { fill: none; stroke: var(--ink-3); stroke-width: 3.5; stroke-dasharray: 9 7; }
.s85-sea { fill: none; stroke: var(--andaman); stroke-width: 5; }
.s85-txt { display: flex; flex-direction: column; font-size: 24px; line-height: 1.3; color: var(--ink-2); }
.s85-txt b { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 34px; color: var(--ink); }

.s85-main { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 1fr 690px; gap: 24px; margin-top: 24px; }
.s85-card { padding: 10px 36px; display: flex; flex-direction: column; justify-content: center; }
.s85-row { display: grid; grid-template-columns: 190px 300px 1fr; column-gap: 20px; align-items: center; min-height: 118px; font-size: 28px; border-bottom: 1px solid #E8EFF2; color: var(--ink); }
.s85-row:last-child { border-bottom: none; }
.s85-head { min-height: 64px; font-size: 24px; color: var(--ink-3); border-bottom: 2px solid #DCE7EB; }
.s85-name { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 38px; }
.s85-guess, .s85-lag, .s85-why { opacity: 0; transition: opacity 0.5s; }
.s85-guess.on, .s85-lag.on, .s85-why.on { opacity: 1; }
.s85-lag { font-size: 27px; line-height: 1.35; }
.s85-lag b { font-weight: 600; }
.s85-lag small { display: block; font-size: 22px; color: var(--ink-3); }

.s85-why { padding: 22px 26px; display: flex; flex-direction: column; gap: 6px; }
.s85-why-h { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 30px; color: var(--ink); }
.s85-why-h .s85-sub { font-family: 'Anuphan', sans-serif; font-style: normal; font-weight: 400; font-size: 22px; color: var(--ink-3); margin-left: 10px; }
.s85-plot { position: relative; width: 640px; height: 330px; }
.s85-plot > svg { position: absolute; left: 0; top: 0; }
.s85-axis { stroke: var(--ink-3); stroke-width: 2; }
.s85-tick { font-size: 20px; fill: var(--ink-3); text-anchor: middle; }
.s85-mark { stroke: var(--ink-2); stroke-width: 2; stroke-dasharray: 4 5; }
.s85-brace { stroke: var(--ink); stroke-width: 3; }
.s85-ytitle { position: absolute; left: 0; top: -4px; font-size: 20px; font-weight: 600; color: var(--ink-2); }
.s85-xtitle { position: absolute; left: 50%; top: 300px; transform: translateX(-50%); font-size: 20px; font-weight: 600; color: var(--ink-2); }
.s85-gap { position: absolute; transform: translateX(-50%); font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 26px; color: var(--ink); white-space: nowrap; }
.s85-pt { position: absolute; font-size: 20px; color: var(--ink-3); white-space: nowrap; }
.s85-pt.sea { color: var(--andaman); }
.s85-key { display: flex; gap: 26px; font-size: 21px; color: var(--ink-2); margin-top: 6px; }
.s85-key span { display: flex; align-items: center; gap: 8px; }
.s85-key i { display: inline-block; width: 36px; height: 0; }
.s85-key i.dash { border-top: 4px dashed var(--ink-3); }
.s85-key i.solid { border-top: 5px solid var(--andaman); }
.s85-steps { margin: 6px 0 0; padding-left: 30px; font-size: 24px; line-height: 1.6; color: var(--ink-2); }
.s85-steps b { color: var(--ink); font-weight: 600; }
</style>

<!--
เฟสของ coherence บอกว่าเมื่อดัชนีขึ้น ระดับน้ำขึ้นตามหรือลง กลไกที่ว่าบอกว่าปีที่ Niño3.4 และ DMI สูง ระดับน้ำต้องลง ส่วน SOI ต้องไปทางเดียวกับระดับน้ำ
ทิศที่วัดได้ตรงกับกลไกทั้งสี่ดัชนี
เฟสยังบอกจังหวะ ระดับน้ำต่ำสุดหลัง SOI และ Niño3.4 ราว 3 เดือน
เลขนี้ได้จากมุมเฟส Niño3.4 ได้ 156 องศา ห่างจากสวนทางที่ 180 องศาอยู่ 24 องศา คิดเป็น 24 ส่วน 360 ของคาบ 38 เดือน ได้ 2.5 เดือน ปัดเป็น 3
แต่ลดลงก่อน DMI ถึงจุดสูงสุดราว 5 เดือน เพราะอ่าวเบงกอลเริ่มต่ำตั้งแต่เมษายน ขณะที่ IOD สูงสุดช่วงกันยายนถึงพฤศจิกายน
ส่วน WNPMI ระดับน้ำนำราว 6 เดือน มรสุมนี้จึงน่าจะเป็นผลตามของเอลนีโญ ไม่ใช่ตัวขับ (อนุมาน)

ถ้าถูกถาม:
- มุมเฟสที่วัดได้คือ Niño3.4 ราว 156 องศา SOI ราว ลบ 28 DMI ราว ลบ 150 และ WNPMI ราว 56 องศา โดย 0 องศาคือไปด้วยกัน 180 องศาคือสวนทาง
- มุมของ DMI กระจายมากกว่าตัวอื่น ความสม่ำเสมอ R เท่ากับ 0.55
- มรสุมแปซิฟิกตะวันตกเฉียงเหนืออ่อนลงในฤดูร้อนหลังเอลนีโญ จึงตอบสนองช้ากว่า (อนุมาน)
-->

---
id: SQ08_S060
clicks: 3
layout: page
seq: '8'
section: กลไกทางกายภาพ
page: 23
kinds: [แผนภาพ]
---

# ลมเหนือเส้นศูนย์สูตรมหาสมุทรอินเดียเป็นกลไกร่วมที่อธิบายผลทั้งหมด

<!--
  ขั้น 1 (ตอนเข้าหน้า) แถบเส้นทาง + ผลข้อ 1–2 อันดามัน · คลิก 1 ผลข้อ 3 รวมดัชนี · คลิก 2 ผลข้อ 4 อ่าวไทย (นอกเส้นทาง ไม่ไฮไลต์แถบ) · คลิก 3 ผลข้อ 5 PDO/TPI/NAO
  ไฮไลต์ชิปในแถบเส้นทางตามแถวล่าสุดที่เปิด · ไม่มีคอลัมน์หลักฐาน · ส้ม = อ่าวไทยเท่านั้น
-->
<div class="s86-path">
  <template v-for="(c, i) in chips" :key="i">
    <span v-if="i > 0" class="s86-arrow">→</span>
    <span class="s86-chip" :class="[{ on: lit.includes(i), last: i === 3 }]">{{ c }}</span>
  </template>
  <span class="s86-out" :class="{ show: step === 2 }">แถวอ่าวไทย: นอกเส้นทาง</span>
</div>
<div class="card s86-card">
  <div class="s86-head">
    <span>ผลที่เราพบ</span><span></span><span>คำอธิบายทางกายภาพ</span>
  </div>
  <div class="s86-row s86-andaman">
    <div class="s86-l"><b class="s86-tag a">อันดามัน</b><span>coherent กับ SOI, DMI, WNPMI และ Niño3.4 พร้อมกัน</span></div>
    <div class="s86-ar">→</div>
    <div class="s86-r">ทุกดัชนีผูกกับลมศูนย์สูตรชุดเดียวกัน → คลื่นเคลวิน → อันดามัน</div>
  </div>
  <div class="s86-row s86-andaman">
    <div class="s86-l"><b class="s86-tag a">อันดามัน</b><span>ทิศ: สวนทาง Niño3.4 และ DMI แต่ไปด้วยกันกับ SOI</span></div>
    <div class="s86-ar">→</div>
    <div class="s86-r">เอลนีโญ / IOD บวก → ลมตะวันออก → คลื่นดูดน้ำขึ้น → น้ำต่ำ</div>
  </div>
  <div v-click="1" class="s86-row s86-andaman">
    <div class="s86-l"><b class="s86-tag a">อันดามัน</b><span>รวมหลายดัชนีไม่ได้อะไรเพิ่ม</span></div>
    <div class="s86-ar">→</div>
    <div class="s86-r">ทุกตัวส่งผลผ่านตัวกลางเดียวกัน</div>
  </div>
  <div v-click="2" class="s86-row s86-gulf">
    <div class="s86-l"><b class="s86-tag g">อ่าวไทย</b><span>ไม่พบสัญญาณที่ตรวจได้</span></div>
    <div class="s86-ar">→</div>
    <div class="s86-r">แอ่งตื้นไม่มีความจำ ฤดูกาลกลบ และอยู่นอกเส้นทางคลื่น</div>
  </div>
  <div v-click="3" class="s86-row s86-other">
    <div class="s86-l"><b class="s86-tag o">ดัชนีอื่น</b><span>PDO, TPI และ NAO ไม่เกิน noise</span></div>
    <div class="s86-ar">→</div>
    <div class="s86-r">PDO / TPI มีพลังงานที่คาบทศวรรษ<br>NAO เป็นโหมดแอตแลนติกไม่มีทางมาถึงไทย</div>
  </div>
</div>
<script setup>
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
const { $clicks: step } = useSlideContext()
const chips = ['เอลนีโญ / IOD บวก', 'ลมตะวันออกที่ศูนย์สูตร', 'คลื่นเคลวิน', 'ระดับน้ำอันดามันลด']
// ชิปที่ไฮไลต์ตามแถวล่าสุดที่เปิด: แถวอันดามัน = ทั้งเส้นทาง · แถวรวมดัชนี = ตัวกลาง (ลม + คลื่น) · อ่าวไทย / ดัชนีอื่น = นอกเส้นทาง
const lit = computed(() => [[0, 1, 2, 3], [1, 2], [], []][step.value] ?? [])
</script>

<style>
.s86-path { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; position: relative; }
.s86-chip { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 28px; line-height: 1.2; padding: 12px 26px; border-radius: 999px; box-sizing: border-box;
  background: #fff; color: var(--ink-3); border: 3px solid #C3D2D8; transition: all 0.4s; }
.s86-chip.on { background: color-mix(in srgb, var(--ink) 9%, white); color: var(--ink); border-color: var(--ink); }
.s86-chip.last.on { background: var(--andaman); border-color: var(--andaman); color: #fff; }
.s86-chip.last:not(.on) { color: var(--andaman); border-color: color-mix(in srgb, var(--andaman) 45%, white); }
.s86-arrow { font-size: 36px; color: var(--ink-3); }
.s86-out { margin-left: auto; font-size: 22px; color: var(--gulf); border: 2px dashed var(--gulf); border-radius: 999px; padding: 4px 18px; opacity: 0; transition: opacity 0.4s; white-space: nowrap; }
.s86-out.show { opacity: 1; }
.s86-card { padding: 20px 36px 14px; display: flex; flex-direction: column; }
.s86-head, .s86-row { display: grid; grid-template-columns: 770px 50px 1fr; column-gap: 14px; align-items: center; }
.s86-head { font-size: 24px; color: var(--ink-3); padding-bottom: 8px; border-bottom: 2px solid #DCE7EB; }
.s86-row { padding: 16px 0 16px 20px; border-bottom: 1px solid #E8EFF2; border-left: 8px solid var(--ink-3); min-height: 118px; box-sizing: border-box; }
.s86-row:last-child { border-bottom: none; }
.s86-andaman { border-left-color: var(--andaman); }
.s86-gulf { border-left-color: var(--gulf); }
.s86-other { border-left-color: #A8B7BF; }
.s86-l { display: flex; align-items: center; gap: 18px; font-size: 27px; line-height: 1.35; color: var(--ink); }
.s86-r { font-size: 27px; line-height: 1.4; color: var(--ink-2); }
.s86-ar { font-size: 36px; color: var(--ink-3); text-align: center; }
.s86-tag { flex: none; min-width: 116px; text-align: center; box-sizing: border-box; font-size: 22px; font-weight: 600; line-height: 1; padding: 8px 16px; border-radius: 999px; white-space: nowrap; }
.s86-tag.a { background: color-mix(in srgb, var(--andaman) 14%, white); color: var(--andaman); }
.s86-tag.g { background: color-mix(in srgb, var(--gulf) 16%, white); color: var(--gulf); }
.s86-tag.o { background: #E4E7EA; color: #44515C; }
</style>

<!--
สรุปฝั่งฟิสิกส์ กลไกเดียวนี้อธิบายผลของเราได้พร้อมกันหลายข้อ
ดัชนีหลายตัว coherent กับอันดามันพร้อมกัน และทิศตรงกับกลไก เพราะทุกตัวผูกกับลมที่ศูนย์สูตรชุดเดียวกัน
การรวมหลายดัชนีจึงไม่ได้อะไรเพิ่ม เพราะทุกตัวส่งผลผ่านเส้นทางเดียวกัน
อ่าวไทยเงียบ เพราะเป็นแอ่งตื้นที่ไม่มีความจำและอยู่นอกเส้นทางคลื่น
(ตัดได้) ส่วน PDO และ TPI พลังงานหลักอยู่ที่คาบทศวรรษ และ NAO เป็นโหมดแอตแลนติกที่ไม่มีเส้นทางมาถึงไทย (อนุมาน)
-->

---
id: SQ10_S010
clicks: 3
layout: page
seq: '9'
section: สรุปผล
page: 24
kinds: []
---

# สรุปผล: ทะเลอันดามันสัมพันธ์กับ ENSO และ IOD ส่วนอ่าวไทยไม่พบสัญญาณที่ตรวจได้

<!--
  ขั้น 1 (ตอนเข้าหน้า) ผลข้อ 1 อันดามัน · คลิก 1 ผลข้อ 2 อ่าวไทย · คลิก 2 ผลข้อ 3 รวมหลายดัชนีไม่ได้ผลมากขึ้น · คลิก 3 กราฟเล็กสองเส้น + ชื่อเรื่อง
  กราฟเล็กใช้ข้อมูลและสเกลเดียวกับ SQ01_S020 (1996–2000 · y ±250 · แกนตั้งไม่มีตัวเลข) · ส้ม = อ่าวไทยเท่านั้น (การ์ดข้อ 3 ใช้สีหมึก)
-->
<div class="s10-row">
  <div class="card s10-card s10-andaman">
    <div class="s10-head andaman">อันดามัน</div>
    <div class="s10-main">coherence เกินระดับ noise กับ</div>
    <div class="s10-chips"><span>SOI</span><span>DMI</span><span>WNPMI</span><span>Niño3.4</span></div>
    <div class="s10-note"><i class="s10-check">✓</i>ทิศของความสัมพันธ์ตรงกับกลไก</div>
  </div>
  <div v-click="1" class="card s10-card s10-gulf">
    <div class="s10-head gulf">อ่าวไทย</div>
    <div class="s10-main">ไม่พบสัญญาณที่ตรวจได้</div>
    <div class="s10-bigrow"><span class="s10-big gulf"><Fact id="indices.n" /></span><span class="s10-bigcap">ดัชนี<br>ไม่มีตัวไหนเกิน noise</span></div>
  </div>
  <div v-click="2" class="card s10-card s10-adj">
    <div class="s10-head">หลายดัชนี (MWC)</div>
    <div class="s10-main">เมื่อปรับเกณฑ์ตามจำนวนดัชนีแล้ว</div>
    <div class="s10-one">รวมหลายดัชนีไม่ได้ผลมากขึ้น</div>
  </div>
</div>
<div v-click="3" class="card s10-recap">
  <div class="s10-mini">
    <div class="s10-minihead"><i class="s10-dot" style="background: var(--andaman)"></i><b class="andaman">อันดามัน</b> ภูเก็ต</div>
    <SeriesChart :width="560" :height="270"
      :series="[{ key: 'andaman_mm_12m', kind: 'line', color: 'var(--andaman)', width: 4.5 }]"
      :x-range="[1996, 2000]" :y-left="[-250, 250]" :ticks-left="[-200, 0, 200]" :ticks-x="[1996, 1998]" y-label="มม." x-label="ปี" :band="[1997.5, 1998.5]" />
  </div>
  <div class="s10-mini">
    <div class="s10-minihead"><i class="s10-dot" style="background: var(--gulf)"></i><b class="gulf">อ่าวไทย</b> ประจวบคีรีขันธ์</div>
    <SeriesChart :width="560" :height="270"
      :series="[{ key: 'gulf_mm_12m', kind: 'line', color: 'var(--gulf)', width: 4.5 }]"
      :x-range="[1996, 2000]" :y-left="[-250, 250]" :ticks-left="[-200, 0, 200]" :ticks-x="[1996, 1998]" y-label="มม." x-label="ปี" :band="[1997.5, 1998.5]" />
  </div>
  <div class="s10-title">ระดับน้ำทะเลสองฝั่ง<br>ตอบสนองต่อภูมิอากาศต่างกัน</div>
</div>

<style>
.s10-row { display: flex; gap: 30px; }
.s10-card { flex: 1 1 0; min-width: 0; min-height: 420px; padding: 30px 36px; display: flex; flex-direction: column; gap: 15px; border-top: 12px solid var(--ink); }
.s10-andaman { border-top-color: var(--andaman); }
.s10-gulf { border-top-color: var(--gulf); }
.s10-head { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 48px; line-height: 1.2; }
.s10-main { font-size: 27px; line-height: 1.45; color: var(--ink-2); }
.s10-chips { display: flex; flex-wrap: wrap; gap: 12px; }
.s10-chips span { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 30px; padding: 3px 21px; border-radius: 999px;
  background: color-mix(in srgb, var(--andaman) 14%, white); color: var(--andaman); }
.s10-note { margin-top: auto; font-size: 24px; color: var(--ink-2); display: flex; align-items: center; gap: 12px; }
.s10-check { font-style: normal; font-weight: 700; color: var(--andaman); font-size: 30px; }
.s10-bigrow { display: flex; align-items: center; gap: 24px; margin-top: auto; }
.s10-big { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 120px; line-height: 1; }
.s10-bigcap { font-size: 24px; line-height: 1.45; color: var(--ink-2); }
.s10-one { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 54px; line-height: 1.25; color: var(--ink); }
.s10-recap { display: flex; align-items: center; gap: 30px; margin-top: 30px; padding: 21px 36px; }
.s10-mini { flex: none; }
.s10-minihead { display: flex; align-items: center; gap: 12px; font-size: 24px; color: var(--ink-2); }
.s10-minihead b { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 30px; }
.s10-dot { width: 18px; height: 18px; border-radius: 50%; display: inline-block; }
.s10-title { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 36px; line-height: 1.4; padding-left: 12px; white-space: nowrap; }
</style>

<!--
ผลข้อแรก ระดับน้ำอันดามันขยับตามเอลนีโญและ IOD สอดคล้องกับเส้นทางของลมที่ศูนย์สูตรและคลื่นเคลวิน
ข้อสอง อ่าวไทยไม่พบสัญญาณที่ตรวจได้จากดัชนีใด ซึ่งเป็นสิ่งที่ฟิสิกส์ของแอ่งตื้นคาดไว้
ข้อสาม เมื่อปรับเกณฑ์ตามจำนวนดัชนีแล้ว การรวมหลายดัชนีไม่ได้ผลมากขึ้น
กลับไปที่คำถามตอนต้น ทะเลสองฝั่งที่อยู่ใกล้กันแค่นี้ ฟังภูมิอากาศคนละแบบ

ถ้าถูกถาม:
- coherence ไม่ใช่เหตุและผล มันบอกว่าสองสัญญาณขยับพร้อมกัน ไม่ได้บอกว่าใครทำให้ใคร ผลของเราจึงสอดคล้องกับกลไกที่มีงานวิจัยรองรับ แต่ไม่ได้พิสูจน์มัน
- คาบ 8 ถึง 16 ปีตอบไม่ได้ เพราะข้อมูล 72 ปีมีรอบยาวแบบนี้น้อยเกินไป noise ล้วนก็ได้ค่าสูงในแถบนี้
- เราใช้มาตรวัดเพียงทะเลละหนึ่งสถานี ยังไม่ได้ตรวจว่าทั้งทะเลให้ผลเดียวกัน
- ข้อสรุปหลักรันทั้งสายใหม่ด้วยการเตรียมข้อมูล 8 แบบ และผ่านครบทั้ง 8 แบบ
- ข้อที่ว่า WNPMI นำ ผ่าน 6 จาก 8 แบบ เราจึงไม่สรุปว่า WNPMI เป็นดัชนีเด่น
- มาตรวัดภูเก็ตหลังปี 2005 มีข้อมูลสองคลังที่ไม่ตรงกัน จากการเปลี่ยนเครื่องมือและการแก้ระดับอ้างอิงที่มีเอกสารยืนยัน
- พอเปลี่ยนคลังข้อมูล SOI แทบไม่เปลี่ยน แต่ WNPMI ลดลงครึ่งหนึ่ง จาก 70.5 เหลือ 34.9 เปอร์เซ็นต์
-->

---
id: SQ10_S020
layout: end
credits: ['ข้อมูล: PSMSL, UHSLC, NOAA PSL/CPC', 'วิธี: Grinsted et al. 2004, Hu & Si 2016, Song & Chen 2022, Torrence & Compo 1998', 'กลไก: Han & Webster 2002, Aparna et al. 2012, Brown et al. 2019, Anutaliya 2023, Liu et al. 2011', 'เครื่องมือ: Slidev, Manim, Blender', 'ผู้จัดทำ: กวินภพ จันเจือ รหัสนิสิต 6710503739']
---

# ขอบคุณครับ ช่วงถาม–ตอบ

<!--
ขอบคุณครับ ยินดีรับคำถามครับ
-->

---
id: SQ11_S010
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 26
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# การสร้างค่ารายเดือนจากข้อมูลรายชั่วโมง

<FigCard src="/figs/w2-monthly-vs-psmsl.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องข้อมูลรายชั่วโมงหรือการเทียบกับ PSMSL ใช้หน้านี้
-->

---
id: SQ11_S020
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 27
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# ผลตอบสนองเชิงความถี่และผลตอบสนองอิมพัลส์ของตัวกรองป้องกัน aliasing

<FigCard src="/figs/w2-filter-response.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องการออกแบบตัวกรอง ใช้หน้านี้
-->

---
id: SQ11_S030
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 28
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# การเตรียมสัญญาณ: การกำจัดแนวโน้มระยะยาวและวงรอบฤดูกาล

<FigCard src="/figs/w1-detrend-deseason.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องการตัดแนวโน้มและฤดูกาล ใช้หน้านี้
-->

---
id: SQ11_S040
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 29
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# การทดสอบนัยสำคัญด้วยกระบวนการ AR(1)

<FigCard src="/figs/w4-q1-pasc-null.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องการทดสอบกับ noise ใช้หน้านี้
-->

---
id: SQ11_S050
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 30
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# เกณฑ์นัยสำคัญของ MWC ตามจำนวนดัชนี

<FigCard src="/figs/fig05_threshold_vs_q.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องเกณฑ์ของ MWC ใช้หน้านี้
-->

---
id: SQ11_S060
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 31
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# ชุดดัชนีที่ดีที่สุดตามจำนวนดัชนี

<FigCard src="/figs/fig07_q3_best_per_q.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องการค้นชุดดัชนี ใช้หน้านี้
-->

---
id: SQ11_S070
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 32
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# การวิเคราะห์ความไวต่อการเตรียมข้อมูล

<FigCard src="/figs/fig09_sensitivity.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องความแข็งแรงของผล ใช้หน้านี้
-->

---
id: SQ11_S080
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 33
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# สรุปผลของดัชนีทั้งหมด

<FigCard src="/figs/fig10_scorecard.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องดัชนีตัวอื่น ใช้หน้านี้
-->

---
id: SQ11_S090
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 34
kinds: [ภาคผนวก, แผนภาพ]
---

# กลไก ENSO และ IOD ต่อระดับน้ำทะเลอันดามัน

<FigCard src="/figs/map03_mechanism.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องกลไกทางทะเลโดยละเอียด ใช้หน้านี้
-->

---
id: SQ11_S100
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 35
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# พื้นที่ที่ใช้คำนวณดัชนีภูมิอากาศ

<FigCard src="/figs/map01_indices.png" note="ภาพจากรายงาน" />

<!--
ถ้ามีคำถามเรื่องดัชนีภูมิอากาศ ใช้หน้านี้
-->

---
id: SQ11_S110
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 36
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# ดัชนีที่มี coherence เกินระดับสัญญาณรบกวนที่ทะเลอันดามัน

<!--
  ภาคผนวก: ดัชนีสี่ตัวที่เกินระดับ noise ที่อันดามัน (ผู้ใช้ 10-14: ขออธิบายดัชนีละเอียดขึ้น)
  นิยาม/พิกัด = C94 (รายงาน §2 + BOXES ใน make_infographics.py) · ผล = facts.json (pasc.* · phase.*) · ไม่มีป้าย "เกิน noise ทุก 8 แบบ" (ผู้ใช้ 10-14 ตัดออก)
  การ์ดละดัชนี แถวเดียวกันทุกใบ: วัดอะไร · เครื่องหมาย · ข้อมูล · อันดามัน · ทิศ/จังหวะ · อ่าวไทย
-->
<div class="ix-note">PASC = สัดส่วนพื้นที่ระนาบเวลา–คาบที่ coherence เกิน noise&emsp;ระดับ noise ทั้งระนาบราว <Fact id="noise.pasc_p95_plane" />% ในแถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปีราว <Fact id="noise.pasc_p95_band" :index="0" />–<Fact id="noise.pasc_p95_band" :index="1" />%</div>
<div class="ix-grid">
  <div class="card ix-card">
    <div class="ix-head"><b>Niño3.4</b><span>อุณหภูมิผิวน้ำแปซิฟิกกลาง</span></div>
    <dl>
      <dt>วัดอะไร</dt><dd>อุณหภูมิผิวน้ำเฉลี่ยในกล่อง <Lit v="5" c="C94" />°S–<Lit v="5" c="C94" />°N, <Lit v="170" c="C94" />°W–<Lit v="120" c="C94" />°W</dd>
      <dt>เครื่องหมาย</dt><dd>ปีเอลนีโญเป็นบวก</dd>
      <dt>ข้อมูล</dt><dd>NOAA PSL รายเดือน</dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.nino34" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.nino34" :digits="1" />%</b></dd>
      <dt>ทิศและจังหวะ</dt><dd>สวนทาง ระดับน้ำตามหลังราว <Fact id="phase.nino34.lag_months" absval /> เดือน</dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.nino34" :digits="1" />% ไม่เกิน noise</dd>
    </dl>
  </div>
  <div class="card ix-card">
    <div class="ix-head"><b>SOI</b><span>ดัชนีความกดอากาศ Southern Oscillation</span></div>
    <dl>
      <dt>วัดอะไร</dt><dd>ความกดอากาศที่ตาฮิติ ลบ ที่ดาร์วิน (ออสเตรเลีย)</dd>
      <dt>เครื่องหมาย</dt><dd>ปีเอลนีโญเป็นลบ (กลับทางกับ Niño3.4)</dd>
      <dt>ข้อมูล</dt><dd>NOAA PSL รายเดือน</dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.soi" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.soi" :digits="1" />%</b></dd>
      <dt>ทิศและจังหวะ</dt><dd>ไปด้วยกัน ระดับน้ำตามหลังราว <Fact id="phase.soi.lag_months" absval /> เดือน</dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.soi" :digits="1" />% ไม่เกิน noise</dd>
    </dl>
  </div>
  <div class="card ix-card">
    <div class="ix-head"><b>DMI</b><span>Indian Ocean Dipole</span></div>
    <dl>
      <dt>วัดอะไร</dt><dd>อุณหภูมิผิวน้ำฝั่งตะวันตก (<Lit v="50" c="C94" />–<Lit v="70" c="C94" />°E, <Lit v="10" c="C94" />°S–<Lit v="10" c="C94" />°N) ลบ ฝั่งตะวันออกนอกสุมาตรา (<Lit v="90" c="C94" />–<Lit v="110" c="C94" />°E, <Lit v="10" c="C94" />°S–ศูนย์สูตร)</dd>
      <dt>เครื่องหมาย</dt><dd>IOD บวกเป็นบวก (ตะวันตกอุ่น ตะวันออกเย็น)</dd>
      <dt>ข้อมูล</dt><dd>NOAA PSL รายเดือน</dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.dmi" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.dmi" :digits="1" />%</b></dd>
      <dt>ทิศและจังหวะ</dt><dd>สวนทาง ระดับน้ำลดก่อน DMI สูงสุดราว <Fact id="phase.dmi.lag_months" /> เดือน</dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.dmi" :digits="1" />% ไม่เกิน noise</dd>
    </dl>
  </div>
  <div class="card ix-card">
    <div class="ix-head"><b>WNPMI</b><span>มรสุมแปซิฟิกตะวันตกเฉียงเหนือ</span></div>
    <dl>
      <dt>วัดอะไร</dt><dd>ลมตะวันตกระดับ <Lit v="850" c="C94" /> hPa กล่องใต้ (<Lit v="5" c="C94" />–<Lit v="15" c="C94" />°N, <Lit v="100" c="C94" />–<Lit v="130" c="C94" />°E) ลบ กล่องเหนือ (<Lit v="20" c="C94" />–<Lit v="30" c="C94" />°N, <Lit v="110" c="C94" />–<Lit v="140" c="C94" />°E)</dd>
      <dt>ข้อมูล</dt><dd>โครงงานประกอบเองจากลม U850 ของ NOAA PSL (Wang &amp; Fan)</dd>
      <dt>หมายเหตุ</dt><dd>กล่องใต้เริ่มที่ <Lit v="100" c="C94" />°E ไม่ครอบคลุมอันดามัน</dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.wnpmi" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.wnpmi" :digits="1" />%</b></dd>
      <dt>ทิศและจังหวะ</dt><dd>ไปด้วยกัน ระดับน้ำนำราว <Fact id="phase.wnpmi.lag_months" /> เดือน</dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.wnpmi" :digits="1" />% ไม่เกิน noise</dd>
    </dl>
  </div>
</div>

<style>
.ix-note { font-size: 21px; color: var(--ink-3); margin: -6px 0 10px; }
.ix-grid { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 18px; }
.ix-card { padding: 16px 26px; display: flex; flex-direction: column; gap: 8px; min-height: 0; }
.ix-head { display: flex; align-items: baseline; gap: 14px; }
.ix-head b { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 34px; color: var(--ink); }
.ix-head span { font-size: 22px; color: var(--ink-2); }
.ix-head em { margin-left: auto; font-style: normal; font-size: 20px; font-weight: 600; padding: 2px 14px; border-radius: 999px; white-space: nowrap; }
.ix-card dl { display: grid; grid-template-columns: 160px 1fr; column-gap: 14px; row-gap: 6px; margin: 0; font-size: 23px; line-height: 1.35; }
.ix-card dt { color: var(--ink-3); }
.ix-card dd { margin: 0; color: var(--ink); }
.ix-card dd b { color: var(--andaman); font-weight: 600; }
.ix-card dd.gulf-t { color: var(--gulf); }
</style>

<!--
ถ้ามีคำถามว่าดัชนีแต่ละตัววัดอะไร ใช้หน้านี้และหน้าถัดไป

ถ้าถูกถาม:
- Niño3.4 คืออุณหภูมิผิวน้ำเฉลี่ยในกล่อง 5 องศาใต้ถึง 5 องศาเหนือ 170 ถึง 120 องศาตะวันตก ปีเอลนีโญเป็นบวก ส่วน SOI คือความกดอากาศตาฮิติลบดาร์วิน ปีเอลนีโญเป็นลบ
- WNPMI โครงงานประกอบเองจากลมระดับ 850 hPa กล่องใต้ลบกล่องเหนือตาม Wang and Fan ซึ่งกล่องใต้เริ่มที่ 100 องศาตะวันออก ไม่ครอบคลุมอันดามัน
-->

---
id: SQ11_S120
layout: page
seq: ภาคผนวก
section: ภาคผนวก (ไม่นับเวลา ใช้ตอบคำถาม)
page: 37
kinds: [ภาคผนวก, ข้อมูลจริง]
---

# ดัชนีที่ไม่มี coherence เกินระดับสัญญาณรบกวน

<!--
  ภาคผนวก: ดัชนีสี่ตัวที่ไม่เกินระดับ noise (ผู้ใช้ 10-14: ขออธิบายดัชนีละเอียดขึ้น)
  นิยาม = C94 (PDO / TPI / NAO จาก docs/source-paper-detail.md · AMO ไม่ใส่พิกัด — ดู note ของ C94) · เหตุผล = C85 · AMO = C95
  ผล = facts.json (pasc.*) · แถวเหมือนหน้าก่อน แต่แทนทิศ/จังหวะด้วย "ทำไมไม่เกิน"
-->
<div class="ix-note">PASC = สัดส่วนพื้นที่ระนาบเวลา–คาบที่ coherence เกิน noise&emsp;ระดับ noise ทั้งระนาบราว <Fact id="noise.pasc_p95_plane" />% ในแถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปีราว <Fact id="noise.pasc_p95_band" :index="0" />–<Fact id="noise.pasc_p95_band" :index="1" />%</div>
<div class="ix-grid">
  <div class="card ix-card">
    <div class="ix-head"><b>PDO</b><span>Pacific Decadal Oscillation</span><em class="ix-fail">ไม่เกิน noise</em></div>
    <dl>
      <dt>วัดอะไร</dt><dd>รูปแบบหลักตัวแรกของอุณหภูมิผิวน้ำแปซิฟิกเหนือ เหนือละติจูด <Lit v="20" c="C94" />°N (Mantua et al.)</dd>
      <dt>ข้อมูล</dt><dd>NOAA PSL รายเดือน</dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.pdo" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.pdo" :digits="1" />%</b></dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.pdo" :digits="1" />% ไม่เกิน noise</dd>
      <dt>ทำไมไม่เกิน</dt><dd>พลังงานหลักอยู่ที่คาบทศวรรษ ไม่ใช่คาบระหว่างปีที่เราศึกษา</dd>
    </dl>
  </div>
  <div class="card ix-card">
    <div class="ix-head"><b>TPI</b><span>Tripole Index ของ IPO</span><em class="ix-fail">ไม่เกิน noise</em></div>
    <dl>
      <dt>วัดอะไร</dt><dd>อุณหภูมิผิวน้ำแปซิฟิกศูนย์สูตรกลาง ลบ ค่าเฉลี่ยของแปซิฟิกตะวันตกเฉียงเหนือและตะวันตกเฉียงใต้ (Henley et al.)</dd>
      <dt>ข้อมูล</dt><dd>NOAA PSL รายเดือน</dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.tpi" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.tpi" :digits="1" />%</b></dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.tpi" :digits="1" />% ไม่เกิน noise</dd>
      <dt>ทำไมไม่เกิน</dt><dd>เป็นโหมดคาบทศวรรษของทั้งแอ่งแปซิฟิก เหมือน PDO</dd>
    </dl>
  </div>
  <div class="card ix-card">
    <div class="ix-head"><b>AMO</b><span>Atlantic Multidecadal Oscillation</span><em class="ix-fail">ไม่นับ</em></div>
    <dl>
      <dt>วัดอะไร</dt><dd>อุณหภูมิผิวน้ำเฉลี่ยของแอตแลนติกเหนือ</dd>
      <dt>ข้อมูล</dt><dd>NOAA PSL รายเดือน สิ้นสุดปี <Lit v="2023" c="C94" /></dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.amo" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.amo" :digits="1" />%</b></dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.amo" :digits="1" />% ไม่เกิน noise</dd>
      <dt>ทำไมไม่นับ</dt><dd>ผ่านในแบบมาตรฐาน แต่ผ่านเพียง <Lit v="4" c="C95" /> จาก <Lit v="7" c="C95" /> แบบ และไม่มีกลไกทางฟิสิกส์รองรับ</dd>
    </dl>
  </div>
  <div class="card ix-card">
    <div class="ix-head"><b>NAO</b><span>North Atlantic Oscillation</span><em class="ix-fail">ไม่เกิน noise</em></div>
    <dl>
      <dt>วัดอะไร</dt><dd>โหมดความกดอากาศของแอตแลนติกเหนือ (Hurrell et al.)</dd>
      <dt>ข้อมูล</dt><dd>NOAA PSL รายเดือน</dd>
      <dt>อันดามัน</dt><dd>PASC ทั้งระนาบ <b><Fact id="pasc.andaman.plane.nao" :digits="1" />%</b> แถบ <Lit v="2" c="C56" />–<Lit v="7" c="C56" /> ปี <b><Fact id="pasc.andaman.band.nao" :digits="1" />%</b></dd>
      <dt>อ่าวไทย</dt><dd class="gulf-t">PASC <Fact id="pasc.gulf.plane.nao" :digits="1" />% ไม่เกิน noise</dd>
      <dt>ทำไมไม่เกิน</dt><dd>เป็นโหมดแอตแลนติก ไม่มีเส้นทางมาถึงไทย</dd>
    </dl>
  </div>
</div>

<style>
.ix-note { font-size: 21px; color: var(--ink-3); margin: -6px 0 10px; }
.ix-grid { flex: 1 1 auto; min-height: 0; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 18px; }
.ix-card { padding: 16px 26px; display: flex; flex-direction: column; gap: 8px; min-height: 0; }
.ix-head { display: flex; align-items: baseline; gap: 14px; }
.ix-head b { font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 34px; color: var(--ink); }
.ix-head span { font-size: 22px; color: var(--ink-2); }
.ix-head em { margin-left: auto; font-style: normal; font-size: 20px; font-weight: 600; padding: 2px 14px; border-radius: 999px; white-space: nowrap; }
.ix-fail { background: var(--infer-bg); color: var(--infer-fg); }
.ix-card dl { display: grid; grid-template-columns: 160px 1fr; column-gap: 14px; row-gap: 6px; margin: 0; font-size: 23px; line-height: 1.35; }
.ix-card dt { color: var(--ink-3); }
.ix-card dd { margin: 0; color: var(--ink); }
.ix-card dd b { color: var(--ink-2); font-weight: 600; }
.ix-card dd.gulf-t { color: var(--gulf); }
</style>

<!--
ถ้ามีคำถามเรื่องดัชนีคาบทศวรรษหรือดัชนีแอตแลนติก ใช้หน้านี้

ถ้าถูกถาม:
- PDO และ TPI ไม่เกิน noise เพราะพลังงานหลักอยู่ที่คาบทศวรรษ ส่วน NAO เป็นโหมดแอตแลนติกที่ไม่มีเส้นทางมาถึงไทย (อนุมาน)
- AMO ผ่านเกณฑ์ในแถบ 2 ถึง 7 ปีในแบบมาตรฐานที่ 13.9 เปอร์เซ็นต์ แต่ผ่านเพียง 4 จาก 7 แบบ และไม่มีกลไกรองรับ จึงไม่นับ
-->
