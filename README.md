## Connect
It is a command and control python project.

### Using Connect
```sh
./run_connect --ip 127.0.0.1 --port 1337
connect~# pwn pwn pwn
connect~# help

Options
=======

'?': Displays the help menu.
'exit': Exits the current command line.
'help': Displays the help menu.
'verbosity': Toggle verbosity mode on and off.
'version': Display the current application version.

Engine Options
==============

'connections': Displays current connections.
'stagers': Displays staged files ready for delivery.

connect~#
```

### Features
* Multiple receivers to avoid signatured implants.
* Applicable user interface.

### Documentation
```
Connection:
  A requested staged file.
  - status: current status of the connection with two possible values (sucessfully and pending).
    - pending (staged file requested waiting for first check in)
    - successfull (a successfully executed implant)
  - stager_format: file format of the staged file delivered (e.g., jscript).

Stager:
  Payloads hosted via an operator defined Flask webserver waiting to be requested and executed.

Return Codes:
  Negative (-1, -2, -3 ect..): Exit.
  0: Impeccable execution.
  1: Invalid command.
```

### Shoutouts
Thanks to [@Kevin J Clark](https://twitter.com/GuhnooPlusLinux) for all the assitance and inspiration from his sub-par but equally as functional C2... [Badrats](https://gitlab.com/KevinJClark/badrats). (:
