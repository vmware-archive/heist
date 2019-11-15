.. _salt-artifact:

====================
Salt Heist Artifacts
====================

The Salt artifacts are automatically downloaded from https://repo.saltstack.com/salt-bin/.
Currently there is a linux and mac binary. Windows support will be added at
a later time. The work to add a windows binary is currently being tracked in
issue `6`_.

Heist will automatically download the latest artifact from the repo, unless
it already exists in the `artifacts_dir` or a specific Salt version is set
via the `artifact_version` option. Heist will automatically detect the target
OS and download the appropriate binary. If `artifact_version` is set, heist
will download the `Salt` binary version from the repo if it exists.


.. _`6`: https://github.com/saltstack/salt-bin/issues/6
