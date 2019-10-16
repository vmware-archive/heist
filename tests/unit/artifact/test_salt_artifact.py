'''
    unit tests for the clustershell roster
'''
# Import Python libs
import os
import secrets

# Import Local libs
import heist.artifact.salt_artifact

# Import 3rd-party libs
import pop.utils.testing as testing
import pytest


class TestSaltArtifact:
    @pytest.mark.asyncio
    async def test_get_version(self,
                               mock_hub):
        '''
        test heist.artifact.salt_artifact.get_version
        with artifact_version set
        '''
        saltbin = '2019.2.1'
        mock_hub.OPT = {'heist': {'artifact_version': '2019.2.1'}}
        ver = await heist.artifact.salt_artifact.get_version(mock_hub, 'linux')
        mock_hub.artifact.salt.fetch.assert_not_called()
        assert ver == saltbin

    @pytest.mark.asyncio
    async def test_get_version_latest(self,
                                      mock_hub):
        '''
        test heist.artifact.salt_version.get_version
        with artifact_version not set and returns latest
        '''
        mock_hub.OPT = {'heist': {'artifact_version': ''}}
        data = {'linux': {'salt-2019.2.1': {'version': '2019.2.1'},
                          'salt-2019.2.3': {'version': '2019.2.3'},
                          'salt-2019.2.2': {'version': '2019.2.2'}}}
        mock_hub.artifact.salt.fetch.return_value = data

        ver = await heist.artifact.salt_artifact.get_version(mock_hub, 'linux')
        mock_hub.artifact.salt.fetch.assert_called()
        assert ver == '2019.2.3'

    @pytest.mark.asyncio
    async def test_get_artifact(self,
                                mock_hub: testing.MockHub,
                                tmp_path):
        '''
        test heist.salt_master.get_artifact
        when artifact does not already exist
        '''
        t_name = secrets.token_hex()
        ver = '2019.2.1'

        art_l = os.path.join(tmp_path, f'salt-{ver}')
        os.mknod(art_l)

        mock_hub.artifact.salt.fetch.return_value = art_l
        mock_hub.heist.salt_master.latest.return_value = False
        ret = await heist.artifact.salt_artifact.get_artifact(mock_hub, t_name,
                                                              'asyncssh', tmp_path,
                                                              'linux', ver)
        assert ret

    @pytest.mark.asyncio
    async def test_get_artifact_exists(self,
                                       mock_hub: testing.MockHub,
                                       tmp_path):
        '''
        test heist.salt_master.get_artifact
        when artifact already exists
        '''
        t_name = secrets.token_hex()
        ver = '2019.2.1'

        art_l = os.path.join(tmp_path, f'salt-{ver}')

        mock_hub.artifact.salt.fetch.return_value = art_l
        mock_hub.heist.salt_master.latest.return_value = True
        ret = await heist.artifact.salt_artifact.get_artifact(mock_hub, t_name,
                                                              'asyncssh', tmp_path,
                                                              'linux', ver)
        assert ret
        mock_hub.artifact.salt.fetch.assert_not_called()
