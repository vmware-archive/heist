=======
Rosters
=======

Rosters is the system that is used to define the target systems to create
connections to with `heist`. The default roster system is called `rend` and
uses the `pop` `rend` system to render the datasets.

.. note::

    By using `rend` you can make roster files using yaml, json, toml etc. and
    template the files making it easy to allow for logic to make larger lists
    easier. Don't worry! You don't need to know anything about `rend` to use
    rosters, just know that there is a robust system under the hood to make
    your life easier!

Defining a basic roster is easy:

.. code-block:: yaml

    192.168.0.24:
      username: harry
      password: foobar

In this roster we are using the default yaml `rend` system. it is also very simple
because it is just a password login. `heist` supports logging into systems
using virtually any login mechanism available to ssh. The options are mapped
directly to asyncssh and can be found here:
https://asyncssh.readthedocs.io/en/latest/api.html#asyncssh.SSHClientConnectionOptions

Bootstrapping Minions to Existing Masters
=========================================

Heist can be used to bootstrap minions to connect to existing masters and not
be connected back through the ssh tunnel. This allows for minions to be deployed
and managed to many system in a very streamlined way.

The only change that needs to take place is that the master that the target system
needs to connect to is defined inside the roster:

.. code-block:: yaml

    hostname:
      username: frank
      password: horsebatterystaple
      master: salt

This now tells the minion that is deployed to connect to the specific master located
at the host named `salt`.
