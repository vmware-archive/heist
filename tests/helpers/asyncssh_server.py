#!/usr/bin/env python3.6
import asyncio
import asyncssh
import crypt
import os
from M2Crypto import RSA


class TestingAsyncSSHServer(asyncssh.SSHServer):
    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if not hasattr(self, '__loop'):
            self.__loop = asyncio.get_event_loop()
        return self.__loop

    def __init__(self,
                 username: str,
                 password: str = '',
                 port: int = 4095,
                 private_key: str = None,
                 public_key: str = None,
                 password_auth_supported: bool = True
                 ):
        asyncssh.SSHServer.__init__(self)
        self.username = username
        self.password = password if password else '*'
        self.port = int(port)
        self.__password_auth_supported = password_auth_supported

        # Validate keys before storing them
        if private_key:
            RSA.load_key(private_key).check_key()
        self.private_key = private_key
        if public_key:
            RSA.load_pub_key(public_key).check_key()
        self.public_key = public_key

    def begin_auth(self, username: str) -> bool:
        # If the user's password is the empty string, no auth is required
        return self.password != ''

    def password_auth_supported(self) -> bool:
        return self.__password_auth_supported

    def validate_password(self, username: str, password: str) -> bool:
        return crypt.crypt(password, self.password) == self.password

    def server_requested(self, listen_host, listen_port) -> bool:
        return listen_port == self.port

    async def __aenter__(self):
        print(f'server opened on port {self.port}')
        self.server = await asyncssh.create_server(TestingAsyncSSHServer, '', self.port,
                                                   server_host_keys=[self.private_key],
                                                   authorized_client_keys=[self.public_key])
        self.loop.run_until_complete(self.server)

    def __aexit__(self):
        print(f'server close on port {self.port}')
        self.server.close()

    def __int__(self):
        return self.port
