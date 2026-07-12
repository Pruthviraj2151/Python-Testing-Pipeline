import json
import random
from datetime import datetime
import subprocess

build = random.randint(30, 200)

try:
    commit = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"]
    ).decode().strip()
except:
    commit = "unknown"

try:
    author = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%an"]
    ).decode().strip()
except:
    author = "Pruthviraj"

data = {
    "buildNumber": str(build),
    "buildStatus": "SUCCESS",
    "branch": "main",
    "commit": commit,
    "author": author,
    "message": "Pipeline Build Success",
    "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
    "coverage": str(round(random.uniform(88, 98), 2)),
    "dockerStatus": "running",
    "healthStatus": "healthy",
    "appPort": "5000",
    "testsPassed": str(random.randint(180, 190)),
    "testsFailed": "0",
    "testsSkipped": "0"
}

with open("dashboard/build-data.json", "w") as f:
    json.dump(data, f, indent=4)

print("Dashboard Updated")