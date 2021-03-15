#!/bin/sh

RUNS=30

for run in `seq $RUNS`
do
   echo "> Executing run $run ..."
   python main_algorithm.py -r $run
done
