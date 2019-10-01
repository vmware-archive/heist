# import Python libs
import sys
from typing import List

# Import 3rd-party libs
import mock
import pop.hub
import pop.utils.testing as testing


def mock_hub(subs: List[str] = None, sys_argv: List[str] = None) -> testing.MockHub:
    hub = pop.hub.Hub()
    if subs is None:
        subs = []

    # heist.heist is the "main", therefore command line args must be patched to remove pytest args
    if 'heist.heist' in subs:
        subs.remove('heist.heist')
        if not sys_argv:
            # If args weren't specified, strip pytest args
            sys_argv = sys.argv[:1]
        with mock.patch.object(sys, 'argv', sys_argv):
            hub.pop.sub.add('heist.heist')

    # Add specified subs
    for sub in subs:
        if '.' in sub:
            hub.pop.sub.add(sub)
        else:
            hub.pop.sub.add(dyne_name=sub)

    return testing.MockHub(hub)
