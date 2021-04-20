# Monte Carlo Tree Search for feature model analyses: a new framework for decision-making
This repository contains all the resources and artifacts of the paper entitled *Monte Carlo Tree Search for feature model analyses: a new framework for decision-making* submitted in the 25th International Systems and Software Product Line Conference (SPLC 2021) by the authors José Miguel Horcas, José A. Galindo, Ruben Heradio, David Fernández-Amoros, and David Benavides.

## Artifact description
We present a [**Monte Carlo conceptual framework**](montecarlo4fms/) that allows analyzing SPL problems by modeling them as a sequence of decision-steps and solving them with Monte Carlo techniques.
The details of the core components of the [**Monte Carlo conceptual framework**](montecarlo4fms/) are described [here](montecarlo4fms/README.md). The framework includes:
- A set of interfaces to be implemented in order to model SPL problems as sequences of *(state, actions)* pairs.
- An implementation of several Monte Carlo methods, including the Monte Carlo Tree Search method, ready to be used to solve any problem which implements the aforementioned interfaces.

The Monte Carlo framework has been developed on top of the [Python framework for automated analysis of feature models](https://github.com/diverso-lab/core) proposed by [Galindo and Benavides](https://doi.org/10.1145/3382026.3425773).

To illustrate the usage of the Monte Carlo framework, we have modeled and analyzed several problems of SPL by proposing two concrete implementation of the *(state, actions)* interfaces:
- An implementation of *(state, actions)* where states represent configurations of a feature model.
- An implementation of *(state, actions)* where states represent feature models.

The analysis of each problem using those definitions are described below.

## Requirements
- [Python 3.9+](https://www.python.org/)
The framework has been tested in Windows and Linux.

## Analyzing problems with the Monte Carlo framework
The following use case diagram shows the four problems that have been implemented.

![Core](img/heatmap.png)


![Core](img/usecases.png)

## How to


## References
- [Python framework for automated analysis of feature models](https://github.com/diverso-lab/core)