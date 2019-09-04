# Import python libs
import asyncio
from typing import Dict


async def check(hub, tgt: str, tgt_type: str, condition: Dict[str: ...]):
    '''
    Pass in the tgt, tgt_type and the condition to match said target to.
    The condition should be a dict containing all information about the
    proposed target so that the condition can be checked for the relative
    data
    '''
    ret = getattr(hub, f'tgt.{tgt_type}.check')(tgt, condition)
    if asyncio.iscoroutine(ret):
        ret = await ret
    return ret
