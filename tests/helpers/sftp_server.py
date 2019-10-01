#!/usr/bin/python3
import argparse
import asyncio
import asyncssh
import inspect
import os
import pidfile
import signal
import tempfile
from typing import Dict, Tuple


async def start_sftp_server(authorized_client_keys: str,
                            sftp_port: int,
                            server_host_keys: str,
                            server_factory: object,
                            ssh_port: int = None,
                            sftp_factory: bool or object = True,
                            **kwargs):
    '''
    Start the sftp server
    Based off of examples at https://github.com/ronf/asyncssh/tree/master/examples
    :param authorized_client_keys:
    :param port:
    :param server_host_keys:
    :param sftp_factory:
    :param kwargs:
    :return:
    '''
    await asyncssh.listen(host='',
                          port=sftp_port,
                          authorized_client_keys=authorized_client_keys,
                          server_host_keys=[server_host_keys],
                          sftp_factory=sftp_factory,
                          **kwargs)

    # 'reuse_address' probably also has to be `True` in this case
    if kwargs.get('reuse_port') and not ssh_port:
        ssh_port = sftp_port

    # Don't create the ssh server unless there is a port available for it
    if ssh_port:
        await asyncssh.create_server(
            host='',
            server_factory=server_factory,
            port=ssh_port,
            authorized_client_keys=authorized_client_keys,
            server_host_keys=[server_host_keys],
        )


def parse_args() -> Tuple[argparse.Namespace, Dict[str, str or int]]:
    # Get arguments from async ssh server options
    possible_options = set(inspect.getfullargspec(asyncssh.SSHServerConnectionOptions.prepare).args)
    possible_options.update(set(inspect.getfullargspec(asyncssh.listen).args))
    # Remove options from `inspect` that don't belong
    possible_options -= {'self', 'args', 'kwargs', 'error_handler'}

    # Setup argument parser
    parser = argparse.ArgumentParser(description='Spawn an asyncssh server for testing Heist')
    parser.add_argument('--sftp-root', type=str)
    parser.add_argument('--sftp-port', type=int)
    parser.add_argument('--ssh-port', type=int)
    parser.add_argument('--pid-file', type=str, default=os.path.join(tempfile.gettempdir(), 'async_sftp_server.pid'))
    for option in possible_options:
        parser.add_argument(f'--{option.replace("_", "-")}', type=str)
    cmdline_args = parser.parse_args()

    # Get all the SSHServerConnectionOptions that were set
    async_ssh_server_options = {}
    for key, value in cmdline_args.__dict__.items():
        if key in ('sftp_root', 'pid_file', 'port'):
            continue
        if value:
            async_ssh_server_options[key] = value

    return cmdline_args, async_ssh_server_options


if __name__ == '__main__':
    args, opts = parse_args()

    class SimpleSFTPServer(asyncssh.SFTPServer):
        def __init__(self, conn):
            super().__init__(conn, chroot=args.sftp_root)

    class SimpleSSHServer(asyncssh.SSHServer):
        def server_requested(self, listen_host, listen_port):
            return listen_port == args.port


    loop = asyncio.get_event_loop()

    loop.run_until_complete(start_sftp_server(
        sftp_factory=SimpleSFTPServer if args.sftp_root else True, **opts,
        server_factory=SimpleSSHServer,
    ))

    # Cleanup properly when terminated
    signal.signal(signal.SIGINT, loop.stop)
    signal.signal(signal.SIGTERM, loop.stop)
    try:
        # Wait until the server is completely ready to go before creating a PID file for the loop
        with pidfile.PidFile(args.pid_file):
            loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
