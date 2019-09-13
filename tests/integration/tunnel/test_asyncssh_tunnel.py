#!/usr/bin/python3
# Import Python libs
import os
import sys
import subprocess
import tempfile
import time
import uuid
from typing import Tuple

# Import local libs
import tests.helpers.sftp_server as sftp_server
import heis.tunnel.asyncssh_tunnel as asyncssh_tunnel

# Import 3rd-party libs
import mock
import pytest
from pop.hub import Hub


def ssh_keypair() -> Tuple[str, str]:
    # Get the static ssh keys from the helpers directory
    helpers_dir = os.path.dirname(sftp_server.__file__)
    return os.path.join(helpers_dir, 'id_rsa_testing'), os.path.join(helpers_dir, 'id_rsa_testing.pub')


def spawn_server(port: int, pid_file: str, **kwargs) -> subprocess.Popen:
    server_cmd = [
                     sys.executable,
                     sftp_server.__file__,
                     f'--port={port}',
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

    time.sleep(1)
    # Verify that it started properly
    assert not process.poll(), b'\n'.join(process.stderr.readlines())
    return process


def random_file(directory: str, name: str, size: int = 1024) -> str:
    path = os.path.join(directory, name)
    with open(path, 'wb+') as out:
        out.write(os.urandom(size))
    return path


def sftp_root() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory(prefix='heis_asyncssh_', suffix='_root_data')
    random_file(directory=temp_dir.name, name='example.text')
    return temp_dir


@pytest.fixture(scope='function')
def hub():
    hub = Hub()
    hub.OPT = {'heis': {}}
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heis.heis')

    hub.pop.sub.add(dyne_name='tunnel')
    return hub


@pytest.fixture(scope='function')
def temp_dir() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory(prefix='heis_asyncssh_', suffix='_test_data')
    yield temp_dir.name


@pytest.fixture(scope='function')
def basic_sftp_server() -> Tuple[int, str]:
    # Generate a unique pid_file name, but do not create the file
    pid_file = os.path.join(tempfile.gettempdir(), f'asyncssh_test_{str(uuid.uuid4())[:8]}.pid')
    private_key, public_key = ssh_keypair()
    port = 8039
    server = spawn_server(
        port=port,
        authorized_client_keys=public_key,
        server_host_keys=private_key,
        pid_file=pid_file,
    )
    yield port, private_key
    server.kill()
    if os.path.exists(pid_file):
        os.remove(pid_file)


@pytest.fixture(scope='function')
def structured_sftp_server() -> Tuple[int, str]:
    # Generate a unique pid_file name, but do not create the file
    pid_file = os.path.join(tempfile.gettempdir(), f'asyncssh_test_{str(uuid.uuid4())[:8]}.pid')
    private_key, public_key = ssh_keypair()
    root = sftp_root().name
    port = 8040
    server = spawn_server(
        port=port,
        authorized_client_keys=public_key,
        server_host_keys=private_key,
        pid_file=pid_file,
        sftp_root=root,
    )
    yield port, private_key
    server.kill()
    if os.path.exists(pid_file):
        os.remove(pid_file)


class TestAsyncSSH:
    @pytest.mark.asyncio
    async def test_create(self, hub: Hub, basic_sftp_server: Tuple[int, str]):
        # Setup
        port, private_key = basic_sftp_server
        name = 'localhost'
        target = {
            'host': name,
            'port': port,
            'known_hosts': None,
            'client_keys': [private_key],
        }

        # Execute
        await asyncssh_tunnel.create(hub, name=name, target=target)

        # Verify
        assert hub.tunnel.asyncssh.CONS[name].get('con')
        assert hub.tunnel.asyncssh.CONS[name].get('sftp')

    @pytest.mark.asyncio
    async def test_send(self):
        ...

    @pytest.mark.asyncio
    async def test_get(self, hub: Hub, structured_sftp_server: Tuple[int, str], temp_dir):
        # Setup
        return
        port, private_key = structured_sftp_server
        name = 'localhost'
        source_file = 'example.text'
        destination = os.path.join(temp_dir, source_file)
        target = {
            'host': name,
            'port': port,
            'known_hosts': None,
            'client_keys': [private_key],
        }

        # Execute
        await asyncssh_tunnel.create(hub, name=name, target=target)

        # Verify
        await asyncssh_tunnel.get(hub, name, source_file, destination)
#        await hub.tunnel.asyncssh.CONS[name]['sftp'].get('taco.txt')

    @pytest.mark.asyncio
    async def test_cmd(self):
        ...

    @pytest.mark.asyncio
    async def test_tunnel(self):
        ...
