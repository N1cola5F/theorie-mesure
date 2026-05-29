import { describe, it, expect } from 'vitest'
import {
  CONCEPT_NODES,
  findConceptByLabel,
  parseNodeKey,
  findConceptByKey
} from '../docs/.vitepress/theme/lib/conceptMap'

describe('conceptMap', () => {
  it('每个节点都有锚点与定义', () => {
    for (const n of CONCEPT_NODES) {
      expect(n.anchor).toMatch(/^\/ch[123]#/)
      expect(n.def.length).toBeGreaterThan(0)
    }
  })

  it('findConceptByLabel 命中已知标签', () => {
    expect(findConceptByLabel('Tribu σ-代数')?.key).toBe('TRIBU')
    expect(findConceptByLabel('Espérance 期望')?.key).toBe('ESPERANCE')
    expect(findConceptByLabel('未知节点 xyz')).toBeUndefined()
  })

  it('parseNodeKey 解析 mermaid DOM id', () => {
    expect(parseNodeKey('flowchart-OMEGA-3')).toBe('OMEGA')
    expect(parseNodeKey('flowchart-TCD-12')).toBe('TCD')
    expect(parseNodeKey('not-a-node')).toBeUndefined()
  })

  it('findConceptByKey 查找', () => {
    expect(findConceptByKey('LOI')?.anchor).toBe('/ch3#sec-3-2')
    expect(findConceptByKey('NOPE')).toBeUndefined()
  })
})
