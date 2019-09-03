# Import third party libs
import asyncssh

__virtualname__ = 'asyncssh'


def __init__(hub):
    '''

    '''
    hub.tunnel.asyncssh.CONS = {}


async def create(hub, name, target):
    '''
    Create a connection to the remote system using a dict of values that map
    to this plugin. Name the connection for future use, the connection data
    will be stored on the hub under hub.tunnel.asyncssh.CONS
    '''
    # TODO: Add support for many more options in the target
    id_ = target.get('host', target.get('id'))
    port = target.get('port', 22)
    username = target.get('username')
    password = target.get('password')
    known_hosts = target.get('known_hosts')

    conn = await asyncssh.connect(
        id_,
        port=port,
        username=username,
        password=password,
        known_hosts=known_hosts,
        agent_path=None)
    sftp = await conn.start_sftp_client()
    hub.tunnel.asyncssh.CONS[name] = {
        'con': conn,
        'sftp': sftp}


async def send(hub, name, source, dest):
    '''
    Take the file located at source and send it to the remote system
    '''
    sftp = hub.tunnel.asyncssh.CONS[name]['sftp']
    await sftp.put(source, dest)


async def get(hub, name, source, dest):
    '''
    Take the file located on the remote system and copy it locally
    '''
    sftp = hub.tunnel.asyncssh.CONS[name]['sftp']
    await sftp.get(source, dest)


async def cmd(hub, name, cmd):
    '''
    Execute the given command on the machine associated witht he named connection
    '''
    con = hub.tunnel.asyncssh.CONS[name]['con']
    return await con.run(cmd)


async def tunnel(hub, name, remote, local):
    '''
    Given the local and remote addrs create a tcp tunnel through the connection
    '''
    con = hub.tunnel.asyncssh.CONS[name]['con']
    listener = await con.forward_remote_port('', remote, 'localhost', local)
