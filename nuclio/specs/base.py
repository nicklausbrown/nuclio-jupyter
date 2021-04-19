import yaml
from enum import Enum
from typing import Dict, List, Union, Optional
from pydantic import Field

from nuclio.specs import CamelBaseModel
from .volume import VolumeSpec
from .trigger import HttpTrigger, KafkaTrigger, V3ioStreamTrigger, CronTrigger
from .code_entry import CodeEntryType, S3Attributes, ArchiveAttributes, GithubAttributes


class FunctionMetadata(CamelBaseModel):
    """ Nuclio function metadata

    Attributes
    ----------
    name : str
        The name of the function
    namespace : str
        A level of isolation provided by the platform (e.g., Kubernetes)
    labels : dict
        A dict that is used for looking up the function (immutable, can't update after first deployment)
    annotations : dict
        A dict of annotations

    """
    name: str = 'nuclio-function'
    namespace: str = 'nuclio'
    labels: Dict[str, str] = Field(default_factory=lambda: dict())
    annotations: Dict[str, str] = Field(default_factory=lambda: dict())


class BuildSpec(CamelBaseModel):

    code_entry_type: Optional[CodeEntryType] = None
    code_entry_attributes: Optional[Union[S3Attributes, ArchiveAttributes, GithubAttributes]] = None

    path: str = None
    function_source_code: str = None

    no_cache: bool = None
    no_base_image_pull: bool = None

    registry: str = None
    onbuild_image: str = None
    base_image: str = None

    commands: List[str] = Field(default_factory=lambda: list(), alias='Commands')

    image: Optional[str] = None


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


class PlatformRestartPolicy(CamelBaseModel):
    name: str = None
    maximum_retry_count: int = None


class PlatformMountOptions(Enum):
    bind = "bind"
    volume = "volume"


class PlatformSpec(CamelBaseModel):

    class Attributes(CamelBaseModel):

        restart_policy: PlatformRestartPolicy = PlatformRestartPolicy()
        mount_mode: Union[PlatformMountOptions, str] = PlatformMountOptions.bind

    attributes: Attributes = Attributes()


class NuclioPythonSpec(CamelBaseModel):
    """ Nuclio function highest level specification

    Learn more here: https://nuclio.io/docs/latest/reference/function-configuration/function-configuration-reference/#function-specification-spec

    Attributes
    ----------
    runtime : str
        The name of the language runtime (python:3.6, python:3.7, etc.)
    handler : str
        The entry point to the function, in the form of package:entrypoint; varies slightly between runtimes, see the
         appropriate runtime documentation for specifics
    description : str, optional
        A textual description of the function
    image : str, optional
        Potential code entry type for specifying a nuclio function as a docker image directly
    min_replicas : int, optional
        The minimum number of replicas
    max_replicas : int, optional
        The maximum number of replicas
    replicas : int, optional
        The number of desired instances; 0 for auto-scaling.
    target_cpu : int, optional
        Target CPU when auto scaling, as a percentage (default: 75%)
    readiness_timeout_seconds : int, optional
        Number of seconds that the controller will wait for the function to become ready before declaring
        failure (default: 60)
    event_timeout : int, optional
        Global event timeout, in the format supported for the Duration parameter of the time.ParseDuration Go function
    avatar : str, optional
        Base64 representation of an icon to be shown in UI for the function
    run_registry : str, optional
        The container image repository from which the platform will pull the image
    env : list
        A list of environment variables dicts or specs
    volumes : list
        A map in an architecture similar to Kubernetes volumes
    triggers : dict
        A map of triggers for a nuclio function like http or kafka
    resources : ResourcesSpec, optional
        Limit resources allocated to deployed function
    platform : PlatformSpec, optional
        Docker options for nuclio functions
    security_context : SecurityContextSpec, optional
        Unix style image security constraints like users and groups

    """
    runtime: str = "python:3.6"
    handler: str = "main:handler"
    description: Optional[str] = None

    image: Optional[str] = None

    min_replicas: Optional[int] = 1
    max_replicas: Optional[int] = 2
    replicas: Optional[int] = None  # should this be zero?
    target_cpu: Optional[int] = Field(default=None, alias="targetCPU")

    readiness_timeout_seconds: Optional[int] = None
    event_timeout: Optional[int] = None
    avatar: Optional[str] = None
    run_registry: Optional[str] = None

    env: List[EnvVariableSpec] = Field(default_factory=lambda: list())
    volumes: List[VolumeSpec] = Field(default_factory=lambda: list())
    triggers: Dict[str, Union[HttpTrigger,
                              KafkaTrigger,
                              V3ioStreamTrigger,
                              CronTrigger]] = Field(default_factory=lambda: dict())
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

    def add_volume(self, volume: VolumeSpec):
        self.spec.volumes.append(volume)

    def add_trigger(self, name, trigger: Union[HttpTrigger, KafkaTrigger, V3ioStreamTrigger, CronTrigger]):
        self.spec.triggers[name] = trigger

    def to_dict(self, *args, **kwargs):
        return self.dict(*args, **kwargs)

    def to_yaml(self):
        return yaml.dump(self.to_dict(by_alias=True, exclude_none=True))

    def to_json(self):
        return self.json(by_alias=True, exclude_none=True)
