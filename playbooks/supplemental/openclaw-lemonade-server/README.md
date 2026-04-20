# Run OpenClaw with Lemonade Server as the backend

## Overview

[**OpenClaw**](https://openclaw.ai/) is an autonomous AI agent that can write and run code, manage files, and work through complex multi-step tasks on your behalf. Unlike a chat assistant that just answers questions, OpenClaw takes real actions on your system, which means it needs a fast, capable AI backend that can keep up with a demanding agent loop.

[**Lemonade Server**](https://lemonade-server.ai/) is that backend. It is an open-source local inference server that runs GenAI models directly on your hardware and exposes them through the industry-standard OpenAI API. Any application that speaks OpenAI can speak Lemonade — no API keys, no usage costs, and no data leaving your machine.

Together, they form a fully local AI agent stack: Lemonade handles model inference, and OpenClaw provides the agent loop that turns model outputs into real actions.

> **Before you continue:** OpenClaw is a highly autonomous AI agent. Giving any AI agent access to your system may result in unpredictable or unintended outcomes. Proceed only if you understand the risks and are comfortable with autonomous software acting on your behalf.

## What You'll Learn

By the end of this playbook you will be able to:

- **Install Lemonade Server** on Linux using the official PPA.
- **Start and verify the Lemonade daemon**
- **Explore the built-in model library** with `lemonade list`
- **Pull a model** from the catalog and **import a custom HuggingFace model** that is not in the default list.
- **Install OpenClaw** and **point it at Lemonade** as its AI backend.
- **Start the OpenClaw gateway** and confirm your agent is ready to work.
- **Connect a Discord bot** to your agent so you can chat with it from any device.

## Prerequisites

<!-- @device:halo -->
<!-- @require:lemonade -->
<!-- @device:end -->

- A PC running **Ubuntu 24.04+** or a compatible Debian-based Linux distribution with `apt-get`
- At least **12 GB of RAM** (32 GB+ recommended for larger models)
- **~10–20 GB of free disk space** for model weights

---

<!-- @device:stx,krk,rx7900xt,rx9070xt -->

## Install and Start Lemonade Server

### Why a Local Model Server?

When OpenClaw works through a task, it calls the model repeatedly, drafting a plan, checking its own output, generating code, recovering from errors. A **local server** keeps the model loaded in GPU or system memory and answers every one of those calls in milliseconds. Without it, each call would reload the model from disk, adding tens of seconds of overhead per step.

Lemonade runs as a background process and exposes an HTTP API at `http://127.0.0.1:13305/api/v1`. OpenClaw sends HTTP requests to that address.

### Install Lemonade via the PPA

Lemonade publishes a Debian PPA. Add the repository and install the package:

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:lemonade-team/bleeding-edge
sudo apt-get update
sudo apt-get install -y lemonade-server
```

This installs two key binaries:

| Binary | Role |
|--------|------|
| `lemonade` | CLI for model management: list, pull, import, configure |
| `lemond` | Daemon that hosts the HTTP inference server |

Confirm the install worked:

```bash
lemonade --version
```

### Verify the Lemonade Daemon is Running

`lemond` is managed by systemd and starts automatically when `lemonade-server` is installed — you do not need to start it manually. Check its status:

```bash
systemctl status lemond
```

You should see `Active: active (running)`. If the service shows as stopped or failed, start it with:

```bash
sudo systemctl start lemond
```

To confirm it is enabled to start automatically on every boot:

```bash
sudo systemctl enable lemond
```

### Verify the Server is Ready

Query the `/api/v1/models` endpoint to confirm the server is accepting requests:

```bash
curl -s http://127.0.0.1:13305/api/v1/models
```

You should see:

```json
{"data":[],"object":"list"}
```

This is the correct response. The empty `data` array simply means no model weights have been downloaded yet, the server itself is running and ready. If the command returns nothing, check the service status with `systemctl status lemond`.

**Congrats — Lemonade Server is live!** You now have a fully local inference server running on your machine. From here on, every model call stays on your hardware, no cloud, no API keys, no data leaving your system.

<!-- @device:end -->

---

## Managing Models

### Explore the Built-In Model Library

Lemonade ships with a curated catalog of pre-configured models.

```bash
lemonade list
```

### Pull a Model from the Catalog

Choose a model from the list and download its weights:

```bash
lemonade pull Gemma-3-4b-it-GGUF
```

Lemonade fetches the weights from HuggingFace and stores them locally. Run `lemonade list` again and the model will show `Yes` in the Downloaded column.

> **Choosing a model for agent work:** Agent tasks like those OpenClaw handles are instruction-following and multi-step reasoning problems. Larger models generally reason more reliably, but they require more RAM. A good starting point is any model in the 7–14B parameter range, which typically requires 4–8 GB of disk space in 4-bit quantization.

### Import a Custom Model from HuggingFace

The built-in catalog covers many popular models, but you can bring in other models hosted on HuggingFace using [`lemonade import`](https://lemonade-server.ai/docs/lemonade-cli/#options-for-import).

#### The import spec format

Create a JSON file that describes your model. This example uses **Qwen3.5-9B** from the `unsloth` HuggingFace org, a 9B vision and tool-calling model at around 5.7 GB in Q4_K_M quantization:

```bash
{
  "model_name": "Qwen3.5-9B-GGUF-Q4-K-M",
  "checkpoint": "unsloth/Qwen3.5-9B-GGUF:Q4_K_M",
  "mmproj": "mmproj-F32.gguf",
  "recipe": "llamacpp",
  "labels": ["vision", "tool-calling"],
  "size": 5.68
}
```

The fields:

| Field | Required | Description |
|-------|----------|-------------|
| `model_name` | Yes | Name Lemonade will use to identify this model |
| `checkpoint` | Yes | `org/repo:VARIANT`, HuggingFace repo path and a variant hint (see below) |
| `mmproj` | No | Multimodal projector filename for vision models, must live in the same HuggingFace repo as `checkpoint` |
| `recipe` | Yes | Inference backend. |
| `labels` | No | Tags for filtering: `tool-calling`, `vision`, `reasoning`, `coding`, `embeddings` |
| `size` | No | Approximate size in GB, informational only |
| `recipe_options` | No | Per-model backend settings, e.g. `{"ctx_size": 32768}` |

> **Checkpoint VARIANT format:** The part after the `:` tells Lemonade which file to fetch. Several forms are accepted:
>
> | Format | Behaviour | Example |
> |--------|-----------|---------|
> | Quantization name | Finds the single file whose name ends with that string (case-insensitive) | `unsloth/Qwen3.5-9B-GGUF:Q4_K_M` |
> | Full filename | Downloads that exact file | `unsloth/Qwen3-8B-GGUF:qwen3.gguf` |
> | Folder name | Downloads all `.gguf` files inside that folder | `unsloth/Qwen3-30B-A3B-GGUF:Q4_0` |
> | `*` | Downloads every `.gguf` file in the repo | `ggml-org/gpt-oss-120b-GGUF:*` |
> | *(omitted)* | Downloads the first `.gguf` file found | `unsloth/Qwen3-30B-A3B-GGUF` |
>

#### Register and download

`lemonade import` does both steps in one: it registers the model spec and immediately downloads the weights.

```bash
lemonade import my-model.json
```

Lemonade automatically prefixes imported models with `user.` to distinguish them from built-in catalog entries.

Verify the import and download status:

```bash
lemonade list
```

Your model appears at the bottom of the list with `Yes` in the Downloaded column once the pull completes.

**Well done! your model is ready to serve requests.**


### Configuring Context Size

For agent workloads, a larger context window lets the model keep more of the task history, tool outputs, and reasoning steps in view at once. Set this once after the server is running:

```bash
lemonade config set ctx_size=32768
```

This takes effect for newly loaded models. A context of 32 768 tokens is a reasonable floor for agent use; increase it if your model and available RAM support it.

---

## Install and Configure OpenClaw

### Install OpenClaw

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

Run OpenClaw's non-interactive onboarding, replacing `YOUR_MODEL_ID` with the model you pulled in Part 2. Use the plain name (e.g., `Gemma-3-4b-it-GGUF`) for catalog models, or the `user.` prefixed name (e.g., `user.MyModel-GGUF`) for imported ones:

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

**What each key flag does:**

| Flag | Value | Why |
|------|-------|-----|
| `--custom-base-url` | `http://127.0.0.1:13305/api/v1` | Points OpenClaw at your running Lemonade server |
| `--custom-provider-id` | `lemonade` | Names this provider in OpenClaw's config file |
| `--custom-compatibility` | `openai` | Tells OpenClaw to use the OpenAI wire protocol |
| `--custom-api-key` | `lemonade` | Lemonade does not require authentication; this is a required placeholder |
| `--gateway-port` | `18789` | The port where the OpenClaw gateway will listen |
| `--accept-risk` | — | Acknowledges that an autonomous agent can take real actions on your system |

This command writes OpenClaw's configuration to `~/.openclaw/openclaw.json`.

### Start the OpenClaw Gateway

The gateway is the OpenClaw process that manages the agent loop and serves the dashboard:

```bash
openclaw gateway run --bind loopback --port 18789
```

Open your browser and navigate to `http://127.0.0.1:18789`. You should see the OpenClaw dashboard with your Lemonade-backed model listed as the active backend. **Your agent is ready.**

<p align="center">
  <img src="https://github.com/user-attachments/assets/fcadf4de-8421-4f14-a63a-2fa5cbb7c4ec" width="500" height="300" />
</p>

**Congratulations — you've built a fully local AI agent stack from scratch.** 

---

## Connect a Discord Bot. [Reference](https://docs.openclaw.ai/channels/discord#ask-your-agent-2)

### Chat with Your Agent via Discord

Once the gateway is running, you can reach your local agent through Discord by wiring up a bot. This lets you send commands from your mobile device to your laptop and trigger workloads from anywhere.

#### Create a Discord application and bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and click **New Application**. Give it a name (e.g. "OpenClaw Agent").
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
# Stop the running gateway (Ctrl+C), then:
openclaw gateway run --bind loopback --port 18789
```

You should see `logged in to discord as <bot-id>` in the gateway output.

#### Pair your Discord account

DM the bot in Discord. It will reply with a short pairing code. Approve it on the machine running OpenClaw:

<p align="center">
  <img width="500" height="300" alt="Screenshot from 2026-04-19 22-51-27" src="https://github.com/user-attachments/assets/bbe5f4aa-d6c0-4958-9578-f2fd38cc97ef" />
</p>

```bash
openclaw pairing approve <CODE>
```

> Pairing codes expire after one hour. If the bot does not reply to your first DM, check that the gateway is running and that **Direct Messages** is enabled in your server's privacy settings.

You can now chat with your agent directly from Discord and offload tasks to your local hardware.

<p align="center">
  <img width="350" height="300" alt="image" src="https://github.com/user-attachments/assets/7d0f9632-5a1d-4f3c-81a2-d1903939f5fd" />
</p>

> **Tip — increase the model context window:** Local models often ship with a small default context limit. If the agent stops responding after a few messages, raise the limit in `~/.openclaw/openclaw.json` under `models.providers.lemonade.models[0].contextWindow` (e.g. `32768`) and restart the gateway.

---

## Next Steps

Now that your agent can receive commands from your phone and act on your local machine, here are three directions worth exploring:

1. **Stock market summarizer**: Schedule OpenClaw to fetch data from financial APIs on a fixed interval, summarize the day's movements with your local model, and push a digest to your Discord DM each morning.

2. **Fine-tuning monitor**: Kick off a training job remotely via Discord, then have the agent tail the training log and report periodic loss values, GPU utilization, and disk usage back to your phone. If the run stalls or VRAM spikes, you find out immediately without needing to be at the machine.

3. **IOT with a local VLM**: Point a camera at your front door, run a vision model on Lemonade, and have OpenClaw analyze frames on demand or on a trigger. Ask "did any packages arrive today?" from your phone and get a straight answer from your own hardware.