#!/usr/bin/env bash
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

# As the provisioning scripts do: the headless CLI and daemon, plus a service that starts them at boot.
lms="$HOME/.lmstudio/bin/lms"
if [ ! -x "$lms" ]; then
  curl -fsSL https://lmstudio.ai/install.sh | bash || exit 1
fi
sudo ln -sf "$lms" /usr/local/bin/lms || exit 1
if [ ! -f /etc/systemd/system/lmstudio.service ]; then
  sudo tee /usr/local/bin/lmstudio-startup.sh >/dev/null <<EOF || exit 1
#!/bin/bash
export PATH="$HOME/.lmstudio/bin:\$PATH"
lms daemon up
lms server start --port 1234
EOF
  sudo chmod +x /usr/local/bin/lmstudio-startup.sh || exit 1
  sudo tee /etc/systemd/system/lmstudio.service >/dev/null <<EOF || exit 1
[Unit]
Description=LM Studio (llmster) headless server
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
KillMode=process
User=$(id -un)
ExecStart=/usr/local/bin/lmstudio-startup.sh
Restart=on-failure
RestartSec=15

[Install]
WantedBy=multi-user.target
EOF
  sudo systemctl daemon-reload || exit 1
  sudo systemctl enable lmstudio || exit 1
fi
sudo systemctl restart lmstudio
