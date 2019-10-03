# -*- coding: utf-8 -*-
'''
This roster resolves hostname in a pdsh/clustershell style.

:depends: clustershell, https://github.com/cea-hpc/clustershell

When you want to use host globs for target matching, use ``--roster clustershell``. For example:

.. code-block:: bash

    heist --roster clustershell --target 'server_[1-10,21-30],test_server[5,7,9]'

'''


# Import python libs
import asyncio
import ipaddress
import logging
import socket
from typing import Any, Dict

# Import 3rd-party libs
from ClusterShell.NodeSet import NodeSet

log = logging.getLogger(__name__)

async def read(hub) -> Dict[str, Any]:
    '''
    Resolve hostname in a clustershell style
    and query the ports for SSH
    '''
    ret = {}
    tgt = hub.OPT['heist'].get('target')
    if not tgt:
        log.critical('Need to define a target for the scan roster')
        return ret
    ports = hub.OPT['heist']['ssh_scan_ports']
    if not isinstance(ports, list):
        # Comma-separate list of integers
        ports = list(map(int, str(ports).split(',')))

    hosts = list(NodeSet(tgt))
    host_addrs = dict([(h, socket.gethostbyname(h)) for h in hosts])

    for host, addr in host_addrs.items():
        addr = ipaddress.ip_address(addr)
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
