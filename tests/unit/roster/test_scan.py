#!/usr/bin/python3
# Import Python libs
import sys

# Import local libs
import heist.roster.scan
import tests.helpers.mock_hub as helpers
import pop.hub

# Import 3rd-party libs
import mock
import pytest


@pytest.fixture
def mock_hub():
    '''
    mock the needed subs for the flat roster tests
    '''
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(subs=['heist.heist', 'heist.roster', 'rend', 'output'])

@pytest.fixture(scope='function')
def hub():
    '''
    Add required subs to the hub.
    '''
    hub = pop.hub.Hub()
    hub.OPT = {'heist': {}}
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heist.heist')

    hub.pop.sub.add(dyne_name='rend')
    yield hub
    hub.heist.init.clean()


class TestScanRoster:
    '''
    unit tests for heist.roster.scan
    '''
    @pytest.mark.asyncio
    async def test_read(self, hub):
        '''
        test scan roster against port 22 localhost
        '''
        # Setup
        target = '127.0.0.1'
        hub.OPT = {'heist': {'target': target,
                             'ssh_scan_ports': [22]}}

        # Execute
        ret = await heist.roster.scan.read(hub)

        assert ret[target]['host'] == target
        assert ret[target]['port'] == 22

    @pytest.mark.asyncio
    async def test_scan_non_ssh_port(self, hub):
        '''
        test scan roster against port not running ssh
        '''
        # Setup
        target = '127.0.0.1'
        hub.OPT = {'heist': {'target': target,
                             'ssh_scan_ports': [22222]}}

        # Execute
        ret = await heist.roster.scan.read(hub)

        assert ret == {}
