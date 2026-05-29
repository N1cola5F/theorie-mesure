# 概率 ↔ 测度论 词典 · Lexique

测度论与概率论是同一套数学的两种语言。下表给出核心对照。

## 核心对照 Correspondance fondamentale

| Théorie de la mesure 测度论 | Théorie des probabilités 概率论 | 说明 |
| :-- | :-- | :-- |
| Ensemble $\Omega$ | Univers $\Omega$ | 样本空间 |
| Tribu $\mathcal{T}$（$\sigma$-algèbre） | Ensemble des événements | 事件域 |
| Partie $A\in\mathcal{T}$ | Événement | 事件 |
| $\emptyset$ | Événement impossible | 不可能事件 |
| $\Omega$ | Événement certain | 必然事件 |
| $A,B$ disjoints | $A,B$ incompatibles | 互不相容 |
| Mesure $\mu$ avec $\mu(\Omega)=1$ | Probabilité $\mathbb{P}$ | 概率测度 |
| Fonction mesurable $X$ | Variable aléatoire | 随机变量 |
| Mesure image $\mu_X=\mu\circ X^{-1}$ | Loi $\mathbb{P}_X$ | 分布 |
| Intégrale $\int X\,d\mu$ | Espérance $\mathbb{E}(X)$ | 期望 |
| $\int_A X\,d\mu$ | $\mathbb{E}(X\mathbf{1}_A)$ | 条件求和 |
| $\mu$-presque partout (p.p.) | $\mathbb{P}$-presque sûrement (p.s.) | 几乎处处 / 几乎必然 |
| Densité $f=\dfrac{d\mu}{d\lambda}$ | Densité de probabilité | 概率密度 |
| Mesure produit $\mu\otimes\nu$ | Indépendance | 独立性 |

## 关键定理 ↔ 概率结论

| 测度论 | 概率论应用 |
| :-- | :-- |
| Borel-Cantelli（$\sum\mu(A_n)<\infty\Rightarrow\mu(\limsup A_n)=0$） | 「几乎必然只发生有限次」 |
| Continuité de la mesure 测度连续性 | 分布函数 $F_X$ 的右连续性与极限 |
| TCM / Fatou / TCD 收敛三定理 | 期望与极限交换、大数律证明工具 |
| Fubini-Tonelli | 独立变量 $\mathbb{E}(XY)=\mathbb{E}(X)\mathbb{E}(Y)$ |
| Théorème de transfert 转移定理 | 由 loi 计算 $\mathbb{E}(g(X))$ |

> 记忆要点：**概率 = 总测度为 1 的测度；随机变量 = 可测函数；期望 = 积分**。
