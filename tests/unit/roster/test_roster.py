#!/usr/bin/python3
# Import local libs
import heist.roster.init
import tests.helpers.mock_hub as helpers

# Import pop libs
import pop.utils.testing as testing
import rend.exc

# Import 3rd-party libs
import pytest


@pytest.fixture
def mock_hub() -> testing.MockHub:
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(['roster'])


class TestSaltMaster:
    @pytest.mark.asyncio
    async def test_read(self, mock_hub: testing.MockHub):
        # Setup
        roster = 'flat'
        ready = {'id_0': {}, 'id_1': {'id': 'id_1'}}
        expected = [{'id': 'id_0'}, {'id': 'id_1'}]
        mock_hub.roster.flat.read.return_value = ready

        # Execute
        result = await heist.roster.init.read(mock_hub, roster)

        # Verify
        mock_hub.roster.flat.read.assert_called_once()
        assert result == expected

    @pytest.mark.asyncio
    async def test_read_error(self, mock_hub: testing.MockHub):
        '''
        test heist.roster.init.read error checking
        '''
        # Setup
        roster = 'flat'
        ready = {'{% test %}'}
        mock_hub.roster.flat.read.return_value = ready

        # Execute
        result = await heist.roster.init.read(mock_hub, roster)

        # Verify
        mock_hub.roster.flat.read.assert_called_once()
        assert not result

    @pytest.mark.asyncio
    async def test_read_id_missing(self, mock_hub: testing.MockHub):
        '''
        test heist.roster.init.read error checking
        '''
        # Setup
        roster = 'flat'
        ready = {'user': 'heist', 'password': 'passwd'}
        mock_hub.roster.flat.read.return_value = ready

        # Execute
        await heist.roster.init.read(mock_hub, roster)

        # Verify
        mock_hub.roster.flat.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_read_read_empty(self, mock_hub: testing.MockHub):
        '''
        test heist.roster.init.read when rend returns empty
        '''
        # Setup
        roster = 'flat'
        ready = {}
        mock_hub.roster.flat.read.return_value = ready

        # Execute
        assert not await heist.roster.init.read(mock_hub, roster)

        # Verify
        mock_hub.roster.flat.read.assert_called_once()

    @pytest.mark.asyncio
    async def test_read_rend_exc(self, mock_hub: testing.MockHub):
        '''
        test heist.roster.init.read when a rend.exc is raised
        '''
        # Setup
        roster = 'flat'
        mock_hub.roster.flat.read.side_effect = rend.exc.RenderException("Jinja error '}'")

        # Execute
        assert not await heist.roster.init.read(mock_hub, roster)

        # Verify
        mock_hub.roster.flat.read.assert_called_once()
