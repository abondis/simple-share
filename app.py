from bottle import run, app
import simpleshare
from simpleshare.tools import DEBUG
simpleshare

if __name__ == "__main__":
    from beaker.middleware import SessionMiddleware

    session_opts = {
        'session.type': 'file',
        'session.cookie_expires': 3600,
        'session.encrypt_key': 'peesh6ke7azuathai4seiyoh7ohFohph ',
        'session.data_dir': './beaker/sessions',
        'session.auto': True,
        'session.validate_key': True,
    }
    web_app = SessionMiddleware(app(), session_opts)
    run(
        app=web_app,
        #server='bjoern',
        host='localhost',
        port=8080,
        debug=DEBUG,
        reloader=True)
