<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Overview

**Tailscale** is a free service that creates secure, private tunnels between your devices. It lets you reach a machine that isn't exposed to the internet — for example, an AMD system sitting on your home network — from anywhere else, like your laptop on coffee shop Wi-Fi.

This matters for local AI work. Your models, workflows, and datasets live on the machine with the GPU, but you aren't always sitting in front of it. Tailscale lets you leave a model server running at home and connect to it from the road, with no port forwarding, no firewall rules, and nothing exposed publicly.

It works on any hardware in this library — an AMD Ryzen™ AI Halo Developer Platform, a Ryzen™ AI mini PC, or a desktop with a Radeon™ GPU — because Tailscale runs at the operating system level and doesn't care which accelerator is inside.

## What You'll Learn

- What Tailscale is and when you actually need it
- How to install and authenticate Tailscale on your AMD device and your laptop
- How to find your device's Tailscale IP and device name
- How to SSH into your device from anywhere
- How to reach local web UIs like Lemonade, Open WebUI, and ComfyUI remotely

## How Tailscale Works

Tailscale connects every device signed in to the same account into one private network, called a **tailnet**. Each device makes an *outbound* connection to Tailscale's coordination service, which is why it works from behind home routers, NAT, and most corporate firewalls — nothing needs to be opened up.

| Term | What it means |
|------|---------------|
| **Tailnet** | Your private network — every device signed in to your Tailscale account |
| **Tailscale IP** | A stable `100.x.y.z` address each device keeps, no matter which network it's on |
| **MagicDNS** | Lets you use a short device name (`my-halo`) instead of remembering the IP |

The key idea is that the address never changes. Your device keeps the same Tailscale IP whether it's at home, in the office, or tethered to a phone — so the connection details you write down today keep working.

> **Note:** Tailscale is free for personal use. You sign up through an existing identity provider such as Google, GitHub, or Microsoft rather than creating a new password.

## Prerequisites

- The AMD device you want to reach remotely, powered on and connected to the internet
- A laptop or second machine to connect *from*
- Administrator access on both machines, since installing Tailscale requires elevated permissions

## Step 1 — Create a Tailscale Account

