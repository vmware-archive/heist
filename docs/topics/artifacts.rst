===============
Heist Artifacts
===============

Heist automatically downloads artifacts from the web and uses them to deploy
agents. In the case of `Salt`, these artifacts are single binary versions of
`Salt` that have been built using the `salt-bin` system.

If you want to deploy a custom version of Salt, or you want a salt binary
that includes a different version of python, or more dependency libraries
this is very easy to do.

When the artifacts are downloaded from the remote repo they are placed in
your `artifacts_dir`. If you are running `heist` as root this dir can be
found at `/var/lib/heist/artifacts`. If you are running as a user this dir
can be found at `~/.heist/artifacts`.

The downloaded executables are versioned with a version number following
an underscore right after the name of the binary. In the case of `salt`
the file looks like this: `salt_2019.2.2`. If you have a custom build
just name it something that has a higher version number, like
`salt_2019.2.2+1`.

Building Custom Salt Bins
=========================

To build a custom Salt binary, follow the instructions found in the
README.rst file in the salt-bin repo:
https://github.com/saltstack/salt-bin/blob/master/README.rst

The `salt-bin` system is completely self contained and makes it easy to
customize your build of Salt. Just add deps to the requirements.txt
file and run, or make your own requirements.txt file to use.
