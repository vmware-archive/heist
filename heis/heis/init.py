'''
The entry point for Heis, this is where config loading and the project
spine is set up
'''
# Import python libs
import asyncio
# Plugin layout
# Rosters: Generate the target data needed for ssh connections
# Tunnel: The tunneling plugin interface that can make tunnels back to a master


def __init__(hub):
    hub.pop.conf.integrate('heis', cli='heis', roots=True)
    hub.heis.init.load_subs()
    # Read in the rosters
    # Create the tunnel to a remote system
    # Send the minion down and start  it up via the tunnel
    hub.heis.init.start()


def load_subs(hub):
    '''
    Load up the needed subs
    '''
    hub.pop.sub.add(dyne_name='roster')
    hub.pop.sub.add(dyne_name='tunnel')


def start(hub):
    '''
    Start the async loop and get the process rolling
    '''
    hub.pop.loop.start(hub.heis.init.run())


async def run(hub):
    '''
    Configs, rosters and targets have been loaded, time to execute the
    remote system calls
    '''
    roster = hub.OPT['heis']['roster']
    remotes = await hub.roster.init.read(roster)
    manager = hub.OPT['heis']['manager']
    await getattr(hub, f'heis.{manager}.run')(remotes)
