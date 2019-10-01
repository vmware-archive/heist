#!/usr/bin/python3
# Import local libs
import heist.roster.init
import tests.helpers.mock_hub as helpers

# Import 3rd-party libs
import pop.utils.testing as testing
import pytest


@pytest.fixture
def mock_hub() -> testing.MockHub:
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(['roster'])


class TestSaltMaster:
    @pytest.mark.asyncio
    async def test_read(self, mock_hub: testing.MockHub):
        # Setup
        roster = 'yaml'
        ready = {'id_0': {}, 'id_1': {'id': 'id_1'}}
        expected = [{'id': 'id_0'}, {'id': 'id_1'}]
        mock_hub.roster.yaml.read.return_value = ready

        # Execute
        result = await heist.roster.init.read(mock_hub, roster)

        # Verify
        mock_hub.roster.yaml.read.assert_called_once()
        assert result == expected

