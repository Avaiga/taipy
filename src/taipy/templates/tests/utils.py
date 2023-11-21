import subprocess
import sys


def _run_template(main_path, time_out=30):
    """Run the templates on a subprocess and get stdout after timeout"""
    with subprocess.Popen([sys.executable, main_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=time_out)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()

    # Print the eror if there is any (for debugging)
    if stderr := str(stderr, "utf-8"):
        print(stderr)

    return stdout
