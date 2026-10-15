// export deck เป็น PDF หน้าละสไลด์ ในสภาพ "คลิกสุดท้าย" — เรียกจาก tools/export_pdf.py
//   node export_pdf.cjs <deck/node_modules> <port ของ slidev dev server> <ไฟล์ออก.pdf> [จากหน้า-ถึงหน้า]
//
// ทำไมไม่ใช้ `slidev export` ตรง ๆ (Slidev 53.0.0):
//   - แบบรวดเดียว (ค่าเริ่มต้น) ย่อสไลด์เหลือ ~79% ชิดมุมซ้ายบน ที่เหลือเป็นขอบดำ และหน้าท้ายหาย
//   - --per-slide แก้ขอบดำได้ แต่เปิดทุกหน้าที่คลิก 0 → ของที่โผล่ด้วย v-click หายจาก PDF
// ตรงนี้: เปิดแต่ละหน้าในโหมดพิมพ์ (?print=true → คลิป Manim เป็นภาพนิ่งตอนจบ · ปกนิ่ง)
// อ่านจำนวนคลิกจริงของหน้าจาก window.__slidev__ (มีเฉพาะ dev server) แล้วเปิดใหม่ที่คลิกสุดท้ายก่อนพิมพ์
const [, , nodeModules, port, output, range] = process.argv
const { chromium } = require(`${nodeModules}/playwright-chromium`)
const { PDFDocument } = require(`${nodeModules}/pdf-lib`)
const fs = require('fs')

const base = `http://localhost:${port}/?print=true#`

;(async () => {
  const browser = await chromium.launch()
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } })

  // เปิดหน้า n แล้วรอให้ฟอนต์ ภาพ และคลิปโหลดครบ
  async function open(n, clicks) {
    await page.goto(`${base}/${n}${clicks ? `?clicks=${clicks}` : ''}`)
    await page.waitForFunction(() => window.__slidev__?.nav)
    await page.waitForLoadState('networkidle')
    await page.evaluate(() => document.fonts.ready)
    await page.waitForTimeout(800)
  }

  await open(1)
  const total = await page.evaluate(() => window.__slidev__.nav.total)
  const [from, to] = range ? range.split('-').map(Number) : [1, total]

  const merged = await PDFDocument.create()
  for (let n = from; n <= (to || from); n++) {
    await open(n)
    const clicks = await page.evaluate(() => window.__slidev__.nav.clicksTotal)
    if (clicks > 0)
      await open(n, clicks)
    // เร่งแอนิเมชัน CSS ทุกตัวไปจบ (เส้นที่วาดทีละนิด จุดที่ค่อย ๆ โผล่) — ไม่งั้น PDF ได้ภาพกลางแอนิเมชัน (s009 หน้า 8)
    await page.evaluate(() => document.getAnimations().forEach((a) => { try { a.finish() } catch {} }))
    await page.waitForTimeout(200)
    // เช็กว่าไปถึงคลิกสุดท้ายจริง (กันกรณี Slidev ไม่รับ ?clicks=)
    const at = await page.evaluate(() => window.__slidev__.nav.clicks)
    const pdf = await page.pdf({
      width: '1920px', height: '1080px', pageRanges: '1',
      margin: { top: 0, right: 0, bottom: 0, left: 0 }, printBackground: true, preferCSSPageSize: true,
    })
    const [copied] = await merged.copyPages(await PDFDocument.load(pdf), [0])
    merged.addPage(copied)
    console.log(`หน้า ${n}: คลิก ${at}/${clicks}${at === clicks ? '' : '  ⚠ ไม่ถึงคลิกสุดท้าย'}`)
  }
  fs.writeFileSync(output, await merged.save())
  await browser.close()
})()
