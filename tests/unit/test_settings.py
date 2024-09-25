import os

import pydantic

from toomanysettings import DictLoader, EnvLoader, Settings, SettingsModel, UNSET


class OtherSettings(SettingsModel):
    foo: str | UNSET = "f"
    bar: str | UNSET


class SomeSettings(SettingsModel):
    x: str | UNSET
    y: str | UNSET = "foo"
    z: OtherSettings | UNSET


def test_ok() -> None:
    s = Settings(
        model=SomeSettings, loaders=[DictLoader(x="x", z=dict(bar="bar"))]
    ).settings

    assert "x" == s.x
    assert OtherSettings(bar="bar") == s.z


def test_env_loader() -> None:
    os.environ["MY_APP_x"] = "x"
    os.environ["MY_APP_z_bar"] = "bar"
    loader = EnvLoader(model=SomeSettings, prefix="MY_APP")
    result = loader.load()
    assert "x" == result["x"]
    assert "bar" in result["z"]
    assert "bar" == result["z"]["bar"]
