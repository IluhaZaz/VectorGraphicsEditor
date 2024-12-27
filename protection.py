import os

import wmi

from json import load


base_dir = os.path.dirname(os.path.abspath("window.py"))
data_file_path = os.path.join(base_dir, "_internal", "protect.json")
with open(data_file_path, 'r') as f:
    true_data = load(f)

def check():
    c = wmi.WMI()

    for disk in c.Win32_DiskDrive():
        if "USB" in disk.InterfaceType:

            disk_data = [disk.SerialNumber, disk.Model, disk.Size]

            for data1, data2 in zip(disk_data, true_data.values()):
                if data1 != data2:
                    return False
            return True
    return False
