# Architecture of SRE Chaos Agent

## Overview

The application is built with Kivy framework and uses Python's threading for stress tests. Android-specific hardware data is obtained either via jnius (Java Native Interface) or by reading sysfs files as fallback.

## Components

### UI (Kivy)
- Main layout: vertical BoxLayout
- Info label (updated every 2 seconds)
- Log area (read-only TextInput)
- Control buttons

### Data Collection
- **JNIUS path**: Uses `PythonActivity`, `BatteryManager` to get battery level, voltage, temperature, technology. Also reads Build properties (manufacturer, model, Android version).
- **Fallback path**: Reads `/sys/class/power_supply/battery/capacity` and `/sys/class/thermal/thermal_zone0/temp` (works on many devices without root).

### CPU Load Indicator
- Because real CPU load retrieval from Android without root is complex (requires parsing /proc/stat with two samples), current version simulates load based on stress activity: high load (50-95%) when a stress test is running, otherwise 0%.

### Stress Tests
- Each test runs a separate thread that performs heavy arithmetic in a loop.
- The main UI remains responsive because Kivy's main loop is not blocked.
- A threading.Event flag (`load_stop`) allows graceful interruption.

### Thread Safety
- UI updates (especially logging) are scheduled via `Clock.schedule_once` to run on the main Kivy thread.

## Build Process

- Use Buildozer to create APK.
- The `buildozer.spec` targets Android API 31, ARM64, includes required permissions and dependencies.

## Future Improvements

- Real CPU load via `/proc/stat` (requires two consecutive reads)
- Graph history of battery and temperature
- Save logs to file
- Widget for controlling stress intensity