<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vitepress'
import {
  CONCEPT_GRAPH,
  findConceptByKey,
  findConceptByLabel,
  parseNodeKey,
  type ConceptNode
} from '../lib/conceptMap'

const router = useRouter()
const host = ref<HTMLElement | null>(null)
const tip = ref<{ show: boolean; x: number; y: number; text: string }>({
  show: false, x: 0, y: 0, text: ''
})

let panZoom: any = null
let observer: MutationObserver | null = null
let lastDark: boolean | null = null

const isDark = () =>
  typeof document !== 'undefined' &&
  document.documentElement.classList.contains('dark')

function resolveNode(g: Element): ConceptNode | undefined {
  return findConceptByKey(parseNodeKey(g.id)) ||
    findConceptByLabel(g.textContent || '')
}

async function render() {
  if (!host.value) return
  const mermaid = (await import('mermaid')).default
  const { default: svgPanZoom } = await import('svg-pan-zoom')

  if (panZoom) { try { panZoom.destroy() } catch {} panZoom = null }
  lastDark = isDark()
  mermaid.initialize({
    startOnLoad: false,
    theme: lastDark ? 'dark' : 'neutral',
    flowchart: { curve: 'basis', padding: 12 }
  })
  const id = 'concept-map-' + Math.random().toString(36).slice(2)
  const { svg } = await mermaid.render(id, CONCEPT_GRAPH)
  host.value.innerHTML = svg

  const svgEl = host.value.querySelector('svg') as SVGSVGElement | null
  if (!svgEl) return
  svgEl.style.maxWidth = 'none'
  svgEl.setAttribute('width', '100%')
  svgEl.setAttribute('height', '100%')

  host.value.querySelectorAll('g.node').forEach((g) => {
    const node = resolveNode(g)
    if (!node) return
    ;(g as HTMLElement).style.cursor = 'pointer'
    g.addEventListener('click', () => router.go(node.anchor))
    g.addEventListener('mouseenter', (e) => {
      const ev = e as MouseEvent
      tip.value = { show: true, x: ev.offsetX + 16, y: ev.offsetY + 16, text: node.def }
    })
    g.addEventListener('mousemove', (e) => {
      const ev = e as MouseEvent
      tip.value.x = ev.offsetX + 16
      tip.value.y = ev.offsetY + 16
    })
    g.addEventListener('mouseleave', () => { tip.value.show = false })
  })

  panZoom = svgPanZoom(svgEl, {
    zoomEnabled: true, controlIconsEnabled: false,
    fit: true, center: true, minZoom: 0.5, maxZoom: 8
  })
}

const zoomIn = () => panZoom?.zoomBy(1.3)
const zoomOut = () => panZoom?.zoomBy(0.77)
const reset = () => { panZoom?.resetZoom(); panZoom?.center(); panZoom?.fit() }

onMounted(() => {
  render()
  observer = new MutationObserver(() => {
    if (isDark() !== lastDark) render()
  })
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
})
onUnmounted(() => {
  observer?.disconnect()
  if (panZoom) { try { panZoom.destroy() } catch {} }
})
</script>

<template>
  <div class="concept-map">
    <div class="cm-toolbar">
      <span class="cm-hint">🖱 拖动平移 · 滚轮缩放 · 点击节点跳转 · 悬停看定义</span>
      <span class="cm-btns">
        <button @click="zoomIn" title="放大">＋</button>
        <button @click="zoomOut" title="缩小">－</button>
        <button @click="reset" title="复位">⟳</button>
      </span>
    </div>
    <div ref="host" class="cm-host"></div>
    <div v-show="tip.show" class="cm-tip" :style="{ left: tip.x + 'px', top: tip.y + 'px' }">
      {{ tip.text }}
    </div>
  </div>
</template>

<style scoped>
.concept-map {
  position: relative;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
  padding: 8px;
  margin: 18px 0;
}
.cm-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  gap: 8px; flex-wrap: wrap; margin-bottom: 6px;
}
.cm-hint { font-size: 12px; color: var(--vp-c-text-2); }
.cm-btns button {
  width: 30px; height: 28px; margin-left: 4px;
  border: 1px solid var(--vp-c-divider); border-radius: 6px;
  background: var(--vp-c-bg); color: var(--vp-c-text-1);
  cursor: pointer; font-size: 15px; line-height: 1;
}
.cm-btns button:hover { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.cm-host { width: 100%; height: 440px; overflow: hidden; }
.cm-tip {
  position: absolute; max-width: 260px; pointer-events: none;
  background: var(--vp-c-bg); color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-brand-1); border-radius: 6px;
  padding: 6px 10px; font-size: 13px; line-height: 1.5;
  box-shadow: 0 4px 14px rgba(0,0,0,.16); z-index: 20;
}
</style>
