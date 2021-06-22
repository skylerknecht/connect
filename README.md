## Connect
It is a command and control python project.

### Using Connect
```sh
./run_connect --ip 127.0.0.1 --port 1337
connect~# pwn pwn pwn
connect~# help

Help Menu
=========

'?': Displays the help menu.
'exit': Exits the current command-line.
'help': Displays the help menu.
'history': Displays the command history. Execute a previous command by appending an index (e.g., history 0)
'version': Display the current application version.
'connections': Displays current connections.
'implants': Displays hosted implants ready for delivery.

connect~#
```

### Features
* Multiple receivers to avoid signatured implants.
* Applicable user interface.

### Documentation
```
Connection:
  A requested implant.
  - status: current status of the connection with two possible values (sucessfully and pending).
    - pending (implant requested waiting for first check in)
    - successfull (a successfully executed implant)
  - implant_format: file format of the implant delivered (e.g., jscript).

Implant:
  Payloads hosted via an operator defined Flask webserver waiting to be requested and executed.

Return Codes:
  Negative (-1, -2, -3 ect..): Exit.
  0: Impeccable execution.
  1: Invalid command.
```

### Shoutouts
Thanks to [@Kevin J Clark](https://twitter.com/GuhnooPlusLinux) for all the assitance and inspiration from his sub-par but equally as functional C2... [Badrats](https://gitlab.com/KevinJClark/badrats). (:
