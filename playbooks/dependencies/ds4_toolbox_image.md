<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pulling the ds4 toolbox container image

`ds4-cockpit` runs the ds4 inference engine inside a container toolbox. In the **Interactive Toolboxes** tab, select the latest available toolbox (e.g. `ds4-rocm-7.2.4`) and click **Create/Update** to pull the image.

To pull the image directly instead:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

The toolbox version changes over time, so the check below matches the image family rather than a fixed tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->
