# Hello World: bundled ULS reference plugin

**This is the existing Hello World plugin shipped with ULS Core.** It is the canonical introductory example; no second Hello World needs to be installed from the external `uls-plugins` repository.

## Source layout

```text
plugins/hello-world/
  uls-plugin.json
  hello_world.py
  README.md
```

- `uls-plugin.json`: valid API v1 metadata identifying `hello-world`, version `0.1.0`, `screen` capability, and `hello_world:HelloWorldScreen` entry point. ULS still supports JSON manifests for compatibility; **new plugins should prefer `uls-plugin.toml`**.
- `hello_world.py`: dependency-free implementation. `HelloWorldScreen.render()` creates `Framebuffer(64, 32)` and draws **HELLO** and **WORLD** on separate rows.
- `README.md`: this guide.

This bundled example has **no `settings-schema.json`**, no `configure()` method, and no external data source. Those are optional features of a screen implementation, but externally installed screen plugins need a valid settings schema including `display_seconds` under the current installer rules.

## Render locally

From the ULS repository root:

```bash
PYTHONPATH=plugins/hello-world:. python3 - <<'PY'
from hello_world import HelloWorldScreen
from pathlib import Path
frame = HelloWorldScreen().render()
assert (frame.width, frame.height) == (64, 32)
Path("hello-world.ppm").write_bytes(frame.ppm())
print("Wrote hello-world.ppm (64x32)")
PY
```

Run the existing regression tests:

```bash
python3 -m unittest discover -s tests -p 'test_hello_world_plugin.py' -v
```

## Make your own externally installable plugin

1. **Copy this directory** into a separate public GitHub repository or into its `plugins/<your-id>` subdirectory.
2. **Rename the folder, Python module, class, and manifest `id` / `entry_point`** to your own unique names.
3. **Replace `uls-plugin.json` with `uls-plugin.toml`** (do not keep both). For example:

   ```toml
   id = "my-screen"
   name = "My Screen"
   version = "0.1.0"
   api_version = 1
   capabilities = ["screen"]
   entry_point = "my_screen:MyScreen"
   description = "My first ULS screen"
   ```

4. Add **`settings-schema.json`**, at minimum:

   ```json
   {
     "fields": {
       "display_seconds": {
         "type": "integer",
         "default": 12,
         "min": 1,
         "max": 120,
         "label": "Display duration"
       }
     }
   }
   ```

5. Implement a zero-argument class with `render()` returning a **64×32 `Framebuffer`**. Optionally implement `configure(settings)` to receive dashboard settings.
6. Test manifest/schema validation and rendering, commit to GitHub, then **Review → Install → Enable** from ULS Plugin Manager. A repository-root URL or `/tree/main/plugins/<id>` URL is supported. Check the **Open Board View** during idle rotation.

### Runtime limitations

Externally installed plugins execute in a **fresh subprocess for each frame** with a default **1.5-second render timeout**. No Python instance state persists between frames. Don't print to stdout or perform slow network fetches in `render()`. Plugins are trusted Python code, **not a security sandbox**. Live games may take precedence over plugin screens.

For exact field definitions, a configurable screen example, GitHub URL rules and worker tests, read [Building native ULS plugins](../../docs/PLUGIN-DEVELOPMENT.md).

**The bundled example and the external plugin installer are distinct concepts.** This source is already part of ULS and should not be installed again from another repository.
