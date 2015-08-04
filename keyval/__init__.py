from os.path import isdir, exists
from os.path import join as join_path
from os.path import sep

DEBUG = True
PATH_ERROR = "The path is not available or doesn't exist"
dir_sep = "#" + sep


def get_config(rel_path, key, subdir='config'):
    """Get configuration from folder/path
    """
    Ukey = key + "K"
    Upath = prep_upath(rel_path)
    print(Upath)
    config_path = protect_path(Upath, subdir)
    path = config_path
    print(path)
    if not exists(path) or not isdir(path):
        raise IOError("The key doesn't exist")
    path = join_path(path, Ukey)
    if not exists(path):
        return defaults[key]
    else:
        with open(path, 'r') as f:
            value = f.read()
        return value


def check_config_path(rel_path, subdir='config'):
    """prepares config folder and check everything is fine
    rel_path: path relative to the 'subdir'
    """
    Upath = prep_upath(rel_path)
    # print("going to try to create {}".format(Upath))
    config_path = protect_path(Upath, subdir)
    print(config_path)
    # print("in {}".format(config_path))
    try:
        return create_path(config_path)
    except IOError:
        raise


def create_path(path):
    """prepares config folder and check everything is fine
    returns True if created False if not. Raises an exception if it's a file
    """
    if exists(path):
        if not isdir(path):
            raise IOError("Configuration path is not accessible")
        return False
    else:
        makedirs(path)
        return True


def prep_upath(rel_path):
    # print("&" * 80)
    # unique path to avoid key vs path collision
    if rel_path.startswith(sep):
        rel_path = rel_path[1:]
    if not rel_path.endswith(sep):
        rel_path = rel_path + sep
    split_path = rel_path.split(sep)
    # print(split_path)
    # relative unique path
    Upath = dir_sep.join(split_path)
    # print(Upath)
    # print("&" * 80)
    return Upath


def configure(rel_path, key, value=None, subdir='config'):
    """Configure things using folders and files
    value == None: keep default or don't modify the file
    path: /a/b/c/config/some#/path#/
    key: key + "K"
    """
    # absolute config path
    key = key + "K"
    Upath = prep_upath(rel_path)
    config_path = protect_path(Upath, subdir)
    # print("*" * 80)
    # print("got {} {} {} {}".format(rel_path, key, value, subdir))
    # print(config_path)
    create_path(config_path)
    if value is None:
        return config_path
    path = join_path(config_path, key)
    # print(path)
    # print("*" * 80)
    with open(path, 'w') as f:
        f.write(value)



