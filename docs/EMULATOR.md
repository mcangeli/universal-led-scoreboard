# Browser emulator (Preview 2)

No HAT, LED panel, GPIO access, pip packages or sudo required.

From the project root, start the preview server:

```sh
python3 -c "from universal_led.web_preview import serve; serve(host='0.0.0.0', port=8765)"
```

Open `http://<pi-ip>:8765` from a browser on the same trusted local network. The browser renders a native 64x32 framebuffer and polls the preview endpoint once per second. The server is **read-only**, has **no authentication**, and should **not** be exposed to the public internet. Bind to `127.0.0.1` for local-only use.

The preview currently shows the static startup splash. Dynamic league frames and a complete web configurator are future milestones.

## Optional physical backend

`universal_led.backends.Hub75Backend` provides an experimental adapter to hzeller's `rgbmatrix` bindings. It is never imported by emulator mode. Do not enable physical output until you have a compatible HAT/panel, a validated driver build, and correct power and wiring. The adapter is untested on physical hardware.
