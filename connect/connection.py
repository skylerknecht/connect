import time
import urllib.parse as parse

from connect import cli, color, loader, util

class Connection():

    def __init__(self, stager):
        self.command_queue = []
        self.connection_cli = None
        self.stager = stager
        self.stager_requested = time.time()
        self.last_checkin = time.time()
        self.loaded_functions = []
        self.menu_options = {}
        self.status = 'pending'
        self.system_information = {}

    def __str__(self):
        internet_addr = self.system_information['ip']
        #return f'A {self.stager.format} implant, {internet_addr}, is {self.status} and last checked in at {self.get_current_time(self.last_checkin)}.'
        return '{:<10} {:<15} {:<10} {:<10}'.format(self.stager.format, internet_addr, self.status, self.get_current_time(self.last_checkin))

    def check_in(self):
        ip = self.system_information['ip']
        if self.status != 'connected':
            self.status = 'connected'
            color.success(f'Successful connection ({ip})')
        self.last_checkin = time.time()
        return 0, 'Success'

    def disconnected(self):
        if time.time() - self.last_checkin >= 60:
            self.status = 'disconnected'
            return True
        return False

    def discover_functions(self, file_name):
        if len(file_name) > 1:
            file_name = file_name[1]
            self.stager.functions.update(loader.discover_functions(file_name))
            self.update_options()
        return 0, 'Success'

    def execute(self, option):
        if option[0] not in self.loaded_functions:
            for function in self.stager.functions.values():
                if function.name == option[0]:
                    function_definition = parse.quote(function.definition)
                    self.menu_options[option[0]] = util.MenuOption(self.execute, f'{function.description}.', 'Connection Options', color.normal, True)
                    self.command_queue.append('{' + '"eval":' + f'"{function_definition}"' + '}')
                    color.verbose('{' + '"eval":' + f'"{function_definition}"' + '}')
                    self.loaded_functions.append(option[0])
                    self.connection_cli.update_options(self.menu_options)
        function = f'{option[0]}()'
        if len(option) > 1:
            arguments = ','.join(option[1:])
            function = f'{option[0]}({arguments})'
        function = parse.quote(function)
        self.command_queue.append('{' + '"eval":' + f'"{function}"' + '}')
        color.verbose('{' + '"eval":' + f'"{function}"' + '}')
        return 0, 'Success'

    def information(self):
        color.header('System Information')
        for key, value in self.system_information.items():
            color.normal(f'{key} : {value}')
        color.normal('')
        return 0, 'Success'

    def interact(self):
        self.menu_options['discover'] = util.MenuOption(self.discover_functions, 'Discovers new options from provided files within the extensions directory (e.g., discover stdlib.jscript).', 'Connection Options', color.normal, True)
        self.menu_options['information'] = util.MenuOption(self.information, 'Displays gathered system information.', 'Connection Options', color.normal, False)
        self.menu_options['kill'] = util.MenuOption(self.execute, 'Kills the current connection.', 'Connection Options', color.normal, False)
        internet_addr = self.system_information['ip']
        self.connection_cli = cli.CommandLine(f'connection ({internet_addr}) :')
        self.update_options()
        self.connection_cli.run()
        return 0, 'Success'

    def stale(self):
        if time.time() - self.last_checkin >= 10:
            self.status = 'stale'
            return True
        return False

    def update_options(self):
        #todo: Hackish-way to handle when to update connection_cli options.
        for function in self.stager.functions.values():
            if function.name not in self.menu_options.keys():
                self.menu_options[function.name] = util.MenuOption(self.execute, f'{function.description} (unloaded).', 'Connection Options', color.unloaded, True)
        if self.connection_cli:
            self.connection_cli.update_options(self.menu_options)
        return 0, 'Success'

    @staticmethod
    def get_current_time(seconds):
        return time.strftime('%H:%M:%S', time.localtime(seconds))
