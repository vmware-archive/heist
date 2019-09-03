# Import python libs
import fnmatch


def check(hub, tgt, condition):
    '''
    Check that the `id` in the condition glob matches the passed tgt
    '''
    if 'id' not in condition:
        return False
    return fnmatch.fnmatch(condition['id'], tgt)
