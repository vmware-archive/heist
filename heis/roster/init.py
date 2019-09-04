# TODO: I want to get renderers fully mapped over to pop, then these should
# use renderers much more

# Import python libs
import asyncio
import types
from typing import Any, Dict, List


async def read(hub, roster: str, tgt: str, tgt_type: str) -> List[Dict[str: Any]]:
    '''
    Given the rosters to read in, the tgt and the tgt_type
    '''
    ready = {}
    ret = []
    conds = []
    func = getattr(hub, f'roster.{roster}.read')
    ready = await func()
    for id_, condition in ready.items():
        if 'id' not in condition:
            condition['id'] = id_
        conds.append(condition)
    for cond in conds:
        if await hub.tgt.init.check(tgt, tgt_type, cond):
            ret.append(cond)
    return ret
