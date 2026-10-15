<!--
  เส้นคลื่นจาง ๆ ใต้ชื่อเรื่อง = ระดับน้ำรายเดือนจริงของสองสถานี (ตัดแนวโน้ม+ฤดูกาลแล้ว · 1951–2023)
  ภูเก็ต = น้ำเงิน · ประจวบฯ = ส้ม · เลื่อนช้า ๆ วนไป (สองชุดต่อกันแล้วเลื่อนครึ่งหนึ่ง) · ตอนพิมพ์/PDF นิ่ง
  ป้ายเล็ก "ข้อมูลจริง" อยู่บนปกแล้ว · SQ02_S010 ดึงเส้นเดียวกันนี้ขึ้นมาเฉลย
-->
<script setup lang="ts">
import { useNav } from '@slidev/client'

withDefaults(defineProps<{ width?: number, height?: number, opacity?: number }>(), { width: 1920, height: 300, opacity: 0.45 })
const { isPrintMode } = useNav()
const series = [
  { key: 'gulf_mm', kind: 'line', color: 'var(--gulf)', width: 2.2 },
  { key: 'andaman_mm', kind: 'line', color: 'var(--andaman)', width: 2.2 },
]
</script>

<template>
  <div class="cover-wave" :style="{ height: `${height}px`, opacity }">
    <div class="strip" :class="{ still: isPrintMode }">
      <SeriesChart v-for="n in 2" :key="n" bare :width="width" :height="height" :series="series" :y-left="[-300, 300]" />
    </div>
  </div>
</template>

<style scoped>
.cover-wave { overflow: hidden; position: relative; }
.strip { display: flex; width: max-content; animation: drift 90s linear infinite; }
.strip.still { animation: none; }
@keyframes drift { from { transform: translateX(0); } to { transform: translateX(-50%); } }
</style>
