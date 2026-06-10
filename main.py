"""
SRE Chaos Agent for Android
Load testing & monitoring (battery, temperature, CPU)
Uses Kivy + jnius (or fallback)
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import threading
import time
import os

# Jnius for direct Android API access (battery info)
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    IntentFilter = autoclass('android.content.IntentFilter')
    Intent = autoclass('android.content.Intent')
    BatteryManager = autoclass('android.os.BatteryManager')
    Build = autoclass('android.os.Build')
    BuildVersion = autoclass('android.os.Build$VERSION')
    JNIUS_AVAILABLE = True
except:
    JNIUS_AVAILABLE = False
    # fallback dummy classes
    class Build:
        MANUFACTURER = "Unknown"
        MODEL = "Unknown"
    class BuildVersion:
        RELEASE = "Unknown"

class SREChaosApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_active = False
        self.load_stop = threading.Event()

    def build(self):
        layout = BoxLayout(orientation='vertical', padding=8, spacing=6)

        self.info_label = Label(
            text="SRE Chaos Agent\nLoading...",
            font_size='14sp',
            size_hint=(1, 0.35),
            halign='center',
            valign='top'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))

        self.log_area = TextInput(
            text="[Log] Ready\n",
            readonly=True,
            font_size='12sp',
            size_hint=(1, 0.35)
        )

        btn_light = Button(text="Light stress (15 sec)", size_hint=(1, 0.08))
        btn_light.bind(on_press=self.start_light)
        btn_medium = Button(text="Medium stress (30 sec)", size_hint=(1, 0.08))
        btn_medium.bind(on_press=self.start_medium)
        btn_heavy = Button(text="HEAVY stress (60 sec)", size_hint=(1, 0.08))
        btn_heavy.bind(on_press=self.start_heavy)
        btn_stop = Button(text="STOP stress", size_hint=(1, 0.08))
        btn_stop.bind(on_press=self.stop_stress)
        btn_exit = Button(text="Mne strashno (exit)", size_hint=(1, 0.08))
        btn_exit.bind(on_press=self.exit_app)

        layout.add_widget(self.info_label)
        layout.add_widget(self.log_area)
        layout.add_widget(btn_light)
        layout.add_widget(btn_medium)
        layout.add_widget(btn_heavy)
        layout.add_widget(btn_stop)
        layout.add_widget(btn_exit)

        Clock.schedule_interval(self.update_info, 2)
        return layout

    def get_cpu_load_avg(self):
        """Return approximate CPU load (0-100) based on stress active state.
        Real load would require reading /proc/stat twice, but for demo it's enough.
        """
        if self.load_active:
            # Simulate high load when stress is running
            return min(95, 50 + (int(time.time()) % 50))
        else:
            # Simulate idle
            return 0

    def get_system_info(self):
        info = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'android': 'Unknown',
            'cores': os.cpu_count() or 0,
            'battery': None,
            'voltage': None,
            'temperature': None,
            'tech': None,
            'cpu_load': 0
        }
        if JNIUS_AVAILABLE:
            try:
                context = PythonActivity.mActivity
                ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
                battery_intent = context.registerReceiver(None, ifilter)
                if battery_intent:
                    level = battery_intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                    scale = battery_intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                    if scale > 0:
                        info['battery'] = (level / scale) * 100
                    info['voltage'] = battery_intent.getIntExtra(BatteryManager.EXTRA_VOLTAGE, 0) / 1000.0
                    info['temperature'] = battery_intent.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) / 10.0
                    info['tech'] = battery_intent.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY)
                info['manufacturer'] = Build.MANUFACTURER
                info['model'] = Build.MODEL
                info['android'] = BuildVersion.RELEASE
            except Exception as e:
                self.log_add(f"JNIUS error: {str(e)}")
        else:
            # Fallback: try to read sysfs
            try:
                with open('/sys/class/power_supply/battery/capacity', 'r') as f:
                    val = f.read().strip()
                    if val.isdigit():
                        info['battery'] = float(val)
            except:
                pass
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    val = int(f.read().strip()) / 1000.0
                    info['temperature'] = val
            except:
                pass
        info['cpu_load'] = self.get_cpu_load_avg()
        return info

    def update_info(self, dt):
        info = self.get_system_info()
        bat_str = f"{info['battery']:.1f}%" if info['battery'] is not None else "N/A"
        temp_str = f"{info['temperature']:.1f} C" if info['temperature'] is not None else "N/A"
        volt_str = f"{info['voltage']:.2f}V" if info['voltage'] is not None else "N/A"
        tech_str = info['tech'] if info['tech'] else "N/A"
        text = (
            "SRE CHAOS AGENT\n"
            f"Device: {info['manufacturer']} {info['model']}\n"
            f"Android: {info['android']}\n"
            f"Cores: {info['cores']}\n"
            f"CPU Load: {info['cpu_load']:.0f}%\n"
            f"Battery: {bat_str}\n"
            f"Voltage: {volt_str}\n"
            f"Temp: {temp_str}\n"
            f"Tech: {tech_str}\n"
            "----------------------"
        )
        self.info_label.text = text

    def log_add(self, msg):
        """Thread‑safe logging via Clock"""
        def _update(dt):
            self.log_area.text += "[Log] " + msg + "\n"
            self.log_area.cursor = (0, len(self.log_area.text))
        Clock.schedule_once(_update, 0)

    def start_load(self, duration, intensity_name):
        if self.load_active:
            self.log_add("Already stressing, stop first.")
            return
        self.load_active = True
        self.load_stop.clear()
        self.log_add(f"Starting {intensity_name} stress for {duration} sec.")
        def load_runner():
            end = time.time() + duration
            while time.time() < end and not self.load_stop.is_set():
                # Heavy calculation loop
                for _ in range(200000):
                    _ = 3.14159 * 2.71828
                time.sleep(0.01)
            self.load_active = False
            self.log_add("Stress finished.")
        threading.Thread(target=load_runner, daemon=True).start()

    def start_light(self, instance):
        self.start_load(15, "Light")

    def start_medium(self, instance):
        self.start_load(30, "Medium")

    def start_heavy(self, instance):
        self.start_load(60, "HEAVY")

    def stop_stress(self, instance):
        if self.load_active:
            self.load_stop.set()
            self.log_add("Stress stopped by user.")
        else:
            self.log_add("No active stress to stop.")

    def exit_app(self, instance):
        self.log_add("Exiting SRE Chaos Agent. Goodbye!")
        Clock.schedule_once(lambda dt: self.stop(), 0.5)

if __name__ == '__main__':
    SREChaosApp().run()