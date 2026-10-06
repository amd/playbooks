<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hermes Kurulumu

Hermes ajan CLI'sini resmi kurulum programıyla yükleyin. `--skip-setup` bayrağı, kurulumun kullanıcı müdahalesi olmadan yapılmasını sağlar:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes, `~/.local/bin` dizinine kurulur; bu dizinin `PATH` değişkeninizde olduğundan emin olun.

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->