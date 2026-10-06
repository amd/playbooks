<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Extrair a imagem do contentor da toolbox ds4

O `ds4-cockpit` executa o motor de inferência ds4 dentro de um contentor toolbox. No separador **Interactive Toolboxes**, selecione a toolbox mais recente disponível (por exemplo, `ds4-rocm-7.2.4`) e clique em **Create/Update** para extrair a imagem.

Para extrair a imagem diretamente:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

A versão da toolbox muda ao longo do tempo, pelo que a verificação abaixo corresponde à família de imagens em vez de a uma tag fixa.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->