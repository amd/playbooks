<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve a configuração de plataforma esperada para executar este playbook.

## Aplicativos/Frameworks Necessários

### Windows/Linux
O Lemonade deve estar pré-instalado a partir [daqui](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (aplicativo web frontend)
- **Lemonade Server** (servidor de modelo backend)

> Este playbook executa o **Lemonade** (servidor/aplicativo Lemonade) **nativamente**. O **Open WebUI** é executado como um **container** no Linux (via Podman) e como um **pacote Python** no Windows. O pacote PyPI `open-webui` suporta apenas Python ≤ 3.12, portanto o container Linux evita a necessidade de gerenciar versões mais antigas do Python.  

## Modelos (no Lemonade)

Os modelos devem ser baixados dentro do **aplicativo Lemonade** (usando o Model Manager integrado) ou por meio dos comandos de gerenciamento de modelos do Lemonade (`lemonade pull <model_name>`). Este playbook presume que os modelos recomendados abaixo estejam baixados e apareçam no endpoint de listagem de modelos.

Verifique a disponibilidade do modelo:
- Abra: `http://localhost:13305/api/v1/models`
- Os modelos baixados serão listados em `"data"`.

### Modelos recomendados

| Capacidade | ID do Modelo | Observações |
|---|----|-----|
| LLM (Entrada de texto → Saída de texto) | `Qwen3-4B-Hybrid` (ou similar) | Qualquer modelo LLM do Lemonade para chat, completação de texto, codificação ou raciocínio |
| VLM (Imagem → Texto) | `Qwen3.5-4B-GGUF` (ou qualquer modelo na categoria **Vision**) | Qualquer modelo multimodal/com capacidade de visão que possa receber imagens como parte de sua entrada |
| Geração de Imagem (Texto → Imagem) | `SDXL-Turbo` (ou qualquer modelo na categoria **Image**) | Qualquer modelo Stable Diffusion que gere imagens a partir de um prompt de texto |
| Áudio (Fala → Texto) | `Whisper-Large-v3` (ou qualquer modelo na categoria **Audio**) | Qualquer modelo ASR que converta áudio em texto |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Portas utilizadas

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Se essas portas já estiverem em uso no seu sistema, altere-as ao iniciar o(s) servidor(es).