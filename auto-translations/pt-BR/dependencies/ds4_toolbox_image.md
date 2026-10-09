<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Baixando a imagem de contêiner do toolbox ds4

O `ds4-cockpit` executa o mecanismo de inferência ds4 dentro de um contêiner toolbox. Na aba **Interactive Toolboxes**, selecione o toolbox mais recente disponível (por exemplo, `ds4-rocm-7.2.4`) e clique em **Create/Update** para baixar a imagem.

Para baixar a imagem diretamente:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

A versão do toolbox muda ao longo do tempo, então a verificação abaixo corresponde à família da imagem, e não a uma tag fixa.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->