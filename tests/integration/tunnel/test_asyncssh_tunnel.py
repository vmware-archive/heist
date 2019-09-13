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
    for _ in range(100):
        if os.path.exists(pid_file) or (process.poll() is not None):
            # At this point either the server is running or crashed because of the args you gave it
            break
        else:
            time.sleep(.1)

    # Verify that it started properly
    assert not process.poll(), b'\n'.join(process.stderr.readlines())
    return process


def sftp_root() -> tempfile.TemporaryDirectory:
    temp_dir = tempfile.TemporaryDirectory(prefix='heis_asyncssh_', suffix='_test_data')
    # TODO create files in the root
    return temp_dir


@pytest.fixture(scope='function')
def hub():
    hub = Hub()
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heis.heis')
    hub.pop.sub.add(dyne_name='tunnel')
    return hub


@pytest.fixture(scope='function')
def basic_sftp_server() -> Tuple[subprocess.Popen, int, str]:
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
    yield server, port, private_key
    server.kill()


class TestAsyncSSH:
    @pytest.mark.asyncio
    async def test_create(self, hub: Hub, basic_sftp_server: Tuple[subprocess.Popen, int, str]):
        # Setup
        server, port, private_key = basic_sftp_server
        name = 'localhost'
        hub.OPT = {'heis': {}}
        target = {
            'host': 'localhost',
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
    async def test_get(self):
        ...
        # await hub.tunnel.asyncssh.CONS['localhost']['sftp'].get('taco.txt')

    @pytest.mark.asyncio
    async def test_cmd(self):
        ...

    @pytest.mark.asyncio
    async def test_tunnel(self):
        ...
