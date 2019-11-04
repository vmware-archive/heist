=====
Heist
=====

Heist creates network tunnels for distributing and managing agents. While it has
been originally built to deploy and manage Salt Minions, it can be used to
distribute and manage other agents or plugins if extended to do so.

Using Heist For Salt
====================
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
you can skip this section, just run `heist` on your Salt Master.

Download the all-in-one Salt binary for Linux or Mac (Windows coming soon!):

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
via ssh. Open a file called `roster.cfg` and add the data needed to connect
to a remote system via ssh:

.. code-block:: yaml

    system_name:
      host: 192.168.4.4
      username: fred
      password: freds_password

.. note::

    This example is very simple, heist supports virtually all available authentication
    options for ssh.

The roster files typically all live inside of a roster directory. But to get
started will will execute a single roster file with `heist`:

.. code-block:: bash

    heist -R roster.cfg

Assuming your roster is correct, heist will now connect to the remote
system, deploy a salt minion, and connect it to your running master! Now you
can use the same binary that you started the master with to accept your new
minion's keys:

.. code-block:: bash

    ./salt key -A

Then give your minion a few seconds to authenticate and then run your first
`salt` command on the newly set up minion:

.. code-block:: bash

    ./salt \* test.version

That's it! Now that the minion is up you can run `salt` commands on it at breakneck
speed, the full power of Salt is at your fingertips!!

Tear Down
=========

Heist is able to automatically clean up your minions as well! Just soft kill
your heist application and it will reach out to all connections, tell them to
remove `salt` from the target systems and stop the minions! Like a proper heist
these should be no evidence left behind!

