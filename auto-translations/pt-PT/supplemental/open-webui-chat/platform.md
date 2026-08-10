<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# Configuração da Plataforma

Este documento descreve a configuração de plataforma esperada para executar este playbook.

## Aplicações/Frameworks Necessários

### Windows/Linux
O Lemonade deve estar pré-instalado a partir [daqui](https://lemonade-server.ai/install_options.html). 

- **Open WebUI** (aplicação web frontend)
- **Lemonade Server** (servidor de modelos backend)

> Este playbook executa o **Lemonade** (servidor/aplicação Lemonade) de forma **nativa**. O **Open WebUI** é executado como **contentor** no Linux (via Podman) e como **pacote Python** no Windows. O pacote PyPI `open-webui` suporta apenas Python ≤ 3.12, pelo que o contentor Linux evita a necessidade de gerir versões mais antigas do Python.  

## Modelos (no Lemonade)

Os modelos devem ser transferidos dentro da **aplicação Lemonade** (utilizando o Model Manager integrado) ou através dos comandos de gestão de modelos do Lemonade (`lemonade pull <model_name>`). Este playbook assume que os modelos recomendados abaixo foram transferidos e aparecem no endpoint da lista de modelos.

Verificar a disponibilidade de modelos:
- Abrir: `http://localhost:13305/api/v1/models`
- Os modelos transferidos serão listados em `"data"`.

### Modelos recomendados

| Capacidade | ID do Modelo | Notas |
|---|----|-----|
| LLM (Entrada de texto → Saída de texto) | `Qwen3-4B-Hybrid` (ou similar) | Qualquer modelo LLM do Lemonade para chat, conclusão de texto, programação ou raciocínio |
| VLM (Imagem → Texto) | `Qwen3.5-4B-GGUF` (ou qualquer modelo na categoria **Vision**) | Qualquer modelo multimodal/com capacidade de visão que possa receber imagens como parte da sua entrada |
| Geração de Imagem (Texto → Imagem) | `SDXL-Turbo` (ou qualquer modelo na categoria **Image**) | Qualquer modelo Stable Diffusion que gere imagens a partir de um prompt de texto |
| Áudio (Fala → Texto) | `Whisper-Large-v3` (ou qualquer modelo na categoria **Audio**) | Qualquer modelo ASR que converta áudio em texto |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## Portas utilizadas

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

Se estas portas já estiverem a ser utilizadas no seu sistema, altere-as ao iniciar o(s) servidor(es).