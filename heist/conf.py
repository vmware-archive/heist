CLI_CONFIG = {
    'artifacts_dir': {
        'default': '/var/lib/heist/artifacts',
        'help': 'The location to look for artifacts that will be sent to target systems',
        },
    'roster': {
        'default': 'flat',
        'help': 'The type of roster to use to load up the remote systems to tunnel to'
        },
    'roster_dir': {
        'default': '/etc/heist/rosters',
        'help': 'The directory to look for rosters',
        },
    'manager': {
        'default': 'salt_master',
        'help': 'The type of manager to use. The manager determines how you want to create the tunnels and if you want to deploy ephemeral agents to the remote systems',
        },
    'checkin_time': {
        'default': 60,
        'type': int,
        'help': 'The number of seconds between checking to see if the managed system needs to get an updated binary or agent restart.'
        },
    'dynamic_upgrade': {
        'default': False,
        'action': 'store_true',
        'help': 'Tell heist to detect when new binaries are available and dynamically upgrade target systems'
        },
    'renderer': {
        'default': 'jinja|yaml',
        'help': 'Specify the renderer to use to render heist roster files'
        },
    }
CONFIG = {}
GLOBAL = {}
SUBS = {}
DYNE = {
        'heist': ['heist'],
        'tunnel': ['tunnel'],
        'roster': ['roster'],
        }
