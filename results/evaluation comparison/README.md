As explained in the final Note about the trade-off between reproducibility and performance of the Monte Carlo methods,
we have modified our framework to provide maximum reproducibility, by using *sorted* data structures in all cases, defining when necessary a total order between the states.
This significally impacts and degrades the performance of the framework as shown in the reproducible experiments for 1000 simulations, in constrast to the efficient original implementation of the framework (see experiments for 5000 simulations).

So, for replication purpose we have maintained both version of the Monte Carlo framework, currently available at:

1. (Master branch) The current version of the framework provides reproducibility of the experiments.
2. (commit e386770b64ed27a6c631e3c70ccf216a20cec24d). The original efficient version of the framework.

Our plan is to provide only support to the efficient version in a separate branch.

