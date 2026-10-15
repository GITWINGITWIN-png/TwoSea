<!--
  แบบหน้าหลักของ deck (theme D): แถบบน = เม็ดยาเลขตอน + ชื่อตอน · ป้ายชนิดภาพ/หลักฐาน + เลขหน้า
  ค่ามาจาก frontmatter ที่ tools/gen_deck.py เขียน: seq · section · page · kinds · evidence
  เนื้อหน้า (slot) = หัวข้อ # + การ์ดหลักฐาน — เรียงเป็นคอลัมน์ การ์ดยืดเต็มพื้นที่ที่เหลือ
-->
<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'

// Slidev ส่งทุกคีย์ใน frontmatter ของหน้าเข้ามาเป็น props ของ layout
const fm = defineProps<{ seq?: string, section?: string, page?: number, kinds?: string[], evidence?: string[] }>()

// ชื่อป้าย → class สีใน style.css
const KIND: Record<string, string> = { 'ข้อมูลจริง': 'real', 'แผนภาพ': 'diag', 'เปรียบเทียบ': 'comp', 'ภาคผนวก': 'appx' }
const EVIDENCE: Record<string, string> = { 'หนักแน่น': 'strong', 'อนุมาน': 'infer' }
const chips = computed(() => [
  ...((fm.evidence as string[]) ?? []).map(t => ({ text: t, cls: EVIDENCE[t] ?? 'infer' })),
  ...((fm.kinds as string[]) ?? []).map(t => ({ text: t, cls: KIND[t] ?? 'diag' })),
])

// หัวข้อยาว (ภาษาทางการตามรายงาน · ผู้ใช้ 10-14) → ย่อตัวอักษรทีละ 1 px จนเหลือบรรทัดเดียว (ต่ำสุด 40 px แล้วจึงยอมขึ้นบรรทัดสอง)
// Slidev โหลดหน้าถัดไปล่วงหน้าแบบซ่อนอยู่ (สูง 0) → วัดตอน mount ไม่ได้ จึงใช้ ResizeObserver: วัดครั้งแรกที่หัวข้อมองเห็นจริง
// offsetHeight ไม่ขึ้นกับ transform ที่ Slidev ใช้ย่อ/ขยายผืน 1920×1080
const body = ref<HTMLElement>()
onMounted(async () => {
  await nextTick()
  const h1 = body.value?.querySelector('h1') as HTMLElement | null
  if (!h1)
    return
  const ro = new ResizeObserver(async () => {
    if (h1.offsetHeight === 0)
      return                                   // ยังซ่อนอยู่ — รอรอบหน้า
    ro.disconnect()                            // วัดครั้งเดียว (การย่อเองก็ทำให้ขนาดเปลี่ยน — ไม่ให้วน)
    await document.fonts?.ready
    const oneLine = () => h1.offsetHeight <= parseFloat(getComputedStyle(h1).lineHeight) * 1.4
    for (let px = 51; px > 40 && !oneLine(); px--)
      h1.style.fontSize = `${px - 1}px`
  })
  ro.observe(h1)
})
</script>

<template>
  <div class="slidev-layout page">
    <header class="bar">
      <div class="left">
        <span v-if="fm.seq" class="pill seq">{{ fm.seq }}</span>
        <span class="muted">{{ fm.section }}</span>
      </div>
      <div class="right">
        <span v-for="c in chips" :key="c.text" class="pill" :class="c.cls">{{ c.text }}</span>
        <span class="no muted">{{ fm.page }}</span>
      </div>
    </header>
    <main ref="body" class="body">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; box-sizing: border-box; padding: 42px 84px 42px; gap: 21px; }
.bar { display: flex; justify-content: space-between; align-items: center; font-size: 22px; }
.left, .right { display: flex; align-items: center; gap: 15px; }
.no { min-width: 36px; text-align: right; }
.body { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; gap: 24px; }
</style>
