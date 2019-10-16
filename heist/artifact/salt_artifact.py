'''
    artifact module to manage the download of salt artifacts
'''
# Import python libs
from distutils.version import LooseVersion
import logging
import os

# Import 3rd party libs
import aiohttp

__virtualname__ = 'salt'

log = logging.getLogger(__name__)


async def fetch(hub, session, url, download=False, location=False):
    '''
    Fetch a url and return json. If downloading artifact
    return the download location.
    '''
    async with session.get(url) as resp:
        if resp.status == 200:
            if download:
                with open(location, 'wb') as fn_:
                    fn_.write(await resp.read())
                return location
            return await resp.json()
        log.critical(f'Cannot query url {url}. Returncode {resp.status} returned')
        return False

async def get_version(hub, t_os):
    '''
    Query latest version from repo if user does not define version
    '''
    ver = hub.OPT['heist'].get('artifact_version')
    if ver:
        return ver

    url = 'https://repo.saltstack.com/salt-bin/repo.json'
    async with aiohttp.ClientSession() as session:
        data = await hub.artifact.salt.fetch(session, url)
        if not data:
            log.critical(f'Query to {url} failed, falling back to'
                         f'pre-downloaded artifacts')
            return False
        # we did not set version so query latest version from the repo
        for binary in data[t_os]:
            b_ver = data[t_os][binary]['version']
            if not ver:
                ver = b_ver
                continue
            if LooseVersion(b_ver) > LooseVersion(ver):
                ver = b_ver
        return ver

async def get_artifact(hub, t_name, t_type, art_dir, t_os, ver):
    '''
    Dowlnoad artifact if does not already exist. If artifact
    version is not specified, download the latest from pypi
    '''
    art_n = f'salt-{ver}'
    url = f'https://repo.saltstack.com/salt-bin/{t_os}/{art_n}'

    await getattr(hub, f'tunnel.{t_type}.cmd')(t_name, f'mkdir -p {art_dir}')

    # check to see if artifact already exists
    if hub.heist.salt_master.latest('salt', art_dir, version=ver):
        log.info(f'The Salt artifact {ver} already exists')
        return True

    # download artifact
    async with aiohttp.ClientSession() as session:
        log.info(f'Downloading the artifact {art_n} to {art_dir}')
        await hub.artifact.salt.fetch(session, url,
                                      download=True,
                                      location=os.path.join(art_dir,
                                                            art_n))
    # ensure artifact was downloaded
    if not any(ver in x for x in os.listdir(art_dir)):
        log.critical(f'Did not find the {ver} artifact in {art_dir}.'
                     f' Untarring the artifact failed or did not include version')
        return False
    return True
