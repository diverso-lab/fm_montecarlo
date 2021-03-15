#!/bin/sh

RUNS=30
FM="aafms_framework_simple_impl"
ITERATIONS=75
EXPLORATION_WEIGHT=0.5

python experiments_config.py

for run in `seq $RUNS`
do
   echo "> Executing run $run ..."
   python algorithm_p3.py -r $run -fm $FM -it $ITERATIONS -ew $EXPLORATION_WEIGHT
done
