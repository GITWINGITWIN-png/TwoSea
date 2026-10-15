import { defineConfig } from 'vite'

// Slidev 53.0.0: lightningcss (ตัวย่อ CSS ค่าเริ่มต้น) ปฏิเสธกฎหนึ่งใน CSS รวมของ Slidev แล้ว build ล้ม
// → ไม่ย่อ CSS (deck เปิดออฟไลน์ ขนาดไฟล์ไม่สำคัญ) (fit test D7 · 2026-10-10)
export default defineConfig({
  build: { cssMinify: false },
})
