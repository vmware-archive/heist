# To manage a salt connection, we need to make sure that we have the right deployment files
# and that we can connect to a salt master

# Import python libs
import secrets
import asyncio
import os
import tempfile
from typing import Any, Dict, List

CONFIG = '''master: 127.0.0.1
master_port: {master_port}
publish_port: {publish_port}
root_dir: {root_dir}
'''


async def run(hub, remotes: List[Dict[str, Any]]):
    '''
    This plugin creates the salt specific tunnel, and then starts the remote
    minion and attatches it to a currently running master
    '''
    coros = []
    for remote in remotes:
        coros.append(hub.heis.salt_master.single(remote))
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


async def single(hub, remote: Dict[str, Any]):
    '''
    Execute a single async connection
    '''
    minion = os.path.join(hub.OPT['heis']['artifacts_dir'], 'salt-minion.pex')
    pytar = os.path.join(hub.OPT['heis']['artifacts_dir'], 'py374.txz')
    run_dir = f'/var/tmp/heis/{secrets.token_hex()[:4]}'
    root_dir = os.path.join(run_dir, 'root')
    config = hub.heis.salt_master.mk_config(root_dir)
    # create tunnel
    t_name = secrets.token_hex()
    t_type = remote.get('tunnel', 'asyncssh')
    await getattr(hub, f'tunnel.{t_type}.create')(t_name, remote)

    # run salt deployment
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'mkdir -p {os.path.join(run_dir, "conf")}')
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'mkdir -p {os.path.join(run_dir, "root")}')
    await getattr(hub, f'tunnel.{t_type}.send')(t_name, config, os.path.join(run_dir, 'conf', 'minion'))
    await getattr(hub, f'tunnel.{t_type}.send')(t_name, minion, os.path.join(run_dir, 'salt-minion.pex'))
    await getattr(hub, f'tunnel.{t_type}.send')(t_name, pytar, os.path.join(run_dir, 'py3.txz'))
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'tar -xvf {os.path.join(run_dir, "py3.txz")} -C {run_dir}')
    os.remove(config)
    # validate deployment
    # Create tunnel back to master
    await getattr(hub, f'tunnel.{t_type}.tunnel')(t_name, 44505, 4505)
    await getattr(hub, f'tunnel.{t_type}.tunnel')(t_name, 44506, 4506)
    # Start minion
    await getattr(hub, f'tunnel.{t_type}.cmd')(
        t_name, f'{os.path.join(run_dir, "py3", "bin", "python3")} {os.path.join(run_dir, "salt-minion.pex")} --config-dir {os.path.join(run_dir, "conf")}')
