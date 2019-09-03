CLI_CONFIG = {
    'artifacts_dir': {
        'default': '/var/lib/heis/artifacts',
        'help': 'The location to look for artifacts that will be sent to target systems',
        },
    'roster': {
        'default': 'yaml',
        'help': 'The type of roster to use to load up the targets being used'
        },
    'roster_dir': {
        'default': '/etc/heis/rosters',
        'help': 'The directory to look for rosters',
        },
    'tgt': {
        'default': '',
        'help': 'The target to use, this is ther designation used to determine what subset of systems defined in the roster to attatch to',
        },
    'tgt_type': {
        'default': 'glob',
        'help': 'The type of target syntax to use, globs or regular expressions can be used.'
        },
    'manager': {
        'default': 'salt_master',
        'help': 'The type of manager to use. The manager determines how you want to create the tunnels and if you want to deploy ephemeral agents to the remote systems',
        },
    }
CONFIG = {}
GLOBAL = {}
SUBS = {}
DYNE = {
        'heis': ['heis'],
        'tunnel': ['tunnel'],
        'roster': ['roster'],
        'tgt': ['tgt'],
        }
