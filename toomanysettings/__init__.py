import abc
import json
import os
import typing

import pydantic

TSettings = typing.TypeVar("TSettings", bound=pydantic.BaseModel)


class SettingsLoader(abc.ABC):
    @abc.abstractmethod
    def load(self) -> dict[str, typing.Any]:
        raise NotImplementedError()


class Settings(typing.Generic[TSettings]):
    def __init__(
        self, *, model: type[TSettings], loaders: typing.Iterable[SettingsLoader]
    ) -> None:
        self._loaders = loaders
        self._model = model

    @property
    def settings(self) -> TSettings:
        self._settings: dict[str, typing.Any] = {}
        for loader in self._loaders:
            self._settings = self.merge_dicts(self._settings, loader.load())
        return self._model.model_validate(self._settings)

    def merge_dicts(self, *ds: dict[str, typing.Any]) -> dict[str, typing.Any]:
        if len(ds) == 0:
            return {}
        if len(ds) == 1:
            return ds[0]
        head = ds[0]
        next_head = ds[1]
        tail = ds[2:]

        merged_head = {}

        for k, v in next_head.items():
            if k not in head:
                merged_head[k] = v
            else:
                merged_head[k] = self.merge_dicts(head[k], next_head)

        return self.merge_dicts(merged_head, *tail)


class DictLoader(SettingsLoader):
    def __init__(self, **values: typing.Any) -> None:
        super().__init__()
        self._values = values

    def load(self) -> dict[str, typing.Any]:
        return self._values


class JSONLoader(SettingsLoader):
    def __init__(self, fp: str) -> None:
        super().__init__()
        self._fp = fp

    def load(self) -> dict[str, typing.Any]:
        with open(self._fp, mode="r") as f:
            content = json.load(f)
            if not isinstance(content, dict):
                raise Exception("Only objects are supported.")
            return content


class TOMLLoader(SettingsLoader):
    def __init__(self, fp: str) -> None:
        super().__init__()
        self._fp = fp

    def load(self) -> dict[str, typing.Any]:
        try:
            import toml
        except ImportError as ex:
            raise Exception(
                "TOMLLoader requires the toml module to work. Consider installing it."
            ) from ex
        with open(self._fp, mode="r") as f:
            content = toml.load(f)
            if not isinstance(content, dict):
                raise Exception("Only objects are supported.")
            return content


class YAMLLoader(SettingsLoader):
    def __init__(self, fp: str) -> None:
        super().__init__()
        self._fp = fp

    def load(self) -> dict[str, typing.Any]:
        try:
            import yaml
        except ImportError as ex:
            raise Exception(
                "YAMLLoader requires the yaml module to work. Consider installing it."
            ) from ex
        with open(self._fp, mode="r") as f:
            content = yaml.load(f)
            if not isinstance(content, dict):
                raise Exception("Only objects are supported.")
            return content


class EnvLoader(typing.Generic[TSettings], SettingsLoader):
    def __init__(self, *, model: type[TSettings], prefix: str = "") -> None:
        self._model = model
        self._prefix = prefix

    def load(self) -> dict[str, typing.Any]:
        return self.load_with_prefix(self._prefix, self._model)

    def load_with_prefix(
        self, prefix: str, model: type[pydantic.BaseModel]
    ) -> dict[str, typing.Any]:
        result: dict[str, typing.Any] = {}
        for field, field_info in model.model_fields.items():
            env_var_name = f"{prefix}_{field}"
            if field_info.annotation is not None and issubclass(
                field_info.annotation, pydantic.BaseModel
            ):
                result[field] = self.load_with_prefix(
                    env_var_name, field_info.annotation
                )
            value = os.environ.get(env_var_name, None)
            if value is not None:
                result[field] = value
        return result
