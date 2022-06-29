![logo](./resources/logo/connect.png)

# Connect
*Command and Control Framework* 

## Installation 
```bash
~# python3 -m venv env
~# source env/bin/activate
(env)~# python3 -m pip install -r requirements.txt
```

## Docker Notes
```
dockerBin/server.sh and dockerBin/start.sh are only for the docker instance. When running via docker:
1. Must be run with the environment variables CALLBACK_IP and CALLBACK_PORT.
2. Must be run with flag --network=host
3. Host/image directory in /data
```


## Overview
Connect is a tool for testing the security posture of internal environments by simulating
real world tactics performed by threat actors. It features an extensible command set and
server architecture to deploy and maintain agents for multiple languages and platforms.
This extensibility provides operators the ability to rapidly conduct and repeat specific
scenarios.

Connect is only to be used for legal applications when the explicit permission of the targeted
organization has been obtained.

## Credits
#### Inspiration
- Kevin Clark 
  - Gitlab [@KevinJClark](https://gitlab.com/KevinJClark)
  - Twitter [@GuhnooPlusLinux](https://twitter.com/GuhnooPlusLinux)

#### Graphics
- Rachel Taniyama 
  - Instagram [@sineater.obj](https://www.instagram.com/sineater.obj/)

#### Development
- Skyler Knecht 
  - Gitlab [@skylerknecht](https://gitlab.com/skylerknecht)
  - Twitter [@skylerknecht](https://twitter.com/skylerknecht)
