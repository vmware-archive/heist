#!/usr/bin/python3
# Import Python libs
import itertools
import os
import sys
import subprocess
import tempfile
import time
import uuid
from typing import Set, Tuple, Generator

# Import local libs
import tests.helpers.sftp_server as sftp_server

# Import 3rd-party libs
import mock
import psutil
import pytest
from pop.hub import Hub


def used_ports() -> Set[int]:
    '''
    :return: A set of all the used ports on the local system
    '''
    return {x.laddr.port for x in psutil.net_connections()}


def unused_ports() -> Generator[int, None, None]:
    '''
    :return: A generator that gets the next unused port from the user range
    '''
    for port in itertools.cycle(range(49152, 65535)):
        if port not in used_ports():
            yield port


def ssh_keypair() -> Tuple[str, str]:
    '''
    :return: The absolute paths of static ssh keys in the helpers directory
    '''
    helpers_dir = os.path.dirname(sftp_server.__file__)
    return os.path.join(helpers_dir, 'id_rsa_testing'), os.path.join(helpers_dir, 'id_rsa_testing.pub')


def spawn_server(sftp_port: int, pid_file: str, **kwargs) -> subprocess.Popen:
    '''
    :param sftp_port: The port for the server to run on
    :param pid_file: The path where the server will create a PID file
    :param kwargs: SSHServer connection options that will be passed to the server
    :return: A subprocess Pipe to the process
    '''
    server_cmd = [
                     sys.executable,
                     sftp_server.__file__,
                     f'--sftp-port={sftp_port}',
                     f'--pid-file={pid_file}',
                 ] + [f'--{key.replace("_", "-")}={value}' for key, value in kwargs.items()]
    print(' '.join(server_cmd))
    process = subprocess.Popen(server_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    # Allow the server time to start up
    for _ in range(1000):
        if os.path.exists(pid_file) or (process.poll() is not None):
            # At this point either the server is running or crashed because of the args you gave it
            break
        else:
            time.sleep(.1)

    # Verify that it started properly
    assert not process.poll(), b'\n'.join(process.stderr.readlines())
    return process


def random_file(directory: str = None, name: str = None, size: int = 1024) -> str:
    '''
    :param name: The text name of the file, defaults to a random string
    :param directory: The directory to create the file in; defaults to /tmp or it's equivalent
    :param size: The amount of random bytes to fill the file with
    :return:
    '''
    if not directory:
        directory = tempfile.gettempdir()
    if not name:
        name = str(uuid.uuid4())[:10]
    path = os.path.join(directory, name)
    with open(path, 'wb+') as out:
        out.write(os.urandom(size))
    return path


def sftp_root() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory(prefix='heist_asyncssh_', suffix='_root_data')
    return temp_dir


@pytest.fixture(scope='function')
def hub() -> Hub:
    hub = Hub()
    hub.OPT = {'heist': {}}
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heist.heist')

    hub.pop.sub.add(dyne_name='tunnel')
    yield hub
    hub.heist.init.clean()


@pytest.fixture(scope='function')
def temp_dir() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory(prefix='heist_asyncssh_', suffix='_test_data')
    yield temp_dir.name


@pytest.fixture(scope='function')
def basic_sftp_server() -> Tuple[int, str, str]:
    # Generate a unique pid_file name, but do not create the file
    pid_file = os.path.join(tempfile.gettempdir(), f'asyncssh_test_{str(uuid.uuid4())[:8]}.pid')
    private_key, public_key = ssh_keypair()
    root = sftp_root()
    port = unused_ports()
    sftp_port = next(port)
    server = spawn_server(
        sftp_port=sftp_port,
        authorized_client_keys=public_key,
        server_host_keys=private_key,
        pid_file=pid_file,
        sftp_root=root.name,
    )
    yield sftp_port, private_key, root.name
    server.kill()
    if os.path.exists(pid_file):
        os.remove(pid_file)


@pytest.fixture(scope='function')
def sftp_ssh_server() -> Tuple[int, int, str]:
    # Generate a unique pid_file name, but do not create the file
    pid_file = os.path.join(tempfile.gettempdir(), f'asyncssh_test_{str(uuid.uuid4())[:8]}.pid')
    private_key, public_key = ssh_keypair()
    port = unused_ports()
    sftp_port = next(port)
    ssh_port = next(port)
    # TODO for testing commands should ssh and sftp be on the same port?
    # If yes then set `reuse_address` and `reuse_port` to `True`
    server = spawn_server(
        sftp_port=sftp_port,
        ssh_port=ssh_port,
        authorized_client_keys=public_key,
        server_host_keys=private_key,
        pid_file=pid_file,
    )
    yield sftp_port, ssh_port, private_key
    server.kill()
    if os.path.exists(pid_file):
        os.remove(pid_file)


class TestAsyncSSH:
    @pytest.mark.asyncio
    async def test_create_and_destroy(self, hub: Hub, basic_sftp_server: Tuple[int, str, str]):
        # Setup
        port, private_key, _ = basic_sftp_server
        name = 'localhost'
        target = {
            'host': name,
            'port': port,
            'known_hosts': None,
            'client_keys': [private_key],
        }

        # Execute
        await hub.tunnel.asyncssh.create(name=name, target=target)

        # Verify
        assert hub.tunnel.asyncssh.CONS[name].get('con')
        assert hub.tunnel.asyncssh.CONS[name].get('sftp')

        # Cleanup, since nothing was accessed the connection will be hanging
        hub.tunnel.asyncssh.destroy(name)

    @pytest.mark.asyncio
    async def test_send(self, hub: Hub, basic_sftp_server: Tuple[int, str, str], temp_dir: str):
        # Setup
        port, private_key, root = basic_sftp_server
        name = 'localhost'
        file_name = 'send_example.text'
        source_path = random_file(temp_dir, file_name)
        target = {
            'host': name,
            'port': port,
            'known_hosts': None,
            'client_keys': [private_key],
        }
        await hub.tunnel.asyncssh.create(name=name, target=target)

        # Execute
        # Send the temporary file to the root of the sftp server
        await hub.tunnel.asyncssh.send(name=name, source=source_path, dest=file_name)

        # Verify
        assert os.path.exists(os.path.join(root, file_name))

    @pytest.mark.asyncio
    async def test_get(self, hub: Hub, basic_sftp_server: Tuple[int, str, str], temp_dir: str):
        # Setup
        port, private_key, root = basic_sftp_server
        name = 'localhost'
        file_name = 'get_example.txt'
        # Create a file in the sftp root
        random_file(directory=root, name=file_name)
        dest_path = os.path.join(temp_dir, file_name)
        target = {
            'host': name,
            'port': port,
            'known_hosts': None,
            'client_keys': [private_key],
        }
        await hub.tunnel.asyncssh.create(name=name, target=target)

        # Execute
        await hub.tunnel.asyncssh.get(name=name, source=file_name, dest=dest_path)

        # Verify
        assert os.path.exists(dest_path)

    @pytest.mark.asyncio
    async def test_cmd(self, hub: Hub, sftp_ssh_server: Tuple[int, int, str]):
        # Setup
        sftp_port, ssh_port, private_key = sftp_ssh_server
        name = 'localhost'
        command = ''
        target = {
            'host': name,
            'port': sftp_port, 'known_hosts': None,
            'client_keys': [private_key],
        }
        await hub.tunnel.asyncssh.create(name=name, target=target)

        # Execute
        # TODO Run a command and verify that it executed correctly on the remote
        # await hub.tunnel.asyncssh.cmd(name=name, command=command)

        # Verify

    @pytest.mark.asyncio
    async def test_tunnel(self, hub: Hub, basic_sftp_server: Tuple[int, str, str]):
        # Setup
        port, private_key, _ = basic_sftp_server
        name = 'localhost'
        remote = next(unused_ports())
        target = {
            'host': name,
            'port': port, 'known_hosts': None,
            'client_keys': [private_key],
        }
        await hub.tunnel.asyncssh.create(name=name, target=target)

        # Execute
        await hub.tunnel.asyncssh.tunnel(name=name, local=port, remote=remote)

        # Verify
        # TODO How to verify that the tunnel was successful? It's clear from the logs that it is:
        # `Creating remote TCP forwarder from port xxxxx to localhost, port xxxxx`
