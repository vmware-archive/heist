#!/usr/bin/python3
# Import Python libs
import os
import sys
import subprocess
import tempfile
from typing import Tuple

# Import local libs
import tests.helpers.sftp_server as sftp_server
import heis.tunnel.asyncssh_tunnel as asyncssh_tunnel

# Import 3rd-party libs
import mock
import pytest
from pop.hub import Hub
from M2Crypto import RSA


@pytest.fixture
def ssh_keypair() -> Tuple[str, str]:
    private_key = tempfile.NamedTemporaryFile(prefix='id_rsa_')
    public_key = tempfile.NamedTemporaryFile(prefix='id_rsa_', suffix='.pub')
    key = RSA.gen_key(1024, 65537)
    key.save_key(private_key.name, cipher=None)
    key.save_pub_key(public_key.name)
    os.chmod(private_key.name, 400)
    os.chmod(public_key.name, 400)
    yield private_key.name, public_key.name


@pytest.fixture
def hub():
    hub = Hub()
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heis.heis')
    hub.pop.sub.add(dyne_name='tunnel')
    return hub


@pytest.fixture
def sftp_root():
    # TODO create a temporary directory with a bunch of files in it
    yield '/tmp/sftp/heis'


def spawn_server(port: int, **kwargs) -> subprocess.Popen:
    return subprocess.Popen(
        [
            sftp_server.__file__,
            f'--port={port}',
        ] + [f'--{key}={value}' for key, value in kwargs.items()]
    )


class TestAsyncSSH:
    @pytest.mark.asyncio
    async def test_create(self, hub: Hub, ssh_keypair: Tuple[str, str], sftp_root: str):
        # Setup
        private_key, public_key = ssh_keypair
        port = 8022
        name = 'localhost'
        hub.OPT = {'heis': {}}
        target = {
            'host': 'localhost',
            'port': port,
            'known_hosts': None,
            # 'client_keys': [private_key],
            'client_keys': [os.path.expanduser('~/.ssh/id_rsa')],
        }

        # Execute
        server = spawn_server(port=port,
                              authorized_client_keys=public_key,
                              server_host_keys=private_key,
                              sftp_root=sftp_root
                              )
        print('created server')
        await asyncssh_tunnel.create(hub, name=name, target=target)
        print('\n' + '*' * 100)

        # verify
        await hub.tunnel.asyncssh.CONS['localhost']['sftp'].get('taco.txt')

        # Cleanup
        server.kill()

    @pytest.mark.asyncio
    async def test_send(self):
        ...

    @pytest.mark.asyncio
    async def test_get(self):
        ...

    @pytest.mark.asyncio
    async def test_cmd(self):
        ...

    @pytest.mark.asyncio
    async def test_tunnel(self):
        ...
