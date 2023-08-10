import readline
import shlex


class Command:

    def __init__(self, name, category, description, parameters):
        self.name = name
        self.category = category
        self.description = description
        self.parameters = parameters

    def help(self):
        print(f'{self.name}:{self.description}')


class BuiltinCommand(Command):
    def __init__(self, name, description, parameters=()):
        super().__init__(name, 'builtin', description, parameters)

    def execute_command(self, parameters):
        raise NotImplementedError(f'{self.name} command has not implemented execute_command')


class AgentCommand(Command):
    def __init__(self, name, description, parameters=()):
        super().__init__(name, 'agent', description, parameters)

    def execute_command(self, parameters, current_agent):
        raise NotImplementedError(f'{self.name} command has not implemented execute_command')


class CommandsManager:

    def __init__(self, commands):
        self.agents = ['1234']
        self.commands = commands
        self.current_agent = None

    def execute_command(self, user_input, set_cli_properties):
        tokens = shlex.split(user_input.replace("\\", "\\\\"))

        if tokens[0] in self.agents:
            set_cli_properties(prompt=f'({tokens[0]})~# ')
            self.current_agent = tokens[0]
            return

        if tokens[0] == '?' or tokens[0] == 'help':
            self.help_menu()
            return

        try:
            command = self.commands[tokens[0]]
        except KeyError:
            print(f'{tokens[0]} is not a valid command.')
            return

        if '--help' in tokens or '-h' in tokens:
            command.help()
            return

        if isinstance(command, BuiltinCommand):
            command.execute_command(tokens[1:])
            return
        if isinstance(command, AgentCommand):
            command.execute_command(tokens[1:], self.current_agent)
            return

    def help_menu(self):
        for command in self.commands.values():
            if not self.current_agent and command.category == 'agent':
                continue
            print('{:<{}}{:<30}'.format(command.name, 10, command.description))