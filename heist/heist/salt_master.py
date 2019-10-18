# To manage a salt connection, we need to make sure that we have the right deployment files
# and that we can connect to a salt master

# Import python libs
import secrets
import asyncio
import logging
import os
import tempfile
from distutils.version import StrictVersion
from typing import Any, Dict, List

log = logging.getLogger(__name__)

CONFIG = '''master: {master}
master_port: {master_port}
publish_port: {publish_port}
root_dir: {root_dir}
'''

SYSTEMD_CONF = '''[Unit]
Description=The Salt Minion
Documentation=man:salt-minion(1) file:///usr/share/doc/salt/html/contents.html https://docs.saltstack.com/en/latest/contents.html
After=network.target salt-master.service

[Service]
KillMode=process
Type=notify
NotifyAccess=all
LimitNOFILE=8192
ExecStart={tgt} minion --config-dir {conf} --pid-file={pfile}

[Install]
WantedBy=multi-user.target
'''


def __init__(hub):
    '''
    Set up data structures for this module to use
    '''
    hub.heist.salt_master.FUTURES = {}


async def _get_start_cmd(hub, t_type, t_name, tgt, run_dir, pfile):
    '''
    determine which command to use when starting the salt-minion
    '''
    at_f = os.path.join(run_dir, 'at-minion-scheduler.sh')
    startup = {'systemctl': {'conf_tgt': os.path.join(os.sep, 'etc',
                                                      'systemd', 'system',
                                                      'salt-minion.service'),
                             'conf': 'systemd',
                             'start_cmd': 'systemctl start salt-minion'},
               'at': {'conf_tgt': at_f,
                      'conf': 'at',
                      'start_cmd': f'at -f {at_f} now + 1 minute'}}
    if hub.heist.ROSTERS[t_name].get('bootstrap'):
        for cmd in startup:
            ret = await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'which {cmd}')
            if ret.returncode == 0:
                log.debug(f'Using {cmd} to startup the minion service')
                config = hub.heist.salt_master.mk_startup_conf(cmd, tgt, run_dir, pfile)
                conf_tgt = startup[cmd]['conf_tgt']
                await getattr(hub, f'tunnel.{t_type}.send')(t_name, config, conf_tgt)
                return startup[cmd]['start_cmd']
    return f' {tgt} minion --config-dir {os.path.join(run_dir, "conf")} --pid-file={pfile}'


async def _start_minion(hub, t_type, t_name, tgt, run_dir):
    '''
    Start a minion on the remote system and store the future
    '''
    pfile = os.path.join(run_dir, 'pfile')
    cmd = await _get_start_cmd(hub, t_type, t_name, tgt, run_dir, pfile)

    future = asyncio.ensure_future(getattr(hub, f'tunnel.{t_type}.cmd')(
        t_name, cmd))
    hub.heist.salt_master.FUTURES[t_name] = future
    # Call an await to give the future a chance to run
    await asyncio.sleep(0)


async def detect_os(hub, t_name, t_type):
    '''
    Detect the os on the target system
    '''
    ret = await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, 'uname -a')
    if ret.returncode == 0:
        if ret.stdout.lower().startswith('linux'):
            return 'linux'
        elif ret.stdout.lower().startswith('darwin'):
            return 'darwin'
    log.critical('Could not determine the OS')
    return False


async def run(hub, remotes: List[Dict[str, Any]]):
    '''
    This plugin creates the salt specific tunnel, and then starts the remote
    minion and attatches it to a currently running master
    '''
    coros = []
    for remote in remotes:
        coros.append(hub.heist.salt_master.single(remote))
    await asyncio.gather(*coros)


def mk_startup_conf(hub, cmd, tgt, run_dir, pfile):
    '''
    Manage the file that will be used to startup the salt-minion service
    '''
    _, path = tempfile.mkstemp()

    if cmd == 'systemctl':
        with open(path, 'w+') as wfp:
            wfp.write(SYSTEMD_CONF.format(tgt=tgt,
                                          conf=os.path.join(run_dir, "conf"),
                                          pfile=pfile))
    elif cmd == 'at':
        with open(path, 'w+') as wfp:
            wfp.write(f'{tgt} minion --config-dir {os.path.join(run_dir, "conf")} --pid-file={pfile}')
        return path

    return path


