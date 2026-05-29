<script setup lang="ts">
import { ref, computed } from 'vue'
import { target, stepValue, levelCount } from '../lib/stepApprox'

const D = 6, YMAX = 4, M = 480
const OX = 40, OW = 425, OY = 215, OH = 200
const sx = (x: number) => OX + (x / D) * OW
const sy = (y: number) => OY - (Math.min(y, YMAX) / YMAX) * OH

const xs = Array.from({ length: M + 1 }, (_, i) => (i / M) * D)
const n = ref(2)

const targetPath = computed(() =>
  xs.map((x, i) => `${i ? 'L' : 'M'}${sx(x).toFixed(1)},${sy(target(x)).toFixed(1)}`).join(' ')
)
// 阶梯路径：逐样本输出常值，水平段 + 竖直跳变
const stepPath = computed(() => {
  let d = ''
  let prev = NaN
  xs.forEach((x, i) => {
    const y = stepValue(target(x), n.value)
    if (i === 0) { d += `M${sx(x).toFixed(1)},${sy(y).toFixed(1)}` }
    else {
      if (y !== prev) d += ` L${sx(x).toFixed(1)},${sy(prev).toFixed(1)}` // 先水平到跳点
      d += ` L${sx(x).toFixed(1)},${sy(y).toFixed(1)}`
    }
    prev = y
  })
  return d
})
const yticks = [0, 1, 2, 3, 4]
</script>

<template>
  <div class="sademo">
    <div class="sa-ctrl">
      <label>逼近阶数 n = <b>{{ n }}</b></label>
      <input type="range" min="0" max="6" v-model.number="n" />
      <span class="sa-tip">阶梯层数 = n·2ⁿ = <b>{{ levelCount(n) }}</b></span>
    </div>

    <svg viewBox="0 0 480 240" class="sa-svg">
      <!-- 坐标轴 -->
      <line :x1="OX" :y1="OY" :x2="OX + OW" :y2="OY" class="sa-axis" />
      <line :x1="OX" :y1="15" :x2="OX" :y2="OY" class="sa-axis" />
      <g v-for="t in yticks" :key="t">
        <line :x1="OX - 4" :y1="sy(t)" :x2="OX" :y2="sy(t)" class="sa-axis" />
        <text :x="OX - 8" :y="sy(t) + 4" class="sa-tick">{{ t }}</text>
      </g>
      <!-- 阶梯函数 X_n -->
      <path :d="stepPath" class="sa-step" />
      <!-- 目标 f -->
      <path :d="targetPath" class="sa-target" />
      <text :x="OX + OW - 4" y="28" class="sa-leg-t">f(x)</text>
      <text :x="OX + OW - 4" y="44" class="sa-leg-s">Xₙ(x)</text>
    </svg>

    <p class="sa-note">
      <b>逼近定理</b>：拖动 n，蓝色阶梯函数 Xₙ 逐点<b>单调增</b>地逼近金色目标 $f\ge 0$。
      每增加 1 阶，量化精度翻倍（误差 &lt; 2⁻ⁿ）。
    </p>
  </div>
</template>

<style scoped>
.sademo { border: 1px solid var(--vp-c-divider); border-radius: 10px; background: var(--vp-c-bg-soft); padding: 14px; margin: 18px 0; }
.sa-ctrl { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.sa-ctrl input[type=range] { flex: 1; min-width: 160px; accent-color: var(--vp-c-brand-1); }
.sa-tip { font-size: 12px; color: var(--vp-c-text-2); }
.sa-svg { width: 100%; max-width: 480px; height: auto; display: block; }
.sa-axis { stroke: var(--vp-c-text-3); stroke-width: 1.2; }
.sa-tick { text-anchor: end; font-size: 11px; fill: var(--vp-c-text-2); }
.sa-target { fill: none; stroke: #b08a47; stroke-width: 2.2; }
.sa-step { fill: none; stroke: var(--vp-c-brand-1); stroke-width: 1.8; }
.sa-leg-t { text-anchor: end; font-size: 12px; fill: #b08a47; font-weight: 700; }
.sa-leg-s { text-anchor: end; font-size: 12px; fill: var(--vp-c-brand-1); font-weight: 700; }
.sa-note { font-size: 13px; line-height: 1.7; margin-top: 8px; }
</style>
