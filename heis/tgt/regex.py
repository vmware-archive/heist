# Import python libs
import re


def check(hub, tgt, condition):
    '''
    Check that the `id` in the condition glob matches the passed tgt
    '''
    if 'id' not in condition:
        return False
    return bool(re.match(tgt, condition['id']))

