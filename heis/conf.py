CLI_CONFIG = {
    'artifacts_dir': {
        'default': '/var/lib/heis/artifacts',
        'help': 'The location to look for artifacts that will be sent to target systems',
        },
    'roster': {
        'default': 'yaml',
        'help': 'The type of roster to use to load up the remote systems to tunnel to'
        },
    'roster_dir': {
        'default': '/etc/heis/rosters',
        'help': 'The directory to look for rosters',
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
        }
