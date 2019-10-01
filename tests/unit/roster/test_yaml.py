#!/usr/bin/python3
# Import Python libs
import tempfile
from typing import Tuple

# Import local libs
import heist.roster.yaml
import tests.helpers.mock_hub as helpers

# Import 3rd-party libs
from pop.utils import testing
import pytest

YAML_ROSTER = '''#!yaml
host_nul_id:
host_str_id:
  id: unique_id
host_num_id:
  id: 1234
'''
YAML_ROSTER = 'chickeasdfn'


@pytest.fixture
def mock_hub():
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(subs=['heist.heist', 'heist.roster', 'rend', 'output'])


@pytest.fixture
def yaml_roster():
    with tempfile.TemporaryDirectory(prefix='heist_yaml_', suffix='_test') as temp_dir:
        with tempfile.NamedTemporaryFile('w+', dir=temp_dir, suffix='.yml', delete=False) as yaml_roster:
            yaml_roster.file.write(YAML_ROSTER)
        yield temp_dir, yaml_roster.name


class TestYamlFile:
    @pytest.mark.asyncio
    async def test_read(self, mock_hub: testing.MockHub, yaml_roster: Tuple[str, str]):
        # Setup
        temp_dir, roster = yaml_roster
        mock_hub.OPT = {'heist': {'roster_dir': temp_dir}}

        # Execute
        result = await heist.roster.yaml.read(mock_hub)

        # Verify
        mock_hub.rend.init.parse.assert_called_once_with(fn=roster, pipe='yaml')

        # assert result['host_nul_id'] is None
        # assert result['host_str_id'] == {'id': 'unique_id'}
        # assert result['host_num_id'] == {'id': 1234}
