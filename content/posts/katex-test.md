Title: KaTeX Test
Date: 2020-04-12T19:15+10:00
Category: Site testing
Slug: katex-test
Summary: Mathematical notation arrives.
Tags: diagnostic

It is true that $3 \ge 1$.

A function $f\colon\reals\to\reals$ is said to be *slowly varying* if
$$
\lim_{t \to \infty} \frac{f(tx)}{f(x)} = 1
\qquad \forall x \in \reals
\mfs
$$

$$@
\newcommand{\probop}{\mathbf}
\newcommand{\prob}{\probop{P}}
\newcommand{\expected}{\probop{E}}
$$

The Borel--Cantelli lemma states that if the sequence $(A_n)_{n = 1}^{\infty}$
of events on a common probability space satisfies
$\sum_{n = 1}^{\infty} \prob(A_n) < \infty$ then it must be that
$$
\prob(A_n \; \text{i.o.}) = 0
\mfs
$$
