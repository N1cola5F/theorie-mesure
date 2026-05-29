import { describe, it, expect } from 'vitest'
import { target, stepValue, levelCount } from '../docs/.vitepress/theme/lib/stepApprox'

describe('stepApprox', () => {
  const ys = [0, 0.3, 0.7, 1.25, 2.4, 3.8]

  it('target 非负', () => {
    for (let x = 0; x <= 6; x += 0.25) expect(target(x)).toBeGreaterThanOrEqual(0)
  })

  it('X_n(x) ≤ f(x)（下逼近）', () => {
    for (const y of ys) for (let n = 1; n <= 6; n++) {
      expect(stepValue(y, n)).toBeLessThanOrEqual(y + 1e-9)
    }
  })

  it('逐点单调递增：X_n ≤ X_{n+1}', () => {
    for (const y of ys) for (let n = 1; n <= 8; n++) {
      expect(stepValue(y, n)).toBeLessThanOrEqual(stepValue(y, n + 1) + 1e-9)
    }
  })

  it('收敛：未封顶时误差 < 2^{-n}', () => {
    for (const y of ys) for (let n = 3; n <= 8; n++) {
      if (y < n) expect(y - stepValue(y, n)).toBeLessThan(2 ** -n + 1e-12)
    }
  })

  it('封顶：y ≥ n 时取 n', () => {
    expect(stepValue(5, 2)).toBe(2)
    expect(stepValue(3.8, 3)).toBe(3) // 3.8 ≥ 3 → 封顶 3
    expect(stepValue(1.9, 2)).toBe(1.75) // 1.9 < 2 → floor(1.9·4)/4 = 7/4 = 1.75
  })

  it('levelCount = n·2^n', () => {
    expect(levelCount(3)).toBe(24)
    expect(levelCount(5)).toBe(160)
  })
})
