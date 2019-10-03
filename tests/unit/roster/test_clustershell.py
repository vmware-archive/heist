#!/usr/bin/python3
'''
    unit tests for the clustershell roster
'''

# Import python libs
import socket

# Import local libs
import heist.roster.clustershell

# Import 3rd-party libs
import pytest


class TestClustershellRoster:
    '''
    unit tests for heist.roster.clustershell
    '''
    @pytest.mark.asyncio
    async def test_read(self, mock_hub):
        '''
        test clustershell roster against port 22 localhost
        '''
        # Setup
        target = socket.gethostname()
        addr = socket.gethostbyname(target)
        mock_hub.OPT = {'heist': {'target': target,
                                  'ssh_scan_ports': [22]}}

        # Execute
        ret = await heist.roster.clustershell.read(mock_hub)

        assert ret[addr]['host'] == addr
        assert ret[addr]['port'] == 22

    @pytest.mark.asyncio
    async def test_clustershell_non_ssh_port(self, mock_hub):
        '''
        test clustershell roster against port not running ssh
        '''
        # Setup
        target = socket.gethostname()

        target = '127.0.0.1'
        mock_hub.OPT = {'heist': {'target': target,
                                  'ssh_scan_ports': [22222]}}

        # Execute
        ret = await heist.roster.clustershell.read(mock_hub)

        assert ret == {}
