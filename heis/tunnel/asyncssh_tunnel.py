# Import third party libs
import asyncssh
import inspect
from typing import Any, Dict

__virtualname__ = 'asyncssh'


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
        result = hub.OPT['heis'].get(option)
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

    ssh_client_connection_options = {}
    # Check for each possible SSHClientConnectionOption in the target, config, then autodetect (if necessary)
    # Skip the first argument which will always be 'self'
    for arg in inspect.getfullargspec(asyncssh.SSHClientConnectionOptions.prepare).args[1:]:
        value = _get_asyncssh_opt(hub, target, arg)
        if value is not None:
            ssh_client_connection_options[arg] = value

    conn = await asyncssh.connect(id_, **ssh_client_connection_options)
    sftp = await conn.start_sftp_client()
    hub.tunnel.asyncssh.CONS[name] = {
        'con': conn,
        'sftp': sftp}


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


async def cmd(hub, name: str, cmd: str):
    '''
    Execute the given command on the machine associated witht he named connection
    '''
    con = hub.tunnel.asyncssh.CONS[name]['con']
    return await con.run(cmd)


async def tunnel(hub, name: str, remote: str, local: str):
    '''
    Given the local and remote addrs create a tcp tunnel through the connection
    '''
    con = hub.tunnel.asyncssh.CONS[name]['con']
    listener = await con.forward_remote_port('', remote, 'localhost', local)
