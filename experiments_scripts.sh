#!/bin/sh

rm -rf results/

mkdir -p final_results/${fm}

ASTAR="a_star"
RANDOM="random_strategy"
FLATMC="flat_montecarlo"
UCTMCTS="uct_mcts"
GREEDYMCTS="greedy_mcts"

runs=30
sim=100

for fm in "pizzas" "GPL" "wget" "jHipster" "tankwar" "mobilemedia2" "WeaFQAs" "aafms_framework-namesAdapted" "busybox-1.18.0"
do
    finalresults="final_results/final_results_${fm}.txt"
    echo "====================${fm}====================" >> ${finalresults}
    python main_complete_partial_config.py -fm models/${fm}.xml -r ${runs} -it ${sim}
    #echo "==========${ASTAR}==========" >> ${finalresults}
    #python montecarlo_framework/utils/csv_stats.py -f results/${ASTAR}_stats.csv >> ${finalresults}
    echo "==========${RANDOM}==========" >> ${finalresults}
    python montecarlo_framework/utils/csv_stats.py -f results/${RANDOM}_stats.csv >> ${finalresults}
    echo "==========${FLATMC}==========" >> ${finalresults}
    python montecarlo_framework/utils/csv_stats.py -f results/${FLATMC}_stats.csv >> ${finalresults}
    #echo "==========${UCTMCTS}==========" >> ${finalresults}
    #python montecarlo_framework/utils/csv_stats.py -f results/${UCTMCTS}_stats.csv >> ${finalresults}
    #echo "==========${GREEDYMCTS}==========" >> ${finalresults}
    #python montecarlo_framework/utils/csv_stats.py -f results/${GREEDYMCTS}_stats.csv >> ${finalresults}

    rm -rf final_results/${fm}
    mv results/ final_results/${fm}
    rm -rf results/
done
