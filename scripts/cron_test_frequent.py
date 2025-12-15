#!/usr/bin/env python3
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[{timestamp}] Test cron job executed")

with open("/var/log/cron_test.log", "a") as f:
    f.write(f"{timestamp} | TEST | Cron job executed\n")