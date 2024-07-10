from horse_logic.logfiles import Logs
from pathlib import Path

path_logfiles = "data/results/data_17Jan2020_email_hillydale_equine"

assert Path(path_logfiles).exists()

logs = Logs(path=path_logfiles, patterns=["*_test*.log", "*freckle*.log"], include=False)

print(logs)

print(logs.logfiles)


print(f"Included logfiles: {len(logs.included_files)}")
print(f"Excluded logfiles: {len(logs.excluded_files)}")
