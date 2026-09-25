<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installing uv

[uv](https://docs.astral.sh/uv/) is the Python package/environment manager Agent Canvas uses to build its agent-server environment. Install it with the official script:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` installs into `~/.local/bin`; make sure that directory is on your `PATH`.

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->
