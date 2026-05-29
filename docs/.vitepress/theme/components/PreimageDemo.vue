<script setup lang="ts">
import { ref, computed } from 'vue'
import { applyOp, preimage, opOfPreimages, OP_SYMBOL, type Op } from '../lib/preimage'

const E = ['1', '2', '3', '4', '5', '6']
const F = ['a', 'b', 'c', 'd']
const X: Record<string, string> = { '1': 'a', '2': 'a', '3': 'b', '4': 'c', '5': 'c', '6': 'd' }

const EY: Record<string, number> = { '1': 40, '2': 80, '3': 120, '4': 160, '5': 200, '6': 240 }
const FY: Record<string, number> = { a: 70, b: 120, c: 170, d: 220 }
const EX = 70, FX = 390

const b1 = ref<string[]>(['a', 'b'])
const b2 = ref<string[]>(['b', 'c'])
const op = ref<Op>('union')

const target = computed(() => applyOp(op.value, b1.value, b2.value, F))
const pre = computed(() => preimage(X, target.value))
const rhs = computed(() => opOfPreimages(X, op.value, b1.value, b2.value, F))
const equal = computed(() => JSON.stringify(pre.value) === JSON.stringify(rhs.value))

const inTarget = (f: string) => target.value.includes(f)
const inPre = (e: string) => pre.value.includes(e)
function memb(f: string) {
  const i1 = b1.value.includes(f), i2 = b2.value.includes(f)
  return i1 && i2 ? 'both' : i1 ? 'b1' : i2 ? 'b2' : 'none'
}
function toggle(set: 'b1' | 'b2', f: string) {
  const r = set === 'b1' ? b1 : b2
  r.value = r.value.includes(f) ? r.value.filter((x) => x !== f) : [...r.value, f].sort()
}
const ops: Op[] = ['union', 'inter', 'diff', 'comp']
const opLabel: Record<Op, string> = { union: '∪ 并', inter: '∩ 交', diff: '∖ 差', comp: 'ᶜ 补' }
</script>

<template>
  <div class="pdemo">
    <div class="pd-controls">
      <span class="pd-label">运算 Opération：</span>
      <button v-for="o in ops" :key="o" :class="{ active: op === o }" @click="op = o">
        {{ opLabel[o] }}
      </button>
      <span class="pd-tip">点击右侧 F 节点下方按钮，调整其属于 B₁ / B₂</span>
    </div>

    <svg viewBox="0 0 460 280" class="pd-svg">
      <!-- 映射连线 -->
      <line v-for="e in E" :key="'l' + e"
        :x1="EX + 14" :y1="EY[e]" :x2="FX - 14" :y2="FY[X[e]]"
        :class="['pd-edge', { hot: inPre(e) }]" />
      <!-- E 元素 -->
      <g v-for="e in E" :key="'e' + e">
        <circle :cx="EX" :cy="EY[e]" r="14" :class="['pd-node', { pre: inPre(e) }]" />
        <text :x="EX" :y="EY[e] + 4" class="pd-txt">{{ e }}</text>
      </g>
      <!-- F 元素 -->
      <g v-for="f in F" :key="'f' + f">
        <circle :cx="FX" :cy="FY[f]" r="15"
          :class="['pd-node', 'm-' + memb(f), { tgt: inTarget(f) }]" />
        <text :x="FX" :y="FY[f] + 4" class="pd-txt">{{ f }}</text>
      </g>
      <text :x="EX" y="20" class="pd-cap">E</text>
      <text :x="FX" y="20" class="pd-cap">F</text>
    </svg>

    <div class="pd-fbtns">
      <span v-for="f in F" :key="'btn' + f" class="pd-fbtn">
        <b>{{ f }}</b>
        <button :class="{ on: b1.includes(f) }" @click="toggle('b1', f)">B₁</button>
        <button :class="{ on: b2.includes(f) }" @click="toggle('b2', f)">B₂</button>
      </span>
    </div>

    <div class="pd-result">
      <div>目标集 {{ OP_SYMBOL[op] }} = {{ '{' + target.join(', ') + '}' }}</div>
      <div>X⁻¹({{ OP_SYMBOL[op] }}) = <b>{{ '{' + pre.join(', ') + '}' }}</b></div>
      <div>{{ op === 'comp' ? '(X⁻¹B₁)ᶜ' : 'X⁻¹B₁ ' + opLabel[op].slice(0,1) + ' X⁻¹B₂' }}
        = {{ '{' + rhs.join(', ') + '}' }}</div>
      <div :class="['pd-eq', equal ? 'ok' : 'bad']">
        {{ equal ? '✓ 两者相等 —— 逆像与运算交换' : '✗ 不一致' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.pdemo {
  border: 1px solid var(--vp-c-divider); border-radius: 10px;
  background: var(--vp-c-bg-soft); padding: 14px; margin: 18px 0;
}
.pd-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-bottom: 8px; }
.pd-label { font-weight: 600; }
.pd-controls button, .pd-fbtn button {
  border: 1px solid var(--vp-c-divider); border-radius: 6px;
  background: var(--vp-c-bg); color: var(--vp-c-text-1); cursor: pointer;
  padding: 3px 10px; font-size: 13px;
}
.pd-controls button.active { background: var(--vp-c-brand-1); color: #fff; border-color: var(--vp-c-brand-1); }
.pd-tip { font-size: 12px; color: var(--vp-c-text-2); margin-left: auto; }
.pd-svg { width: 100%; max-width: 460px; height: auto; display: block; margin: 0 auto; }
.pd-node { fill: var(--vp-c-bg); stroke: var(--vp-c-text-3); stroke-width: 1.5; }
.pd-node.m-b1 { fill: #cfe0f3; }
.pd-node.m-b2 { fill: #d2ead7; }
.pd-node.m-both { fill: #e0d6ef; }
.pd-node.tgt { stroke: var(--vp-c-brand-1); stroke-width: 3.5; }
.pd-node.pre { fill: #f3e2c0; stroke: #b08a47; stroke-width: 3; }
.dark .pd-node.m-b1 { fill: #2a3a4f; }
.dark .pd-node.m-b2 { fill: #25402c; }
.dark .pd-node.m-both { fill: #382f4a; }
.dark .pd-node.pre { fill: #4a3c1f; }
.pd-txt { text-anchor: middle; font-size: 13px; fill: var(--vp-c-text-1); font-weight: 600; }
.pd-cap { text-anchor: middle; font-size: 14px; fill: var(--vp-c-text-2); font-weight: 700; }
.pd-edge { stroke: var(--vp-c-divider); stroke-width: 1.5; }
.pd-edge.hot { stroke: #b08a47; stroke-width: 2.5; }
.pd-fbtns { display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; margin: 10px 0; }
.pd-fbtn { display: inline-flex; align-items: center; gap: 4px; }
.pd-fbtn button.on { background: var(--vp-c-brand-1); color: #fff; border-color: var(--vp-c-brand-1); }
.pd-result { font-size: 14px; line-height: 1.9; margin-top: 6px; }
.pd-eq.ok { color: #3c6049; font-weight: 700; }
.dark .pd-eq.ok { color: #a9cfb2; }
.pd-eq.bad { color: #b71c1c; font-weight: 700; }
</style>
