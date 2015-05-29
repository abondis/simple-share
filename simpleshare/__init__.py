from bottle import get, post, delete
from bottle import request
from bottle import abort, template, static_file
from os.path import join as join_path, abspath, realpath
from os.path import relpath, basename
from simpleshare.tools import get_real_path
from simpleshare.tools import list_dir, get_path_from_uid
from simpleshare.tools import delete_path, get_files
from simpleshare.tools import check_config_path, create_random_folder
from simpleshare.tools import configure, root_dir
from simpleshare.tools import permitted_files_path, protect_path
from simpleshare.tools import permitted_config_path, DEBUG
from cork import Cork

aaa = Cork('cork_conf')
authorize = aaa.make_auth_decorator(fail_redirect="/login", role="user")

PATH_ERROR = "The path is not available or doesn't exist"


def post_get(name, default=''):
    return request.POST.get(name, default).strip()


@get('/')
@authorize()
def index(path=None):
    return template('index')


@get('/login')
def login_page():
    return template('login')


@post('/login')
def login():
    username = post_get('user')
    password = post_get('password')
    aaa.login(username, password, success_redirect='/')


@get('/logout')
def logout():
    aaa.logout(success_redirect='/login')


@get('/files')
@get('/files/<path:path>')
@authorize()
def default(path=None):
    return template('index')


@get('/shared')
@get('/shared/<path:path>')
def default_public(path=None):
    return template('index')


@get('/static/<path:path>')
def static(path):
    return static_file(path, root="./static")


@get('/bower_components/<path:path>')
def bower(path):
    return static_file(path, root="./bower_components")


@get('/partials/<template:path>')
@authorize()
def partials(template):
    return template(template)


@get('/get/shared/<user>/<uid>')
@get('/get/shared/<user>/<uid>/<path:path>')
@get('/api/shared/<user>/<uid>')
@get('/api/shared/<user>/<uid>/<path:path>')
def list_shared(user, uid, path='.'):
    """Return a list of files in a shared folder"""
    real_shared_path = get_path_from_uid(user, uid)
    permitted = join_path(root_dir, real_shared_path)
    try:
        real_path = get_real_path(permitted, path)
    except IOError:
        abort(403, PATH_ERROR)
    print("getting {}".format(real_path))
    return list_dir(real_path)


@get('/get/files')
@get('/get/files/<path:path>')
@get('/api/files')
@get('/api/files/<path:path>')
@authorize()
def list_path(path='.'):
    """Return a list of files in a path if permitted
    """
    try:
        real_path = protect_path(path)
    except IOError:
        abort(403, PATH_ERROR)
    return list_dir(real_path)


@delete('/api/files/<path:path>')
@authorize()
def api_delete_path(path='.'):
    """Return a list of files in a path if permitted
    """
    real_path = protect_path(path)
    try:
        delete_path(real_path)
        try:
            # after deleting we want to re-list what the current folder hosts
            # append /..
            # follow symlink ???
            # get absolutepath
            permitted = abspath(realpath(join_path(real_path, '..')))
            assert real_path.startswith(permitted)
        except:
            abort(403, PATH_ERROR)
        ls = list_dir(permitted)
        if DEBUG:
            ls = {
                'dirs':
                ['deleted', 'something'],
                'files':
                ['maybe it was', path]}
        return ls
    except OSError:
        abort(404)


@post('/api/files')
@post('/api/files/<path:path>')
@authorize()
def create(path='.'):
    """Create a folder or a file"""
    real_path = protect_path(path)
    file_type = post_get('type')
    overwrite = post_get('overwrite') or False
    uploads = request.files

    check_config_path(real_path)
    if file_type == "file":
        for f in uploads:
            uploads.get(f).save(
                real_path, overwrite=overwrite)
    elif file_type == 'dir':
        pass
    return {'status': 'ok'}


@post('/api/share')
@post('/api/share/<path:path>')
@authorize()
def share(path="."):
    """Share a file or a folder"""
    reuse = post_get('reuse') or None
    print(reuse)
    public = post_get('public')
    users = post_get('users')
    config = permitted_config_path()
    # /.../user/files/....
    real_path = protect_path(path)
    try:
        # /.../user/files
        # get relative path, to use in configuration path
        rel_shared_path = relpath(real_path, permitted_files_path())
        config_shared_path = join_path(
            config, rel_shared_path)
        check_config_path(config_shared_path)
    except IOError:
        abort(403, PATH_ERROR)
    if reuse is not None:
        files = get_files(config_shared_path)
        if reuse in files:
            uid_path = join_path(config, reuse)
        else:
            abort(400, "This sharing ID is invalid")
    else:
        uid, uid_path = create_random_folder(config)
    configure(
        config_shared_path,
        basename(uid_path),
        real_path)
    configure(uid_path, 'path', real_path)
    configure(uid_path, 'public', public)
    configure(uid_path, 'users', users)
    return {'status': 'shared', 'msg': uid}
