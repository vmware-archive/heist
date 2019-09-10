#!/usr/bin/python3
import heis.roster.yaml_file
import mock
import pytest
import tempfile
import tests.unit.helpers.mock_hub as helpers

ROSTER = '''
host_nul_id:
host_str_id:
  id: unique_id
host_num_id:
  id: 1234
'''


@pytest.fixture
def mock_hub():
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(subs=['heis.heis', 'heis.roster'])


class TestYamlFile:
    @pytest.mark.asyncio
    async def test_read(self, mock_hub):
        # Setup
        mock_hub.OPT = {'heis': {'roster_dir': tempfile.gettempdir()}}

        # Execute
        with mock.patch('builtins.open', mock.mock_open(read_data=ROSTER)):
            result = await heis.roster.yaml_file.read(mock_hub)

        # Verify
        assert result['host_nul_id'] is None
        assert result['host_str_id'] == {'id': 'unique_id'}
        assert result['host_num_id'] == {'id': 1234}
