#!/usr/bin/python3
# Import Python libs
import os
import secrets
from typing import Any, Dict, Tuple

# Import Local libs
import heist.heist.salt_master
import tests.helpers.mock_hub as helpers

# Import 3rd-party libs
import mock
import pop.utils.testing as testing
import pop.hub
import pytest


@pytest.fixture
def mock_hub() -> testing.MockHub:
    # A fixture is required for asynchronous tests to access a mock_hub
    return helpers.mock_hub(subs=['heist.heist', 'roster', 'tunnel'])


@pytest.fixture
def mk_config_data():
    # Setup
    hub = pop.hub.Hub()
    root_dir = 'arbitrary_string'
    minion_config = heist.heist.salt_master.mk_config(hub, root_dir)
    # Pass resources to test
    yield minion_config, root_dir
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

    def test_mk_config(self, mk_config_data: Tuple[str, str]):
        minion_config, root_dir = mk_config_data
        with open(minion_config, 'r') as min_conf:
            conf = dict(line.strip().split(': ') for line in min_conf.readlines())

        assert conf['master'] == '127.0.0.1'
        assert conf['master_port'] == '44506'
        assert conf['publish_port'] == '44505'
        assert conf['root_dir'] == root_dir

    @pytest.mark.asyncio
    async def test_single(self,
                          mock_hub: testing.MockHub,
                          remote: Dict[str, Dict[str, str]],
                          mk_config_data: Tuple[str, str]):
        # Setup
        artifacts_dir = 'art'
        mock_hub.OPT = {'heist': {'artifacts_dir': artifacts_dir,
                                 'checkin_time': 1,
                                 'dynamic_upgrade': False}}
        minion = os.path.join(artifacts_dir, 'salt-minion.pex')
        pytar = os.path.join(artifacts_dir, 'py374.txz')
        minion_config, _ = mk_config_data
        mock_hub.heist.salt_master.mk_config.return_value = minion_config
        # We need to know exactly what the token hex will be, patch it's call
        t_name = secrets.token_hex()
        run_dir = f'/var/tmp/heist/{t_name[:4]}'

        # Execute
        with mock.patch.object(secrets, 'token_hex', lambda: t_name):
            await heist.heist.salt_master.single(mock_hub, remote)

        # Verify
        mock_hub.tunnel.asyncssh.create.assert_called_once_with(t_name, remote)
        for cmd in [
            f'mkdir -p {os.path.join(run_dir, "conf")}',
            f'mkdir -p {os.path.join(run_dir, "root")}',
            f'tar -xvf {os.path.join(run_dir, "py3.txz")} -C {run_dir}',
            f'{os.path.join(run_dir, "py3", "bin", "python3")} {os.path.join(run_dir, "salt-minion.pex")} --config-dir {os.path.join(run_dir, "conf")}',
        ]:
            mock_hub.tunnel.asyncssh.cmd.assert_any_call(t_name, cmd)

        for send in [
            (minion_config, os.path.join(run_dir, 'conf', 'minion')),
            (minion, os.path.join(run_dir, 'salt-minion.pex')),
            (pytar, os.path.join(run_dir, 'py3.txz')),
        ]:
            mock_hub.tunnel.asyncssh.send.assert_any_call(t_name, *send)

        for tunnel in [
            (44505, 4505),
            (44506, 4506),
        ]:
            mock_hub.tunnel.asyncssh.tunnel.assert_any_call(t_name, *tunnel)
