from cmd import Cmd
import subprocess

class MyPrompt(Cmd):
    prompt = 'montecarlo> '
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, args):
        print("Thank you for using our montecarlo FM implementation!")
        return True
 
    def do_completion_partial_configs(self, args):
        print(args)
        subprocess.call(['python','./main_completion_partial_configs.py'])

    def do_jhipster_localizing_defective_configs(self, args):
        print(args)
        subprocess.call(['python','./main_jhipster_localizing_defective_configs.py'])
        
    def do_completion_partial_configs(self, args):
        print(args)
        subprocess.call(['python','./main_localizing_defective_configs.py'])
        
    def do_reverse_engineering_fms(self, args):
        print(args)
        subprocess.call(['python','./main_reverse_engineering_fms.py'])    

MyPrompt().cmdloop()