# -*- coding: utf-8 -*-
'''
    tests.unit.conftest
    ~~~~~~~~~~~~~~

    Provide mock_hub fixture for all unit tests.
'''

import sys
import unittest.mock as mock

import pytest

import pop.hub
import pop.mods.pop.testing as testing


@pytest.fixture('session')
def _hub():
    # provides a full hub that is used as a reference by mock_hub
    hub = pop.hub.Hub()

    # strip pytest args (Akm0d)
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heist.heist')

    return hub


@pytest.fixture
def mock_hub(_hub):
    return testing.MockHub(_hub)
