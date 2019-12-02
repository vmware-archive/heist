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

Before you start please be advised that a more detailed quickstart is
available in the docs for `heist`.

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

Now you can just run it!

.. code-block:: bash

    chmod +x salt
    sudo ./salt master

Now you have a running Salt Master to control your minions!

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

Thats it! Now that the minion is up you can run `salt` commands on it at breakneck
speed, the full power of Salt is at your fingertips!!

