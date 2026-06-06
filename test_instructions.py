import subprocess
try:
    result = subprocess.run(["pre_commit_instructions"], capture_output=True, text=True, check=True)
    print(result.stdout)
except Exception as e:
    print(f"Error: {e}")
