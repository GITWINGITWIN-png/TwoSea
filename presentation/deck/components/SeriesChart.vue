<!--
  กราฟอนุกรมเวลาจากข้อมูลจริง (deck/data/series.json ที่ tools/gen_deck.py ส่งออกจาก data/derived.npz) · theme D

  <SeriesChart :width="1700" :height="620"
    :series="[
      { key: 'andaman_mm_12m', kind: 'area', color: 'var(--andaman)' },
      { key: 'neg_nino34_12m', kind: 'line', axis: 'right', color: 'var(--nino)', at: 1 },
    ]"
    :y-left="[-250, 250]" :y-right="[-2.5, 2.5]" :band="[1997.5, 1998.5]" :band-at="0"
    unit-left="มม." unit-right="SD" />

  series[].key   ชื่ออาร์เรย์ใน series.json (แกน x = t เสมอ)
  series[].kind  'line' | 'area' (พื้นที่จาก 0 · ส่วนติดลบเข้มกว่า = "ต่ำกว่าปกติ")
  series[].axis  'left' (ค่าเริ่มต้น) | 'right'
  series[].at    คลิกที่เส้นนี้ปรากฏ (0 = ตั้งแต่เข้าหน้า) — ค่าเดียวกับ v-click="n" · frontmatter `clicks:` ต้องครอบคลุม
  x-range        [ปีเริ่ม, ปีจบ] — ตัดช่วงได้ (เช่น [1996, 2000] สำหรับซูมเหตุการณ์)
  bare           ไม่มีแกน กริด เส้นศูนย์ ตัวเลข — ใช้เป็นเส้นคลื่นตกแต่งที่เป็นข้อมูลจริง (ปก · SQ02_S010)
  x-key          อาร์เรย์แกน x (ค่าเริ่มต้น 't' = ปี) · เช่น 'fir_w' (รอบต่อวัน) คู่กับ series 'fir_h_db'
  hlines         เส้นแนวนอน [{ y, color?, dash?, at? }] — เช่นเส้นสเปก −70 dB
  points         จุด [{ x, y, color?, at? }] — เช่นตำแหน่งน้ำขึ้นน้ำลงแต่ละตัว (ป้ายตัวเลขให้วาง HTML ทับเอง)
  y-label        ชื่อแกนซ้าย เช่น "ระดับน้ำ (มม.)" — เขียนแนวนอนเหนือแกน (ตัวไทยหมุนแนวตั้งอ่านยาก) · ใช้แทน unit-left
  y-label-right  ชื่อแกนขวา (ชิดขวาเหนือแกน) · ใช้แทน unit-right
  x-label        ชื่อแกนนอน เช่น "ปี" — กึ่งกลางใต้ตัวเลขแกน (เพิ่มขอบล่างให้เอง)
  (ผู้ใช้ 10-15: ทุกกราฟต้องมีชื่อแกนทั้ง x และ y)
  ตัวเลขแกนมาจาก props (ไม่ใช่ข้อความในหน้า) จึงไม่ต้องผ่าน <Fact/> — แต่ตัวเลขที่เป็นข้อความอธิบายบนหน้ายังต้องผ่าน
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import data from '../data/series.json'

interface HLine { y: number, color?: string, dash?: boolean, at?: number }
interface Point { x: number, y: number, color?: string, at?: number }
interface Series { key: string, kind?: 'line' | 'area', axis?: 'left' | 'right', color?: string, at?: number, width?: number }

const props = withDefaults(defineProps<{
  series: Series[]
  width?: number
  height?: number
  xRange?: [number, number]
  yLeft?: [number, number]
  yRight?: [number, number]
  ticksX?: number[]
  ticksLeft?: number[]
  ticksRight?: number[]
  unitLeft?: string
  unitRight?: string
  yLabel?: string
  yLabelRight?: string
  xLabel?: string
  band?: [number, number]
  bandAt?: number
  zero?: boolean
  xKey?: string
  bare?: boolean
  hlines?: HLine[]
  points?: Point[]
}>(), { xKey: 't', hlines: () => [], points: () => [], width: 1700, height: 620, yLeft: () => [-250, 250], zero: true, bandAt: 0 })

const { $clicks } = useSlideContext()
const clicks = $clicks  // ชื่อที่ขึ้นต้นด้วย $ อาจไม่ถูกส่งเข้า template — ใช้ชื่อธรรมดา
const D = data as Record<string, (number | null)[]>

// ระยะขอบภายในกราฟ (px) — ตัวเลขแกนซ้าย 21 px · ตัวเลขแกนขวา · ปีด้านล่าง
const M = props.bare
  ? { l: 0, r: computed(() => 0), t: 0, b: 0 }
  : { l: 84, r: computed(() => (props.yRight ? 72 : 24)), t: 36, b: props.xLabel ? 82 : 48 }
const XS = computed(() => D[props.xKey])
const xr = computed<[number, number]>(() => props.xRange ?? [XS.value[0] as number, XS.value[XS.value.length - 1] as number])
const X = (t: number) => M.l + (t - xr.value[0]) / (xr.value[1] - xr.value[0]) * (props.width - M.l - M.r.value)
const Y = (v: number, axis: 'left' | 'right' = 'left') => {
  const [lo, hi] = axis === 'right' && props.yRight ? props.yRight : props.yLeft
  return M.t + (hi - v) / (hi - lo) * (props.height - M.t - M.b)
}
const y0 = computed(() => Y(0))

