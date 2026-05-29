// limsup / liminf 集合序列的纯逻辑（供 Vitest 单测）
// 元素的成员模式用「前缀 + 周期」表示，使 limsup/liminf 可判定。

export interface Pattern {
  id: string
  label: string
  prefix: number[]  // 前若干项（0/1）
  period: number[]  // 此后无限重复的周期段（0/1）
}

/** 元素在第 n 项 A_n 中是否出现（n 从 0 开始） */
export function inA(p: Pattern, n: number): boolean {
  if (n < p.prefix.length) return p.prefix[n] === 1
  const k = (n - p.prefix.length) % p.period.length
  return p.period[k] === 1
}

/** 出现于无限多个 A_n ⟺ 周期段含 1 ⟺ ∈ limsup */
export function inLimsup(p: Pattern): boolean {
  return p.period.some((v) => v === 1)
}

/** 从某项起一直出现 ⟺ 周期段全为 1 ⟺ ∈ liminf */
export function inLiminf(p: Pattern): boolean {
  return p.period.every((v) => v === 1)
}

/** 尾部并 ∪_{n≤m≤end} A_m */
export function tailUnion(p: Pattern, start: number, end: number): boolean {
  for (let m = start; m <= end; m++) if (inA(p, m)) return true
  return false
}

/** 尾部交 ∩_{n≤m≤end} A_m */
export function tailInter(p: Pattern, start: number, end: number): boolean {
  for (let m = start; m <= end; m++) if (!inA(p, m)) return false
  return true
}
