from cmd import Cmd
import subprocess

class MyPrompt(Cmd):
    prompt = 'montecarlo> '
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, args):
        print("Thank you for using our montecarlo FM implementation!")
        return True
 
    def do_comparison_aafm(self, args):
        '''
        The experiment of the evaluation compares the different Monte Carlo methods over the problem 
        of finding defective configurations in both the AAFMs Python Framework and the jHipster feature 
        models. To replicate the experiments of the evaluation, we provide the following scripts that 
        can be executed as follows:

        For the AAFMs Python Framework feature model (results here):
            python main_comparison_aafm.py -it 1000 -s 2021 -m MCTS
        
        Note that the -it ITERATIONS parameter here is the maximum number of iterations/simulations to be 
        performed (5000 default). The script will run the Monte Carlo methods from 1 to ITERATIONS with a 
        step of 250 iterations.
        
        Note: Setting up the random seed, the execution can take a while (around 1 hour for each experiment)
        so be patient. For impatients, we also present additional results for a small-quick comparison using 
        the -e option for the excerpt version of the model. To understand this, read the final note at the end of this document.
        Change the -m parameter to flat for flat Monte Carlo method, Greedy for Greedy MCTS, and random 
        for Random Sampling. For the Random Sampling, in case of using the complete version of the feature 
        model (10e9 configurations) or other large-scale feature models you need to use the BDD Sampler of Heradio 
        et al.). The integration of BDD Sampler within our framework is out of scope of this work, thus, there is 
        not script at this moment to automate the random sampling results from the BDD Sampler.
        '''
        subprocess.call(['python','./main_comparison_aafm.py'] + args.split())

    def do_comparison_jhipster(self, args):
        '''
        The experiment of the evaluation compares the different Monte Carlo methods over the problem 
        of finding defective configurations in both the AAFMs Python Framework and the jHipster feature 
        models. To replicate the experiments of the evaluation, we provide the following scripts that 
        can be executed as follows:

        For the AAFMs Python Framework feature model (results here):
            python main_comparison_jhipster.py -it 1000 -s 2021 -m MCTS
        
        The Random Sampling strategy can be directly used for the jHipster feature model because all configurations are available.
        
        Note that the -it ITERATIONS parameter here is the maximum number of iterations/simulations to be 
        performed (5000 default). The script will run the Monte Carlo methods from 1 to ITERATIONS with a 
        step of 250 iterations.
        
        Note: Setting up the random seed, the execution can take a while (around 1 hour for each experiment)
        so be patient. For impatients, we also present additional results for a small-quick comparison using 
        the -e option for the excerpt version of the model. To understand this, read the final note at the end of this document.
        Change the -m parameter to flat for flat Monte Carlo method, Greedy for Greedy MCTS, and random 
        for Random Sampling. For the Random Sampling, in case of using the complete version of the feature 
        model (10e9 configurations) or other large-scale feature models you need to use the BDD Sampler of Heradio 
        et al.). The integration of BDD Sampler within our framework is out of scope of this work, thus, there is 
        not script at this moment to automate the random sampling results from the BDD Sampler.
        '''
        subprocess.call(['python','./main_comparison_jhipster.py'] + args.split())

    def do_completion_partial_configs(self, args):
        '''
        The completion of partial configuration problem consists of finding the set of non-selected features 
        necessary for getting a complete valid configuration. While in a complete configuration each feature 
        is decided to be either present or absent in the resulting configuration, in partial configurations, 
        some features are undecided. So, given a feature model and a partial configuration, we can use Monte Carlo 
        methods to complete the given partial configuration with valid selections.
        
        The problem can be executed with: completion_partial_configs.py -fm feature_model -cnf cnf_model -f features

            The `feature_model` parameters is mandatory and specifies the filepath of the feature model in FeatureIDE format.
            The `cnf_model` is optional and specifies the feature model in CNF with FeatureIDE (textual) format. This parameters is 
            only required is the feature model have complex constraints (others than "requires" and "excludes").

        The `features` parameter is optional, it is a list of the features selection of the user representing the initial 
        partial configuration. If not provided, the empty configuration is used by default.
        
        The analysis can be also configured with the following parameters:

            -it ITERATIONS`: specify the number of simulations to be executed by the Monte Carlo method (default 100).
            -ew EXPLORATION_WEIGHT`: the exploration weight constant for MCTS to balance exploitation vs exploration (default 0.5).
            -m METHOD`: the Monte Carlo method to be executed: "MCTS" for the UCT Algorithm (default), "Greedy" for the Greedy MCTS, and 
               "flat" for the basic Monte Carlo method.
        
        Minimizing valid configurations: This problem consists in finding a valid configuration with the minimum number of features.
        This problem can be executed as the previous one to complete partial configurations, but using the -min option to indicate that 
        the number of feature selections must be minimized:

            The problem can be executed with: completion_partial_configs.py -fm feature_model -cnf cnf_model -f 
        '''
        subprocess.call(['python','./main_completion_partial_configs.py'] + args.split())

    def do_jhipster_localizing_defective_configs(self, args):
        '''
        This problem consists in identifying the feature model configurations that lead to a 
        given defect or some other undesired program behavior. Those defects may happen due to
        incompatibilities of features, anomalies or errors when the configuration is compiled, 
        deployed or executed.

        This command will execute the case study of the Jhipster feature model.
        '''
        subprocess.call(['python','./main_jhipster_localizing_defective_configs.py'] + args.split())
        
    def do_completion_defective_configs(self, args):
        '''This problem consists in identifying the feature model configurations that lead to a 
        given defect or some other undesired program behavior. Those defects may happen due to
        incompatibilities of features, anomalies or errors when the configuration is compiled, 
        deployed or executed.
        
        The analysis can be configured with the following parameters:

            -it ITERATIONS`: specify the number of simulations to be executed by the Monte Carlo method (default 100).

            -ew EXPLORATION_WEIGHT`: the exploration weight constant for MCTS to balance exploitation vs exploration (default 0.5).

            -m METHOD`: the Monte Carlo method to be executed: "MCTS" for the UCT Algorithm (default), 
               "Greedy" for the Greedy MCTS, and "flat" for the basic Monte Carlo method.
        '''
        subprocess.call(['python','./main_localizing_defective_configs.py'] + args.split())
        
    def do_reverse_engineering_fms(self, args):
        '''
        Reverse engineering of feature models: A well-known problem in SPLs is to synthesize a feature model from a set of configurations 
        automatically. Given a set of feature combinations present in an SPL (i.e., a set of configurations), the goal is to extract a 
        feature model that represents all the configurations.
        
        The problem can be executed with: reverse_engineering_fms.py -fm feature_model -cnf cnf_model 

        The `feature_model` parameters is mandatory and specifies the filepath of the feature model in FeatureIDE format.
        The `cnf_model` is optional and specifies the feature model in CNF with FeatureIDE (textual) format. This parameters is only required 
        is the feature model have complex constraints (others than "requires" and "excludes").
        
        We use all configurations of the given feature model as input configurations to extract a new feature model.

        The analysis can be also configured with the following parameters:

            -it ITERATIONS`: specify the number of simulations to be executed by the Monte Carlo method (default 100).
            -ew EXPLORATION_WEIGHT`: the exploration weight constant for MCTS to balance exploitation vs exploration (default 0.5).
            -m METHOD`: the Monte Carlo method to be executed: "MCTS" for the UCT Algorithm (default), "Greedy" for the Greedy MCTS, and "flat" 
               for the basic Monte Carlo method.
        '''
        subprocess.call(['python','./main_reverse_engineering_fms.py'] + args.split())    
    
    def do_EOF(self, args):
        print('Remember to execute this in docker using the -i option')
        return True
MyPrompt().cmdloop()