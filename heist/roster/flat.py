# Import python libs
import os
from typing import Any, Dict


async def read(hub) -> Dict[str, Any]:
    '''
    Read in the data from the configured rosters
    '''
    ret = {}
    if hub.OPT['heist'].get('roster_file'):
        return hub.rend.init.parse(hub.OPT['heist']['roster_file'])
    for fn in os.listdir(hub.OPT['heist']['roster_dir']):
        full = os.path.join(hub.OPT['heist']['roster_dir'], fn)
        ret.update(hub.rend.init.parse(full, hub.OPT['heist']['renderer']))
    # TODO: Validate format (Maybe do it in the init)
    return ret
