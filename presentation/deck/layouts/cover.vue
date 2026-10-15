<!--
  ปก (SQ01_S030): ชื่อเรื่องใหญ่ (slot = # ชื่อเรื่อง) · ชื่อรอง · วิชา · ผู้จัดทำ จาก frontmatter
  เส้นคลื่นข้อมูลจริงใต้ชื่อ (บท v4) จะมาใน slot `wave` เมื่อมีข้อมูล Y_mm
-->
<script setup lang="ts">

// Slidev ส่งทุกคีย์ใน frontmatter ของหน้าเข้ามาเป็น props ของ layout
const fm = defineProps<{ subtitle?: string, course?: string, byline?: string }>()
</script>

<template>
  <div class="slidev-layout cover">
    <div class="top"><span class="pill real">ข้อมูลจริง</span></div>
    <div class="title">
      <slot />
      <div class="subtitle">{{ fm.subtitle }}</div>
    </div>
    <div class="wave"><slot name="wave" /></div>
    <div class="meta">
      <div>{{ fm.course }}</div>
      <div class="author">{{ fm.byline }}</div>
    </div>
  </div>
</template>

<style scoped>
.cover { height: 100%; box-sizing: border-box; padding: 63px 120px 72px; display: flex; flex-direction: column; gap: 30px; }
.top { display: flex; justify-content: flex-end; }
.title { margin-top: 90px; display: flex; flex-direction: column; gap: 24px; }
.title :deep(h1) { font-size: 60px; line-height: 1.35; max-width: 1700px; }   /* ชื่อทางการตามรายงานยาว 3 บรรทัด (เดิม 108 px) */
.subtitle { font-size: 28px; color: var(--ink-2); max-width: 1600px; line-height: 1.45; }
.wave { flex: 1 1 auto; min-height: 0; }
.meta { font-size: 26px; color: var(--ink-2); display: flex; flex-direction: column; gap: 6px; }
.author { color: var(--ink); font-weight: 600; }
</style>
