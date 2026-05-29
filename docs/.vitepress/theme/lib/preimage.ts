// 逆像与集合运算的纯逻辑（供 Vitest 单测）

export type Op = 'union' | 'inter' | 'diff' | 'comp'

export const OP_SYMBOL: Record<Op, string> = {
  union: 'B₁ ∪ B₂',
  inter: 'B₁ ∩ B₂',
  diff: 'B₁ ∖ B₂',
  comp: 'B₁ᶜ'
}

const uniq = (xs: string[]) => Array.from(new Set(xs)).sort()

/** 对到达域子集做集合运算 */
export function applyOp(op: Op, b1: string[], b2: string[], universe: string[]): string[] {
  const s1 = new Set(b1)
  const s2 = new Set(b2)
  switch (op) {
    case 'union': return uniq([...b1, ...b2])
    case 'inter': return uniq(b1.filter((x) => s2.has(x)))
    case 'diff': return uniq(b1.filter((x) => !s2.has(x)))
    case 'comp': return uniq(universe.filter((x) => !s1.has(x)))
  }
}

/** 逆像 X⁻¹(target) = { e ∈ E : X(e) ∈ target } */
export function preimage(mapping: Record<string, string>, target: string[]): string[] {
  const t = new Set(target)
  return uniq(Object.keys(mapping).filter((e) => t.has(mapping[e])))
}

/** 逆像与运算交换：X⁻¹(op(B₁,B₂)) 应等于 op 作用在各自逆像上 */
export function preimageOfOp(
  mapping: Record<string, string>, op: Op,
  b1: string[], b2: string[], universe: string[]
): string[] {
  return preimage(mapping, applyOp(op, b1, b2, universe))
}

export function opOfPreimages(
  mapping: Record<string, string>, op: Op,
  b1: string[], b2: string[], universe: string[]
): string[] {
  const p1 = preimage(mapping, b1)
  const p2 = preimage(mapping, b2)
  const allE = Object.keys(mapping).sort()
  return applyOp(op, p1, p2, allE)
}
