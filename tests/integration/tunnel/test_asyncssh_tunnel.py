#!/usr/bin/python3
# Import testing utils
from unittest.mock import create_autospec
from pop.hub import Hub
import pop.utils.testing as testing
import heis.tunnel.asyncssh_tunnel as asyncssh_tunnel
import pytest
import mock

class TestAsyncSSH:
    def test_create(self):
        hub = Hub()

        mock_hub = testing.MockHub(hub)
        mock_create = create_autospec(asyncssh_tunnel.create)
        name = ''
        target = {}
        print('ye')
        mock_create(mock_hub, name, target)

    def test_create2(self):
        hub = Hub()
        fn_hub = testing.NoContractHub(hub)
        create_autospec(asyncssh_tunnel)
        #asyncssh_tunnel.__init__(hub)

    @pytest.mark.asyncio
    async def test_create(self):
        hub = Hub()
        mock_hub = testing.MockHub(hub)
        mock_hub.OPT = {'heis': {}}

        name = ''
        target = {}
        #await asyncssh_tunnel.create(mock_hub, name=name, target=target)

        # TODO spin up asyncssh server then connect to it; Start 10 servers on differetn ports

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