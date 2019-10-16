# -*- coding: utf-8 -*-
'''
    tests.unit.heist.conftest
    ~~~~~~~~~~~~~~

    Setup fixtures specifically for the heist unit tests
'''

# Import python libs
import sys

# Import local libs
import tests.helpers.mock_hub as helpers

# Import 3rd-party libs
import mock
import pytest
import pop
import pop.utils.testing as testing

@pytest.fixture(scope='function')
async def hub():
    '''
    Add required subs to the hub.
    '''
    hub = pop.hub.Hub()
    hub.OPT = {'heist': {}}
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heist.heist')

    hub.pop.sub.add(dyne_name='tunnel')
    hub.pop.sub.add(dyne_name='artifact')
    yield hub
    await hub.heist.init.clean()

@pytest.fixture
def mock_hub() -> testing.MockHub:
    '''
    mock the needed subs for the heist tests
    '''
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(subs=['heist.heist', 'roster', 'tunnel', 'artifact'])
