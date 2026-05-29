// 阶梯函数逼近的纯逻辑（供 Vitest 单测）
// 逼近定理构造：X_n(x) = min( floor(f(x)·2^n)/2^n , n )

/** 目标非负函数 f：演示用，f(x) ≥ 0 */
export function target(x: number): number {
  return 2.2 + 1.6 * Math.sin(1.3 * x)
}

/** 把非负值 y 量化为第 n 个阶梯函数的取值 */
export function stepValue(y: number, n: number): number {
  if (y < 0) y = 0
  if (y >= n) return n // 封顶 n·1_{X≥n}
  return Math.floor(y * 2 ** n) / 2 ** n
}

/** 第 n 个阶梯函数的层数（不含封顶层）= n·2^n */
export function levelCount(n: number): number {
  return n * 2 ** n
}
