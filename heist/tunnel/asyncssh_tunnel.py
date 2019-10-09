# Import third party libs
import asyncssh
import inspect
import logging
from typing import Any, Dict

__virtualname__ = 'asyncssh'

log = logging.getLogger(__name__)


def __init__(hub):
    '''
    Set up the objects to hold connection instances
    '''
    hub.tunnel.asyncssh.CONS = {}


def _autodetect_asyncssh_opt(hub, option: str) -> Any:
    '''
    '''
    # TODO autodetect certain options
    return None


def _get_asyncssh_opt(hub, target: Dict[str, Any], option: str, default: Any = None) -> Any:
    '''
    Get an assyncssh option from the target/roster first, if that fails get it from the config, if not there
    then try to autodetect the option (I.E. Checking for keys in the .ssh folder of the target)
    :param option:
    :param target:
    :return:
    '''
    result = target.get(option)
    if not result:
        result = hub.OPT['heist'].get(option)
        if not result:
            result = hub.OPT['heist']['roster_defaults'].get(option)
    if not result:
        result = _autodetect_asyncssh_opt(hub, option)
    if not result:
        result = default
    return result


async def create(hub, name: str, target: Dict[str, Any]):
    '''
    Create a connection to the remote system using a dict of values that map
    to this plugin. Name the connection for future use, the connection data
    will be stored on the hub under hub.tunnel.asyncssh.CONS
    :param name:
    :param target:
    '''
    # The id MUST be in the target, everything else might be in the target, conf, or elsewhere
    id_ = target.get('host', target.get('id'))

    possible_options = set(inspect.getfullargspec(asyncssh.SSHClientConnectionOptions.prepare).args)
    # Remove options from `inspect` that don't belong
    possible_options -= {'self', 'args', 'kwargs'}
    # Add connection options that aren't specified in `SSHClientConnectionOptions.prepare`
    possible_options.update({'port', 'loop', 'tunnel', 'family', 'flags', 'local_addr', 'options'})
    # Check for each possible SSHClientConnectionOption in the target, config, then autodetect (if necessary)
    con_opts = {'known_hosts': None}
    for arg in possible_options:
        opt = _get_asyncssh_opt(hub, target, arg)
        if opt is not None:
            con_opts[arg] = opt

    try:
        conn = await asyncssh.connect(id_, **con_opts)
    except Exception:
        log.error(f'Failed to connect to {id_}')
        return False
    sftp = await conn.start_sftp_client()
    hub.tunnel.asyncssh.CONS[name] = {
        'con': conn,
        'sftp': sftp,
        'sudo': target.get('sudo', None)}
    return True


async def send(hub, name: str, source: str, dest: str):
    '''
    Take the file located at source and send it to the remote system
    '''
    sftp = hub.tunnel.asyncssh.CONS[name]['sftp']
    await sftp.put(source, dest)


async def get(hub, name: str, source: str, dest: str):
    '''
    Take the file located on the remote system and copy it locally
    '''
    sftp = hub.tunnel.asyncssh.CONS[name]['sftp']
    await sftp.get(source, dest)


async def cmd(hub, name: str, command: str):
    '''
    Execute the given command on the machine associated with the named connection
    '''
    sudo = hub.tunnel.asyncssh.CONS[name].get('sudo')
    if sudo:
        command = f'sudo {command}'
    con = hub.tunnel.asyncssh.CONS[name]['con']
    return await con.run(command)


async def tunnel(hub, name: str, remote: str, local: str):
    '''
    Given the local and remote addrs create a tcp tunnel through the connection
    '''
    con = hub.tunnel.asyncssh.CONS[name]['con']
    listener = await con.forward_remote_port('', remote, 'localhost', local)


async def destroy(hub, name: str):
    '''
    Destroy the named connection
    '''
    con = hub.tunnel.asyncssh.CONS[name]['con']
    con.close()
    await con.wait_closed()
