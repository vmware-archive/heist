#!/usr/bin/python3
# Import local libs
import heist.tunnel.asyncssh_tunnel as asyncssh_tunnel
import tests.helpers.mock_hub as helpers

# Import 3rd Party libs
import mock


class TestAsyncSSH:
    def test__get_asyncssh_opt_target(self):
        '''
        Test getting option from the target
        '''
        mock_hub = helpers.mock_hub()
        mock_hub.OPT = {'heist': {'username', 'opt'}}
        target = {'username': 'target'}
        result = asyncssh_tunnel._get_asyncssh_opt(mock_hub, target=target, option='username', default='default')
        assert result == 'target'

    def test__get_asyncssh_opt_config(self):
        '''
        Test getting option from the config if target isn't available
        '''
        mock_hub = helpers.mock_hub()
        mock_hub.OPT = {'heist': {'username': 'opt'}}
        target = {}
        result = asyncssh_tunnel._get_asyncssh_opt(mock_hub, target=target, option='username', default='default')
        assert result == 'opt'

    @mock.patch('heist.tunnel.asyncssh_tunnel._autodetect_asyncssh_opt', return_value='autodetect')
    def test__get_asyncssh_opt_autodetect(self, mocked_autodetect):
        '''
        Test getting option from autodetect of target and config aren't available
        '''
        mock_hub = helpers.mock_hub()
        mock_hub.OPT = {'heist': {}}
        target = {}
        result = asyncssh_tunnel._get_asyncssh_opt(mock_hub, target=target, option='username', default='default')
        assert result == 'autodetect'

    def test_autodetect_asyncssh_opt(self):
        ...
