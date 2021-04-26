from cmd import Cmd
import subprocess

class MyPrompt(Cmd):
    prompt = 'montecarlo> '
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, args):
        print("Thank you for using our montecarlo FM implementation!")
        return True
 
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