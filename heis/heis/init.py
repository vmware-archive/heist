'''
The entry point for Heis, this is where config loading and the project
spine is set up
'''
# Import python libs
import asyncio
import logging

log = logging.getLogger(__name__)


def __init__(hub):
    hub.heis.CONS = {}
    hub.pop.conf.integrate('heis', cli='heis', roots=True)
    hub.heis.init.load_subs()
    hub.heis.init.start()


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
        hub.heis.init.run(),
        sigint=hub.heis.init.clean,
        sigterm=hub.heis.init.clean)


async def run(hub):
    '''
    Configs, rosters and targets have been loaded, time to execute the
    remote system calls
    '''
    roster = hub.OPT['heis']['roster']
    remotes = await hub.roster.init.read(roster)
    manager = hub.OPT['heis']['manager']
    await getattr(hub, f'heis.{manager}.run')(remotes)


async def clean(hub, signal):
    '''
    Clean up the connections
    '''
    log.warning(f'Got signal {signal}! Cleaning up connections')
    coros = []
    # First clean up the remote systems
    for t_name, vals in hub.heis.CONS.items():
        manager = vals['manager']
        coros.append(getattr(hub, f'heis.{manager}.clean')(t_name))
    await asyncio.gather(*coros)
    # Then shut down conenctions
    coros = []
    for t_name, vals in hub.heis.CONS.items():
        t_type = vals['t_type']
        coros.append(getattr(hub, f'tunnel.{t_type}.destroy')(t_name))
    await asyncio.gather(*coros)
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    for task in tasks:
        log.warning('Task remains that were not cleaned up, shuting down violently')
        task.cancel()