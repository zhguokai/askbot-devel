from django.core.management.base import NoArgsCommand
from askbot.startup_procedures import run_self_test

class Command(NoArgsCommand):
    def handle_noargs(self, **kwargs):
        run_self_test()
        
        
    
