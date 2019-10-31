#!/usr/bin/python3
'''
    tests.unit.heist.test_heist
    ~~~~~~~~~~~~~~

    tests for heist.init code
'''

# Import local libs
import heist.heist.init
import tests.helpers.mock_hub as helpers

# import 3rd-party libs
import mock
import pop.mods.pop.testing as testing
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
        mock_hub.roster.init.read.return_value = {'id': {'host': 'test'}}

        await heist.heist.init.run(mock_hub)

        mock_hub.roster.init.read.assert_called_with(mock.sentinel.roster)
        mock_hub.heist.salt_master.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_roster_false(self, mock_hub: testing.MockHub):
        '''
        test heist.heist.init when roster does not render correctly
        '''
        mock_hub.OPT = {'heist': {'roster': mock.sentinel.roster, 'manager': 'salt_master'}}
        mock_hub.roster.init.read.return_value = False

        await heist.heist.init.run(mock_hub)

        mock_hub.roster.init.read.assert_called_with(mock.sentinel.roster)
        mock_hub.heist.salt_master.run.assert_not_called()


    @pytest.mark.parametrize('addr',
                             [('127.0.0.1', True),
                              ('::1', True),
                              ('2001:0db8:85a3:0000:0000:8a2e:0370:7334', False),
                              ('localhost', True),
                              ('1.1.1.1', False),
                              ('google.com', False)])
    def test_ip_is_loopback(self, addr, mock_hub):
        '''
        Test for function ip_is_loopback
        when socket error raised, expected
        return is False
        '''
        ret = heist.heist.init.ip_is_loopback(mock_hub, addr[0])
        assert ret == addr[1]

    def test_ip_is_loopback_exception(self, mock_hub):
        '''
        Test for function ip_is_loopback
        when address is not valid
        '''
        assert not heist.heist.init.ip_is_loopback(mock_hub, '')
