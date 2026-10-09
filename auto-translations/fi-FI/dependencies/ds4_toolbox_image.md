<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4-toolbox-säilötuvan kuvan hakeminen

`ds4-cockpit` suorittaa ds4-päättelymoottoria säilön toolbox-ympäristössä. Valitse **Interactive Toolboxes** -välilehdellä uusin saatavilla oleva toolbox (esim. `ds4-rocm-7.2.4`) ja napsauta **Create/Update** hakeaksesi kuvan.

Jos haluat sen sijaan hakea kuvan suoraan:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Toolboxin versio muuttuu ajan myötä, joten alla oleva tarkistus täsmää kuvaperheeseen eikä kiinteään tagiin.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->