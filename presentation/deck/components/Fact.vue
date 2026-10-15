<!--
  ตัวเลขบนสไลด์ — มาจาก data/facts.json เท่านั้น (คัดลอกจาก ../data/facts.json โดย generator)
  จัดรูปแบบเหมือน num() ใน manim/facts.py ทุกประการ: ปัดทศนิยม · จุลภาคหลักพัน · ลบเป็น "−" (U+2212)
  ใช้: <Fact id="alias.K1_days" :digits="1" /> · ไม่มี id นี้ = แสดง ⚠ และ build_deck จะไม่ผ่าน
  plain = ไม่ใส่จุลภาคหลักพัน (ใช้กับปี ค.ศ. เช่น 1951 ไม่ใช่ 1,951)
-->
<script setup lang="ts">
import { computed } from 'vue'
import facts from '../data/facts.json'

const props = withDefaults(defineProps<{
  id: string
  digits?: number
  index?: number
  absval?: boolean
  roundTo?: number
  sign?: boolean
  plain?: boolean
}>(), { digits: 0 })

const text = computed(() => {
  const fact = (facts as Record<string, { value: unknown }>)[props.id]
  if (!fact)
    return `⚠${props.id}`
  let value = fact.value as number | number[] | Record<string, number>
  if (props.index !== undefined)
    value = (Array.isArray(value) ? value : Object.values(value)).at(props.index) as number // ติดลบ = นับจากท้าย
  let x = value as number
  if (props.absval)
    x = Math.abs(x)
  if (props.roundTo)
    x = Math.round(x / props.roundTo) * props.roundTo
  const out = x.toLocaleString('en-US', {
    minimumFractionDigits: props.digits,
    maximumFractionDigits: props.digits,
    useGrouping: !props.plain,
  })
  return ((props.sign && x > 0) ? `+${out}` : out).replace('-', '−')
})
</script>

<template>
  <span class="fact" :data-fact="id">{{ text }}</span>
</template>
