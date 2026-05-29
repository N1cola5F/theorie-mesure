import { describe, it, expect } from 'vitest'
import { applyOp, preimage, preimageOfOp, opOfPreimages, type Op } from '../docs/.vitepress/theme/lib/preimage'

const F = ['a', 'b', 'c', 'd']
// X: E={1..6} -> F
const X: Record<string, string> = { '1': 'a', '2': 'a', '3': 'b', '4': 'c', '5': 'c', '6': 'd' }
const B1 = ['a', 'b']
const B2 = ['b', 'c']

describe('preimage', () => {
  it('applyOp 基本运算', () => {
    expect(applyOp('union', B1, B2, F)).toEqual(['a', 'b', 'c'])
    expect(applyOp('inter', B1, B2, F)).toEqual(['b'])
    expect(applyOp('diff', B1, B2, F)).toEqual(['a'])
    expect(applyOp('comp', B1, B2, F)).toEqual(['c', 'd'])
  })

  it('preimage 计算正确', () => {
    expect(preimage(X, ['a'])).toEqual(['1', '2'])
    expect(preimage(X, ['c', 'd'])).toEqual(['4', '5', '6'])
    expect(preimage(X, [])).toEqual([])
  })

  it('逆像与运算交换：X⁻¹(op) = op(X⁻¹) 对所有运算成立', () => {
    const ops: Op[] = ['union', 'inter', 'diff', 'comp']
    for (const op of ops) {
      expect(preimageOfOp(X, op, B1, B2, F)).toEqual(opOfPreimages(X, op, B1, B2, F))
    }
  })
})
