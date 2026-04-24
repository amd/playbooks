<!--
Copyright Advanced Micro Devices, Inc.
SPDX-License-Identifier: MIT
-->
# Run OpenClaw with Lemonade Server as the backend

## Overview

[**OpenClaw**](https://openclaw.ai/) is an autonomous AI agent that can write and run code, manage files, and work through complex multi-step tasks on your behalf. Unlike a chat assistant that just answers questions, OpenClaw takes real actions on your system, which means it needs a fast, capable AI backend that can keep up with a demanding agent loop.

[**Lemonade Server**](https://lemonade-server.ai/) is that backend. It is an open-source local inference server that runs GenAI models directly on your hardware and exposes them through the industry-standard OpenAI API.

Together, they form a fully local AI agent stack: Lemonade handles model inference, and OpenClaw provides the agent loop that turns model outputs into real actions.

> **Before you continue:** OpenClaw is a highly autonomous AI agent. Giving any AI agent access to your system may result in unpredictable or unintended outcomes. Proceed only if you understand the risks and are comfortable with autonomous software acting on your behalf.

---

## What You'll Learn

By the end of this playbook you will be able to:

- Learn about **Lemonade Server**
- **Install OpenClaw** and **point it at Lemonade Server** as its AI backend.
- **Start the OpenClaw gateway** and confirm your agent is ready to work.
- **Connect a Discord bot** to your agent so you can chat with it from any device.

---

## Prerequisites

<!-- @os:linux -->
- A PC running **Ubuntu 24.04+** or a compatible Debian-based Linux distribution with `apt-get`
- At least **12 GB of RAM** (32 GB+ recommended for larger models)
- AMD recommends setting the minimum dedicated VRAM in the BIOS (0.5GB)
- Install the amd-debug-tools wheel from PyPi, and run the amd-ttm tool to reconfigure shared memory settings to **120 GB**:
```bash
amd-ttm --set 120
```
- **~10–30 GB of free disk space** for model weights
<!-- @os:end -->
<!-- @os:windows -->
- A PC running **Windows 10/11**
- Visual Studio Community Edition [2022](https://aka.ms/vs/17/release/vs_community.exe)
- At least **12 GB of RAM** (32 GB+ recommended for larger models)
- You could increase the dedicated GPU memory using [AMD Software: Adrenalin Edition™](https://www.amd.com/en/support/download/drivers.html) to try out larger models
- **~10–30 GB of free disk space** for model weights
<!-- @os:end -->

<!-- @require:lemonade -->

---

## Configuring Context Size

For agent workloads, a larger context window lets the model keep more of the task history, tool outputs, and reasoning steps in view at once. Set this once after the server is running:

```bash
lemonade config set ctx_size=190000
```

This takes effect for newly loaded models. A context of 190000 tokens is a reasonable floor for agent use; increase it if your model and available RAM support it.

---

<!-- @os:windows -->

## Set Up WSL

We run OpenClaw inside WSL (Recommended) and connect it to Lemonade running natively on Windows. This gives you a Linux shell environment for OpenClaw while keeping Lemonade's GPU acceleration on the Windows side.

### Install WSL and Ubuntu

Open PowerShell as Administrator and install the WSL kernel:

```powershell
wsl --install --no-distribution
```

Then install Ubuntu:

```powershell
wsl --install -d Ubuntu-24.04
```

### Enable systemd in WSL

Run this inside the Ubuntu terminal:

```bash
sudo tee /etc/wsl.conf > /dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Restart WSL:

```powershell
wsl --shutdown
wsl
```

### Bridge Lemonade from Windows into WSL

WSL2 runs in a virtual network. Lemonade on Windows binds to `127.0.0.1`, which WSL cannot reach directly. A Windows port proxy forwards traffic from the WSL gateway IP to Windows localhost.

**Find your WSL gateway IP** (run inside WSL):

```bash
ip route show default | awk '{print $3}' | head -1
```

**Add the port proxy** (run in PowerShell as Administrator, replacing `<WSL-Gateway-IP>` with your WSL gateway IP):

```powershell
netsh interface portproxy add v4tov4 `
  listenaddress=<WSL-Gateway-IP> listenport=13305 `
  connectaddress=127.0.0.1 connectport=13305
```

**Add a firewall rule** (same elevated PowerShell):

```powershell
New-NetFirewallRule -DisplayName "Lemonade-WSL" -Direction Inbound -Protocol TCP -LocalPort 13305 -Action Allow
```

**Verify from WSL**:

```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)
curl -s "http://$WINDOWS_HOST:13305/api/v1/models"
```

You should see:

```json
{"data":[],"object":"list"}
```

The empty `data` array simply means no model weights have been downloaded yet, the server itself is running and ready.

> The `netsh portproxy` rule survives reboots but the WSL gateway IP can change after `wsl --shutdown`. If Lemonade becomes unreachable from WSL after a restart, get the updated gateway IP and update the proxy with this new IP.

---
<!-- @os:end -->

## Install and Configure OpenClaw

### Install OpenClaw
<!-- @os:windows -->
> Run the commands in this section inside your **WSL terminal**.
<!-- @os:end -->
```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

The `--no-onboard` flag skips the interactive setup wizard, you will configure the model backend manually in the next step, which gives you precise control over which model and server are used.

After installation, confirm `openclaw` is on your `PATH`:

```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```

To persist this across terminal sessions:

```bash
echo 'export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Configure OpenClaw to Use Lemonade

Run OpenClaw's non-interactive onboarding, replacing `YOUR_MODEL_ID` with your Lemonade Model ID. Use the plain name (e.g., `Qwen3.5-35B-A3B-GGUF`) for catalog models, or the `user.` prefixed name (e.g., `user.Qwen3.6-35B-A3B-UD-Q4_K_M`) for custom imported ones:
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "YOUR_MODEL_ID" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->
<!-- @os:windows -->
```bash
WINDOWS_HOST=$(ip route show default | awk '{print $3}' | head -1)

openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://$WINDOWS_HOST:13305/api/v1" \
  --custom-model-id "YOUR_MODEL_ID" \
  --custom-provider-id "lemonade" \
  --custom-compatibility "openai" \
  --custom-api-key "lemonade" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-health \
  --accept-risk
```
<!-- @os:end -->

This command writes OpenClaw's configuration to `~/.openclaw/openclaw.json`.

### Start the OpenClaw Gateway

The gateway is the OpenClaw process that manages the agent loop and serves the dashboard:

```bash
openclaw gateway run --bind loopback --port 18789
```

To open the dashboard, run this in a second terminal while the gateway is still running:

```bash
openclaw dashboard
```

This prints the authenticated URL, open it in your browser. You should see the OpenClaw dashboard with your Lemonade model listed as the active backend. **Your agent is ready.**

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

**Congratulations — you've built a fully local AI agent stack from scratch.** 

---

## Optional: Connect a Discord Bot to your Openclaw. [Reference](https://docs.openclaw.ai/channels/discord#ask-your-agent-2)

### Chat with Your Agent via Discord

Once the gateway is running, you can reach your local agent through Discord by wiring up a bot. This lets you send commands from your mobile device to your laptop and trigger workloads from anywhere.

#### Create a Discord application and bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**. Give it a name (e.g. "openclaw-bot").
2. In the sidebar, click **Bot**. Set a username for the bot.
3. Still on the Bot page, scroll to **Privileged Gateway Intents** and enable:
   - **Message Content Intent** (required)
4. Scroll back up and click **Reset Token** to generate your bot token. Copy it.

#### Add the bot to your server

1. In the sidebar, click **OAuth2/ URL Generator**.
2. Under **Scopes**, enable `bot` and `applications.commands`.
3. Under **Bot Permissions**, enable: View Channels, Send Messages, Read Message History, Embed Links, Attach Files.
4. Copy the generated URL, paste it in your browser, select your server, and confirm. The bot should now appear in your server's member list.

#### Collect your IDs

Enable Developer Mode in Discord (**User Settings/ Advanced/ Developer Mode**), then:
- Right-click your server icon: **Copy Server ID**
- Right-click your own avatar: **Copy User ID**

#### Allow DMs from server members

Right-click your server icon/ **Privacy Settings**/ toggle on **Direct Messages**. This allows the bot to DM you, which is required for the pairing step.

#### Set the bot token and enable Discord in OpenClaw

Your bot token is a secret, store it as an environment variable and reference it from config:

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
openclaw config set channels.discord.token \
  --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN
openclaw config set channels.discord.enabled true --strict-json
```

Restart the gateway so it picks up the new channel config:

```bash
openclaw gateway run --bind loopback --port 18789
```

You should see `logged in to discord as <bot-id>` in the gateway output.

#### Configure Openclaw with the Server details

Open your Openclaw Dashboard and send this message in the chat window replacing `<user_id>` and `<server_id>` with the IDs collected earlier

```bash
I already set my Discord bot token in config. Please finish Discord setup with User ID <user_id> and Server ID <server_id>.
```

#### Pair your Discord account

DM the bot in Discord. It will reply with a short pairing code.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approve it on the machine running OpenClaw Dashboard
```bash
openclaw pairing approve <CODE>
```

> Pairing codes expire after one hour.

You can now chat with your agent directly from Discord and offload tasks to your local hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

## Next Steps

Now that your agent can receive commands from your phone and act on your local machine, here are three directions worth exploring:

1. **Stock market summarizer**: Schedule OpenClaw to fetch data from financial APIs on a fixed interval, summarize the day's movements with your local model, and push a digest to your Discord DM each morning.

2. **Fine-tuning monitor**: Kick off a training job remotely via Discord, then have the agent tail the training log and report periodic loss values, GPU utilization, and disk usage back to your phone. If the run stalls or VRAM spikes, you find out immediately without needing to be at the machine.

3. **IOT with a local VLM**: Point a camera at your front door, run a vision model on Lemonade, and have OpenClaw analyze frames on demand or on a trigger. Ask "did any packages arrive today?" from your phone and get a straight answer from your own hardware.
