#!/usr/bin/python3
import argparse
import asyncio
import asyncssh
import inspect
import os
import pidfile
import tempfile
from typing import Dict, Tuple


async def start_async_sftp_server(authorized_client_keys: str,
                                  port: int,
                                  server_host_keys: str,
                                  sftp_factory: bool or asyncssh.SFTPServer = True,
                                  **kwargs):
    await asyncssh.listen('',
                          port=port,
                          authorized_client_keys=authorized_client_keys,
                          server_host_keys=[server_host_keys],
                          sftp_factory=sftp_factory,
                          **kwargs,)


def parse_args() -> Tuple[argparse.Namespace, Dict[str, str or int]]:
    # Get arguments from async ssh server options
    possible_options = set(inspect.getfullargspec(asyncssh.SSHServerConnectionOptions.prepare).args)
    possible_options.update(set(inspect.getfullargspec(asyncssh.listen).args))
    # Remove options from `inspect` that don't belong
    possible_options -= {'self', 'args', 'kwargs', 'error_handler'}

    # Setup argument parser
    parser = argparse.ArgumentParser(description='Spawn an asyncssh server for testing Heis')
    parser.add_argument('--sftp-root', type=str)
    parser.add_argument('--pid-file', type=str, default=os.path.join(tempfile.gettempdir(), 'async_sftp_server.pid'))
    for option in possible_options:
        parser.add_argument(f'--{option.replace("_", "-")}', type=str)
    cmdline_args = parser.parse_args()

    # Get all the SSHServerConnectionOptions that were set
    async_ssh_server_options = {}
    for key, value in cmdline_args.__dict__.items():
        if key in ('sftp_root', 'pid_file'):
            continue
        if value:
            if value.isnumeric():
                async_ssh_server_options[key] = int(value)
            else:
                async_ssh_server_options[key] = value

    return cmdline_args, async_ssh_server_options


if __name__ == '__main__':
    args, opts = parse_args()

    class SimpleSFTPServer(asyncssh.SFTPServer):
        def __init__(self, conn):
            super().__init__(conn, chroot=args.sftp_root)


    loop = asyncio.get_event_loop()

    with pidfile.PidFile(args.pid_file):
        loop.run_until_complete(start_async_sftp_server(
            sftp_factory=SimpleSFTPServer if args.sftp_root else True, **opts
        ))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
