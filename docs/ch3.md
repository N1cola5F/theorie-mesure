# 第三章 — Variables aléatoires réelles

*Cadre :* $(\Omega,\mathcal{T},\mathbb{P})$ 概率空间，$X:\Omega\to\mathbb{R}$ 随机变量。研究 **loi**、**fonction de répartition**、**densité**、**espérance**、**indépendance**。

## 3.1 Compléments — Fubini-Tonelli & changement de variable {#sec-3-1}

::: def Déf 3.1.1 — Tribu et mesure produit 乘积 σ-代数与乘积测度
$(E,\mathcal{T},\mu),(F,\mathcal{S},\nu)$：
- $\mathcal{T}\otimes\mathcal{S}=\sigma\big((A\times B)_{A\in\mathcal{T},B\in\mathcal{S}}\big)$；
- $\mu\otimes\nu$ 是唯一满足 $(\mu\otimes\nu)(A\times B)=\mu(A)\nu(B)$ 的测度（约定 $0\cdot\infty=0$）。

例：$\lambda^{\otimes 2}$ 即 $\mathbb{R}^2$ 上的 Lebesgue 测度。
:::

::: theo Th 3.1.1 — Tonelli（$f\ge 0$）
$\mu,\nu$ $\sigma$-finies。对正可测 $f:E\times F\to[0,+\infty]$：
$$\int_{E\times F}\!f\,d(\mu\otimes\nu)=\int_E\!\Big(\int_F f(x,y)\,d\nu\Big)d\mu=\int_F\!\Big(\int_E f(x,y)\,d\mu\Big)d\nu.$$
正性自动保证三式合理（可以 $=+\infty$）。
:::

::: theo Th 3.1.2 — Fubini（$f$ intégrable）
若 $\int_{E\times F}|f|\,d(\mu\otimes\nu)<+\infty$，则 $\mu$-p.p. $x$ 处 $y\mapsto f(x,y)$ $\nu$-可积、$\nu$-p.p. $y$ 类似，且积分可换序（同 Tonelli 公式）。

**实用**：先用 Tonelli 检查 $\int|f|<\infty$，再用 Fubini 换序。
:::

::: theo Th 3.1.3 — Changement de variable 换元公式（$\mathbb{R}^n$）
$\Phi:\Omega\to U$ 双射、$C^1$、且 $\det\mathrm{Jac}_\Phi(x)\ne 0$。则
$$\int_U f(y)\,dy=\int_\Omega (f\circ\Phi)(x)\,|\det\mathrm{Jac}_\Phi(x)|\,dx.$$
（$f\ge 0$ 时无需可积性假设。）
:::

::: exer Exemples 例
- $\displaystyle\int_{0\le x_1\le\cdots\le x_n\le a}\!dx_1\cdots dx_n=\frac{a^n}{n!}$；
- 极坐标 $\Rightarrow\displaystyle\int_{\mathbb{R}}e^{-t^2}\,dt=\sqrt{\pi}$；
- $u=xy,\,v=y$：$\displaystyle\int_{[0,1]^2}\varphi(xy)\,dx\,dy=\int_0^1\varphi(u)(-\ln u)\,du$。
:::

::: attn Attention
Tonelli 与 Fubini 都要求 $\sigma$-finie！例如 $\mathbb{R}$ 上的计数测度不是 $\sigma$-finie，结论可能失败。
:::

## 3.2 Variables aléatoires — Loi, $F_X$, espérance, transfert {#sec-3-2}

::: def Déf 3.2.1 — Variable aléatoire (VA)
$X:(\Omega,\mathcal{T},\mathbb{P})\to(E,\mathcal{S})$ 可测。$E=\mathbb{R}$ 时称 **VA réelle**。
:::

::: def Déf 3.2.2 — Loi $\mathbb{P}_X$（mesure image 像测度）
$$\forall A\in\mathcal{S},\quad\mathbb{P}_X(A)=\mathbb{P}\big(X^{-1}(A)\big)=\mathbb{P}(X\in A).$$
$\mathbb{P}_X$ 是 $(E,\mathcal{S})$ 上的概率测度。
:::

::: def Déf 3.2.3 — Fonction de répartition $F_X$ 分布函数
$$\forall a\in\mathbb{R},\quad F_X(a)=\mathbb{P}(X\le a).$$
:::

::: prop Prop 3.2.2 — Propriétés de $F_X$
- 在 $\mathbb{R}$ 上**递增**；
- **右连续**（càdlàg），左极限存在：$F_X(a^-)=\mathbb{P}(X<a)$，跳跃量 $=\mathbb{P}(X=a)$；
- $\displaystyle\lim_{a\to-\infty}F_X(a)=0$，$\displaystyle\lim_{a\to+\infty}F_X(a)=1$；
- $\mathbb{P}(a<X\le b)=F_X(b)-F_X(a)$。

