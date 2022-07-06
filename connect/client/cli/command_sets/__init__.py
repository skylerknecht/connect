from . import agent
from . import tokens
from . import system
from . import execution
from . import files

COMMAND_SETS = [
    tokens.TokenCommands,
    agent.AgentCommands,
    system.SystemCommands,
    execution.ExecutionCommands,
    files.FilesCommands
]