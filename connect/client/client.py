import atexit
import functools
import json
import os
import readline
import shlex
import signal
import sys
import threading
import traceback

from connect import output
from connect import convert
from collections import namedtuple

class Options:
    
    Option = namedtuple('Option', ['name', 'function', 'parameters', 'description'])
    Agents = []
    current_agent = None
    current_agent_options = []
    
    def __init__(self, sio_client) -> None:
        self.sio_client = sio_client
        self.OPTIONS = [
            self.Option('agents', self.agents, [], 'Request and display avaliable agents.'),
            self.Option('all', self.all, [], 'Interact with all agents.'),
            self.Option('back', self.back, [], 'Return to the main menu.'),
            self.Option('exit', self.exit, [], 'Exits the application.'),
            self.Option('help', self.help, [], 'Displays the help menu.'),
            self.Option('hello', self.hello, [output.Parameter('name', 'individual to greet')], 'Greets an individual.'),
            self.Option('implants', self.implants, [output.Parameter('--create IMPLANT_NAME /path/to/profile.json', 'Create an Implant.'), output.Parameter('--delete [IMPLANT_ID, all]', 'Delete an Implant.')], 'Create, delete and display avaliable implants.'),
            self.Option('socks', self.socks, [
                output.Parameter('--local ADDRESS PORT', 'Emit a socks event with the action set to local and the given address and port.'),
                output.Parameter('--remote ADDRESS PORT AGENT_ID', 'Emit a socks event with the action set to remote and the given address and port.')
            ], 'Emit a socks event with the given action and address and port.')
        ]

    def _complete_path(self, incomplete_option):
        path = incomplete_option.split('/')
        incomplete_filename = path[-1]
        if len(path) == 1:
            return [filename for filename in os.listdir(f'/') if filename.startswith(incomplete_filename)]
        valid_path = '/'.join(path[:-1])
        return [f'{valid_path}/{filename}' if os.path.isfile(f'/{valid_path}/{filename}') else f'{valid_path}/{filename}/' for filename in os.listdir(f'/{valid_path}') if filename.startswith(incomplete_filename)]

    def complete_option(self, incomplete_option, state):
            '''
            Analyzes the length of current line buffer / incomplete_option and
            determines the user(s) completion.

            If the current line buffer is greater or equal to one and the current line
            buffer ends with a trailing space then that indicates the user is attempting
            to complete a multi-worded option. The length of the current line buffer,
            when delimeted by a space, must be incremented by one to correctly search
            for the next option.

            Otherwise, generate a list of all current menu options and file names that
            start with the current incomplete_option aka the last line in the buffer.

            Parameters:
                    incomplete_option (str()): The current incomplete option.
                    state (int()): An integer so that when the funciton is called
                                recursivley by readline it can gather all items
                                within the current finished_option list.

            Returns:
                    finished_option (str): Whatever option the callee has not
                                        gathered yet.
            '''
            current_line = readline.get_line_buffer()
            current_line_list = current_line.split()
            if len(current_line_list) >= 1 and current_line.endswith(' '):
                current_line_list.append('')
            options = []
            for agent in self.Agents:
                options.append(agent.name)
            for option in self.OPTIONS:
                options.append(option.name)
            for option in self.current_agent_options:
                options.append(option.name)
            finished_options = [option for option in options if option.startswith(incomplete_option)]
            if '/' in incomplete_option:
                finished_options.extend(self._complete_path(incomplete_option))
            return finished_options[state]

    def detailed_help(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if '--' in args:
                parameters = args[:args.index('--')]
                args = args[:args.index('--')] + args[args.index('--') + 1:]
            else:
                parameters = args
            if '-h' in parameters or '--help' in parameters:
                option = args[0]
                output.display('DEFAULT', option.description)
                output.display('DEFAULT', '')
                output.display('DEFAULT', 'Parameters:')
                output.display('DEFAULT', '-'*11)
                if option.parameters:
                    longest_parameter = max(len(parameter.name) for parameter in option.parameters) + 4
                    longest_parameter = 13 if longest_parameter < 13 else longest_parameter # '-h,--help' is not included in option.parameters
                    for parameter in option.parameters:
                        output.display('DEFAULT', '{:<4}{:<{}}{:<30}'.format('', parameter.name, longest_parameter, parameter.description))
                    output.display('DEFAULT', '{:<4}{:<{}}{:<30}'.format('', '-h/--help', longest_parameter, 'Display this menu.'))
                else:
                    output.display('DEFAULT', '{:<4}{:<30}{:<30}'.format('', '-h/--help', 'Display this menu.'))
            else:
                func(self, *args, **kwargs)
        return wrapper

    def set_agent(self, agent):
        self.current_agent = agent
        self.current_agent_options = []
        self.current_agent_options = agent.options

    # Option Functions

    @detailed_help
    def socks(self, option, *args):
        """\
        Emit a socks event with the given action and address and port.

        Usage: socks [--local ADDRESS PORT | --remote ADDRESS PORT] [-h,--help]

        Parameters:
            -h/--help               Display this menu.
            --local ADDRESS PORT    Emit a socks event with the action set to local and the given address and port.
            --remote ADDRESS PORT   Emit a socks event with the action set to remote and the given address and port.\
        """
        try:
            if not args:
                self.sio_client.emit('socks', '')
            elif '--local' in args:
                pos = args.index('--local')
                data = {'action':'local','address':args[pos+1], 'port':args[pos+2]}
                self.sio_client.emit('socks', json.dumps(data))
            elif '--remote' in args:
                pos = args.index('--remote')
                data = {'action':'remote','address':args[pos+1], 'port':args[pos+2], 'agent_id': args[pos+3]}
                self.sio_client.emit('socks', json.dumps(data))
            else:
                option.function(option, '--help')
        except Exception:
            output.display('DEFAULT', traceback.format_exc())
            option.function(option, '--help')

    @detailed_help
    def agents(self, option, *args):
        """\
        Request and display avaliable agents.

        Usage: agents [-h,--help]

        Parameters:
            -h/--help     Display this menu.\
        """
        if '--all' in args:
            self.sio_client.emit('agents', {"all":"True"})
            return
        self.sio_client.emit('agents', {"all":"False"})

    @detailed_help
    def all(self, option, *args):
        """\
        Interact with all agents.

        Usage: back [-h,--help]

        Parameters:
            -h/--help     Display this menu.\
        """
        non_duplicates = []
        self.current_agent = self.Agents
        self.current_agent_options = []
        for agent in self.current_agent:
            for option in agent.options:
                if option in non_duplicates:
                    continue
                non_duplicates.append(option)
        self.current_agent_options = non_duplicates

    @detailed_help
    def back(self, option, *args):
        """\
        Return to the main prompt.

        Usage: back [-h,--help]

        Parameters:
            -h/--help     Display this menu.\
        """
        self.current_agent = None
        self.current_agent_options = []

    @detailed_help
    def exit(self, option, *args):
        """\
        Leave the application.

        Usage: exit [-h,--help]

        Parameters:
            -h/--help     Display this menu.\
        """
        self.sio_client.disconnect()
        sys.exit()

    @detailed_help
    def help(self, option, *args):
        """\
        Retrieve the name and description of all options and display them.

        Usage: help [-h,--help]
        
        Parameters:
            -h/--help     Display this menu.
            name          Name of the individual to greet.\
        """
        output.display('DEFAULT', 'Usage: <option> [parameters]')
        output.display('DEFAULT', '')
        output.display('DEFAULT', 'Options:')
        longest_parameter = max(len(parameter.name) for parameter in self.OPTIONS + self.current_agent_options) + 4 
        for option in self.OPTIONS:
            output.display('DEFAULT', '  {:<{}}{}'.format(option.name, longest_parameter, option.description))
        if not self.current_agent:
            return
        output.display('DEFAULT', '\nAgent Options:')
        for option in self.current_agent_options:
            output.display('DEFAULT', '  {:<{}}{}'.format(option.name, longest_parameter, option.description))

    @detailed_help
    def hello(self, option, *args):
        """\
        Greet an individual by proving their name.

        Usage: hello [-h,--help] name

        Parameters:
            -h/--help     Display this menu.
            name          Name of the individual to greet.\
        """
        output.display('INFORMATION', 'Hello, {}! :)'.format(args[0]))

    @detailed_help
    def implants(self, option, *args):
        """\
        Create, delete and display available implants.

        usage:
            implants [-h, --help, --create, --delete]

        optional arguments:
            -h, --help                          show this help message and exit
            --create IMPLANT_NAME IMPLANT_JSON  create an implant
            --delete IMPLANT_ID                 delete an implant\
        """
        try: 
            if not args:
                self.sio_client.emit('implants', '')
            elif '--create' in args:
                    pos = args.index('--create')
                    implant_json = ''
                    with open(args[pos+2], 'rb') as fd:
                        implant_json = json.loads(fd.read())
                    if not implant_json:
                        output.display('ERROR', 'JSON file empty.')
                        return
                    implant_name = args[pos+1]
                    data = {"action": "create", "options": implant_json, 'name': implant_name}
                    self.sio_client.emit('implants', json.dumps(data))
            elif '--delete' in args:
                pos = args.index('--delete')
                implant_id = args[pos+1]
                data = {"action": "delete", "implant_id": implant_id}
                self.sio_client.emit('implants', json.dumps(data))
            else:
                option.function(option, '--help')
        except json.decoder.JSONDecodeError:
            output.display('ERROR', 'Failed to parse JSON file.')
        except Exception:
            output.display('DEFAULT', traceback.format_exc())
            option.function(option, '--help')

    @detailed_help
    def agent_option(self, agent_option, *args):
        if len(agent_option.parameters) > len(args):
            self.agent_option(agent_option, '--help')
            return
        if not self.current_agent:
            output.display('ERROR', 'Not intreacting with an agent.')
        if isinstance(self.current_agent, list):
            for agent in self.current_agent:
                task = output.Task(agent_option.name, agent_option.description, args, agent_option.type)
                self.sio_client.emit('task', f'{{"agent":"{agent.name}", "task": {json.dumps(task)}}}')
            return
        task = output.Task(agent_option.name, agent_option.description, args, agent_option.type)
        self.sio_client.emit('task', f'{{"agent":"{self.current_agent.name}", "task": {json.dumps(task)}}}')

class Interface:

    WORKING_DIRECTORY = os.path.expanduser("~/.connect")
    HISTORY_FILE = f'{WORKING_DIRECTORY}/command_history.txt'
    MAIN_THREAD_IDENTIFIER = threading.current_thread().ident 
    PROMPT = '(connect)~#'

    def __init__(self, options: Options) -> None:
        self.prompt = self.PROMPT
        self.options = options
        readline.set_history_length(10000)
        if not os.path.exists(self.WORKING_DIRECTORY):
            os.mkdir(self.WORKING_DIRECTORY)
            self.notify('INFORMATION', f'Created working directory {self.WORKING_DIRECTORY}')
        if not os.path.exists(self.HISTORY_FILE):
            with open(self.HISTORY_FILE, "w") as file:
                file.write("welcome to connect")
            self.notify('INFORMATION', f'Created command history file {self.HISTORY_FILE}')
        try:
            readline.read_history_file(self.HISTORY_FILE)
        except Exception:
            self.notify('ERROR', f'Failed to open {self.HISTORY_FILE}!')
        atexit.register(readline.write_history_file, self.HISTORY_FILE)
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.options.complete_option)
        readline.set_completer_delims(" \t\n\"\\'`@$><=;|&{(")

    def notify(self, type: str, stdout: str, reprompt: bool = False):
        output.display(type, stdout)
        if self.MAIN_THREAD_IDENTIFIER != threading.current_thread().ident or reprompt:
            output.display('DEFAULT', self.prompt + ' ', newline=False)

    def process_agent_interaction(self, input):
        agents = [agent for agent in self.options.Agents]
        for agent in agents:
            if input == agent.name:
                self.options.set_agent(agent)
                self.prompt = f'({input})~#'
                return True
        return False
    
    def process_agent_options(self, tokens):
        agent_option = next((option for option in self.options.current_agent_options if option.name == tokens[0].lower()), None)
        if agent_option:
            try:
                self.options.agent_option(agent_option, *tokens[1:])
                return True
            except KeyError as ke:
                output.display('ERROR', f'Invalid option: {ke}.')
                self.notify('DEFAULT', traceback.format_exc())
            except ValueError as ve:
                output.display('ERROR', f'Invalid value: {ve}')
                self.notify('DEFAULT', traceback.format_exc())
            except IndexError as ie:
                output.display('ERROR', f'Arguments expected: {ie}.')
                self.notify('DEFAULT', traceback.format_exc())
            except Exception as e:
                output.display('ERROR', f'Unknown error occured: {e}')
                self.notify('DEFAULT', traceback.format_exc())

        return False

    def process_options(self, tokens):
        option = next((option for option in self.options.OPTIONS if option.name == tokens[0].lower()), None)
        if option:
            if option.name == 'back':
                option.function(option)
                self.prompt = self.PROMPT
                return True
            if option.name == 'all':
                option.function(option)
                self.prompt = '(all)~#'
                return True
            try:
                option.function(option, *tokens[1:])
                return True
            except KeyError as ke:
                output.display('ERROR', f'Invalid option: {ke}.')
                self.notify('DEFAULT', traceback.format_exc())
            except ValueError as ve:
                output.display('ERROR', f'Invalid value: {ve}')
                self.notify('DEFAULT', traceback.format_exc())
            except IndexError as ie:
                output.display('ERROR', f'Arguments expected: {ie}.')
                self.notify('DEFAULT', traceback.format_exc())
            except Exception as e:
                output.display('ERROR', f'Unknown error occured: {e}')
                self.notify('DEFAULT', traceback.format_exc())
        return False

    def run(self, team_server_uri, key):
            self.options.sio_client.connect(team_server_uri, auth=key)
            while True:
                try:
                    self.ignore_input = False
                    user_input = output.display('PROMPT', self.prompt)
                    if not user_input or self.ignore_input:
                        continue
                    if self.process_agent_interaction(user_input):
                        continue
                    tokens = shlex.split(user_input.replace("\\", "\\\\"))
                    if self.process_agent_options(tokens):
                        continue
                    if self.process_options(tokens):
                        continue
                    output.display('ERROR', 'Invalid option. Type "help" for a list of available options.')
                except EOFError:
                    self.notify('DEFAULT', traceback.format_exc())
                    sys.exit()
                except Exception:
                    self.notify('DEFAULT', traceback.format_exc())
                except KeyboardInterrupt:
                    # ToDo: Find a better way to prevent the socket_io client from disconnecting when KeyboardInterrupt is caught.
                    self.notify('INFORMATION', 'Keyboard Interrupt Caught. Type exit to leave the application.')  
                    self.options.sio_client.disconnect()
                    self.options.sio_client.connect(team_server_uri, auth=key)
                    continue