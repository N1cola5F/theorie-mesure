import { describe, it, expect } from 'vitest'
import { measure, limitMeasure, targetMeasure, continuityHolds } from '../docs/.vitepress/theme/lib/measureContinuity'

describe('measureContinuity', () => {
  it('μ(A_n) 数值', () => {
    expect(measure('inc', 1)).toBeCloseTo(0)
    expect(measure('inc', 2)).toBeCloseTo(0.5)
    expect(measure('dec', 2)).toBeCloseTo(1.5)
    expect(measure('counter', 5)).toBe(Infinity)
  })

  it('递增/递减(有限)：连续性成立', () => {
    expect(continuityHolds('inc')).toBe(true)
    expect(continuityHolds('dec')).toBe(true)
    expect(limitMeasure('inc')).toBe(targetMeasure('inc'))
  })

  it('反例：μ(A_n)≡∞ 不收敛到 μ(∩)=0', () => {
    expect(limitMeasure('counter')).toBe(Infinity)
    expect(targetMeasure('counter')).toBe(0)
    expect(continuityHolds('counter')).toBe(false)
  })

  it('μ(A_n) 趋于极限值', () => {
    expect(measure('inc', 1000)).toBeCloseTo(limitMeasure('inc'), 2)
    expect(measure('dec', 1000)).toBeCloseTo(limitMeasure('dec'), 2)
  })
})
