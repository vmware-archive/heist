#!/usr/bin/python3

# Import local libs
import heist.roster.scan

# Import 3rd-party libs
import pytest


class TestScanRoster:
    '''
    unit tests for heist.roster.scan
    '''
    @pytest.mark.asyncio
    async def test_read(self, mock_hub):
        '''
        test scan roster against port 22 localhost
        '''
        # Setup
        target = '127.0.0.1'
        mock_hub.OPT = {'heist': {'target': target,
                                  'ssh_scan_ports': [22]}}

        # Execute
        ret = await heist.roster.scan.read(mock_hub)

        assert ret[target]['host'] == target
        assert ret[target]['port'] == 22

    @pytest.mark.asyncio
    async def test_scan_non_ssh_port(self, mock_hub):
        '''
        test scan roster against port not running ssh
        '''
        # Setup
        target = '127.0.0.1'
        mock_hub.OPT = {'heist': {'target': target,
                                  'ssh_scan_ports': [22222]}}

        # Execute
        ret = await heist.roster.scan.read(mock_hub)

        assert ret == {}
