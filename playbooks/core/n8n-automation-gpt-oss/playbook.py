import subprocess
import sys
import os
import webbrowser
import time
import shutil
import requests
import json

# --- ENVIRONMENT/INSTALL CONFIG ---
ENV_NAME = "n8n_automation_env"
NODEJS_VERSION = "24"
N8N_VERSION = "2.6.3"
LEMONADE_MODEL_NAME = "gpt-oss-120b-mxfp-GGUF"
LEMONADE_SERVER_PORT = 8000

# --- n8n API TEST CONFIG ---
N8N_HOST = "http://localhost:5678"
N8N_API = f"{N8N_HOST}/rest"
USERNAME = "rradjabi@amd.com"
PASSWORD = "Fr1no321!"
# FIRSTNAME = "Ryan"
# LASTNAME = "R"
WORKFLOW_FILE = "assets/financial-news-workflow.json"
LEMONADE_BASE_URL = f"http://localhost:{LEMONADE_SERVER_PORT}/api/v1"
LEMONADE_API_KEY = "lemonade"
LEMONADE_NODE_TYPE = "n8n-nodes-base.lemonadeChatModelApi"  # may vary, see below

session = requests.Session()

########## ENVIRONMENT AND SERVER LAUNCH ##########
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


########## n8n WORKFLOW/API AUTOMATION ##########

def login_or_register():
    login_payload = {"email": USERNAME, "password": PASSWORD}
    login = session.post(f"{N8N_API}/login", json=login_payload)
    if login.status_code == 200:
        print("[n8n API] Logged in to n8n")
        return
    # Try registration
    reg_payload = {"email": USERNAME, "password": PASSWORD, "firstName": FIRSTNAME, "lastName": LASTNAME}
    reg = session.post(f"{N8N_API}/register", json=reg_payload)
    if reg.status_code not in (200, 409):  # 409: already exists
        print(f"[API ERROR] Registration failed: {reg.text}")
        sys.exit(1)
    print("[n8n API] Registered new n8n user (or exists)")
    # Try login again
    login = session.post(f"{N8N_API}/login", json=login_payload)
    if login.status_code == 200:
        print("[n8n API] Logged in as test user.")
    else:
        print(f"[n8n API ERROR] Login failed after registration: {login.text}")
        sys.exit(1)

def login_or_abort():
    login_payload = {"emailOrLdapLoginId": USERNAME, "password": PASSWORD}
    login = session.post(f"{N8N_API}/login", json=login_payload)
    if login.status_code == 200:
        print("[n8n API] Logged in to n8n")
        return
    else:
        print(f"[API ERROR] Login failed (user likely not pre-created or password wrong): {login.text}")
        sys.exit(1)

def import_workflow_old():
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        wf_content = f.read()
    resp = session.post(f"{N8N_API}/workflows/import", files={'file': ('assets/financial-news-workflow.json', wf_content)})
    if resp.status_code != 200:
        print(f"[API ERROR] Workflow import failed: {resp.status_code}: {resp.text}")
        sys.exit(1)
    wfid = resp.json()['id']
    print(f"[API] Workflow imported with ID: {wfid}")
    return wfid

def import_workflow():
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    resp = session.post(f"{N8N_API}/workflows", json=workflow)
    if resp.status_code not in (200, 201):
        print(f"[API ERROR] Workflow create failed: {resp.status_code}: {resp.text}")
        sys.exit(1)
    wfid = resp.json()['id']
    print(f"[API] Workflow created with ID: {wfid}")
    return wfid

def fetch_workflow(workflow_id):
    resp = session.get(f"{N8N_API}/workflows/{workflow_id}")
    resp.raise_for_status()
    return resp.json()

def get_lemonade_nodes(workflow):
    nodes = []
    for node in workflow.get('nodes', []):
        if "lemonade" in node['type'].lower():
            nodes.append(node)
    return nodes

