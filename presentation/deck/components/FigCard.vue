<!--
  การ์ดหลักฐานที่เป็นรูป: การ์ดขาวมุมมน ยืดเต็มพื้นที่ที่เหลือใต้หัวข้อ · รูปย่อให้พอดีโดยไม่บิดสัดส่วน
  ใช้กับรูปจากรายงาน (ภาพสำรองของหน้าที่ยังไม่มีแอนิเมชัน) และภาพนิ่งอื่น ๆ
  <FigCard src="/figs/fig11_events.png" note="ภาพสำรอง: รูปจากรายงาน" />
-->
<script setup lang="ts">
defineProps<{ src: string, note?: string }>()
</script>

<template>
  <div class="card fig-card">
    <img :src="src" alt="">
    <div v-if="note" class="note">{{ note }}</div>
  </div>
</template>

<style scoped>
.fig-card { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; align-items: center; gap: 9px; }
.fig-card img { flex: 1 1 auto; min-height: 0; max-width: 100%; object-fit: contain; }
.note { font-size: 20px; color: var(--ink-3); align-self: flex-start; }
</style>
