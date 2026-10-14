# Development quick start

Requires Python 3.10+ for the current foundation. No hardware or third-party packages are required for these first tests.

```sh
python3 -m unittest discover -s tests -v
python3 -m universal_led --output splash.ppm
```

The preview is a native 64x32 PPM image, viewable with image editors that support PPM. It is not yet a Raspberry Pi matrix driver.

## Release discipline

For every implementation change: add regression tests, update the user/developer documentation, and record compatibility and migration notes. Preserve the classic visual language of each upstream sport. Do not claim support for a league or SBC until tested.
