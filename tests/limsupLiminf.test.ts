import { describe, it, expect } from 'vitest'
import { inA, inLimsup, inLiminf, tailUnion, tailInter, type Pattern } from '../docs/.vitepress/theme/lib/limsupLiminf'

const always: Pattern = { id: 'a', label: '总在', prefix: [], period: [1] }
const alt: Pattern = { id: 'b', label: '交替', prefix: [], period: [1, 0] }
const finite: Pattern = { id: 'c', label: '仅前4次', prefix: [1, 1, 1, 1], period: [0] }
const eventually: Pattern = { id: 'd', label: '第3项起常在', prefix: [0, 0], period: [1] }

describe('limsupLiminf', () => {
  it('inA 按前缀+周期取值', () => {
    expect(inA(alt, 0)).toBe(true)
    expect(inA(alt, 1)).toBe(false)
    expect(inA(finite, 3)).toBe(true)
    expect(inA(finite, 4)).toBe(false)
    expect(inA(eventually, 1)).toBe(false)
    expect(inA(eventually, 2)).toBe(true)
  })

  it('inLimsup：出现无限多次', () => {
    expect(inLimsup(always)).toBe(true)
    expect(inLimsup(alt)).toBe(true)
    expect(inLimsup(finite)).toBe(false)
    expect(inLimsup(eventually)).toBe(true)
  })

  it('inLiminf：最终一直在', () => {
    expect(inLiminf(always)).toBe(true)
    expect(inLiminf(alt)).toBe(false)
    expect(inLiminf(finite)).toBe(false)
    expect(inLiminf(eventually)).toBe(true)
  })

  it('liminf ⊂ limsup', () => {
    for (const p of [always, alt, finite, eventually]) {
      if (inLiminf(p)) expect(inLimsup(p)).toBe(true)
    }
  })

  it('尾部交收敛到 liminf：n 足够大时 tailInter == inLiminf', () => {
    const end = 40
    for (const p of [always, alt, finite, eventually]) {
      expect(tailInter(p, 20, end)).toBe(inLiminf(p))
    }
    expect(tailUnion(alt, 20, end)).toBe(true)
  })
})
