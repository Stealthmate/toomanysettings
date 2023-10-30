A module for easily loading settings in your app.

## Example usage

```python3
from toomanysettings import Settings, JSONLoader
from pydantic import BaseModel

class MySettings(BaseModel):
    foo: str
    bar: int

s = Settings(model=MySettings, loaders=[
    JSONLoader("my-settings.json")
])
print(s.settings)
# foo='xyz' bar=123

# my-settings.json
# {
#   "foo": "xyz",
#   "bar": 123
# }
```
