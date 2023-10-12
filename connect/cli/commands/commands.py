import os


class Command:

    def __init__(self, name, description, category='undefined', parameters=None):
        self.name = name
        self.category = category
        self.description = description
        self.parameters = parameters

    def help(self):
        print(f'{self.description}')
        if not self.parameters:
            return
        print('\nparameters:')
        longest_parameter = 0
        for parameter in self.parameters.keys():
            if len(parameter) > longest_parameter:
                longest_parameter = len(parameter)
        for parameter, description in self.parameters.items():
            print('{:<{}}{:<{}}{}'.format(' ', 4, parameter, longest_parameter + 4, description))
        if self.usage: print('\n' + self.usage)

    @property
    def usage(self) -> str:
        return ''


class ConnectCommand(Command):
    def __init__(self, name, description, category='connect', parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)

    def execute_command(self, parameters, client_sio):
        raise NotImplementedError(f'{self.name} command has not implemented execute_command')


class AgentCommand(Command):
    def __init__(self, name, description, category=None, parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)

    def execute_command(self, parameters, current_agent, client_sio):
        raise NotImplementedError(f'{self.name} command has not implemented execute_command')


class STDPapiAgentCommand(AgentCommand):
    def __init__(self, name, description, category='stdpapi', parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)


class ModuleAgentCommand(AgentCommand):

    MODULE_PATH = f'{os.getcwd()}/resources/modules'

    def __init__(self, name, description, category=None, parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)


class ExecutionCommand(ModuleAgentCommand):

    def __init__(self, name, description, category='execution', parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)
        self.module = f'{self.MODULE_PATH}/Execution.dll'


class FileSystemCommand(ModuleAgentCommand):

    def __init__(self, name, description, category='file system', parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)
        self.module = f'{self.MODULE_PATH}/FileSystem.dll'


class MiscAgentCommand(ModuleAgentCommand):

    def __init__(self, name, description, category='misc', parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)


class ProcessesCommand(ModuleAgentCommand):

    def __init__(self, name, description, category='system information', parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)
        self.module = f'{self.MODULE_PATH}/Processes.dll'


class SystemInformationCommand(ModuleAgentCommand):

    def __init__(self, name, description, category='system information', parameters=None):
        super().__init__(name, description, category=category, parameters=parameters)
        self.module = f'{self.MODULE_PATH}/SystemInformation.dll'


