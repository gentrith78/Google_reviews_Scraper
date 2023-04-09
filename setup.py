import subprocess

# Install all dependencies using pip
subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])

# Check if playwright is installed
try:
    import playwright
except ImportError:
    # Install playwright if it is not installed
    subprocess.check_call(['npx', 'playwright', 'install'])