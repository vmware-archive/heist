# -*- coding: utf-8 -*-
'''
Scan a netmask or ipaddr for open ssh ports
'''

# Import python libs
import asyncio
import ipaddress
import logging
import socket
from typing import Any, Dict

log = logging.getLogger(__name__)

async def read(hub) -> Dict[str, Any]:
    '''
    read data from connection to specified ports
    to detect SSH ports
    '''
    ret = {}
    target = hub.OPT['heist'].get('target')
    if not target:
        log.critical('Need to define a target for the scan roster')
        return ret
    ports = hub.OPT['heist']['ssh_scan_ports']
    if not isinstance(ports, list):
        # Comma-separate list of integers
        ports = list(map(int, str(ports).split(',')))
    try:
        addrs = [ipaddress.ip_address(target)]
    except ValueError:
        try:
            addrs = ipaddress.ip_network(hub.OPT['heist']['target']).hosts()
        except ValueError:
            pass

    for addr in addrs:
        for port in ports:
            log.debug(f'Scanning host: {addr} on port: {port}')
            try:
                if addr.version == 4:
                    fam = socket.AF_INET
                elif addr.version == 6:
                    fam = socket.AF_INET6

                addr = addr.exploded
                reader, writer = await asyncio.open_connection(
                    addr, port, family=fam)
                data = await reader.read(100)
                if 'ssh' not in data.decode().lower():
                    log.critical(f'Connection successful to {addr} '
                                 f'but SSH information not returned.'
                                 f'Port {port} might not be an SSH port.')
                ret[addr] = ({'host': addr, 'port': port})
                writer.close()
                await writer.wait_closed()
            except ConnectionRefusedError:
                log.critical(f'Not able to connect to host: {addr} on port: {port}')
                pass
    return ret
