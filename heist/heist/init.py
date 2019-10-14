'''
The entry point for Heist, this is where config loading and the project
spine is set up
'''
# Import python libs
import asyncio
import ipaddress
import logging
import socket

log = logging.getLogger(__name__)


def __init__(hub):
    hub.heist.CONS = {}
    hub.heist.ROSTERS = {}
    hub.pop.conf.integrate('heist', cli='heist', roots=True)
    hub.heist.init.load_subs()


def load_subs(hub):
    '''
    Load up the needed subs
    '''
    hub.pop.sub.add(dyne_name='roster')
    hub.pop.sub.add(dyne_name='tunnel')
    hub.pop.sub.add(dyne_name='rend')


def start(hub):
    '''
    Start the async loop and get the process rolling
    '''
    hub.pop.loop.start(
        hub.heist.init.run(),
        sigint=hub.heist.init.clean,
        sigterm=hub.heist.init.clean)


async def run(hub):
    '''
    Configs, rosters and targets have been loaded, time to execute the
    remote system calls
    '''
    roster = hub.OPT['heist']['roster']
    remotes = await hub.roster.init.read(roster)
    manager = hub.OPT['heist']['manager']
    if not remotes:
        return False
    await getattr(hub, f'heist.{manager}.run')(remotes)


async def clean(hub, signal: int = None):
    '''
    Clean up the connections
    '''
    if signal:
        log.warning(f'Got signal {signal}! Cleaning up connections')
    coros = []
    # First clean up the remote systems
    for t_name, vals in hub.heist.ROSTERS.items():
        if not vals.get('bootstrap'):
            for t_name, vals in hub.heist.CONS.items():
                manager = vals['manager']
                coros.append(getattr(hub, f'heist.{manager}.clean')(t_name))
                await asyncio.gather(*coros)
    # Then shut down connections
    coros = []
    for t_name, vals in hub.heist.CONS.items():
        t_type = vals['t_type']
        coros.append(getattr(hub, f'tunnel.{t_type}.destroy')(t_name))
    await asyncio.gather(*coros)
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    for task in tasks:
        log.warning('Task remains that were not cleaned up, shutting down violently')
        task.cancel()


def ip_is_loopback(hub, addr):
    '''
    helper function to determine if an addr
    or hostname is a loopback address
    '''
    try:
        info = socket.getaddrinfo(addr, 0)
    except socket.gaierror:
        log.critical('Could not determine if addr is loopback')
        return False
    return ipaddress.ip_address(info[0][-1][0]).is_loopback
