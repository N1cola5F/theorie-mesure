<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { interval, measure, limitMeasure, targetMeasure, continuityHolds, type Mode } from '../lib/measureContinuity'

const N = 20
const mode = ref<Mode>('inc')
const n = ref(1)
const playing = ref(false)
let timer: any = null

const W = 440, OX = 12
const domain = computed<[number, number]>(() => (mode.value === 'counter' ? [0, N + 2] : [-0.3, 2.3]))
const px = (x: number) => {
  const [lo, hi] = domain.value
  return OX + ((x - lo) / (hi - lo)) * W
}
const iv = computed(() => interval(mode.value, n.value))
const barL = computed(() => px(iv.value.a))
const barR = computed(() => (iv.value.infinite ? OX + W : px(iv.value.b)))
const ticks = computed(() => (mode.value === 'counter' ? [0, 5, 10, 15, 20] : [0, 1, 2]))

const fmt = (x: number) => (x === Infinity ? '+∞' : x.toFixed(3))
const muN = computed(() => measure(mode.value, n.value))
const muLim = computed(() => limitMeasure(mode.value))
const muTgt = computed(() => targetMeasure(mode.value))
const holds = computed(() => continuityHolds(mode.value))
const tgtLabel = computed(() => (mode.value === 'inc' ? '∪ Aₙ = [0,1)' : mode.value === 'dec' ? '∩ Aₙ = [0,1]' : '∩ Aₙ = ∅'))

function stop() { playing.value = false; if (timer) { clearInterval(timer); timer = null } }
function play() {
  if (playing.value) return stop()
  if (n.value >= N) n.value = 1
  playing.value = true
  timer = setInterval(() => {
    if (n.value >= N) return stop()
    n.value++
  }, 350)
}
function setMode(m: Mode) { stop(); mode.value = m; n.value = 1 }
watch(mode, () => { n.value = 1 })
onUnmounted(stop)

const modes: { k: Mode; t: string }[] = [
  { k: 'inc', t: '递增 ↑' }, { k: 'dec', t: '递减 ↓ (有限)' }, { k: 'counter', t: '反例 [n,∞)' }
]
</script>

<template>
  <div class="mcdemo">
    <div class="mc-modes">
      <button v-for="m in modes" :key="m.k" :class="{ active: mode === m.k }" @click="setMode(m.k)">{{ m.t }}</button>
    </div>

    <svg viewBox="0 0 464 96" class="mc-svg">
      <line :x1="OX" y1="60" :x2="OX + W" y2="60" class="mc-axis" />
      <g v-for="t in ticks" :key="'t' + t">
        <line :x1="px(t)" y1="56" :x2="px(t)" y2="64" class="mc-axis" />
        <text :x="px(t)" y="80" class="mc-tick">{{ t }}</text>
      </g>
      <!-- 当前集合 A_n -->
      <rect :x="barL" y="40" :width="Math.max(0, barR - barL)" height="16" rx="3" class="mc-bar" :class="{ inf: iv.infinite }" />
      <polygon v-if="iv.infinite" :points="`${OX + W},38 ${OX + W + 10},48 ${OX + W},58`" class="mc-arrow" />
      <text v-if="iv.infinite" :x="OX + W - 4" y="34" class="mc-inf">+∞</text>
      <text :x="OX" y="22" class="mc-label">A<tspan dy="3" font-size="9">n</tspan> (n = {{ n }})</text>
    </svg>

    <div class="mc-ctrl">
      <button class="mc-play" @click="play">{{ playing ? '⏸ 暂停' : '▶ 播放' }}</button>
      <input type="range" min="1" :max="N" v-model.number="n" @input="stop" />
    </div>

    <div class="mc-read">
      <span>μ(Aₙ) = <b>{{ fmt(muN) }}</b></span>
      <span>lim μ(Aₙ) = <b>{{ fmt(muLim) }}</b></span>
      <span>μ({{ tgtLabel }}) = <b>{{ fmt(muTgt) }}</b></span>
      <span class="mc-eq" :class="holds ? 'ok' : 'bad'">
        {{ holds ? '✓ 连续性成立' : '✗ 连续性失败：μ(Aₙ)≡∞ 不趋于 μ(∩)=0' }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.mcdemo { border: 1px solid var(--vp-c-divider); border-radius: 10px; background: var(--vp-c-bg-soft); padding: 14px; margin: 18px 0; }
.mc-modes { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.mc-modes button, .mc-play {
  border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg);
  color: var(--vp-c-text-1); cursor: pointer; padding: 4px 12px; font-size: 13px;
}
.mc-modes button.active { background: var(--vp-c-brand-1); color: #fff; border-color: var(--vp-c-brand-1); }
.mc-svg { width: 100%; max-width: 464px; height: auto; display: block; }
.mc-axis { stroke: var(--vp-c-text-3); stroke-width: 1.5; }
.mc-tick { text-anchor: middle; font-size: 11px; fill: var(--vp-c-text-2); }
.mc-bar { fill: var(--vp-c-brand-1); opacity: .8; }
.mc-bar.inf { fill: #b71c1c; opacity: .65; }
.mc-arrow { fill: #b71c1c; }
.mc-inf { text-anchor: end; font-size: 12px; fill: #b71c1c; font-weight: 700; }
.mc-label { font-size: 12px; fill: var(--vp-c-text-1); font-weight: 600; }
.mc-ctrl { display: flex; align-items: center; gap: 12px; margin: 8px 0; }
.mc-ctrl input[type=range] { flex: 1; accent-color: var(--vp-c-brand-1); }
.mc-read { display: flex; flex-wrap: wrap; gap: 16px; font-size: 14px; line-height: 1.8; }
.mc-eq.ok { color: #3c6049; font-weight: 700; }
.dark .mc-eq.ok { color: #a9cfb2; }
.mc-eq.bad { color: #b71c1c; font-weight: 700; }
</style>
