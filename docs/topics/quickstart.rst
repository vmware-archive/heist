==========================
Getting Started With Heist
==========================

Heist is a modular system used to create network tunnels and deploy software
over said tunnels. Heist was primarily created to make the deployment of
Salt easier, but the system is completely modular and can be extended to
manage virtually and application over a network of devices/machines.

Setting up Salt With Heist
==========================

This tutorial will go over how to set up Heist to manage ephemeral Salt
Minions. The whole point of Heist is to make deployment and management
of Salt easy!

Using Heist is very easy, Start by downloading Heist. Just install via
`pip`:

.. code-block:: bash

        pip install heist

Setting up a Salt Master
========================

Don't worry, this is a snap!  Once Heist is installed you will need a
Salt Master to connect to. If you have an existing Salt Master running
you can skip this section.

Download the all-in-one Salt binary for Linux (Windows coming soon!):

For Linux:

.. code-block:: bash

    wget https://repo.saltstack.com/salt-bin/linux/salt

For Mac:

.. code-block:: bash

    wget https://repo.saltstack.com/salt-bin/osx/salt

.. note::

    If you want to verify the file, various checksums are located inside the
    repo file: https://repo.saltstack.com/salt-bin/repo.json

Now you can just run it!

.. code-block:: bash

    ./salt master

.. note::

    This binary contains all of the salt commands that typically ship with
    packages of salt. instead of running `salt-call` run `salt call`, instead
    of running `salt-minion` run `salt minion`. Running `salt` maps directly
    to running `salt` normally. Please be aware that the single binary of salt
    is a little slower to start than a standard install of salt, but once it is
    running it should run just as fast as a standard install of salt.

Now you have a running Salt Master to control your minions!

.. note::

    This example is a very simple and easy way to get a Salt Master started.
    If you prefer to have a Salt Master installed in a more traditional way
    please see: http://repo.saltstack.com/

Making Your Roster
==================

A Roster is a file used by Heist to map login information to the
systems in your environment. This file can be very simple and just
needs to tell Heist where your systems are and how to log into them
via ssh:

.. code-block:: yaml

    system_name:
      host: 192.168.4.4
      username: fred
      password: freds_password

That's it! Now you can run Heist to deploy a salt minion and have it connect to
your master! Now that it is connected you can run remote execution and
configuration management routines to your heart's delight using the salt
binary you just downloaded.

This example is very simple, heist support virtually all available authentication
options for ssh.
