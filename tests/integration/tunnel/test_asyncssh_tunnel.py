#!/usr/bin/python3
# Import Python libs
import os
import sys
import subprocess
import tempfile
import time
from typing import Tuple

# Import local libs
import tests.helpers.sftp_server as sftp_server
import heis.tunnel.asyncssh_tunnel as asyncssh_tunnel

# Import 3rd-party libs
import mock
import pytest
from pop.hub import Hub
from M2Crypto import RSA


def ssh_keypair() -> Tuple[str, str]:
    private_key = tempfile.NamedTemporaryFile(prefix='id_rsa_')
    public_key = tempfile.NamedTemporaryFile(prefix='id_rsa_', suffix='.pub')
    key = RSA.gen_key(1024, 65537)
    key.save_key(private_key.name, cipher=None)
    key.save_pub_key(public_key.name)
    os.chmod(private_key.name, 400)
    os.chmod(public_key.name, 400)
    return os.path.expanduser('~/.ssh/id_rsa'), os.path.expanduser('~/.ssh/id_rsa.pub')
    # TODO This should be using these automatically created keys, not the exiting user keys
    return private_key.name, public_key.name


def spawn_server(port: int, **kwargs) -> subprocess.Popen:
    server_cmd = [
                     sys.executable,
                     sftp_server.__file__,
                     f'--port={port}',
                 ] + [f'--{key.replace("_", "-")}={value}' for key, value in kwargs.items()]
    print(' '.join(server_cmd))
    process = subprocess.Popen(server_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    # Allow the server to start up
    # TODO get a message from the server that it is started instead of sleeping
    time.sleep(1)
    # Verify that it started properly
    assert not process.poll(), b'\n'.join(process.stderr.readlines())
    return process


@pytest.fixture
def hub():
    hub = Hub()
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heis.heis')
    hub.pop.sub.add(dyne_name='tunnel')
    return hub


@pytest.fixture
def sftp_root() -> str:
    temp_dir = tempfile.TemporaryDirectory(prefix='heis_asyncssh_', suffix='_test_data')
    # TODO create files in the root
    yield temp_dir.name


@pytest.fixture(scope='function')
def basic_sftp_server() -> Tuple[subprocess.Popen, int, str]:
    private_key, public_key = ssh_keypair()
    port = 8039
    server = spawn_server(
        port=port,
        authorized_client_keys=public_key,
        server_host_keys=private_key,
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