def create_lemonade_credential():
    cred_payload = {
        "name": "lemonade-cred-ci",
        "type": "lemonadeChatModelApi",
        "data": {
            "baseUrl": LEMONADE_BASE_URL, "apiKey": LEMONADE_API_KEY
        }
    }
    resp = session.post(f"{N8N_API}/credentials", json=cred_payload)
    if resp.status_code == 409:
        creds = session.get(f"{N8N_API}/credentials").json()
        cred = [c for c in creds if c["name"] == "lemonade-cred-ci"]
        if cred:
            print(f"[API] Reusing existing Lemonade credential id={cred[0]['id']}")
            return cred[0]['id']
        else:
            print("[API ERROR] Credential name conflict but not found.")
            sys.exit(1)
    elif resp.status_code != 200:
        print(f"[API ERROR] Could not create Lemonade credential: {resp.status_code}: {resp.text}")
        sys.exit(1)
    cid = resp.json()['id']
    print(f"[API] Lemonade credential created: {cid}")
    return cid

def update_workflow_with_creds(wf_id, workflow, lemonade_nodes, cred_id):
    modified = False
    for node in lemonade_nodes:
        cred_type = node['type'].split('.')[-1] if '.' in node['type'] else node['type']
        node['credentials'] = {cred_type: {"id": cred_id}}
        modified = True
    if not modified:
        print("[API ERROR] No Lemonade nodes updated!")
        sys.exit(1)
    resp = session.patch(f"{N8N_API}/workflows/{wf_id}", json={"nodes": workflow['nodes']})
    if resp.status_code != 200:
        print(f"[API ERROR] Could not update workflow with creds: {resp.status_code}: {resp.text}")
        sys.exit(1)
    print("[API] Workflow updated to use Lemonade credentials.")

def execute_workflow(wf_id, max_wait=60):
    print("[API] Triggering workflow execution ...")
    resp = session.post(f"{N8N_API}/workflows/{wf_id}/run")
    if resp.status_code != 200:
        print(f"[API ERROR] Failed to trigger workflow: {resp.status_code}: {resp.text}")
        sys.exit(1)
    run_id = resp.json().get("id")
    if not run_id:
        print(f"[API ERROR] Run ID not found in response: {resp.text}")
        sys.exit(1)
    for _ in range(max_wait):
        time.sleep(2)
        rep = session.get(f"{N8N_API}/executions/{run_id}")
        if rep.status_code == 200:
            exe = rep.json()
            if exe.get("finished", False):
                print("[API] Workflow execution finished.")
                return exe
            else:
                print("[API] Workflow still running...")
        elif rep.status_code == 404:
            continue
        else:
            print(f"[API ERROR] Execution fetch failed: {rep.status_code} | {rep.text}")
            sys.exit(1)
    print("[API ERROR] Timeout waiting for workflow to finish.")
    sys.exit(1)

def print_output_summary(execution):
    print("\n===== Workflow Execution Output =====")
    try:
        for nd, exec_data in execution['data']['resultData']['runData'].items():
            print(f"\n--- Node: {nd} ---")
            for item in exec_data:
                print(json.dumps(item, indent=2))
    except Exception as e:
        print("Could not extract execution output:", e)

########## MAIN SEQUENCE ##########

# def print_manual_steps():
#     print("""
# ⚡ n8n server is ready in your browser!
# ⦿ In n8n: Sign up or log in if prompted.
# ⦿ Import your workflow:
#     1. Click "...", then "Import from file"
#     2. Select financial-news-workflow.json you just downloaded
    
# ⦿ Configure Lemonade credentials:
#     - Double-click the 'Lemonade Chat Model' node
#     - For Base URL:      http://localhost:8000/api/v1
#     - For API Key:       lemonade
#     - Click Save
# ⦿ Make sure Lemonade is running a model!
# ⦿ Click "Execute workflow" to generate the AI financial news summary.
# """)

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

    # 4. Open browser
    # open_n8n_web_ui()

    # n8n API automation
    # login_or_register()
    login_or_abort()
    wf_id = import_workflow()
    workflow = fetch_workflow(wf_id)
    lemonade_nodes = get_lemonade_nodes(workflow)
    if not lemonade_nodes:
        print("[ERROR] No Lemonade Chat Model node found in workflow!")
        sys.exit(1)
    cred_id = create_lemonade_credential()
    update_workflow_with_creds(wf_id, workflow, lemonade_nodes, cred_id)
    execution = execute_workflow(wf_id)
    # print_output_summary(execution)


if __name__ == "__main__":
    main()