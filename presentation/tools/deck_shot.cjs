// ถ่ายภาพหน้า deck ที่ build แล้ว — เรียกจาก tools/deck_shots.py เท่านั้น
//   node deck_shot.cjs <playwright-chromium path> <port> <outdir> <index:id:clicks> ...
// พิมพ์ error ของหน้า (pageerror / console.error) ต่อหน้า เพื่อให้รู้ว่าหน้าไหนพัง
const [, , pw, port, outdir, ...targets] = process.argv
const { chromium } = require(pw)

;(async () => {
  const browser = await chromium.launch()
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } })
  let errors = []
  page.on('pageerror', (e) => {
    if (!e.message.includes('Wake Lock')) // headless ขอ wake lock ไม่ได้ — ไม่เกี่ยวกับหน้า
      errors.push(`pageerror: ${e.message}`)
  })
  page.on('console', (m) => {
    if (m.type() === 'error' && !m.text().includes('FloatingVue'))
      errors.push(`console: ${m.text().slice(0, 300)}`)
  })
  for (const t of targets) {
    const [index, id, clicks] = t.split(':')
    errors = []
    await page.goto(`http://localhost:${port}/#/${index}?clicks=${clicks}`)
    await page.waitForTimeout(1500)
    // เร่งแอนิเมชัน CSS ไปจบ ให้ภาพตรวจตรงกับ PDF (tools/export_pdf.cjs ทำแบบเดียวกัน)
    await page.evaluate(() => document.getAnimations().forEach((a) => { try { a.finish() } catch {} }))
    await page.waitForTimeout(200)
    // หน้าเต็ม 1920×1080 เฉพาะตัวสไลด์ (ไม่เอาแถบควบคุม)
    const slide = await page.$('#slide-content') ?? page
    await slide.screenshot({ path: `${outdir}/${id}.png` })
    console.log(`${id}: ${errors.length ? errors.join(' | ') : 'ok'}`)
  }
  await browser.close()
})()
