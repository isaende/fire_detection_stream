
import psutil
import os

class HardwareMonitor:
    def get_ram_usage(self):
        """
        Returns the current RAM usage in GB and percentage.
        """
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        return used_gb, total_gb, mem.percent

    # ... restante do código

    def get_temperature(self):
        """
       Reads the CPU temperature from the system's thermal sensors.
        """
        # Default path for Linux systems (Raspberry Pi, etc.)
        thermal_path = "/sys/class/thermal/thermal_zone0/temp"
        
        try:
            if os.path.exists(thermal_path):
                with open(thermal_path, "r") as f:
                    #Value is in millidegrees Celsius, so divide by 1000 to get degrees Celsius
                    temp_c = int(f.read().strip()) / 1000.0
                    return temp_c
            return 0.0
        except Exception:
            # Return 0.0 if temperature reading fails or the system is windows
            return 0.0