def mk_config(hub, root_dir: str, t_name):
    '''
    Create a minion config to use with this execution and return the file path
    for said config
    '''
    _, path = tempfile.mkstemp()
    roster = hub.heist.ROSTERS[t_name]
    master = roster.get('master', '127.0.0.1')

    if not roster.get('bootstrap') and not hub.heist.init.ip_is_loopback(master):
        roster['bootstrap'] = True

    with open(path, 'w+') as wfp:
        wfp.write(CONFIG.format(master=master,
                                master_port=roster.get('master_port', 44506),
                                publish_port=roster.get('publish_port', 44505),
                                root_dir=root_dir))
    return path


def latest(hub, name: str, a_dir: str, version=False):
    '''
    Given the artifacts directory return the latest desired artifact

    :param str version: Return the artifact for a specific version.
    '''
    names = []
    paths = {}
    for fn in os.listdir(a_dir):
        if fn.startswith(name):
            ver = fn[len(name)+1:]
            names.append(ver)
            paths[ver] = fn
    names = sorted(names, key=StrictVersion)
    if version:
        if version in names:
            return os.path.join(a_dir, paths[version])
        return False
    return os.path.join(a_dir, paths[names[-1]])


async def deploy(hub, t_name, t_type, bin_, run_dir):
    '''
    Deploy the salt minion to the remote system
    '''
    tgt = os.path.join(run_dir, os.path.basename(bin_))
    root_dir = os.path.join(run_dir, 'root')
    config = hub.heist.salt_master.mk_config(root_dir, t_name)
    conf_tgt = os.path.join(run_dir, 'conf', 'minion')

    # run salt deployment
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'mkdir -p {os.path.join(run_dir, "conf")}')
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'mkdir -p {os.path.join(run_dir, "root")}')
    try:
        await getattr(hub, f'tunnel.{t_type}.send')(t_name, config, conf_tgt)
    except Exception:
        host = hub.heist.CONS[t_name]
        log.error(f'Failed to send {config} to {t_name} at {conf_tgt}')
        os.remove(config)
    await getattr(hub, f'tunnel.{t_type}.send')(t_name, bin_, tgt)
    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'chmod +x {tgt}')
    os.remove(config)
    return tgt


async def update(hub, t_name, t_type, bin_, tgt, run_dir):
    '''
    Re-deploy the latest minion to the remote system
    '''
    # TODO: When updating clean out the old deployment
    await hub.heist.salt_master.clean(t_name)
    tgt = await hub.heist.salt_master.deploy(t_name, t_type, bin_, run_dir)
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
    hub.heist.ROSTERS[t_name] = remote
    user = hub.heist.ROSTERS[t_name].get('user')
    if not user:
        user = 'root'
    run_dir = os.path.join(os.sep, 'var', 'tmp', f'heist_{user}',
                           f'{secrets.token_hex()[:4]}')
    t_type = remote.get('tunnel', 'asyncssh')
    a_type = remote.get('artifact', 'salt')
    created = await getattr(hub, f'tunnel.{t_type}.create')(t_name, remote)
    if not created:
        log.error(f'Connection to host {remote["host"]} failed')
        return
    t_os = await hub.heist.salt_master.detect_os(t_name, t_type)
    art_dir = os.path.join(hub.OPT['heist']['artifacts_dir'], t_os)
    ver = await getattr(hub, f'artifact.{a_type}.get_version')(t_os)
    if ver:
        await getattr(hub, f'artifact.{a_type}.get_artifact')(t_name, t_type,
                                                              art_dir, t_os, ver=ver)
    # Deploy
    bin_ = hub.heist.salt_master.latest('salt', art_dir, version=ver)
    tgt = await hub.heist.salt_master.deploy(t_name, t_type, bin_, run_dir)
    hub.heist.CONS[t_name] = {
        'run_dir': run_dir,
        't_type': t_type,
        'manager': 'salt_master',
        'bin': bin_,
        'tgt': tgt}
    # Create tunnel back to master
    if not hub.heist.ROSTERS[t_name].get('bootstrap'):
        await getattr(hub, f'tunnel.{t_type}.tunnel')(t_name, 44505, 4505)
        await getattr(hub, f'tunnel.{t_type}.tunnel')(t_name, 44506, 4506)
    # Start minion
    await _start_minion(hub, t_type, t_name, tgt, run_dir)
    while True:
        await asyncio.sleep(hub.OPT['heist']['checkin_time'])
        if hub.OPT['heist']['dynamic_upgrade']:
            latest = hub.heist.salt_master.latest('salt', art_dir)
            if latest != bin_:
                bin_ = latest
                await hub.heist.salt_master.update(t_name, t_type, latest, tgt, run_dir)
