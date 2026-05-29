<script setup lang="ts">
import { ref, computed } from 'vue'
import { inA, inLimsup, inLiminf, tailInter, type Pattern } from '../lib/limsupLiminf'

const N = 14
const cols = Array.from({ length: N }, (_, i) => i + 1) // 显示项 m = 1..N

const PATTERNS: Pattern[] = [
  { id: 'w1', label: 'ω₁ 总是正面', prefix: [], period: [1] },
  { id: 'w2', label: 'ω₂ 隔次正面', prefix: [], period: [1, 0] },
  { id: 'w3', label: 'ω₃ 每三次一正', prefix: [], period: [1, 0, 0] },
  { id: 'w4', label: 'ω₄ 仅前四次', prefix: [1, 1, 1, 1], period: [0] },
  { id: 'w5', label: 'ω₅ 第三次起常正', prefix: [0, 0], period: [1] }
]

const n = ref(1) // 起始项（1-based）
const cell = (p: Pattern, m: number) => inA(p, m - 1)
const inTail = (m: number) => m >= n.value
const ls = (p: Pattern) => inLimsup(p)
const li = (p: Pattern) => inLiminf(p)
// 「从第 n 项起一直出现」：尾部交（在可见范围内近似，n 足够大即等于 liminf）
const tailAlways = (p: Pattern) => tailInter(p, n.value - 1, N - 1)
</script>

<template>
  <div class="lldemo">
    <div class="ll-ctrl">
      <label>起始项 n = <b>{{ n }}</b></label>
      <input type="range" min="1" :max="N" v-model.number="n" />
      <span class="ll-tip">抛硬币：A<sub>m</sub> = 「第 m 次正面」。深色列为尾部 m ≥ n。</span>
    </div>

    <div class="ll-grid" :style="{ gridTemplateColumns: `150px repeat(${N}, 1fr) 70px 86px` }">
      <div class="ll-h"></div>
      <div v-for="m in cols" :key="'h' + m" class="ll-h" :class="{ tail: inTail(m) }">{{ m }}</div>
      <div class="ll-h ls">limsup</div>
      <div class="ll-h li">从n起</div>

      <template v-for="p in PATTERNS" :key="p.id">
        <div class="ll-name">{{ p.label }}</div>
        <div v-for="m in cols" :key="p.id + m"
          class="ll-cell" :class="{ on: cell(p, m), tail: inTail(m) }"></div>
        <div class="ll-badge" :class="{ yes: ls(p) }">{{ ls(p) ? '∈' : '∉' }}</div>
        <div class="ll-badge" :class="{ yesli: tailAlways(p) }">{{ tailAlways(p) ? '一直在' : '否' }}</div>
      </template>
    </div>

    <p class="ll-note">
      <b>limsup</b> = 出现于<b>无限多个</b> A<sub>n</sub>（金色 ∈）：ω₁,ω₂,ω₃,ω₅。
      <b>liminf</b> = 从某项起<b>一直</b>出现（绿色）：仅 ω₁,ω₅ —— 增大 n，「从n起」一列即收敛到 liminf。
      ω₄ 只出现有限次，既不在 limsup 也不在 liminf。
    </p>
  </div>
</template>

<style scoped>
.lldemo {
  border: 1px solid var(--vp-c-divider); border-radius: 10px;
  background: var(--vp-c-bg-soft); padding: 14px; margin: 18px 0;
}
.ll-ctrl { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
.ll-ctrl input[type=range] { flex: 1; min-width: 160px; accent-color: var(--vp-c-brand-1); }
.ll-tip { font-size: 12px; color: var(--vp-c-text-2); }
.ll-grid { display: grid; gap: 3px; align-items: center; font-size: 12px; overflow-x: auto; }
.ll-h { text-align: center; color: var(--vp-c-text-2); font-weight: 600; padding: 2px 0; }
.ll-h.tail { color: var(--vp-c-brand-1); }
.ll-h.ls { color: #b08a47; } .ll-h.li { color: #3c6049; }
.dark .ll-h.li { color: #a9cfb2; }
.ll-name { font-weight: 600; font-size: 12.5px; }
.ll-cell {
  height: 20px; border-radius: 4px; background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
}
.ll-cell.on { background: var(--vp-c-text-3); }
.ll-cell.tail { border-color: var(--vp-c-brand-1); }
.ll-cell.on.tail { background: var(--vp-c-brand-1); }
.ll-badge { text-align: center; font-weight: 700; color: var(--vp-c-text-3); }
.ll-badge.yes { color: #b08a47; }
.ll-badge.yesli { color: #3c6049; }
.dark .ll-badge.yesli { color: #a9cfb2; }
.ll-note { font-size: 13px; line-height: 1.7; margin-top: 12px; color: var(--vp-c-text-1); }
</style>
