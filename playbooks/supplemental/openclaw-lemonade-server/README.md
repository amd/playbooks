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
- **Connect a communication channel** (Discord or Telegram) so you can chat with your agent from any device.

---

## Prerequisites

<!-- @os:linux -->
- A PC running **Ubuntu 24.04+** or a compatible Debian-based Linux distribution with `apt-get`
- At least **24 GB of RAM** (64 GB+ recommended for larger models)
- Depending on the size of the model you're running, set the minimum possible dedicated VRAM in the BIOS.
- Next, install the amd-debug-tools wheel from PyPI, and run the amd-ttm tool to reconfigure shared memory settings to the maximum:
```bash
  sudo apt install pipx
  pipx ensurepath
  pipx install amd-debug-tools
  amd-ttm --set 96 # Strix Halos can be set to 96GB. Set the shared memory value for other devices accordingly.
```
- **~10–30 GB of free disk space** for model weights
<!-- @os:end -->
<!-- @os:windows -->
- A PC running **Windows 10/11**
- Visual Studio Community Edition [2022](https://aka.ms/vs/17/release/vs_community.exe)
- At least **24 GB of RAM** (64 GB+ recommended for larger models)
- You could increase the dedicated GPU memory using [AMD Software: Adrenalin Edition™](https://www.amd.com/en/support/download/drivers.html) to try out larger models
- **~10–30 GB of free disk space** for model weights
<!-- @os:end -->

<!-- @require:lemonade -->

---

## Pull and Load the Recommended Model

The recommended model for this playbook is **Qwen3.6-35B-A3B-GGUF**, a strong MoE model with a 263k-token context window that is well-suited to agent workloads. Pull it now:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

Then load it with a large context window and save that setting for future runs:

```bash
lemonade load Qwen3.6-35B-A3B-GGUF --ctx-size 190000 --save-options
```

A context of 190,000 tokens is a safe working floor for agent use on this model. Increase it if your available RAM allows.

> **Tip: Disable thinking for faster agent responses:** Qwen3.6-35B-A3B runs in thinking mode by default, which adds latency before each response. For agent loops this overhead accumulates quickly. The [lemonade-sdk/recipes](https://github.com/lemonade-sdk/recipes/blob/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json) repo provides a ready-made config that disables thinking. To use it, download the file and import it:
>
> ```bash
> curl -LO https://raw.githubusercontent.com/lemonade-sdk/recipes/main/coding-agents/Qwen3.6-35B-A3B-NoThinking.json
> lemonade import Qwen3.6-35B-A3B-NoThinking.json
> ```
>
> This registers the model as `user.Qwen3.6-35B-A3B-NoThinking`. If you use this variant, replace `Qwen3.6-35B-A3B-GGUF` with `user.Qwen3.6-35B-A3B-NoThinking` in the OpenClaw onboard command below.

> **OpenClaw context window sizing:** OpenClaw's compaction triggers when `contextTokens > contextWindow − reserveTokens`. The default `reserveTokensFloor` is 20,000 tokens, a floor that overrides `reserveTokens` when lower, so any model context below ~37k will trigger an infinite compaction loop. Set a low reserve and disable the floor once in your config and it applies to every model, no per-model tuning needed:
>
> ```json
> "compaction": {
>   "reserveTokens": 4096,
>   "reserveTokensFloor": 0
> }
> ```
>
> `reserveTokensFloor` is a *floor* (minimum guard), not the reserve itself, setting only the floor has no effect. `reserveTokensFloor: 0` disables the guard so the lower `reserveTokens` is accepted.
>
> **When to apply this:** Use this config if your model's effective context window is below ~37k, either because the model is small (e.g. 8k, 16k, 32k) or because you've intentionally capped it to a lower value (e.g. loading a 128k model but setting context to 16k in Lemonade). Without it, OpenClaw enters an infinite compaction loop on startup.
>
> **Large-context models at full context:** You can skip this entirely. The defaults work fine, compaction will kick in well before the window fills and the model has ample room to generate long responses. If you do apply it, be aware that `reserveTokens: 4096` limits response length to ~4k tokens, which may cut off long file generation or detailed plans.
>
> **Where to add this:** Place the `compaction` block inside `agents.defaults` in your `openclaw.json` (usually at `~/.openclaw/openclaw.json`):
>
> ```json
> {
>   "agents": {
>     "defaults": {
>       "workspace": "/home/<you>/.openclaw/workspace",
>       "model": {
>         "primary": "lemonade/<your-model-id>"
>       },
>       "compaction": {
>         "reserveTokens": 4096,
>         "reserveTokensFloor": 0
>       }
>     }
>   }
> }
> ```
>
> The rest of your config (gateway, channels, models, etc.) stays unchanged, only the `compaction` key needs to be added.

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

Open a new terminal and confirm the installation:

```bash
openclaw --version
```

### Configure OpenClaw to Use Lemonade

Run OpenClaw's non-interactive onboarding.
<!-- @os:linux -->
```bash
openclaw onboard \
  --non-interactive \
  --mode local \
  --auth-choice custom-api-key \
  --custom-base-url "http://127.0.0.1:13305/api/v1" \
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
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
  --custom-model-id "Qwen3.6-35B-A3B-GGUF" \
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

<!-- @os:linux -->
### (Recommended) Enable Docker Sandboxing

OpenClaw can route all agent file and code operations through an isolated Docker container rather than running them directly on your host. This limits the blast radius of any unintended action to the sandbox, leaving your host filesystem and network untouched.

Build the sandbox image once (Docker must be installed):

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

Add the following `sandbox` key inside the existing `agents.defaults` block in `~/.openclaw/openclaw.json`:

```json
"agents": {
  "defaults": {
    "workspace": "...",
    "model": { ... },
    "sandbox": {
      "mode": "non-main",
      "scope": "session",
      "workspaceAccess": "none"
    }
  }
}
```

Sandbox containers have **no network access** by default. See the [sandboxing reference](https://docs.openclaw.ai/gateway/sandboxing) for bind mounts and network overrides.

> To verify sandboxing is active, ask the agent to `run hostname` from the dashboard. If you see a short container ID instead of your machine's hostname, the sandbox is working.

<!-- @os:end -->
### Start the OpenClaw Gateway

The gateway is the OpenClaw process that manages the agent loop and serves the dashboard:

```bash
openclaw gateway run --bind loopback --port 18789
```

To open the dashboard, run this in a second terminal while the gateway is still running:

```bash
openclaw dashboard
```

Because the gateway binds to loopback, the dashboard auto-authenticates when opened from the same machine, no token entry or device approval is needed for local access. You should see the OpenClaw dashboard with your Lemonade model listed as the active backend.

**Congratulations, you've built a fully local AI agent stack from scratch.**

> **Need the gateway token?** Run `openclaw dashboard --no-open` to print the dashboard URL with the token embedded (it also attempts to copy it to your clipboard). Alternatively, the token is at `gateway.auth.token` in `~/.openclaw/openclaw.json`.
>
> **Approving a remote device:** When you open the dashboard from a second machine or phone, the browser displays a request ID. Back on the machine running the gateway, run:
> ```bash
> openclaw devices approve <requestId>
> ```
> This is only needed for remote or secondary devices, loopback access from the same machine auto-authenticates.

<p align="center">
  <img src="assets/openclaw_dashboard.png" width="500" height="300" />
</p>

---

## Optional: Connect a Communication Channel

Once the gateway is running you can reach your local agent from any device. Pick the option that fits your setup. OpenClaw supports [Discord](https://docs.openclaw.ai/channels/discord), [Telegram](https://docs.openclaw.ai/channels/telegram), and other channels, see the full list at [docs.openclaw.ai](https://docs.openclaw.ai).

---

### Option A: Discord

Discord requires a server where **you have administrator access** to add a bot. If you share servers but don't own one, use Option B (Telegram) instead.

#### Create a Discord account and server

If you do not have a Discord account, sign up at [discord.com](https://discord.com). You also need a server where you are administrator, create one by clicking the **+** icon in the Discord sidebar and selecting **Create My Own**. A private server is fine.

#### Create a Discord application and bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**. Give it a name (e.g. "openclaw-bot").
2. In the sidebar, click **Bot**. Set a username for the bot.
3. Still on the Bot page, scroll to **Privileged Gateway Intents** and enable:
   - **Message Content Intent** (required)
   - **Server Members Intent** (recommended)
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

#### Configure OpenClaw for Discord

Store your bot token as an environment variable, then create a single patch file that enables Discord, references the token, and allowlists your server. Replace `<server_id>` and `<user_id>` with the IDs collected above.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"

cat > discord.patch.json5 <<JSON5
{
  channels: {
    discord: {
      enabled: true,
      token: { source: "env", provider: "default", id: "DISCORD_BOT_TOKEN" },
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      guilds: {
        "<server_id>": {
          requireMention: false,
          users: ["<user_id>"],
        },
      },
    },
  },
}
JSON5
openclaw config patch --file ./discord.patch.json5
```

> **Do not rely on asking the agent to configure this.** When sandboxing is enabled, the agent cannot write to `~/.openclaw/openclaw.json` from inside the sandbox, use the CLI commands above on the host instead.

Restart the gateway so it picks up the new channel config:

```bash
openclaw gateway run --bind loopback --port 18789
```

You should see `logged in to discord as <bot-name>` in the gateway output within a few seconds.

#### Pair your Discord account

DM the bot in Discord. It will reply with a short pairing code.

<p align="center">
  <img width="400" height="400" src="assets/discord_pair_code.png" />
</p>

Approve it on the machine running OpenClaw:
```bash
openclaw pairing approve discord <CODE>
```

> Pairing codes expire after one hour.

You can now chat with your agent directly from Discord and offload tasks to your local hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="assets/discord_bot.png" />
</p>

---

### Option B: Telegram

Telegram is simpler than Discord for most users, it requires no server and no admin access.

#### Create a Telegram bot

1. Open Telegram and message **@BotFather**.
2. Send `/newbot` and follow the prompts. Save the bot token it gives you.

#### Configure OpenClaw for Telegram

Store the token as an environment variable:

```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

Add the channel configuration to `~/.openclaw/openclaw.json` (or patch it via the dashboard):

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "YOUR_BOT_TOKEN",
      "dmPolicy": "pairing"
    }
  }
}
```

Restart the gateway, then send your bot any message in Telegram. Approve the pairing:

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Pairing codes expire after one hour. You can now chat with your agent via Telegram DM.

---

## Next Steps

Now that your agent can receive commands from your phone and act on your local machine, here are three directions worth exploring:

1. **Stock market summarizer**: Schedule OpenClaw to fetch data from financial APIs on a fixed interval, summarize the day's movements with your local model, and push a digest to your phone each morning via your chosen channel.

2. **Fine-tuning monitor**: Kick off a training job remotely via Telegram or Discord, then have the agent tail the training log and report periodic loss values, GPU utilization, and disk usage back to your phone. If the run stalls or VRAM spikes, you find out immediately without needing to be at the machine.

3. **IOT with a local VLM**: Point a camera at your front door, run a vision model on Lemonade, and have OpenClaw analyze frames on demand or on a trigger. Ask "did any packages arrive today?" from your phone and get a straight answer from your own hardware.