反之，任何满足这些性质的 $F$ 都唯一对应一个 $\mathbb{R}$ 上的概率测度（loi）。
:::

::: def Déf 3.2.4 — Loi discrète / à densité 离散 / 有密度
- **离散**：$\mathbb{P}_X=\sum_i p_i\,\delta_{x_i}$，$p_i=\mathbb{P}(X=x_i)\ge 0$，$\sum_i p_i=1$；
- **有密度** $f\ge 0$（关于 $\lambda$）：$\displaystyle\mathbb{P}(X\in A)=\int_A f\,d\lambda$，且 $F_X(a)=\int_{-\infty}^a f(t)\,dt$、$\int_{\mathbb{R}}f\,d\lambda=1$。
:::

::: def Déf 3.2.5 — Espérance 期望
当 $X$ 可积（$\mathbb{E}|X|<\infty$）：
$$\mathbb{E}(X)=\int_\Omega X\,d\mathbb{P}.$$
:::

::: theo Th 3.2.1 — Théorème de transfert 转移定理
$g:(E,\mathcal{S})\to(\mathbb{R},\mathcal{B})$ 可测，$g\ge 0$ 或 $g(X)$ 可积：
$$\mathbb{E}\big(g(X)\big)=\int_\Omega g(X)\,d\mathbb{P}=\int_E g\,d\mathbb{P}_X.$$
故只需知道 **loi** $\mathbb{P}_X$ 即可算期望。
- 离散：$\mathbb{E}(g(X))=\sum_i g(x_i)\,p_i$；
- 有密度：$\mathbb{E}(g(X))=\int_{\mathbb{R}}g(t)\,f(t)\,dt$。
:::

::: def Déf 3.2.6 — Variance 方差
$X$ 平方可积（$\mathbb{E}(X^2)<\infty$）：
$$\mathrm{Var}(X)=\mathbb{E}\big[(X-\mathbb{E}X)^2\big]=\mathbb{E}(X^2)-\big(\mathbb{E}X\big)^2\ge 0.$$
:::

::: def Déf 3.2.7 — Indépendance 独立性
- 事件 $A,B$ 独立 $\iff\mathbb{P}(A\cap B)=\mathbb{P}(A)\mathbb{P}(B)$。
- VA $X_1,\dots,X_n$ 独立 $\iff$ loi 为乘积：$\mathbb{P}_{(X_1,\dots,X_n)}=\mathbb{P}_{X_1}\otimes\cdots\otimes\mathbb{P}_{X_n}$，即
$$\forall B_i,\quad\mathbb{P}\Big(\bigcap_i\{X_i\in B_i\}\Big)=\prod_i\mathbb{P}(X_i\in B_i).$$
:::

::: prop Prop 3.2.3 — Conséquences 推论
$X,Y$ 独立且可积：
- $\mathbb{E}(XY)=\mathbb{E}(X)\,\mathbb{E}(Y)$；
- $\mathrm{Var}(X+Y)=\mathrm{Var}(X)+\mathrm{Var}(Y)$；
- 由 Fubini 在乘积空间 $(\Omega,\mathcal{T},\mathbb{P})^{\otimes}$ 上得证。
:::

::: loi Lois usuelles 常用分布
- **Bernoulli** $\mathcal{B}(p)$：$\mathbb{P}(X=1)=p$，$\mathbb{E}=p$，$\mathrm{Var}=p(1-p)$；
- **Binomiale** $\mathcal{B}(n,p)$：$\mathbb{E}=np$，$\mathrm{Var}=np(1-p)$；
- **Poisson** $\mathcal{P}(\lambda)$：$\mathbb{P}(X=k)=e^{-\lambda}\lambda^k/k!$，$\mathbb{E}=\mathrm{Var}=\lambda$；
- **Uniforme** $\mathcal{U}([a,b])$：$f=\frac{1}{b-a}\mathbf{1}_{[a,b]}$，$\mathbb{E}=\frac{a+b}{2}$；
- **Exponentielle** $\mathcal{E}(\lambda)$：$f(t)=\lambda e^{-\lambda t}\mathbf{1}_{t\ge 0}$，$\mathbb{E}=1/\lambda$；
- **Gaussienne** $\mathcal{N}(m,\sigma^2)$：$f(t)=\frac{1}{\sigma\sqrt{2\pi}}e^{-(t-m)^2/2\sigma^2}$，$\mathbb{E}=m$，$\mathrm{Var}=\sigma^2$。
:::
