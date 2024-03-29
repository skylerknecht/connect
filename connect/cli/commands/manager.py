import shlex

from .commands import AgentCommand, ConnectCommand
from connect.output import display


class CommandsManager:

    def __init__(self, commands, client_sio):
        self.client_sio = client_sio
        self.commands = commands
        self.current_agent = None

    def execute_command(self, user_input, set_cli_properties, get_cli_properties):
        tokens = shlex.split(user_input.replace("\\", "\\\\"))
        if tokens[0] in get_cli_properties(agent_ids=True):
            agent = tokens[0]
            set_cli_properties(prompt=f'({agent})~# ')
            self.current_agent = agent
            return

        if tokens[0] == '?' or tokens[0] == 'help':
            self.help_menu()
            return

        if tokens[0] == 'back':
            set_cli_properties(reset=True)
            self.current_agent = None
            return

        if tokens[0] == 'all':
            set_cli_properties(prompt=f'(all)~# ')
            self.current_agent = 'all'
            return

        try:
            command = self.commands[tokens[0]]
        except KeyError:
            display(f'{tokens[0]} is not a valid command.', 'ERROR')
            return

        if '--help' in tokens or '-h' in tokens:
            command.help()
            return

        if isinstance(command, ConnectCommand):
            command.execute_command(tokens[1:], self.client_sio)
            return

        if isinstance(command, AgentCommand):
            if not self.current_agent:
                display(f'Please interact with an agent to execute {command.name}', 'ERROR')
                return
            if self.current_agent == 'all':
                for agent_id in get_cli_properties(agent_ids=True):
                    command.execute_command(tokens[1:], agent_id, self.client_sio)
                return
            command.execute_command(tokens[1:], self.current_agent, self.client_sio)
            return

    def help_menu(self):
        categories = {}
        for command in self.commands.values():
            if not self.current_agent and isinstance(command, AgentCommand):
                continue
            if command.category not in categories:
                categories[command.category] = []
            categories[command.category].append(command)
        alphabetically_sorted_categories = {k: categories[k] for k in sorted(categories)}
        for index, (category, category_commands) in enumerate(alphabetically_sorted_categories.items()):
            print(category)
            print('-' * len(category))
            alphabetically_sorted_commands = sorted(category_commands, key=lambda cmd: cmd.name)
            longest_cmd = 0
            for cmd in alphabetically_sorted_commands:
                if len(cmd.name) > longest_cmd:
                    longest_cmd = len(cmd.name)
            for cmd in alphabetically_sorted_commands:
                print('{:<{}}{}'.format(cmd.name, longest_cmd + 4, cmd.description))
            if index < len(categories) - 1:
                print()