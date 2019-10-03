# -*- coding: utf-8 -*-
'''
    tests.unit.roster.conftest
    ~~~~~~~~~~~~~~

    Setup fixtures specifically for the roster unit tests
'''

# Import local libs
import tests.helpers.mock_hub as helpers

# Import 3rd-party libs
import pytest

@pytest.fixture
def mock_hub():
    '''
    mock the needed subs for the flat roster tests
    '''
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(subs=['heist.heist', 'heist.roster', 'rend', 'output'])
