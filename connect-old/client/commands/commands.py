class Command:
    def __init__(self, name, description, parameters):
        self.name = name
        self.description = description
        self.parameters = parameters

    def execute_command(self, arguments):
        raise NotImplementedError(f'{self.name} command has not implemented execute_command')

    def help(self):
        print(f'{self.name}:{self.description}')


class CommandsManager:

    def __init__(self, commands):
        self.commands = commands


