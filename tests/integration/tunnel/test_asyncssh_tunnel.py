#!/usr/bin/python3
# Import Python libs
import asyncio
import tempfile
from typing import Tuple

# Import local libs
import heis.tunnel.asyncssh_tunnel as asyncssh_tunnel
from tests.helpers.asyncssh_server import TestingAsyncSFTPServer

# Import 3rd-party libs
import asyncssh
import pytest
from pop.hub import Hub
from M2Crypto import RSA


@pytest.fixture
def hub():
    hub = Hub()
    hub.pop.sub.add(dyne_name='tunnel')
    return hub


@pytest.fixture
async def async_sftp_server_data(port: int = 5050, *args, **kwargs) -> TestingAsyncSFTPServer:
    private_key = tempfile.NamedTemporaryFile(prefix='id_rsa_')
    public_key = tempfile.NamedTemporaryFile(prefix='id_rsa_', suffix='.pub')
    key = RSA.gen_key(1024, 65537)
    key.save_key(private_key.name, cipher=None)
    key.save_pub_key(public_key.name)

    server = await asyncssh.listen(
        '',
        port=port,
        server_host_keys=[private_key.name],
        authorized_client_keys=[public_key.name],
        sftp_factory=asyncssh.SFTPServer,
        *args,
        **kwargs
    )
    yield server, private_key.name, port

    server.close()


class TestAsyncSSH:
    @pytest.mark.asyncio
    async def test_create(self, hub: Hub, async_sftp_server_data: Tuple[TestingAsyncSFTPServer, str, int]):
        server, private_key, port = async_sftp_server_data
        name = 'localhost'
        hub.OPT = {'heis': {}}
        target = {
            'host': 'localhost',
            'port': port,
            'known_hosts': None,
            'client_keys': [private_key],
        }

        return
        await asyncssh_tunnel.create(hub, name=name, target=target)
        print('created')
        result = await hub.tunnel.asyncssh.CONS[name]['sftp'].get('taco.txt')
        assert result

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
