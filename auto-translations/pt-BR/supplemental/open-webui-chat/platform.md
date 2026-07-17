<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Configuração da Plataforma

Este documento descreve a configuração de plataforma esperada para executar este playbook.

## Aplicativos/Frameworks Necessários

### Windows/Linux
O Lemonade deve ser pré-instalado a partir [daqui](https://lemonade-server.ai/install_options.html).

- **Open WebUI** (aplicativo web de frontend)
- **Lemonade Server** (servidor de modelos backend)

> Este playbook executa o **Lemonade** (servidor/aplicativo Lemonade) de forma **nativa**. O **Open WebUI** é executado como um **contêiner** no Linux (via Podman) e como um **pacote Python** no Windows. O pacote `open-webui` do PyPI suporta apenas Python ≤ 3.12, portanto o contêiner Linux evita a necessidade de gerenciar versões mais antigas do Python.

## Modelos (no Lemonade)

Os modelos devem ser baixados dentro do **aplicativo Lemonade** (usando o Gerenciador de Modelos integrado) ou por meio dos comandos de gerenciamento de modelos do Lemonade (`lemonade pull <model_name>`). Este playbook assume que os modelos recomendados abaixo foram baixados e aparecem no endpoint da lista de modelos.

Verifique a disponibilidade dos modelos:
- Abra: `http://localhost:13305/api/v1/models`
- Os modelos baixados serão listados em `"data"`.

### Modelos recomendados

| Capacidade | ID do Modelo | Observações |
|---|----|-----|
| LLM (Entrada de texto → Saída de texto) | `Qwen3-4B-Hybrid` (ou similar) | Qualquer modelo LLM do Lemonade para chat, conclusão de texto, codificação ou raciocínio |
| VLM (Imagem → Texto) | `Qwen3.5-4B-GGUF` (ou qualquer modelo na categoria **Vision**) | Qualquer modelo multimodal/com capacidade de visão que aceite imagens como parte de sua entrada |
| Geração de Imagens (Texto → Imagem) | `SDXL-Turbo` (ou qualquer modelo na categoria **Image**) | Qualquer modelo Stable Diffusion que gere imagens a partir de um prompt de texto |
| Áudio (Fala → Texto) | `Whisper-Large-v3` (ou qualquer modelo na categoria **Audio**) | Qualquer modelo ASR que converta áudio em texto |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Portas utilizadas

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Se essas portas já estiverem em uso no seu sistema, altere-as ao iniciar o(s) servidor(es).