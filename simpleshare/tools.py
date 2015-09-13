from cork import Cork
from os import listdir, getcwd, remove
from os.path import join as join_path, abspath, realpath
from os.path import isdir, isfile, exists
from os.path import split as split_path
from os.path import getsize, getmtime, relpath
from shutil import rmtree
import string
import random
from bottle import abort, response, static_file
from basicKVstore import get_config, get_real_path
from basicKVstore import check_config_path, prep_upath
# from zipfile import ZipFile
from shutil import make_archive

aaa = Cork('cork_conf')
root_dir = join_path(getcwd(), 'files')
DEBUG = True

files_path = 'files'
config_path = 'config'
uidshares_path = 'shares'

permitted_path = lambda user, postfix: join_path(root_dir, user, postfix)
permitted_files_path = lambda: permitted_path(
    aaa.current_user.username, files_path)
permitted_config_path = lambda: permitted_path(
    aaa.current_user.username, config_path)
permitted_shares_path = lambda: permitted_path(
    aaa.current_user.username, uidshares_path)

type_to_path = {
    'files': permitted_files_path,
    'config': permitted_config_path,
    'shares': permitted_shares_path}

defaults = {
    'public': True,
    'users': None,
    'expires': False
    }
sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
PATH_ERROR = "The path is not available or doesn't exist"


def nice_size(size):
    mul = len(str(size))/3
    size = float(size) / float(1 << (10 * mul))
    return "{:.2f} {}".format(size, sizes[mul])


def random_generator(size=4, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def prep_ls(path, details=True):
    """prepares a list of files and folders ready for the API.
    if a user is connected, we can see the sharing IDs associated to each.
    path: absolute path to list
    details: see files and folders informations
    """
    ls = {'dirs': [], 'files': []}
    if aaa.user_is_anonymous:
        user = None
    else:
        user = aaa.current_user
    _ls = listdir(path)
    for p in _ls:
        ls_path = join_path(path, p)
        if details:
            f = {'name': p,
                 'size': nice_size(getsize(ls_path)),
                 'mtime': getmtime(ls_path),
                 }
            if user:
                shares = [
                    (user.username, x)
                    for x in get_uid_from_path(ls_path)]
                # print('share list for {}: {}'.format(ls_path, shares))
                f['shares'] = shares
        else:
            f = p
        if isdir(ls_path):
            ls['dirs'].append(f)
        elif isfile(ls_path):
            ls['files'].append(f)
    return ls


def list_dir(path):
    """Return folder content or filename
    """
    try:
        if isdir(path) and exists(path):
            ls = prep_ls(path)
            return ls
        elif isfile(path):
            if DEBUG:
                root, filename = split_path(path)
                return static_file(filename, root=root, download=True)
            else:
                response.headers['X-Accel-Redirect'] = path
                return ''
    except OSError:
        abort(404)


def get_uid_from_path(path):
    """
    Get a list of sharing IDs associated to a path.
    path: path relative to a users folder
    """
    # get path relative to the permitted path where we upload files
    rel_path = relpath(path, permitted_files_path())
    # get a path in the form of <path>#/<path#>...
    Upath = prep_upath(rel_path)
    # get the protected path in the configuration folder
    config_path = protect_path(Upath, 'config')
    print(("config path is", config_path))
    if isdir(config_path):
        shares_names = prep_ls(config_path, False)['files']
        sharing_uids = [x[:-1] for x in shares_names]
        return sharing_uids
    return []


def get_path_from_uid(user, uid):
    # config/user/shares/uid
    jail = protect_path('.', '{}/shares'.format(user))
    return get_config(jail, uid, 'path')


def delete_path(real_path):
    if exists(real_path):
        if isfile(real_path):
            if DEBUG:
                return {real_path: 'deleted'}
            else:
                remove(real_path)
        elif isdir(real_path):
            if DEBUG:
                return {real_path: 'deleted'}
            else:
                rmtree(real_path)


def create_random_folder():
    count = 0
    ruid = random_generator()
    jail = type_to_path['shares']()
    while not check_config_path(jail, ruid) and count < 10:
        ruid = random_generator()
        count += 1
    # return ruid, create
    return ruid, ruid


def get_files(path):
    """Check if a path is shared and return the list of aliases"""
    files = list_dir(path)
    return files['files']


def protect_path(path, path_type='files'):
    """Get a path based on permitted paths"""
    f = type_to_path.get(path_type)
    if f is not None:
        permitted = f()
    elif path_type.endswith('shares'):
        permitted = join_path(root_dir, path_type)
    print(permitted)
    try:
        real_path = get_real_path(permitted, path)
        return real_path
    except IOError:
        raise
        abort(403)


def relist_parent_folder(path):
    try:
        # after deleting we want to re-list what the current folder hosts
        # append /..
        # follow symlink ???
        # get absolutepath
        permitted = abspath(realpath(join_path(path, '..')))
        assert path.startswith(permitted)
    except:
        abort(403, PATH_ERROR)
    ls = list_dir(permitted)
    if DEBUG:
        ls['dirs'].append({'name': 'edited something'})
        ls['files'].append({'name': 'edited {}'.format(path)})
    return ls


def archive_path(path, files=None):
    """Archives a folder or some files in this folder"""
    split = split_path(path)
    chdir = join_path(*split[:-1])
    print(chdir)
    dest = split[-1]
    dest_path = '/tmp/' + dest + str(random.randint(0, 200000)).zfill(6)
    print(dest)
    return make_archive(dest_path, 'zip', chdir, dest)
