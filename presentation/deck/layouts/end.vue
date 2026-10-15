<!--
  หน้าจบ (SQ10_S020): ข้อความใหญ่ (slot) + เครดิตย่อจาก frontmatter `credits` (รายการบรรทัด)
-->
<script setup lang="ts">

// Slidev ส่งทุกคีย์ใน frontmatter ของหน้าเข้ามาเป็น props ของ layout
const fm = defineProps<{ credits?: string[] }>()
</script>

<template>
  <div class="slidev-layout end">
    <div class="big"><slot /></div>
    <div class="card credits">
      <div v-for="line in (fm.credits ?? [])" :key="line">{{ line }}</div>
    </div>
  </div>
</template>

<style scoped>
.end { height: 100%; box-sizing: border-box; padding: 120px 120px 72px; display: flex; flex-direction: column; justify-content: space-between; }
.big :deep(h1) { font-size: 96px; }
.credits { font-size: 22px; color: var(--ink-2); display: flex; flex-direction: column; gap: 6px; line-height: 1.5; }
</style>
