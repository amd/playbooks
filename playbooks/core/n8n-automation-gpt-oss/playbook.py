
## Prerequisites

## Install Lemonade

## Launch Lemonade

import subprocess
import sys
import os
import webbrowser
import time
import shutil

ENV_NAME = "n8n_automation_env"
LEMONADE_SERVER_PORT = 8000
LEMONADE_MODEL_NAME = "gpt-oss-120b-mxfp-GGUF"
LEMONADE_CLI = "lemonade-server"  # Must be installed in the conda env

def conda_env_exists(env_name):
    try:
        result = subprocess.check_output(['conda', 'env', 'list']).decode()
        return any(line.startswith(env_name) or f"{os.sep}{env_name}" in line for line in result.splitlines())
    except Exception:
        print("Could not check for Conda environment. Is Conda installed?")
        sys.exit(1)

def create_conda_env(env_name):
    print(f"Creating conda environment '{env_name}' with python=3.11...")
    subprocess.check_call(['conda', 'create', '-n', env_name, 'python=3.11', '-y'])

def conda_install_nodejs(env_name):
    print(f"Installing nodejs=24 from conda-forge in '{env_name}'...")
    subprocess.check_call([
        'conda', 'install', '-n', env_name, '-c', 'conda-forge', 'nodejs=24', '-y'
    ])

def npm_install_n8n(env_name):
    print("Installing n8n@2.6.3 via npm globally in conda environment...")
    if os.name == 'nt':
        activate_cmd = f'conda activate {env_name} && npm install -g n8n@2.6.3'
        subprocess.check_call(activate_cmd, shell=True)
    else:
        bash_cmd = f'source $(conda info --base)/etc/profile.d/conda.sh && conda activate {env_name} && npm install -g n8n@2.6.3'
        subprocess.check_call(bash_cmd, executable='/bin/bash', shell=True)

def start_n8n_in_env(env_name):
    print('Starting n8n in the background (from conda environment)...')
    if os.name == 'nt':
        activate_cmd = f'conda activate {env_name} && n8n start'
        proc = subprocess.Popen(activate_cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        bash_cmd = f'source $(conda info --base)/etc/profile.d/conda.sh && conda activate {env_name} && nohup n8n start >/dev/null 2>&1 &'
        proc = subprocess.Popen(bash_cmd, executable='/bin/bash', shell=True)
    time.sleep(7)  # Give n8n time to boot

def open_n8n_web_ui():
    url = 'http://localhost:5678'
    print(f'Opening n8n editor at {url}')
    webbrowser.open(url)

def download_workflow_json():
    import requests
    WORKFLOW_URL = 'https://github.com/amd/halo_playbooks/raw/d277fc8d96fd1067555c1c1d63c2dd260a0188fc/playbooks/core/n8n-automation-gpt-oss/assets/financial-news-workflow.json'
    LOCAL_FILE = 'financial-news-workflow.json'
    print('Downloading workflow JSON...')
    r = requests.get(WORKFLOW_URL)
    if r.status_code == 200:
        with open(LOCAL_FILE, 'wb') as f:
            f.write(r.content)
        print('Downloaded:', LOCAL_FILE)
    else:
        print('Failed to download workflow JSON. Please download manually from:\n', WORKFLOW_URL)

def ensure_lemonade_installed(env_name):
    print("Checking if lemonade-server is installed...")
    if os.name == 'nt':
        activate_cmd = f'conda activate {env_name} && lemonade-server -v'
        result = subprocess.run(
            ["cmd.exe", "/c", activate_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    else:
        bash_cmd = (
            f'source $(conda info --base)/etc/profile.d/conda.sh && '
            f'conda activate {env_name} && '
            f'lemonade-server -v'
        )
        result = subprocess.run(bash_cmd, executable='/bin/bash', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("lemonade-server is not installed or not found in PATH of conda environment.")
        sys.exit(1)
    print("lemonade-server found:", result.stdout.strip() or result.stderr.strip())

def pull_lemonade_model(env_name, model_name):
    print(f"Pulling Lemonade model '{model_name}' (this may take several minutes)...")
    if os.name == 'nt':
        activate_cmd = f'conda activate {env_name} && lemonade-server pull {model_name}'
        process = subprocess.Popen(
            ["cmd.exe", "/c", activate_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
    else:
        bash_cmd = (
            f'source $(conda info --base)/etc/profile.d/conda.sh && '
            f'conda activate {env_name} && '
            f'lemonade-server pull {model_name}'
        )
        process = subprocess.Popen(bash_cmd, executable='/bin/bash', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode != 0:
        print(f"Error: Lemonade model pull failed (exit code {process.returncode})")
        sys.exit(1)
    print(f"Model '{model_name}' is now available.")

def launch_lemonade_server(env_name, model_name, host="127.0.0.1", port=8000):
    print(f"Launching lemonade-server on {host}:{port} with model {model_name} ...")
    if os.name == 'nt':
        serve_cmd = f'conda activate {env_name} && lemonade-server serve --host {host} --port {port} --model {model_name}'
        subprocess.Popen(
            ["powershell", "-Command", f"Start-Process cmd -ArgumentList '/c {serve_cmd}'"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        bash_cmd = (
            f'source $(conda info --base)/etc/profile.d/conda.sh && '
            f'conda activate {env_name} && '
            f'nohup lemonade-server serve --host {host} --port {port} --model {model_name} '
            '> lemonade-server.log 2>&1 &'
        )
        subprocess.Popen(bash_cmd, executable='/bin/bash', shell=True)
    time.sleep(8)

def print_manual_steps():
    print("""
⚡ n8n server is ready in your browser!
⦿ In n8n: Sign up or log in if prompted.
⦿ Import your workflow:
    1. Click "...", then "Import from file"
    2. Select financial-news-workflow.json you just downloaded
    
⦿ Configure Lemonade credentials:
    - Double-click the 'Lemonade Chat Model' node
    - For Base URL:      http://localhost:8000/api/v1
    - For API Key:       lemonade
    - Click Save
⦿ Make sure Lemonade is running a model!
⦿ Click "Execute workflow" to generate the AI financial news summary.
""")

def main():
    print("=== n8n AI Financial News Summarizer Setup (with Conda) ===")

    # 1. Create and set up conda env if needed
    if not shutil.which("conda"):
        print("Error: Conda not found on PATH. Please install Miniconda/Anaconda and try again.")
        sys.exit(1)

    if not conda_env_exists(ENV_NAME):
        create_conda_env(ENV_NAME)
    else:
        print(f"Conda environment '{ENV_NAME}' already exists.")
    
    conda_install_nodejs(ENV_NAME)
    npm_install_n8n(ENV_NAME)

    ensure_lemonade_installed(ENV_NAME)
    pull_lemonade_model(ENV_NAME, LEMONADE_MODEL_NAME)
    launch_lemonade_server(ENV_NAME, LEMONADE_MODEL_NAME, host="127.0.0.1", port=LEMONADE_SERVER_PORT)

    # 2. Start n8n from environment
    start_n8n_in_env(ENV_NAME)

    # 3. Download workflow file (to current dir)
    download_workflow_json()

    # 4. Open browser
    open_n8n_web_ui()

    print_manual_steps()

if __name__ == "__main__":
    main()