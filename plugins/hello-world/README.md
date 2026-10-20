# Hello World: native ULS plugin example

This is the smallest practical **screen plugin example** for Universal LED Scoreboard.

## Files

- `uls-plugin.json`: metadata validated by `universal_led.plugin_manifest`
- `hello_world.py`: Python screen with a zero-argument constructor and `render()` method returning a 64×32 `Framebuffer`

## Run the example locally

From the repository root:

```bash
PYTHONPATH=plugins/hello-world:. python3 - <<'PY'
from hello_world import HelloWorldScreen
from pathlib import Path
frame = HelloWorldScreen().render()
Path("hello-world.ppm").write_bytes(frame.ppm())
print("Wrote hello-world.ppm (64x32)")
PY
```

The PPM can be viewed with an image viewer supporting PPM, or converted to PNG using an image conversion tool.

Run its regression tests:

```bash
python3 -m unittest discover -s tests -p 'test_hello_world_plugin.py' -v
```

## How it works

`uls-plugin.json` uses API version `1` and a `screen` capability. The entry point `hello_world:HelloWorldScreen` identifies the Python module and class. The class exposes `render()`, which creates a 64×32 framebuffer and draws two words. It does not access the network, settings, filesystem, or physical LED matrix.

To create another simple screen, copy this folder, change the plugin ID, folder name, module and entry point, and implement your own `render()`. Use a unique plugin ID and keep frames exactly 64×32.

## Current integration status

**Example and test fixture, not an automatically loaded screen.** The v0.9.0 Plugin Manager can validate and inventory plugin packages, but runtime loading and rotation integration are not yet connected. Merely copying this folder to an installation directory does **not** make HELLO WORLD appear in the rotation. The sample is deliberately not enabled automatically, and no third-party code is imported during discovery.

See [Plugin Development Guide](../../docs/PLUGIN-DEVELOPMENT.md) for the native plugin roadmap and the separate Bullpen compatibility path.
