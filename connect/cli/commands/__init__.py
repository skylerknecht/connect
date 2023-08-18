from .commands import CommandsManager
from connect.cli.commands.agents import Agent
from .exit import Exit

agent = Agent()
exit = Exit()

COMMANDS = {
    agent.name: agent,
    exit.name: exit
}


