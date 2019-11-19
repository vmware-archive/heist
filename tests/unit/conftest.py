# -*- coding: utf-8 -*-
'''
    tests.unit.conftest
    ~~~~~~~~~~~~~~

    Provide mock_hub fixture for all unit tests.
'''

import pop.mods.pop.testing as testing

import pytest
from tests.helpers.mock_hub import hub


@pytest.fixture('session')
def _hub():
    # A fixture is required for asynchronous tests to access a mock_hub
    return hub(subs=['heist.heist', 'roster', 'tunnel', 'artifact'])


@pytest.fixture
def mock_hub(_hub):
    return testing.MockHub(_hub)
