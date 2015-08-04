import keyval as t
from os import makedirs, path
from shutil import rmtree
from mock import patch, Mock


def prep_folder(conf=False):
    """prepare a temporary folder
    conf: is it a configuration folder ? else it is just a normal folder
    """
    try:
        rmtree('/tmp/test')
    except:
        pass
    if conf:
        makedirs('/tmp/test/usertest/config/testhash#/XYZ22#')
        makedirs('/tmp/test/usertest/shares/XYZ22#')
        with open('/tmp/test/usertest/config/testhash#/XYZ22K', 'w') as f:
            f.write('a')
        with open(
                '/tmp/test/usertest/shares/XYZ22#/pathK',
                'w') as f:
            f.write('/test/path')
        return
    makedirs('/tmp/test/folder')
    with open('/tmp/test/file', 'w') as f:
        f.write('a')


def del_folder(conf=False):
    rmtree('/tmp/test')


def test_get_config():
    """Query a key in a specific path"""
    t.root_dir = '/tmp/test'
    prep_folder(True)
    val = t.get_config('testhash', 'public')
    assert val is True
    del_folder(True)


def test_check_config_path():
    """prepares config folder and check everything is fine
    returns True if created False if not. Raises an exception if it's a file
    """
    t.root_dir = '/tmp/test'
    prep_folder(True)
    r = t.check_config_path('testhash')
    assert r is False
    r = t.check_config_path('nonexistent')
    assert r is True
    del_folder(True)
def test_prep_upath():
    """I want to get a Unique path for a specific path in the KV store"""
    r = t.prep_upath('relative/path')
    assert r == 'relative#/path#/'
    r = t.prep_upath('/relative/path')
    assert r == 'relative#/path#/'
    r = t.prep_upath('relative/path/')
    assert r == 'relative#/path#/'


def test_configure():
    """Configure a Path/Key with a value"""
    t.root_dir = '/tmp/test'
    t.configure('some/path', 'somekey', 'somevalue')
    assert path.isdir('/tmp/test/usertest/config/some#')
    assert path.isdir('/tmp/test/usertest/config/some#/path#')
    assert path.isfile('/tmp/test/usertest/config/some#/path#/somekeyK')
    assert open(
        '/tmp/test/usertest/config/some#/path#/somekeyK',
        'r').read() == 'somevalue'
