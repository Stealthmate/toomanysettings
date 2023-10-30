import pydantic

from toomanysettings import DictLoader, Settings


class OtherSettings(pydantic.BaseModel):
    foo: str = "f"
    bar: str


class SomeSettings(pydantic.BaseModel):
    x: str
    y: str = "foo"
    z: OtherSettings


def test_ok() -> None:
    s = Settings(
        model=SomeSettings, loaders=[DictLoader(x="x", z=dict(bar="bar"))]
    ).settings

    assert "x" == s.x
    assert OtherSettings(bar="bar") == s.z
