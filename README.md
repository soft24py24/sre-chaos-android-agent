# SRE Chaos Agent for Android

An Android application for stress testing and real-time monitoring of your device (battery, temperature, voltage, CPU load). Built with Kivy and jnius.

## Features

- Real-time metrics: device model, Android version, battery level, voltage, temperature, CPU load (simulated based on stress activity)
- Stress tests: Light (15s), Medium (30s), HEAVY (60s)
- Stop stress and emergency exit ("Mne strashno")
- Thread‑safe logging

## Requirements

- Python 3.9+
- Kivy 2.3.1
- pyjnius (for direct Android battery access; if not available, falls back to sysfs)

## Run in Pydroid3 (easiest)

1. Install Pydroid3 from Google Play.
2. Install Kivy and pyjnius inside Pydroid (use its built-in pip).
3. Copy `main.py` to Pydroid and run.

## Build APK with Buildozer (Linux/Windows WSL)

1. Install buildozer: `pip install buildozer`
2. Place `main.py`, `buildozer.spec`, and `requirements.txt` in a folder.
3. Run `buildozer android debug deploy run`
4. APK will be in `bin/`

## Permissions

- `READ_BATTERY_STATS` (may not work without system signature; jnius does not require it)
- Fallback reading from `/sys/class/power_supply` works on most devices without extra permissions.

## License

MIT © soft24py24