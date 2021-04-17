import yaml
from enum import Enum
from typing import Dict, List, Union, Optional
from pydantic import Field

from nuclio.specs import CamelBaseModel
from volume import VolumeSpec


class FunctionMetadata(CamelBaseModel):
    name: str = 'function'
    namespace: str = 'nuclio'
    labels: Dict[str, Union[str, int]] = Field(default_factory=lambda: dict())
    annotations: Dict[str, Union[str, int]] = Field(default_factory=lambda: dict())


class BuildSpec(CamelBaseModel):
    path: str = None
    function_source_code: str = None
    registry: str = None
    no_base_image_pull: bool = None
    no_cache: bool = None
    base_image: str = 'python:3.6'
    commands: List[str] = Field(default_factory=lambda: list(), alias='Commands')
    onbuild_image: str = None
    image: str = None
    code_entry_type: str = None
    code_entry_attributes: str = None


class EnvVariableSpec(CamelBaseModel):
    name: str
    value: str


class SecurityContextSpec(CamelBaseModel):
    run_as_user: int = None
    run_as_group: int = None
    fs_group: int = None


class ResourcesSpec(CamelBaseModel):

    class Resources(CamelBaseModel):
        cpu: int = None
        memory: str = None
        gpu: str = Field(default=None, alias='nvidia.com/gpu')

    requests: Resources = Resources()
    limits: Resources = Resources()


class PlatformSpec(CamelBaseModel):

    class Attributes(CamelBaseModel):

        class RestartPolicy(CamelBaseModel):
            name: str = None
            maximum_retry_count: int = None

        class MountOptions(Enum):
            bind = "bind"
            volume = "volume"

        restart_policy: RestartPolicy = RestartPolicy()
        mount_mode: Union[MountOptions, str] = MountOptions.bind

    attributes: Attributes = Attributes()


class NuclioPythonSpec(CamelBaseModel):

    runtime: str = "python:3.6"
    handler: str = "main:handler"

    description: Optional[str] = None
    image: Optional[str] = None

    replicas: int = 0
    min_replicas: int = 1
    max_replicas: int = 4
    target_cpu: Optional[int] = Field(default=None, alias="targetCPU")

    readiness_timeout_seconds: Optional[int] = None
    event_timeout: Optional[int] = None
    avatar: Optional[str] = None

    env: List[EnvVariableSpec] = Field(default_factory=lambda: list())
    volumes: List[VolumeSpec] = Field(default_factory=lambda: list())
    resources: Optional[ResourcesSpec] = ResourcesSpec()
    platform: Optional[PlatformSpec] = PlatformSpec()
    security_context: Optional[SecurityContextSpec] = SecurityContextSpec()


class NuclioConfig(CamelBaseModel):

    api_version: str = "nuclio.io/v1"
    kind: str = "NuclioFunction"
    metadata: FunctionMetadata = FunctionMetadata()
    spec: NuclioPythonSpec = NuclioPythonSpec()

    def add_env(self, variable: Union[Dict, EnvVariableSpec]):
        if type(variable) is dict:
            for key, value in variable.items():
                self.spec.env.append(EnvVariableSpec(name=key, value=value))
        else:
            self.spec.env.append(variable)

    def mount(self, volume: VolumeSpec):
        self.spec.volumes.append(volume)

    def to_dict(self, *args, **kwargs):
        return self.dict(*args, **kwargs)

    def to_yaml(self):
        return yaml.dump(self.to_dict(by_alias=True, exclude_none=True))

    def to_json(self):
        return self.json(by_alias=True, exclude_none=True)
