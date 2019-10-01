# To manage a salt connection, we need to make sure that we have the right deployment files
# and that we can connect to a salt master

# Import python libs
import secrets
import asyncio
import os
import tempfile
from distutils.version import StrictVersion
from typing import Any, Dict, List

CONFIG = '''master: 127.0.0.1
master_port: {master_port}
publish_port: {publish_port}
root_dir: {root_dir}
'''


def __init__(hub):
    '''
    Set up data structures for this module to use
    '''
    hub.heist.salt_master.FUTURES = {}


async def _start_minion(hub, t_type, t_name, tgt, run_dir):
    '''
    Start a minion on the remote system and store the future
    '''
    pfile = os.path.join(run_dir, 'pfile')
    future = asyncio.ensure_future(getattr(hub, f'tunnel.{t_type}.cmd')(
        t_name,
        f' {tgt} minion --config-dir {os.path.join(run_dir, "conf")} --pid-file={pfile}'))
    hub.heist.salt_master.FUTURES[t_name] = future
    # Call an await to give the future a chance to run
    await asyncio.sleep(0)


async def run(hub, remotes: List[Dict[str, Any]]):
    '''
    This plugin creates the salt specific tunnel, and then starts the remote
    minion and attatches it to a currently running master
    '''
    coros = []
    for remote in remotes:
        coros.append(hub.heist.salt_master.single(remote))
    await asyncio.gather(*coros)


def mk_config(hub, root_dir: str):
    '''
    Create a minion config to use with this execution and return the file path
    for said config
    '''
    _, path = tempfile.mkstemp()
    with open(path, 'w+') as wfp:
        wfp.write(CONFIG.format(master_port=44506, publish_port=44505, root_dir=root_dir))
    return path


def latest(hub, name: str, a_dir: str):
    '''
    Given the artifacts directory return the latest desired artifact
    '''
    names = []
    paths = {}
    for fn in os.listdir(a_dir):
        if fn.startswith(name):
            ver = fn[len(name)+1:]
            names.append(ver)
            paths[ver] = fn
    names = sorted(names, key=StrictVersion)
    return os.path.join(a_dir, paths[names[-1]])


async def deploy(hub, t_name, t_type, bin, run_dir):
    '''
    Deploy the salt minion to the remote system
    '''
    tgt = os.path.join(run_dir, os.path.basename(bin))
    root_dir = os.path.join(run_dir, 'root')
    config = hub.heist.salt_master.mk_config(root_dir)

    # run salt deployment
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'mkdir -p {os.path.join(run_dir, "conf")}')
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'mkdir -p {os.path.join(run_dir, "root")}')
    await getattr(hub, f'tunnel.{t_type}.send')(t_name, config, os.path.join(run_dir, 'conf', 'minion'))
    await getattr(hub, f'tunnel.{t_type}.send')(t_name, bin, tgt)
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'chmod +x {tgt}')
    os.remove(config)
    return tgt


async def update(hub, t_name, t_type, bin, tgt, run_dir):
    '''
    Re-deploy the latest minion to the remote system
    '''
    # TODO: When updating clean out the old deployment
    await hub.heist.salt_master.clean(t_name)
    tgt = await hub.heist.salt_master.deploy(t_name, t_type, bin, run_dir)
    hub.heist.CONS[t_name]['tgt'] = tgt
    await _start_minion(hub, t_type, t_name, tgt, run_dir)


async def clean(hub, t_name):
    run_dir = hub.heist.CONS[t_name]['run_dir']
    t_type = hub.heist.CONS[t_name]['t_type']
    pfile = os.path.join(run_dir, 'pfile')
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'kill `cat {pfile}`')
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'rm -rf {run_dir}')
    await hub.heist.salt_master.FUTURES[t_name]


async def single(hub, remote: Dict[str, Any]):
    '''
    Execute a single async connection
    '''
    # create tunnel
    t_name = secrets.token_hex()
    run_dir = f'/var/tmp/heist/{secrets.token_hex()[:4]}'
    t_type = remote.get('tunnel', 'asyncssh')
    await getattr(hub, f'tunnel.{t_type}.create')(t_name, remote)
    # Deploy
    bin = hub.heist.salt_master.latest('salt', hub.OPT['heist']['artifacts_dir'])
    tgt = await hub.heist.salt_master.deploy(t_name, t_type, bin, run_dir)
    hub.heist.CONS[t_name] = {
        'run_dir': run_dir,
        't_type': t_type,
        'manager': 'salt_master',
        'bin': bin,
        'tgt': tgt}
    # Create tunnel back to master
    await getattr(hub, f'tunnel.{t_type}.tunnel')(t_name, 44505, 4505)
    await getattr(hub, f'tunnel.{t_type}.tunnel')(t_name, 44506, 4506)
    # Start minion
    await _start_minion(hub, t_type, t_name, tgt, run_dir)
    while True:
        await asyncio.sleep(hub.OPT['heist']['checkin_time'])
        if hub.OPT['heist']['dynamic_upgrade']:
            latest = hub.heist.salt_master.latest('salt', hub.OPT['heist']['artifacts_dir'])
            if latest != bin:
                bin = latest
                await hub.heist.salt_master.update(t_name, t_type, latest, tgt, run_dir)
