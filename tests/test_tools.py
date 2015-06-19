from simpleshare import tools as t


def test_nice_size():
    """Depending on the size in bytes of a file, I want it's size in B,
    KiB, MiB etc"""
    assert t.nice_size(1) == '1.00 B'
    assert t.nice_size(104) == '0.10 KiB'
    assert t.nice_size(1024) == '1.00 KiB'
    assert t.nice_size(104000) == '0.10 MiB'
    assert t.nice_size(1048576) == '1.00 MiB'


def test_random_generator():
    """I'd like at least 1000's of generated strings to be different"""
    results = [t.random_generator() for x in xrange(1, 10000)]
    results_set = set(results)
    assert len(results) > 9990
    assert len(results_set) > 9990


def test_get_real_path():
    """I want to get an absolute, cleaned path that is really inside the 'permitted' path"""
    assert False


def test_prep_ls():
    """I want to get a simple list of files and folders separated by type"""
    assert False


def test_prep_ls_details():
    """I want to get a list of files and folders separated by type
    with details about the folder:
    - name, size, mtime
    """
    assert False


def test_list_dir_folder():
    """Get a list of files in a specific folder"""
    assert False


def test_list_dir_file():
    """Listing a 'file' gives us it's content or path when not in debug"""
    assert False


def test_get_config():
    """Query a key in a specific path"""
    assert False


def test_get_uid_from_path():
    """Get a list of sharing UID for a specifi path"""
    assert False


def test_get_path_from_uid():
    """Find the path shared from a specific sharing UID"""
    assert False


def test_delete_path():
    """Delete a file or a folder"""
    assert False


def test_check_config_path():
    """prepares config folder and check everything is fine"""
    assert False


def test_create_path():
    """Create a folder if it doesn't exist"""
    assert False


def test_create_random_folder():
    """Get a sharing UID that doesn't already exist"""
    assert False


def test_prep_upath():
    """I want to get a Unique path for a specific path in the KV store"""
    assert False


def test_configure():
    """Configure a Path/Key with a value"""
    assert False


def test_get_files():
    """Get only the file list from the listing of a path"""
    assert False


def test_protect_path():
    """I want to get a clean safe path inside one of the configured
    authorized paths"""
    assert False


def test_relist_parent_folder():
    """Get a list of files and folders in the parent of the specified path"""
    assert False


def test_validate_path():
    """Check if a path exists in the config, to avoid creating a folder
    with the same name as the path"""
    # Might not be needed anymore
    assert False
