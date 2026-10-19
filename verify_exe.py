import os
import subprocess
import sys
import time
from pathlib import Path

exe_path = Path("dist/TWSNameChanger.exe").resolve()
print(f"Testing executable: {exe_path}")
if not exe_path.exists():
    print("ERROR: Executable does not exist!")
    sys.exit(1)

size_mb = exe_path.stat().st_size / (1024 * 1024)
print(f"File size: {size_mb:.2f} MB ({exe_path.stat().st_size} bytes)")

# Check log before
local_app = os.environ.get("LOCALAPPDATA", "")
log_file = Path(local_app) / "TWSNameChanger" / "tws_name_changer.log"
print(f"Expected log path: {log_file}")

proc = subprocess.Popen([str(exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"Launched process PID: {proc.pid}")

# Wait for process initialization
time.sleep(5)

ret = proc.poll()
if ret is not None:
    stdout, stderr = proc.communicate()
    print(f"ERROR: Process exited prematurely with code {ret}")
    print("Stdout:", stdout.decode(errors="replace"))
    print("Stderr:", stderr.decode(errors="replace"))
    sys.exit(1)
else:
    print(f"SUCCESS: Process PID {proc.pid} is running stably without crashing!")

# Terminate process cleanly
proc.terminate()
try:
    proc.wait(timeout=3)
except subprocess.TimeoutExpired:
    proc.kill()

print("Process terminated cleanly.")
if log_file.exists():
    print("Log file content:")
    print(log_file.read_text(encoding="utf-8"))
else:
    print("Note: Log file not yet written or created.")
