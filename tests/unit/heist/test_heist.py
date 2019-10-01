#!/usr/bin/python3
# Import local libs
import heist.heist.init
import tests.helpers.mock_hub as helpers

# import 3rd-party libs
import mock
import pop.utils.testing as testing
import pytest


@pytest.fixture
def mock_hub() -> testing.MockHub:
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(subs=['heist.heist', 'heist.roster'])


class TestSaltMaster:
    def test_load_subs(self):
        mock_hub = helpers.mock_hub()
        heist.heist.init.load_subs(mock_hub)
        mock_hub.pop.sub.add.assert_any_call(dyne_name='rend')
        mock_hub.pop.sub.add.assert_any_call(dyne_name='roster')
        mock_hub.pop.sub.add.assert_any_call(dyne_name='tunnel')

    def test_start(self):
        mock_hub = helpers.mock_hub(['heist.heist'])
        heist.heist.init.start(mock_hub)
        mock_hub.pop.loop.start.assert_called_once()
        mock_hub.heist.init.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run(self, mock_hub: testing.MockHub):
        mock_hub.OPT = {'heist': {'roster': mock.sentinel.roster, 'manager': 'salt_master'}}
        mock_hub.roster.init.read.return_value = {}

        await heist.heist.init.run(mock_hub)

        mock_hub.roster.init.read.assert_called_with(mock.sentinel.roster)
        mock_hub.heist.salt_master.run.assert_called_once()