// เดือนที่ไม่มีข้อมูล (null) = ช่องว่างในเส้น ไม่ลากเส้นตรงข้าม — gaps เก็บตำแหน่งที่ต้องยกปากกา
function seriesPoints(s: Series) {
  const out: [number, number][] = []
  const gaps = new Set<number>()
  XS.value.forEach((t, i) => {
    const v = D[s.key]?.[i]
    if (t === null || t < xr.value[0] || t > xr.value[1])
      return
    if (v === null || v === undefined) {
      gaps.add(out.length)
      return
    }
    out.push([X(t as number), Y(v, s.axis)])
  })
  return Object.assign(out, { gaps })
}
const line = (pts: [number, number][] & { gaps?: Set<number> }) =>
  pts.map((p, i) => `${i === 0 || pts.gaps?.has(i) ? 'M' : 'L'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ')
const area = (pts: [number, number][], sign: 1 | -1) => {
  if (!pts.length)
    return ''
  const z = y0.value
  const clip = pts.map(([x, y]) => [x, sign > 0 ? Math.min(y, z) : Math.max(y, z)] as [number, number])
  return `M${clip[0][0].toFixed(1)},${z} L${clip.map(p => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' L')} L${clip[clip.length - 1][0].toFixed(1)},${z} Z`
}

const drawn = computed(() => props.series.map((s) => {
  const pts = seriesPoints(s)
  return { ...s, visible: $clicks.value >= (s.at ?? 0), line: line(pts), pos: area(pts, 1), neg: area(pts, -1) }
}))
const ticksX = computed(() => props.ticksX ?? [1960, 1980, 2000, 2020].filter(t => t >= xr.value[0] && t <= xr.value[1]))
const ticksL = computed(() => props.ticksLeft ?? [props.yLeft[0] * 0.8, 0, props.yLeft[1] * 0.8])
const ticksR = computed(() => props.yRight ? (props.ticksRight ?? [props.yRight[0] * 0.8, 0, props.yRight[1] * 0.8]) : [])
const fmt = (v: number) => (Math.round(v * 10) / 10).toString().replace('-', '−')
</script>

<template>
  <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" class="series-chart" role="img">
    <g v-if="!bare" class="sc-grid">
      <line v-for="v in ticksL" :key="`g${v}`" :x1="M.l" :x2="width - M.r.value" :y1="Y(v)" :y2="Y(v)" />
    </g>
    <rect v-if="band" v-show="clicks >= bandAt" class="sc-band"
      :x="X(band[0])" :y="M.t" :width="X(band[1]) - X(band[0])" :height="height - M.t - M.b" rx="9" />
    <g v-for="s in drawn" :key="s.key" class="sc-series" :class="{ hidden: !s.visible }">
      <template v-if="s.kind === 'area'">
        <path :d="s.pos" :fill="s.color ?? 'var(--andaman)'" opacity="0.25" />
        <path :d="s.neg" :fill="s.color ?? 'var(--andaman)'" opacity="0.6" />
      </template>
      <path v-else :d="s.line" fill="none" :stroke="s.color ?? 'var(--nino)'" :stroke-width="s.width ?? 2.7"
        stroke-linecap="round" stroke-linejoin="round" />
    </g>
    <line v-for="(h, i) in hlines" :key="`h${i}`" v-show="clicks >= (h.at ?? 0)" :x1="M.l" :x2="width - M.r.value"
      :y1="Y(h.y)" :y2="Y(h.y)" :stroke="h.color ?? 'var(--ink)'" stroke-width="2.5" :stroke-dasharray="h.dash ? '12 9' : undefined" />
    <circle v-for="(p, i) in points" :key="`p${i}`" v-show="clicks >= (p.at ?? 0)" :cx="X(p.x)" :cy="Y(p.y)" r="9"
      :fill="p.color ?? 'var(--ink)'" stroke="#FFFFFF" stroke-width="3" />
    <line v-if="zero && !bare" class="sc-zero" :x1="M.l" :x2="width - M.r.value" :y1="y0" :y2="y0" />
    <g v-if="!bare" class="sc-ticks">
      <text v-for="v in ticksL" :key="`l${v}`" :x="M.l - 12" :y="Y(v) + 7" text-anchor="end">{{ fmt(v) }}</text>
      <text v-for="v in ticksR" :key="`r${v}`" :x="width - M.r.value + 12" :y="Y(v, 'right') + 7">{{ fmt(v) }}</text>
      <text v-for="t in ticksX" :key="`x${t}`" :x="X(t)" :y="height - M.b + 36" text-anchor="middle">{{ t }}</text>
      <text v-if="yLabel ?? unitLeft" class="sc-title" :x="0" :y="20">{{ yLabel ?? unitLeft }}</text>
      <text v-if="yLabelRight ?? unitRight" class="sc-title" :x="width" :y="20" text-anchor="end">{{ yLabelRight ?? unitRight }}</text>
      <text v-if="xLabel" class="sc-title" :x="(M.l + width - M.r.value) / 2" :y="height - 6" text-anchor="middle">{{ xLabel }}</text>
    </g>
  </svg>
</template>

<style scoped>
/* ชื่อ class ขึ้นต้น sc- ทุกตัว: Slidev/UnoCSS ใช้ class "grid" ฯลฯ ที่ ancestor — ชื่อสั้นจะไปจับเส้นอื่นแล้วทับสี */
.series-chart { display: block; overflow: visible; font-family: 'Anuphan', sans-serif; }
.sc-grid line { stroke: #E6EEF1; stroke-width: 1.5; }
.sc-zero { stroke: #9FB3BC; stroke-width: 1.5; }
.sc-band { fill: var(--event); opacity: 0.55; }
.sc-ticks text { font-size: 20px; fill: var(--ink-3); }
.sc-ticks text.sc-title { font-size: 21px; fill: var(--ink-2); font-weight: 600; }
.sc-series { transition: opacity 0.6s ease; }
.sc-series.hidden { opacity: 0; }
</style>
