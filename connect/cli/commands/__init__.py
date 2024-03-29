from .agents import Agent
from .bypause import ByPause
from .dir import Dir
from .drives import Drives
from .download import Download
from .execute_assembly import ExecuteAssembly
from .exit import Exit
from .hostname import Hostname
from .implants import Implant
from .integrity import Integrity
from .interactive import Interactive
from .ip import IP
from .kill import Kill
from .listeners import Listeners
from .os import OS
from .pid import PID
from .ps import PS
from .pwd import PWD
from .shell import Shell
from .streamers import Streamers
from .spawn import Spawn
from .type import Type as _Type
from .upload import Upload
from .whoami import Whoami

agent = Agent()
bypause = ByPause()
dir = Dir()
drives = Drives()
download = Download()
execute_assembly = ExecuteAssembly()
exit = Exit()
hostname = Hostname()
implant = Implant()
integrity = Integrity()
interactive = Interactive()
ip = IP()
kill = Kill()
listeners = Listeners()
os = OS()
pid = PID()
ps = PS()
pwd = PWD()
shell = Shell()
socks = Streamers()
spawn = Spawn()
_type = _Type()
upload = Upload()
whoami = Whoami()

COMMANDS = {
    agent.name: agent,
    bypause.name: bypause,
    dir.name: dir,
    drives.name: drives,
    download.name: download,
    execute_assembly.name: execute_assembly,
    exit.name: exit,
    hostname.name: hostname,
    implant.name: implant,
    integrity.name: integrity,
    interactive.name: interactive,
    ip.name: ip,
    kill.name: kill,
    listeners.name: listeners,
    os.name: os,
    pid.name: pid,
    ps.name: ps,
    pwd.name: pwd,
    shell.name: shell,
    socks.name: socks,
    spawn.name: spawn,
    _type.name: _type,
    upload.name: upload,
    whoami.name: whoami
}
