import os
import random
import sys
import time

from connect import cli, color, connection, implants, util


class Engine():

    connections = {}
    IMPLANTS = {}

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.IMPLANTS ={
            #util.generate_id():(implants.MshtaImplant(ip, port)),
            util.generate_id():(implants.JScriptImplant(ip, port))
        }

    def display_connections(self):
        color.display_banner('Connections')
        if not self.connections:
            color.normal('No connections to display.\n')
            return 0
        for connection_id, connection in self.connections.items():
            if connection.status == 'connected':
                color.success(f'> {connection}', symbol=False)
                continue
            color.normal(f'{connection}')
        color.normal('')
        return 0

    def display_implants(self):
        color.display_banner('Implants')
        for implant_id, implant in self.IMPLANTS.items():
            color.normal(f'{implant.format}: http://{self.ip}:{self.port}/{implant_id}')
        color.normal('')
        return 0
