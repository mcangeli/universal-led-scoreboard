# Development and release workflow

The v0.1.0 candidate implements MLB, 64×32 framebuffer rendering, web configuration, clock, weather, news, Wi-Fi controls, and shared opening-day countdowns. NBA, NFL, NHL, MLS, and EFL modules remain future work.

## Tests

From a checkout with dependencies installed:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m universal_led --output splash.ppm
```

The physical reference installation is managed using system services rather than the original user-level preview:

```bash
sudo ulsctl update
sudo ulsctl health
sudo ulsctl logs
```

See [installation guide](INSTALLATION.md) for the distinction between legacy preview and current system layout.

## Release discipline

Every change should include regression tests, compatibility notes, and user-facing documentation. Do not merge or tag `v0.1.0` until the clean-image installer and manual release checklist pass. Preserve original sport-specific visual language where applicable; the opening-day countdown uses a shared 64×32 layout.

Do not treat the migration scripts `stage-system-services.sh` and `cutover-to-system.sh` as a clean-image installer.
