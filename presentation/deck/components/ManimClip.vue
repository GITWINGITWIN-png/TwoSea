<!--
  คลิป Manim ทีละขั้นของหน้าหนึ่ง (clip mode) — ไฟล์มาจาก tools/export_clips.py:
  public/clips/<page>/<n>.mp4 + <n>.png (เฟรมสุดท้ายของขั้น n)

  ขั้น = คลิกของหน้า: ขั้น 1 เล่นเมื่อเข้าหน้า (clicks = start) แล้วคลิกละขั้น
  · เดินหน้า: เล่นคลิปขั้นใหม่จากต้น แล้วค้างเฟรมสุดท้าย (วิดีโอหยุดที่เฟรมสุดท้ายเองเมื่อจบ)
  · ถอยหลัง: แสดง PNG เฟรมสุดท้ายของขั้นนั้นทับ ไม่เล่นถอยหลัง (เหมือน skip_reversing ของ manim-slides)
    — ไม่ใช้การ seek วิดีโอ เพราะ server ธรรมดา (python http.server) ไม่รองรับ Range → seek ตกไปที่ 0 (fit test D2)
  · ภาพนิ่ง (export PDF, ภาพย่อ, ช่อง "ถัดไป" ใน presenter): ใช้ PNG เฟรมสุดท้าย — ไม่มีวิดีโอเล่นซ้อน
  หน้าที่ใช้ต้องตั้ง `clicks:` ใน frontmatter = start + steps − 1 เพราะ Slidev นับคลิกจาก v-click เท่านั้น
-->
<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useNav, useSlideContext } from '@slidev/client'

const props = withDefaults(defineProps<{
  page: string
  steps: number
  start?: number
  loop?: number[]
  width?: number
  height?: number
}>(), { start: 0, loop: () => [], width: 1760, height: 800 })

const { $clicks, $renderContext } = useSlideContext()
const { isPrintMode } = useNav()
const base = import.meta.env.BASE_URL

const step = computed(() => Math.min(props.steps, Math.max(0, $clicks.value - props.start + 1)))
const live = computed(() => !isPrintMode.value && $renderContext.value === 'slide')
const src = (n: number, ext: string) => `${base}clips/${props.page}/${n}.${ext}`

const videos = ref<HTMLVideoElement[]>([])
const still = ref(false) // true = กำลังแสดงภาพนิ่งของขั้นนี้ (หลังถอยหลัง)

watch([step, live], async ([now, isLive], [before]) => {
  if (!isLive || now < 1)
    return
  await nextTick()
  videos.value.forEach((v, i) => { if (i + 1 !== now) v.pause() })
  const v = videos.value[now - 1]
  if (!v)
    return
  if (before !== undefined && now < before) {
    still.value = true
    return
  }
  still.value = false
  v.currentTime = 0
  v.play().catch(() => {})
}, { immediate: true })
</script>

<template>
  <div class="manim-clip" :style="{ width: `${width}px`, height: `${height}px` }">
    <template v-if="live">
      <video
        v-for="n in steps" :key="n" ref="videos"
        :src="src(n, 'mp4')" :poster="n > 1 ? src(n - 1, 'png') : undefined"
        :loop="loop.includes(n)" muted playsinline preload="auto"
        v-show="n === step"
      />
      <img v-if="still && step >= 1" :src="src(step, 'png')" alt="">
    </template>
    <img v-else-if="step >= 1" :src="src(step, 'png')" alt="">
  </div>
</template>

<style scoped>
.manim-clip { position: relative; }
.manim-clip video, .manim-clip img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }
</style>
