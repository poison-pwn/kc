from utils.keyfiles import PasswdFile
from utils.exceptions import EmptyError
from utils.exceptions import PasswdFileExistsErr
from pathlib import Path
from nacl.public import PrivateKey
import shutil
import pytest


@pytest.fixture(autouse=True, scope="module")
def passfile_parent(tmp_path_factory) -> Path:
    parent_dir: Path = tmp_path_factory.mktemp("passfile_parent")
    yield parent_dir
    shutil.rmtree(parent_dir)


def test_empty_service_name(passfile_parent):
    with pytest.raises(EmptyError):
        PasswdFile.from_service_name("", passfile_parent)


@pytest.mark.parametrize(
    "malicious_service_name_pair",
    [
        ("nested_folder/../../../../test_service_name_0", "test_service_name_0"),
        ("../test_service_name_1", "test_service_name_1"),
    ],
)
def test_malicious_service_name(
    malicious_service_name_pair: str, passfile_parent: Path
):
    malicious_service_name, resolved_service_name = malicious_service_name_pair
    passwd_file = PasswdFile.from_service_name(malicious_service_name, passfile_parent)
    assert passwd_file.with_suffix("") == passfile_parent / resolved_service_name


@pytest.fixture(autouse=True, scope="module")
def pass_file(passfile_parent, service_name="service_name"):
    pass_file = PasswdFile.from_service_name(service_name, passfile_parent)
    assert not pass_file.exists()
    yield pass_file


passwd = "M0Ms_-Sp46h377i"


@pytest.fixture(params=["parent_folder/nested_service_name.ext", "something.ext"])
def tmp_alias_dest_path(passfile_parent: Path, request):
    path = passfile_parent / request.param
    yield path
    path.unlink(missing_ok=True)


@pytest.mark.run(before="test_passwd_write")
def test_nonexistant_read(
    pass_file: PasswdFile,
    secret_key: PrivateKey,
):
    assert not pass_file.exists()
    get_secret_key_callback = lambda: secret_key
    with pytest.raises(FileNotFoundError):
        pass_file.retrieve_passwd(get_secret_key_callback)


@pytest.mark.run(before="test_passwd_write")
def test_alias_nonexistant_source(pass_file: PasswdFile, tmp_alias_dest_path: Path):
    assert not pass_file.exists()
    with pytest.raises(FileNotFoundError):
        pass_file.alias(tmp_alias_dest_path)
    assert not tmp_alias_dest_path.exists()


def test_passwd_write(pass_file: PasswdFile, public_key):
    assert not pass_file.exists()
    pass_file.write_passwd(passwd, public_key)
    assert pass_file.exists()
    with pytest.raises(PasswdFileExistsErr):
        pass_file.write_passwd(passwd, public_key)


@pytest.mark.run(after="test_passwd_write")
def test_password_read(pass_file: PasswdFile, secret_key):
    assert pass_file.exists()
    get_secret_key_callback = lambda: secret_key
    decrpyted_passwd = pass_file.retrieve_passwd(get_secret_key_callback)
    assert decrpyted_passwd == passwd


@pytest.mark.run(after="test_passwd_write")
def test_alias(pass_file: PasswdFile, tmp_alias_dest_path: Path):
    assert pass_file.exists()
    pass_file.alias(tmp_alias_dest_path)
    assert tmp_alias_dest_path.exists()
    assert tmp_alias_dest_path.is_symlink()
    assert tmp_alias_dest_path.readlink() == pass_file
