from bottle import get, post, delete
from bottle import request
from bottle import abort, template, static_file
from os.path import join as join_path
from os.path import relpath, basename, dirname
from simpleshare.tools import get_real_path
from simpleshare.tools import list_dir, get_path_from_uid
from simpleshare.tools import delete_path, get_config
from simpleshare.tools import create_path, create_random_folder
from simpleshare.tools import root_dir
from simpleshare.tools import permitted_files_path, protect_path
from simpleshare.tools import permitted_config_path
from simpleshare.tools import permitted_shares_path
from simpleshare.tools import relist_parent_folder
from simpleshare.tools import PATH_ERROR
from keyval import configure
from cork import Cork

aaa = Cork('cork_conf')
authorize = aaa.make_auth_decorator(fail_redirect="/login", role="user")


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
    # print(real_shared_path)
    permitted = join_path(root_dir, real_shared_path)
    try:
        real_path = get_real_path(permitted, path)
    except IOError:
        abort(403, PATH_ERROR)
    # print("getting {}".format(real_path))
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
        return relist_parent_folder(real_path)
    except OSError:
        abort(404)


@delete('/api/shared/<path:path>')
@authorize()
def _delete_shared_path(path='.'):
    """
    We delete .../user/shares/<uid>
    and .../user/config/<path>/<uid>
    """
    uid = basename(path)
    folder = dirname(path)
    abs_folder_path = protect_path(folder)
    config_folder_path = protect_path(path, 'config')
    config_uid_path = protect_path(uid, 'config')
    try:
        delete_path(config_folder_path)
        delete_path(config_uid_path)
        return relist_parent_folder(abs_folder_path)
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
    # if not validate_path(path):
    #     abort(403, "You cannot create a sub-folder or a file with "
    #           "the same name as it's parent's 'sharing' name"
    #           "{}".format(basename(path)))
    create_path(real_path)
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
    # print(reuse)
    public = post_get('public')
    users = post_get('users')
    # .../user/config
    path_config = permitted_config_path()
    # .../user/shares
    uidshares_config = permitted_shares_path()
    # /.../user/files/....
    real_path = protect_path(path)
    try:
        # /.../user/files
        # get relative path, to use in configuration path
        rel_shared_path = relpath(real_path, permitted_files_path())
    except IOError:
        abort(403, PATH_ERROR)
    if reuse is not None:
        try:
            shared_path = get_config(reuse, 'path', 'shares')
        except IOError:
            abort(400, "This sharing ID is invalid")
        if shared_path != rel_shared_path:
            abort(400, "This sharing ID is invalid")
    else:
        uid, uid_path = create_random_folder()
    # create .../user/config/rel/path/UID
    print('uid {} Uid_path {}'.format(reuse or uid, uid_path))
    configure(
        rel_shared_path,
        reuse or uid,
        rel_shared_path)
    # configure .../user/shares/UID/
    configure(uid_path, 'path', real_path, 'shares')
    configure(uid_path, 'public', public, 'shares')
    configure(uid_path, 'users', users, 'shares')
    return relist_parent_folder(real_path)
