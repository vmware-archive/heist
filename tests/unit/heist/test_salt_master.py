#!/usr/bin/python3
# Import Python libs
import asyncio
import os
import secrets
from typing import Any, Dict, Tuple

# Import Local libs
import heist.heist.salt_master
import heist.tunnel.asyncssh_tunnel

# Import 3rd-party libs
import asyncssh.process
import mock
import pop.utils.testing as testing
import pytest
import tarfile


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
    @pytest.mark.asyncio
    async def test_single(self,
                          mock_hub: testing.MockHub,
                          remote: Dict[str, Dict[str, str]],
                          mk_config_data: Tuple[str, str]):
        '''
        test heist.salt_master.single
        '''
        # Setup
        artifacts_dir = 'art'
        mock_hub.OPT = {'heist': {'artifacts_dir': artifacts_dir,
                                  'checkin_time': 1,
                                  'dynamic_upgrade': False}}
        mock_hub.heist.ROSTERS = {}
        minion_config, _, _ = mk_config_data
        mock_hub.heist.salt_master.mk_config.return_value = minion_config
        mock_hub.heist.salt_master.detect_os.return_value = 'linux'
        mock_hub.heist.salt_master.get_version_pypi.return_value = ('2019.2.1', {})
        patch_asyncio = mock.Mock(asyncio.sleep)
        patch_asyncio.side_effect = [InterruptedError]
        # We need to know exactly what the token hex will be, patch it's call
        t_name = secrets.token_hex()

        # Execute
        with mock.patch.object(secrets, 'token_hex', lambda: t_name):
            with mock.patch.object(heist.heist.salt_master, '_start_minion', patch_asyncio):
                # Raises an error here so we do not stay in while loop during test
                with pytest.raises(InterruptedError):
                    await heist.heist.salt_master.single(mock_hub, remote)

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
        ret = await heist.heist.salt_master.detect_os(mock_hub, t_name,
                                                      'asyncssh')
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

    @pytest.mark.asyncio
    async def test_get_version_pypi(self,
                                    hub):
        '''
        test heist.heist.salt_master.get_version_pypi
        with artifact_version set
        '''
        saltbin = '2019.2.1'
        hub.OPT = {'heist': {'artifact_version': '2019.2.1'}}
        ver, data = await heist.heist.salt_master.get_version_pypi(hub, 'linux')
        assert ver == saltbin
        assert saltbin in data['releases']

    @pytest.mark.asyncio
    async def test_get_artifact(self,
                                mock_hub: testing.MockHub,
                                tmp_path):
        '''
        test heist.salt_master.get_artifact
        when artifact does not already exist
        '''
        t_name = secrets.token_hex()
        ver = '2019.2.1'
        tar_f = f'salt-{ver}.tar.gz'
        data = {'releases': {ver: {0: {'url': f'https://pypi.org/project/saltbin/{tar_f}'}}}}

        # create test tar file
        files = ['PKG-INFO', f'salt-{ver}']
        tar_l = os.path.join(tmp_path, f'salt-{ver}.tar.gz')

        with tarfile.open(tar_l, 'w:gz') as tar:
            for fn_ in files:
                tmp = tmp_path / fn_
                tmp.write_text(f'test-info for {fn_}')
                tar.add(tmp, arcname=os.path.basename(tmp))

        [os.remove(os.path.join(tmp_path, x)) for x in files]

        mock_hub.heist.salt_master.fetch.return_value = tar_l
        mock_hub.heist.salt_master.latest.return_value = False
        ret = await heist.heist.salt_master.get_artifact(mock_hub, t_name,
                                                         'asyncssh', tmp_path,
                                                         ver, data)
        assert ret
