import readline
import shlex

from connect.output import display


class Command:

    def __init__(self, name, category, description, parameters):
        self.name = name
        self.category = category
        self.description = description
        self.parameters = parameters

    def help(self):
        print(f'{self.description}\n')
        if not self.parameters:
            return
        print('parameters:')
        for parameter, description in self.parameters.items():
            print('{:<{}}{:<{}}{}'.format(' ', 4, parameter, 8, description))
        print(self.usage)

    @property
    def usage(self) -> str:
        return f"""
            No usage available for {self.name}.
        """


class BuiltinCommand(Command):
    def __init__(self, name, description, parameters=()):
        super().__init__(name, 'builtin', description, parameters)

    def execute_command(self, parameters, client_sio):
        raise NotImplementedError(f'{self.name} command has not implemented execute_command')


class AgentCommand(Command):
    def __init__(self, name, description, parameters=()):
        super().__init__(name, 'agent', description, parameters)

    def execute_command(self, parameters, current_agent, client_sio):
        raise NotImplementedError(f'{self.name} command has not implemented execute_command')


class CommandsManager:

    def __init__(self, commands, client_sio):
        self.client_sio = client_sio
        self.commands = commands
        self.current_agent = None

    def execute_command(self, user_input, set_cli_properties):
        tokens = shlex.split(user_input.replace("\\", "\\\\"))

        if '@' in tokens[0][0]:
            if not len(tokens[0]) > 1:
                set_cli_properties(reset=True)
                self.current_agent = None
                return
            agent = tokens[0].split('@')[1]
            set_cli_properties(prompt=f'({agent})~# ')
            self.current_agent = agent
            return

        if tokens[0] == '?':
            self.help_menu()
            return

        try:
            command = self.commands[tokens[0]]
        except KeyError:
            display(f'{tokens[0]} is not a valid command.', 'INFORMATION')
            return

        if '--help' in tokens or '-h' in tokens:
            command.help()
            return

        if isinstance(command, BuiltinCommand):
            command.execute_command(tokens[1:], self.client_sio)
            return

        if isinstance(command, AgentCommand):
            if not self.current_agent:
                display(f'Please interact with an agent to execute {command.name}', 'ERROR')
                return
            command.execute_command(tokens[1:], self.current_agent, self.client_sio)
            return

    def help_menu(self):
        for command in self.commands.values():
            if not self.current_agent and command.category == 'agent':
                continue
            print('{:<{}}{:<30}'.format(command.name, 10, command.description))