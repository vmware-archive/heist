#!/usr/bin/python3
import asyncio
import asyncssh
from typing import Set


async def start_async_sftp_server(authorized_client_keys: str,
                                  port: int,
                                  server_host_keys: str,
                                  sftp_factory: bool or asyncssh.SFTPServer = True,
                                  **kwargs):
    await asyncssh.listen('',
                          port=port,
                          authorized_client_keys=[authorized_client_keys],
                          server_host_keys=[server_host_keys],
                          sftp_factory=sftp_factory,
                          **kwargs)


def asyncssh_options() -> Set[str]:
    possible_options = set(inspect.getfullargspec(asyncssh.SSHServerConnectionOptions.prepare).args)
    possible_options.update(set(inspect.getfullargspec(asyncssh.listen).args))
    # Remove options from `inspect` that don't belong
    possible_options -= {'self', 'args', 'kwargs'}
    # Add connection options that aren't specified in `SSHClientConnectionOptions.prepare`
    return possible_options


if __name__ == '__main__':
    import argparse
    import inspect
    import sys

    parser = argparse.ArgumentParser(description='Spawn an asyncssh server for testing Heis')
    parser.add_argument('--sftp_root', type=str)
    for option in asyncssh_options():
        parser.add_argument(f'--{option}', type=str)
    args = parser.parse_args()
    opts = {}
    for key, value in args.__dict__.items():
        if key in ('sftp_root',):
            continue
        if value:
            opts[key] = value


    class SimpleSFTPServer(asyncssh.SFTPServer):
        def __init__(self, conn):
            super().__init__(conn, chroot=args.sftp_root)

    print(args)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_async_sftp_server(
            sftp_factory=SimpleSFTPServer if args.sftp_root else True,
            **opts
        ))
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Error starting server: ' + str(exc))

    try:
        loop.run_forever()
        # Create a pid_file and except on it not existing anymore
    except KeyboardInterrupt:
        print('stopping gracefully')
        loop.stop()
