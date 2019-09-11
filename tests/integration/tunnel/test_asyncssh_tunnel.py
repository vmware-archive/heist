#!/usr/bin/python3
# Import Python libs
import asyncio
import tempfile
from typing import List, Tuple
from unittest.mock import create_autospec
import secrets

# Import local libs
import heis.tunnel.asyncssh_tunnel as asyncssh_tunnel
import tests.helpers.mock_hub as helpers
from tests.helpers.asyncssh_server import TestingAsyncSSHServer

# Import 3rd-party libs
import pop.utils.testing as testing
import pytest
from pop.hub import Hub
from M2Crypto import RSA, X509

PORT_RANGE = range(4400, 4410)


@pytest.fixture
def hub():
    hub = Hub()
    hub.pop.sub.add(dyne_name='tunnel')
    return hub


@pytest.fixture
def async_ssh_server_data():
    # Create temporary SSH keys for server
    private_key = tempfile.NamedTemporaryFile(prefix='id_rsa_')
    public_key = tempfile.NamedTemporaryFile(prefix='id_rsa_', suffix='.pub')
    key = RSA.gen_key(1024, 65537)
    key.save_key(private_key.name, cipher=None)
    key.save_pub_key(public_key.name)

    servers = []
    for port in PORT_RANGE:
        server = TestingAsyncSSHServer(username='test', port=port, private_key=private_key.name, public_key=public_key.name)
        servers.append(server)
    yield servers, (private_key.name, public_key.name)


class TestAsyncSSH:
    '''
    def test_create1(self):
        mock_hub = helpers.mock_hub()
        mock_create = create_autospec(asyncssh_tunnel.create)
        name = ''
        target = {}
        print('ye')
        mock_create(mock_hub, name, target)

    def test_create2(self):
        hub = Hub()
        fn_hub = testing.NoContractHub(hub)
        create_autospec(asyncssh_tunnel)
        # asyncssh_tunnel.__init__(hub)
    '''

    @pytest.mark.asyncio
    async def test_create(self, hub: Hub, async_ssh_server_data: Tuple[List[TestingAsyncSSHServer], Tuple[str, str]]):
        # spin up asyncssh server then connect to it; Start 10 servers on different ports
        # Setup
        async_ssh_servers, keys = async_ssh_server_data
        hub.OPT = {'heis': {}}
        target = {
            'client_keys': keys,
            #'x509_trusted_certs': [''],
        }
        coros = []

        # Execute
        for server in async_ssh_servers:
            coros.append(asyncssh_tunnel.create(hub, name=f'test_server{server.port}', target=target))

        # Verify

        # Cleanup
        await asyncio.gather(*coros)

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
