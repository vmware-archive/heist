# TODO: I want to get renderers fully mapped over to pop, then these should
# use renderers much more

# Import python libs
import asyncio
import types
from typing import Any, Dict, List


async def read(hub, roster: str) -> List[Dict[str, Any]]:
    '''
    Given the rosters to read in, the tgt and the tgt_type
    '''
    ret = []

    ready = await getattr(hub, f'roster.{roster}.read')()
    for id_, condition in ready.items():
        if 'id' not in condition:
            condition['id'] = id_
        ret.append(condition)
    return ret
