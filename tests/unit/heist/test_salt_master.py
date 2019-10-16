#!/usr/bin/python3
# Import Python libs
import asyncio
import os
import secrets
from typing import Any, Dict, Tuple

# Import Local libs
import heist.heist.salt_master

# Import 3rd-party libs
import asyncssh.process
import mock
import pop.utils.testing as testing
import pytest


@pytest.fixture
def mk_config_data(hub, roster):
    # Setup
    t_name = secrets.token_hex()
    hub.heist.ROSTERS = {t_name: roster}
    root_dir = 'arbitrary_string'
    minion_config = heist.heist.salt_master.mk_config(hub, root_dir, t_name)
    # Pass resources to test
    yield minion_config, root_dir, hub.heist.ROSTERS
    # TearDown
    if os.path.exists(minion_config):
        os.remove(minion_config)


@pytest.fixture
def remote() -> Dict[str, Any]:
    return {
        'tunnel': 'asyncssh',
        'host': '127.0.0.1',
        'id': 'localhost',
    }


class TestSaltMaster:
    @pytest.mark.asyncio
    async def test_run(self, mock_hub: testing.MockHub, remote: Dict[str, Dict[str, str]]):
        await heist.heist.salt_master.run(mock_hub, [remote])
        mock_hub.heist.salt_master.single.assert_called_with(remote)


    @pytest.mark.parametrize('roster',
                             [{'publish_port': '4505'},
                              {'master': '1.1.1.1',
                               'master_port': '4506'},
                              {}])
    def test_mk_config(self, roster, mk_config_data: Tuple[str, str]):
        '''
        test heist.salt_master.mk_config
        '''
        minion_config, root_dir, roster_data = mk_config_data
        with open(minion_config, 'r') as min_conf:
            conf = dict(line.strip().split(': ') for line in min_conf.readlines())

        for key, default in [('master', '127.0.0.1'),
                             ('master_port', '44506'),
                             ('publish_port', '44505')]:
            if roster.get(key):
                assert conf[key] == roster[key]
            else:
                assert conf[key] == default

        if roster.get('master') == '1.1.1.1':
            assert roster_data[list(roster_data.keys())[0]]['bootstrap']
        else:
            assert not roster_data[list(roster_data.keys())[0]].get('bootstrap')

        assert conf['root_dir'] == root_dir

    @pytest.mark.parametrize('roster',
                             [{'publish_port': '4505'}])
    @pytest.mark.parametrize('user',
                             ['', 'heist'])
    @pytest.mark.asyncio
    async def test_single(self,
                          mock_hub: testing.MockHub,
                          remote: Dict[str, Dict[str, str]],
                          mk_config_data: Tuple[str, str],
                          user):
        '''
        test heist.salt_master.single
        '''
        # Setup
        mock_hub.OPT = {'heist': {'artifacts_dir': 'art',
                                  'checkin_time': 1,
                                  'dynamic_upgrade': False}}
        mock_hub.heist.ROSTERS = {}
        mock_hub.heist.CONS = {}
        minion_config, _, _ = mk_config_data
        mock_hub.heist.salt_master.mk_config.return_value = minion_config
        mock_hub.heist.salt_master.detect_os.return_value = 'linux'
        mock_hub.artifact.salt.get_version.return_value = ('2019.2.1', {})
        patch_asyncio = mock.Mock(asyncio.sleep)
        patch_asyncio.side_effect = [InterruptedError]
        # We need to know exactly what the token hex will be, patch it's call
        t_name = secrets.token_hex()

        # Execute
        remote['user'] = user
        with mock.patch.object(secrets, 'token_hex', lambda: t_name):
            with mock.patch.object(heist.heist.salt_master, '_start_minion', patch_asyncio):
                # Raises an error here so we do not stay in while loop during test
                with pytest.raises(InterruptedError):
                    await heist.heist.salt_master.single(mock_hub, remote)

        # ensure the user is added to the run_dirs path
        ret_cons = mock_hub.heist.CONS
        run_dir = ret_cons[list(ret_cons.keys())[0]]['run_dir']
        if not remote['user']:
            assert 'root' in run_dir
        else:
            assert remote['user'] in run_dir

        # Verify
        mock_hub.tunnel.asyncssh.create.assert_called_once_with(t_name, remote)

        for tunnel in [
                (44505, 4505),
                (44506, 4506),
        ]:
            mock_hub.tunnel.asyncssh.tunnel.assert_any_call(t_name, *tunnel)

    @pytest.mark.asyncio
    async def test_detect_os(self,
                             mock_hub):
        '''
        test heist.heist.salt_master.detect_os
        when returncode is 0 and os is linux
        '''
        cmd_ret = asyncssh.process.SSHCompletedProcess(
            command={'uname -a'},
            exit_status=0,
            returncode=0,
            stdout='Linux test-name 5.0',
            stderr='')

        # Setup
        t_name = secrets.token_hex()
        mock_hub.tunnel.asyncssh.cmd.return_value = cmd_ret
        ret = await heist.heist.salt_master.detect_os(mock_hub, t_name, 'asyncssh')
        assert ret == 'linux'

    @pytest.mark.asyncio
    async def test_detect_os_bad_return(self,
                                        mock_hub: testing.MockHub):
        '''
        test heist.heist.salt_master.detect_os
        when returncode is not 0 and os is linux
        '''
        cmd_ret = asyncssh.process.SSHCompletedProcess(
            command={'uname -a'},
            exit_status=0,
            returncode=127,
            stdout='',
            stderr='zsh:1: command not found: name\n')

        # Setup
        t_name = secrets.token_hex()
        mock_hub.tunnel.asyncssh.cmd.return_value = cmd_ret
        ret = await heist.heist.salt_master.detect_os(mock_hub, t_name,
                                                      'asyncssh')
        assert not ret
