<!--
  ตัวเลขบนจอที่ไม่ได้มาจาก facts.json แต่ claim ประกาศไว้เป็น lit (เช่น ปี 1997 · จำนวนชุด 218 · ขนาดชุด 1–5)
  แสดงตามที่เขียน · check_claims ตรวจว่า v อยู่ใน numbers ของ claim c จริง — ใช้แทนการพิมพ์เลขเองบนหน้า
  <Lit v="1997" c="C01" />
-->
<script setup lang="ts">
defineProps<{ v: string, c: string }>()
</script>

<template>
  <span class="fact" :data-claim="c">{{ v }}</span>
</template>
