from typing import Union, Optional
from pydantic import SecretStr, PrivateAttr
from nuclio.specs import CamelBaseModel


class PersistentVolume(CamelBaseModel):

    class Attributes(CamelBaseModel):
        claim_name: str = None

    name: str = None
    persistent_volume_claim: Attributes = Attributes()


class HostVolume(CamelBaseModel):

    class Attributes(CamelBaseModel):
        path: str = None

    name: str = None
    host_path: Attributes = Attributes()


class SecretVolume(CamelBaseModel):

    class Attributes(CamelBaseModel):
        secret_name: str = None

    name: str = None
    secret: Attributes = Attributes()


class V3ioVolume(CamelBaseModel):

    class Attributes(CamelBaseModel):

        class Options(CamelBaseModel):
            container: str = None
            sub_path: str = None
            access_key: SecretStr = None

        driver: str = 'v3io/fuse'
        options: Options = Options()

    name: str = None
    flex_volume: Attributes = Attributes()


class VolumeSpec(CamelBaseModel):

    _name: str = PrivateAttr(default='volume')

    class Mount(CamelBaseModel):
        name: str = None
        read_only: Optional[bool] = None
        mount_path: str = None

    volume_mount = Mount()
    volume: Union[PersistentVolume, HostVolume, SecretVolume, V3ioVolume]

    def __init__(self, **data):
        super().__init__(**data)
        self._apply_name()

    def name(self, name=None):
        if name is None:
            return self._name
        else:
            self._name = name
            self._apply_name()

    def _apply_name(self):
        self.volume_mount.name = self._name
        self.volume.name = self._name