Go to [login.tailscale.com/start](https://login.tailscale.com/start) and sign up using Google, GitHub, or Microsoft.

You only do this once. Both your AMD device and your laptop sign in to this same account — that shared account is what allows them to find each other.

## Step 2 — Install Tailscale on Your AMD Device

<!-- @os:linux -->
Open a terminal on the device and run the official install script:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Then bring the device onto your tailnet:

```bash
sudo tailscale up
```

The command prints an authentication URL. Open it in a browser, sign in to the account you created in Step 1, and approve the device. Tailscale runs as a service, so the device reconnects automatically after a reboot.
<!-- @os:end -->

<!-- @os:windows -->
1. Download the installer from [tailscale.com/download/windows](https://tailscale.com/download/windows).
2. Run it and accept the prompts.
3. Click the Tailscale icon in the system tray and select **Log in**.
4. Sign in to the account you created in Step 1 and approve the device.

Tailscale starts automatically with Windows, so the device stays reachable after a reboot.
<!-- @os:end -->

<!-- @device:halo_box -->
> **AMD Ryzen™ AI Halo:** The Halo Developer Platform is designed to sit on a desk and stay powered on, which makes it an ideal always-available Tailscale node — leave a model server running and reach it from anywhere.
<!-- @device:end -->

<!-- @device:halo,grgh,stx,krk -->
> **Mini PCs:** Ryzen™ AI mini PCs work the same way. Because they're small and usually left running, they make good always-on remote nodes. If the machine sleeps when idle, disable sleep in your power settings so it stays reachable.
<!-- @device:end -->

## Step 3 — Install Tailscale on Your Laptop

Install Tailscale on whichever machine you want to connect *from*. Downloads for macOS, Windows, Linux, iOS, and Android are at [tailscale.com/download](https://tailscale.com/download).

Sign in with the **same account** you used in Step 2. Both machines now belong to the same tailnet and can see each other.

## Step 4 — Verify the Connection

On the AMD device, check its status and note its address:

```bash
tailscale status
tailscale ip -4
```

`tailscale status` lists every device on your tailnet, and `tailscale ip -4` prints this device's address. The output looks something like:

```text
100.101.102.103  my-halo     you@example.com  linux   -
100.98.12.44     my-laptop   you@example.com  macOS   active; direct
```

The first column is the Tailscale IP and the second is the device name. Note both — either one works as an address from here on.

From your laptop, confirm the two can reach each other:

```bash
tailscale ping my-halo
```

A successful reply looks like this:

```text
pong from my-halo (100.101.102.103) via 203.0.113.7:41641 in 24ms
```

Once that works, repeat the same command with your laptop off the local network — tethered to your phone, for example. If it still succeeds, you've confirmed the tunnel genuinely works from outside rather than just finding the device on the LAN. It's worth doing once before you depend on it while traveling.

> **Tip:** With MagicDNS enabled (the default on new tailnets), that short device name works anywhere you would otherwise type the IP.

> **Important — stop the device key from expiring:** By default, Tailscale device keys expire after 180 days. When that happens the device drops off your tailnet and has to be signed in again *in person* — which is exactly what you can't do while traveling. For a machine you rely on remotely, open the [Machines page](https://login.tailscale.com/admin/machines) in the admin console, find the device, and choose **Disable key expiry** from its `···` menu.

## Connecting Over SSH

SSH is the most direct way to use the machine remotely. First make sure an SSH server is running on the AMD device.

<!-- @device:halo_box -->
On the Ryzen AI Halo you don't need to configure SSH by hand. Open the **AMD Ryzen™ AI Developer Center**, go to the **Remote** tab, and enable the **SSH Server**. That tab also shows the username and port to use. The Linux Developer Center UI differs slightly from Windows but has the same Remote controls.
<!-- @device:end -->

<!-- @device:halo,grgh,stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @os:linux -->
Install and enable the OpenSSH server:

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```
<!-- @os:end -->

<!-- @os:windows -->
Enable the built-in OpenSSH server: go to **Settings → System → Optional features → Add a feature**, install **OpenSSH Server**, then start the **OpenSSH SSH Server** service from the Services app and set it to start automatically.
<!-- @os:end -->
<!-- @device:end -->

Then connect from your laptop using the device's Tailscale name or IP:

```bash
ssh <username>@<device-name-or-tailscale-ip>
```

<!-- @os:linux -->
> **Tip — skip SSH keys entirely:** Tailscale can handle SSH authentication using your tailnet identity instead of key pairs. Run `sudo tailscale up --ssh` on the AMD device, then connect as usual. With the default tailnet policy you'll be asked to re-approve the session in a browser about every 12 hours. See [Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh) for details.
<!-- @os:end -->
<!-- @os:windows -->
> **Note:** Tailscale SSH (`tailscale up --ssh`) runs only on Linux and macOS hosts, so on Windows use the OpenSSH server above. Connecting *from* Windows works fine either way.
<!-- @os:end -->

## Reaching Local Web UIs

Several playbooks in this library finish with a web interface you'd normally open at `localhost`. Over Tailscale you can open those same interfaces from your laptop, with one adjustment.

**Most servers listen only on `localhost` by default**, which means they refuse connections from anywhere else — including your tailnet. There are two ways around that.

### Recommended: publish to your tailnet only

[`tailscale serve`](https://tailscale.com/kb/1312/serve) proxies a local service to your tailnet over HTTPS while the service itself stays bound to `localhost`. Run this on the AMD device, using the port of whatever you're serving:

```bash
tailscale serve --bg 8188
```

The command prints the `https://<device>.<tailnet>.ts.net` address to open from your laptop. Keep the `--bg` flag — without it the proxy runs in the foreground and stops the moment you close the terminal. Use `tailscale serve status` to see what's published and `tailscale serve reset` to clear it. On Linux, prefix the command with `sudo` if you get a permissions error. (This relies on MagicDNS and HTTPS certificates, both on by default for new tailnets.)

### Alternative: bind the service to all interfaces

Start the service on `0.0.0.0`, then reach it at the device's Tailscale address and the same port — for example `http://my-halo:8188`.

| Service | Local address | Bind to all interfaces |
|---------|---------------|------------------------|
| **ComfyUI** | `http://localhost:8188` | Launch with `--listen 0.0.0.0` |
| **Lemonade Server** | `http://localhost:13305` | Set the server's host/bind address to `0.0.0.0` |
| **Open WebUI** | `http://localhost:8080` | Already published on all interfaces when run in a container |

> **Security note:** These web UIs have no login of their own. Binding one to `0.0.0.0` exposes it to every device on the local network, not just your tailnet — acceptable on a trusted home network, risky on shared or public Wi-Fi. `tailscale serve` avoids this entirely, since the service stays on `localhost` and only members of your tailnet can reach it.

<!-- @device:halo_box -->
## Using Tailscale with AMD Sync

If you use [AMD Sync](https://developer.amd.com/playbooks/amd-sync) for one-click remote VS Code, Terminal, and JupyterLab, Tailscale is what makes it work away from home. In the **Add a Remote Device** form, enter the device's Tailscale IP or device name as the **Hostname or IP** instead of its local network address. The same connection then works from any network, without changing anything when you move.
<!-- @device:end -->

## Troubleshooting

- **`tailscale` isn't recognized as a command** — The installer adds Tailscale to your `PATH`, but programs only read `PATH` when they start, so a terminal window you already had open won't see it. Close that window and open a new one, then try again. A reboot is rarely needed. If a fresh terminal still can't find the command, restart the machine so every process picks up the updated `PATH`.
<!-- @os:windows -->
  This is most common on Windows. To confirm the install itself worked, call the executable by its full path: `& "C:\Program Files\Tailscale\tailscale.exe" status`. If that works, the install is fine and it's purely a `PATH` issue.
<!-- @os:end -->
- **The device doesn't appear in `tailscale status`** — Confirm both machines are signed in to the *same* Tailscale account. Devices under different accounts cannot see each other.
- **`tailscale up` never finishes** — The authentication URL has to be opened in a browser and approved. If the device has no browser, copy the URL to another machine and approve it there.
- **SSH connection refused** — Tailscale is connected but the SSH server isn't running. Re-check the SSH step above.
- **A web UI times out** — The service is almost certainly still bound to `localhost`. Publish it with `tailscale serve --bg <port>`, or restart the service bound to `0.0.0.0`.
- **The connection works but feels slow** — Run `tailscale status`. If it reports `relay` rather than a direct connection, traffic is being routed through a relay server. It still works, but throughput is lower.

## Next Steps

- **Add more devices** — The same account can hold many machines. Install Tailscale on a phone or tablet and your device list stays in sync everywhere.
- **Use Tailscale SSH** — On a Linux device, run `sudo tailscale up --ssh` to drop SSH key management entirely. Tailscale SSH has no Windows server support.
- **Explore the documentation** — The [Tailscale docs](https://tailscale.com/kb) cover access controls, sharing a device with another user, and routing traffic through an exit node.
