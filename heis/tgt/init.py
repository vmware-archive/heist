# Import python libs
import asyncio


async def check(hub, tgt, tgt_type, condition):
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
