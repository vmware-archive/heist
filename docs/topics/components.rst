================
Heist Subsystems
================

Since `heist` is built on `pop` it is comprosed of several plugin subsystems,
or `subs`. Each `sub` is loaded using pop's dynamic names interface and therefore
can be extended using vertical app-merging or adding additional plugins directly
to `heist`.

Heist Subsystem
===============

The heist subsystem is used to create managers for specific daemons. Therefore
if there is another agent that someone wanted to add to heist to make it
disolvable and distributable via heist they would add a plugin to the heist
subsystem.

The required functions to add a new managed agent to heist are:

run
----

This is the entry function. The `run` function is used to start the process
of creating tunnels and sending daemon code to target systems.

deploy
------

The `deploy` function is used to deploy the desired code down to the target
systems.

update
------

The `update` function is used to send an updated version of the dasired code
down to the target system.

clean
-----

The `clean` function is called when heist gets shut down. This is used to send
commands to the remote systems to shut down and clean up the agents.

Roster Subsystem
================

The roster subsystem is used to add ways to load up target system data. If
it is desired to load roster data from an alternative source a roster
can be easily added.

Rosters are very simple, they just need a single async function:

read
----

The `read` function is called to read in the roster data and returns the roster
data structure. The roster data structure is a python dict following this structure:

.. code-block:: yaml

    hostname/id:
      logincred: data
      logindata: data
    hostname/id:
      logincred: data
      logindata: data

Artifact Subsystem
==================

The artifact system allows for code artifacts that will be deployed to target systems
to be downloaded from an artifact source. The artifact source will be specific to the
code that is being deployed. It is typical that an artifact plugin will be built
in concert with a specific heist plugin.

get_version
-----------

Gather the available version data for the artifacts

get_artifact
------------

Download the actual artifact and store it locally so it can be sent down with the
`heist` subsystem.

Tunnel Subsystem
================

The `tunnel` subsystem is used to establish communication tunnels with target
systems. If you want to use a system for tunneling other than ssh, or you want to use
a different ssh backend, just make a new tunnel plugin! The tunnel plugin needs to be
able to connect to remote systems, make network tunnels, copy files and execute commands.

create
------

Used to create the new tunnel instance on the hub. This is where the persistent connection
or re-connection (if needed) logic is created.

send
----

The ability to send files to the target system is implemented here.

get
----

The ability to retrieve files from the target system is set up here.

cmd
----

This function runs shell commands on the target system

tunnel
------

This function creates a network tunnel from ports on the target system back to ports on the source system

destroy
-------

Properly destroy a connection.
