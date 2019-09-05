# Import python libs
import os
# Import third party libs
import yaml
from typing import Any, Dict


__virtualname__ = 'yaml'


async def read(hub) -> Dict[str, Any]:
    '''
    Read in the data from the configured rosters
    '''
    ret = {}
    for fn in os.listdir(hub.OPT['heis']['roster_dir']):
        full = os.path.join(hub.OPT['heis']['roster_dir'], fn)
        with open(full, 'r') as rfh:
            ret.update(yaml.safe_load(rfh.read()))
    # TODO: Validate format (Maybe do it in the init)
    return ret
