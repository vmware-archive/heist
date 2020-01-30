#!/usr/bin/python3
# Import Python libs
import sys
import tempfile
import textwrap
from typing import Tuple
import unittest.mock as mock

# Import local libs
import heist.roster.flat
import pop.hub
from pop.mods.pop import testing

# Import 3rd-party libs
import pytest


FLAT_ROSTER = '''#!yaml
host_nul_id:
host_str_id:
  id: unique_id
host_num_id:
  id: 1234
'''


@pytest.fixture(scope='function')
async def hub():
    '''
    Add required subs to the hub.
    '''
    hub = pop.hub.Hub()
    hub.OPT = {'heist': {}}
    with mock.patch.object(sys, 'argv', sys.argv[:1]):
        hub.pop.sub.add('heist.heist')

    hub.pop.sub.add(dyne_name='rend')
    yield hub
    await hub.heist.init.clean()


@pytest.fixture
def flat_roster():
    '''
    setup temporary roster directory and file
    '''
    with tempfile.TemporaryDirectory(prefix='heist_flat_', suffix='_test') as temp_dir:
        with tempfile.NamedTemporaryFile('w+', dir=temp_dir, suffix='.yml',
                                         delete=False) as flat_roster:
            flat_roster.file.write(FLAT_ROSTER)
        yield temp_dir, flat_roster.name


class TestFlatFile:
    '''
    unit tests for heist.roster.flat
    '''
    @pytest.mark.asyncio
    async def test_read(self, mock_hub: testing.MockHub, flat_roster: Tuple[str, str]):
        '''
        test reading a yaml file with mock_hub
        '''
        # Setup
        temp_dir, roster = flat_roster
        mock_hub.OPT = {'heist': {'roster_dir': temp_dir,
                                  'renderer': 'jinja|yaml'}}

        # Execute
        await heist.roster.flat.read(mock_hub)

        # Verify
        mock_hub.rend.init.parse.assert_called_once_with(fn=roster, pipe='jinja|yaml')

    @pytest.mark.asyncio
    async def test_read_rend_shebang(self, hub: testing.MockHub, flat_roster: Tuple[str, str]):
        '''
        read yaml file with shebang at top of roster,
        and renderer is set to 'toml'
        '''
        # Setup
        temp_dir, roster = flat_roster
        with open(roster, 'w') as _f:
            _f.write(textwrap.dedent('''\
                     #!jinja|yaml
                     {% set user = 'heist' %}
                     localhost:
                       user: {{ user }}
                     '''))
        hub.OPT = {'heist': {'roster_dir': temp_dir,
                             'renderer': 'toml'}}

        # Execute
        result = await heist.roster.flat.read(hub)

        assert result['localhost']['user'] == 'heist'

    @pytest.mark.asyncio
    async def test_read_rend_no_shebang(self, hub: testing.MockHub, flat_roster: Tuple[str, str]):
        '''
        read yaml file without shebang at top of roster,
        and renderer is set to 'jinja|yaml'
        '''
        # Setup
        temp_dir, roster = flat_roster
        with open(roster, 'w') as _f:
            _f.write(textwrap.dedent('''\
                     {% set user = 'heist' %}
                     localhost:
                       user: {{ user }}
                     '''))
        hub.OPT = {'heist': {'roster_dir': temp_dir,
                             'renderer': 'jinja|yaml'}}

        # Execute
        result = await heist.roster.flat.read(hub)

        assert result['localhost']['user'] == 'heist'

    @pytest.mark.asyncio
    async def test_roster_file(self, mock_hub: testing.MockHub, flat_roster: Tuple[str, str]):
        '''
        test when using roster_file in flat roster
        '''
        # Setup
        temp_dir, roster = flat_roster
        mock_hub.OPT = {'heist': {'renderer': 'jinja|yaml',
                                  'roster_file': roster}}

        # Execute
        ret = await heist.roster.flat.read(mock_hub)

        # Verify
        assert ret.return_value()
        mock_hub.rend.init.parse.assert_called_once_with(fn=roster, pipe='jinja|yaml')
