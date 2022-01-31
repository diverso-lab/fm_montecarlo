#!/bin/sh

rm -rf results/

mkdir -p final_results/${fm}

ASTAR="a_star"
RANDOM="random_strategy"
FLATMC="flat_montecarlo"
PFLATMC="parallel_flat_montecarlo"
UCTMCTS="uct_mcts"
GREEDYMCTS="greedy_mcts"

runs=30
sim=100

for fm in "pizzas" "GPL" "wget" "jHipster" "tankwar" "mobilemedia2" "WeaFQAs" "aafms_framework-namesAdapted" "busybox-1.18.0"
do
    finalresults="final_results/final_results_${fm}.txt"
    echo "******************************${fm}******************************"
    echo "******************************${fm}******************************" >> ${finalresults}

    echo "==========${RANDOM}=========="
    echo "==========${RANDOM}==========" >> ${finalresults}
    python main_complete_partial_config.py -fm models/${fm}.xml -alg random -min -r ${runs} -mc_sc sim -mc_sv ${sim} >> ${finalresults} 

    echo "==========${FLATMC}=========="
    echo "==========${FLATMC}==========" >> ${finalresults}
    python main_complete_partial_config.py -fm models/${fm}.xml -alg flat -min -r ${runs} -mc_sc sim -mc_sv ${sim} >> ${finalresults} 

    echo "==========${UCTMCTS}=========="
    echo "==========${UCTMCTS}==========" >> ${finalresults}
    python main_complete_partial_config.py -fm models/${fm}.xml -alg mcts -min -r ${runs} -mc_sc sim -mc_sv ${sim} >> ${finalresults} 

    echo "==========${GREEDYMCTS}=========="
    echo "==========${GREEDYMCTS}==========" >> ${finalresults}
    python main_complete_partial_config.py -fm models/${fm}.xml -alg greedy -min -r ${runs} -mc_sc sim -mc_sv ${sim} >> ${finalresults} 

    echo "==========${PFLATMC}=========="    
    echo "==========${PFLATMC}==========" >> ${finalresults}
    python main_complete_partial_config.py -fm models/${fm}.xml -alg flat -min -r ${runs} -p -mc_sc sim -mc_sv ${sim} >> ${finalresults} 

    rm -rf final_results/${fm}
    mv results/ final_results/${fm}
    rm -rf results/
done
