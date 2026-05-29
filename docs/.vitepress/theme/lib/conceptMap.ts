// ConceptMap 纯逻辑：概念节点定义 + 按标签查找（供 Vitest 单测）

export interface ConceptNode {
  key: string        // mermaid 节点 id
  label: string      // 显示文本（含中法双语）
  anchor: string     // 点击跳转目标
  def: string        // 悬停定义
}

export const CONCEPT_NODES: ConceptNode[] = [
  { key: 'OMEGA', label: 'Ω 集合 / Univers', anchor: '/ch1#sec-1-1', def: '样本空间 Ω：一切结果的全集。' },
  { key: 'TRIBU', label: 'Tribu σ-代数', anchor: '/ch1#sec-1-3', def: '对补集与可数并封闭的子集族，构成事件域。' },
  { key: 'MESURE', label: 'Mesure 测度', anchor: '/ch1#sec-1-4', def: 'μ:𝒯→[0,∞]，μ(∅)=0 且 σ-可加。' },
  { key: 'PROBA', label: 'Probabilité ℙ', anchor: '/ch1#sec-1-4', def: '总测度为 1 的测度：μ(Ω)=1。' },
  { key: 'MESURABLE', label: 'Fonction mesurable 可测函数', anchor: '/ch2#sec-2-2', def: '逆像保持可测性：∀B∈𝒮, f⁻¹(B)∈𝒯。' },
  { key: 'INTEGRALE', label: 'Intégrale 积分', anchor: '/ch2#sec-2-3', def: 'Lebesgue 积分：阶梯→正→实，四步构造。' },
  { key: 'TCD', label: 'TCM / Fatou / TCD', anchor: '/ch2#sec-2-3p', def: '三大收敛定理：极限与积分交换。' },
  { key: 'VA', label: 'Variable aléatoire 随机变量', anchor: '/ch3#sec-3-2', def: '概率空间上的可测函数 X:Ω→ℝ。' },
  { key: 'LOI', label: 'Loi ℙ_X 分布', anchor: '/ch3#sec-3-2', def: '像测度 ℙ_X(A)=ℙ(X∈A)。' },
  { key: 'ESPERANCE', label: 'Espérance 期望', anchor: '/ch3#sec-3-2', def: 'E(X)=∫X dℙ；转移定理 E(g(X))=∫g dℙ_X。' }
]

export const CONCEPT_GRAPH = `flowchart TB
  OMEGA["Ω 集合 / Univers"] --> TRIBU["Tribu σ-代数"]
  TRIBU --> MESURE["Mesure 测度"]
  MESURE --> PROBA["Probabilité ℙ"]
  TRIBU --> MESURABLE["Fonction mesurable 可测函数"]
  MESURABLE --> INTEGRALE["Intégrale 积分"]
  INTEGRALE --> TCD["TCM / Fatou / TCD"]
  MESURABLE --> VA["Variable aléatoire 随机变量"]
  PROBA --> VA
  VA --> LOI["Loi ℙ_X 分布"]
  INTEGRALE --> ESPERANCE["Espérance 期望"]
  VA --> ESPERANCE`

/** 根据 mermaid 渲染出的节点文本，匹配对应概念节点（按 label 首词/包含关系） */
export function findConceptByLabel(text: string): ConceptNode | undefined {
  const t = (text || '').trim()
  if (!t) return undefined
  // 优先精确包含 label 的首段（mermaid 可能把 label 拆成多行）
  return CONCEPT_NODES.find((n) => {
    const head = n.label.split(/[\s/]/)[0]
    return t.includes(head)
  })
}

/** 从 mermaid 生成的节点 DOM id（形如 flowchart-OMEGA-3）解析出 key */
export function parseNodeKey(domId: string): string | undefined {
  const m = /^flowchart-([A-Za-z0-9_]+)-\d+$/.exec(domId || '')
  return m?.[1]
}

export function findConceptByKey(key: string | undefined): ConceptNode | undefined {
  if (!key) return undefined
  return CONCEPT_NODES.find((n) => n.key === key)
}
