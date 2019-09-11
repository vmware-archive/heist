# Import python libs
import os
from typing import Any, Dict
import rend


async def read(hub) -> Dict[str, Any]:
    '''
    Read in the data from the configured rosters
    '''
    ret = {}
    for fn in os.listdir(hub.OPT['heis']['roster_dir']):
        full = os.path.join(hub.OPT['heis']['roster_dir'], fn)
        ret.update(hub.rend.init.parse(full, 'yaml'))
    # TODO: Validate format (Maybe do it in the init)
    return ret
