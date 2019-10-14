# TODO: I want to get renderers fully mapped over to pop, then these should
# use renderers much more

# Import python libs
import logging
from typing import Any, Dict, List

# Import pop libs
import rend.exc

log = logging.getLogger(__name__)


async def read(hub, roster: str) -> List[Dict[str, Any]]:
    '''
    Given the rosters to read in, the tgt and the tgt_type
    '''
    ret = []

    try:
        ready = await getattr(hub, f'roster.{roster}.read')()
    except rend.exc.RenderException as exc:
        log.critical(f'Could not render the {roster} roster, error: {exc.args[0]}')
        return False

    if not ready:
        log.critical(f'The roster {roster} did not return data when rendered')
        return False

    if not isinstance(ready, dict):
        log.critical(f'The roster {roster} is not formatted correctly')
        return False

    for id_, condition in ready.items():
        if not isinstance(condition, dict):
            log.critical(f'The roster {roster} is not formatted correctly.')
            return False
        if 'id' not in condition:
            condition['id'] = id_
        ret.append(condition)
    return ret
