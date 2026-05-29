// 测度连续性的纯逻辑（供 Vitest 单测）
// 三种集合列：递增 / 递减(有限) / 反例(递减但测度无穷)

export type Mode = 'inc' | 'dec' | 'counter'

export interface Interval { a: number; b: number; infinite: boolean }

/** 第 n 个集合 A_n 表示为区间（n ≥ 1） */
export function interval(mode: Mode, n: number): Interval {
  switch (mode) {
    case 'inc': return { a: 0, b: 1 - 1 / n, infinite: false }       // [0, 1-1/n] ↑ [0,1)
    case 'dec': return { a: 0, b: 1 + 1 / n, infinite: false }       // [0, 1+1/n] ↓ [0,1]
    case 'counter': return { a: n, b: Infinity, infinite: true }     // [n, +∞) ↓ ∅
  }
}

/** μ(A_n) = Lebesgue 长度 */
export function measure(mode: Mode, n: number): number {
  const iv = interval(mode, n)
  return iv.infinite ? Infinity : Math.max(0, iv.b - iv.a)
}

/** lim_n μ(A_n) */
export function limitMeasure(mode: Mode): number {
  switch (mode) {
    case 'inc': return 1
    case 'dec': return 1
    case 'counter': return Infinity
  }
}

/** μ(目标集)：递增取 μ(∪A_n)，递减取 μ(∩A_n) */
export function targetMeasure(mode: Mode): number {
  switch (mode) {
    case 'inc': return 1        // ∪ = [0,1)
    case 'dec': return 1        // ∩ = [0,1]
    case 'counter': return 0    // ∩ = ∅
  }
}

/** 连续性是否成立：lim μ(A_n) == μ(目标集) */
export function continuityHolds(mode: Mode): boolean {
  return limitMeasure(mode) === targetMeasure(mode)
}
