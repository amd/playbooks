<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente do inglês e não foi revisada por um ser humano. Ela pode conter erros, e determinadas instruções, comandos, downloads, disponibilidade de produtos ou outros conteúdos podem variar de acordo com o idioma ou a região. Em caso de qualquer inconsistência ou divergência, a versão original em inglês do playbook prevalecerá.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão Geral

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) é a variante focada em eficiência da família DeepSeek V4 — um modelo Mixture of Experts de 284 bilhões de parâmetros, com 13 bilhões de parâmetros ativos. De acordo com o [relatório técnico da DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), ele pontua 79% no SWE-bench Verified e 91,6% no LiveCodeBench.

[ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) é um motor de inferência dedicado, construído especificamente para essa arquitetura de modelo. Em vez de um runtime de propósito geral, o ds4 tem como alvo diretamente a família DeepSeek V4, com otimizações de kernel específicas de arquitetura para o software AMD ROCm™. Atualmente, é uma das implementações de melhor desempenho do DeepSeek V4 Flash no Strix Halo.

Este tutorial mostra como usar o `ds4-cockpit`, uma interface de terminal, para configurar o ds4, baixar os pesos do modelo e começar a servir o DeepSeek V4 Flash localmente na AMD Ryzen™ AI Halo Developer Platform.

## O Que Você Vai Aprender

- Como instalar e iniciar a interface de terminal `ds4-cockpit`
- Como criar o container toolbox ROCm do ds4
- Como baixar a quantização recomendada para um único nó Halo
- Como iniciar o servidor de inferência ds4 e expor um endpoint compatível com OpenAI
- Como conectar uma Web UI ou um agente de codificação ao servidor local

## Definindo a Configuração de Memória

<!-- @require:memory-config -->

## Instalando os Pré-requisitos de Software

> **Requisitos do sistema para esta configuração (IQ2_XXS de nó único com contexto de 126k):**
> - Um sistema Strix Halo com **pelo menos 128 GB de memória unificada**.
> - **VRAM dedicada da BIOS (frame buffer UMA) definida no mínimo**, para que o pool de memória compartilhada possa ser o maior possível.
> - O **pool de memória compartilhada da GPU definido em pelo menos 110 GB**: execute `amd-ttm --set 110` (veja a etapa de configuração de memória acima) e reinicie. Valores mais baixos podem falhar por falta de memória quando o modelo é carregado com um contexto de 126k. Se o seu sistema tiver menos memória disponível, diminua o valor de **Contexto** no Modo Servidor em vez disso.
>
> **Observação:** Tente definir o **pool de memória compartilhada da GPU** para **110 GB** como ponto de partida. Se você encontrar erros de falta de memória, aumente o pool de memória compartilhada ou diminua o tamanho do contexto.

O ds4-cockpit usa containers toolbox para executar o motor ds4. Instale `podman`, `distrobox` e `pipx`:

```bash
sudo apt update
sudo apt install -y podman distrobox pipx
```

<!-- @test:id=ds4-prereqs-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
echo "OK: podman, distrobox, and pipx are installed"
```
<!-- @test:end -->

## Quantizações Disponíveis

O autor do ds4 fornece várias versões quantizadas do DeepSeek V4 Flash no formato GGUF. Todos os modelos abaixo usam calibração por matriz de importância (imatrix), que preserva maior precisão nas partes do modelo que mais importam para tarefas de codificação e raciocínio.

| Quantização | Tamanho | Descrição |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80.8 GB | Recomendado para um único nó de 128 GB |
| [Hybrid Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Mantém as camadas 37–42 em precisão Q4 para melhor precisão. Cabe em 128 GB, mas deixa menos espaço para contexto |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Qualidade superior. Requer dois nós Halo via clustering multi-nó |
| [MTP Speculative Decoding](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3.6 GB | Complemento opcional para decodificação especulativa, para melhorar a velocidade de geração |

O modelo **IQ2_XXS imatrix** é um bom ponto de partida. Ele cabe confortavelmente em um único nó e deixa memória suficiente para uma janela de contexto razoável.

## Instalando o ds4-cockpit

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) é uma interface de terminal leve para facilitar a configuração e execução do ds4 no Strix Halo. Ele cuida da criação de containers toolbox, do download dos pesos do modelo e da inicialização dos servidores. Instale-o com `pipx`:

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

Inicie o cockpit:
```bash
ds4-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ds4-cockpit
echo "OK: ds4-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Criando o Toolbox

Na aba **Interactive Toolboxes**, selecione o toolbox estável/disponível mais recente (por exemplo, `ds4-rocm-7.2.4`) e clique em **Create/Update**. Isso baixa a imagem do container e cria o ambiente toolbox.


<p align="center">
  <img src="assets/ds4-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ds4-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Baixando o Modelo

Vá até a aba **Model Manager**. Selecione **IQ2_XXS imatrix (~80.8 GB)** no menu suspenso e clique em **Download**. Os arquivos do modelo serão salvos em `~/ds4` por padrão (você pode alterar o caminho de armazenamento).

> **Observação:** O modelo IQ2_XXS tem cerca de 80 GB, então o download pode demorar um pouco, dependendo da sua conexão. Você pode continuar assim que ele terminar.

<p align="center">
  <img src="assets/ds4-cockpit-model-manager.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ds4-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ds4-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ds4-cockpit first."
  exit 1
fi

# Prefer to confirm the recommended IQ2_XXS imatrix quantization is present.
if find "$model_dir" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' | grep -q .; then
  echo "OK: IQ2_XXS imatrix model is downloaded"
else
  echo "OK: a GGUF model is present (recommended IQ2_XXS imatrix file not detected by name)"
fi
```
<!-- @test:end -->

## Iniciando o Servidor

Vá até a aba **Server Mode**. Selecione o modelo baixado e o toolbox, depois configure o tamanho do contexto, o host e a porta. Quando estiver pronto, clique em **Start ds4-server**.

> **Dica** Um tamanho de contexto de `126000` é um valor inicial razoável, que deve caber em um único nó — você pode aumentá-lo se tiver memória de sobra, ou diminuí-lo se encontrar erros de falta de memória. A porta (`8000` neste guia) é arbitrária; escolha qualquer porta livre.

> **Cache de Disco KV (opcional).** Ativar o **KV Disk Cache** transfere o cache KV para o disco (em **Host Cache Dir**, padrão `~/.cache/ds4-kv`), para que prompts de sistema repetidos sejam restaurados do SSD em vez de serem recalculados. É uma otimização de desempenho para fluxos de trabalho de agentes de codificação com prompts longos e repetidos, e **não é necessária** para executar o servidor.

<p align="center">
  <img src="assets/ds4-cockpit-server-mode.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

O servidor será iniciado e ficará escutando na porta 8000, expondo um endpoint de API compatível com OpenAI em `http://localhost:8000/v1`.

**Teste rápido:**
```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'
```

<!-- @test:id=ds4-server-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

# This runner is shared with other playbooks, and ds4 at a 126k context consumes almost the entire GPU memory pool.
# So rather than keeping ds4 resident, CI starts the server, verifies a chat completion, then stops it again.
# This frees the memory for the next job.
# ds4 has no separate "unload"; stopping the server process is what releases the ~80 GB model.

CONTAINER="ds4-ci-server"
MODEL_DIR="$HOME/ds4"

# Locate the downloaded model (prefer the recommended IQ2_XXS imatrix file).
model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*IQ2*imatrix*.gguf' 2>/dev/null | head -1)"
if [ -z "$model_file" ]; then
  model_file="$(find "$MODEL_DIR" -maxdepth 2 -iname '*.gguf' 2>/dev/null | head -1)"
fi
if [ -z "$model_file" ]; then
  echo "No .gguf model found under $MODEL_DIR. Download it in ds4-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ds4-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# Remove any stale instance, then start ds4-server detached (same flags ds4-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns=keep-id \
  -p 127.0.0.1:8000:8000 \
  -v "$MODEL_DIR":/models:ro \
  "$image" \
  ds4-server -m "/models/$model_name" --ctx 126000 --host 0.0.0.0 --port 8000

# Wait for readiness; the ~80 GB model can take a few minutes to load.
up=false
for i in $(seq 1 240); do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8000/v1/models || true)"
  if [ -n "$code" ] && [ "$code" != "000" ]; then
    up=true
    break
  fi
  if ! podman inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null | grep -q true; then
    echo "ds4-server container exited during startup:"
    podman logs "$CONTAINER" 2>&1 | tail -40 || true
    exit 1
  fi
  sleep 2
done

if [ "$up" != "true" ]; then
  echo "ds4 server did not become ready on http://127.0.0.1:8000"
  podman logs "$CONTAINER" 2>&1 | tail -40 || true
  exit 1
fi
echo "OK: ds4 server is responding on :8000"

body='{
  "model": "deepseek-v4-flash",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32,
  "stream": false
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d "$body")"

if [ -z "$out" ]; then
  echo "Empty response from ds4 /v1/chat/completions"
  exit 1
fi

export DS4_OUT="$out"
python3 - <<'PY'
import json, os, sys

data = json.loads(os.environ["DS4_OUT"])
choices = data.get("choices")
if not choices:
    print("Response has no 'choices':")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

message = choices[0].get("message", {}) or {}
content = message.get("content") or message.get("reasoning_content")
if not content:
    print("Response choice has empty content:")
    print(json.dumps(data, indent=2)[:2000])
    sys.exit(1)

print("OK: ds4 chat/completions returned content")
PY

echo "OK: ds4 server test complete; server stopped and GPU memory released"
```
<!-- @test:end -->

## Conectando uma Web UI

Você pode conectar qualquer interface de chat que suporte o formato da API OpenAI. Por exemplo, para usar o HuggingFace ChatUI:

```bash
docker run -p 3000:3000 \
  --add-host=host.docker.internal:host-gateway \
  -e OPENAI_BASE_URL=http://host.docker.internal:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Abra `http://localhost:3000` no seu navegador para começar a conversar.
## Conectando um Agente de Codificação

O servidor ds4 expõe endpoints compatíveis tanto com OpenAI quanto com Anthropic, então a maioria dos agentes de codificação pode se conectar a ele diretamente. Por exemplo, para adicioná-lo ao agente de codificação `pi`, adicione o seguinte bloco a `~/.pi/agent/models.json`:

```json
"ds4": {
  "name": "ds4.c local",
  "baseUrl": "http://localhost:8000/v1",
  "api": "openai-completions",
  "apiKey": "dsv4-local",
  "compat": {
    "supportsStore": false,
    "supportsDeveloperRole": false,
    "supportsReasoningEffort": true,
    "supportsUsageInStreaming": true,
    "maxTokensField": "max_tokens",
    "supportsStrictMode": false,
    "thinkingFormat": "deepseek",
    "requiresReasoningContentOnAssistantMessages": true
  },
  "models": [
    {
      "id": "deepseek-v4-flash",
      "name": "DeepSeek V4 Flash (ds4.c local)",
      "reasoning": true,
      "thinkingLevelMap": {
        "off": null,
        "minimal": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "xhigh": "xhigh"
      },
      "input": ["text"],
      "contextWindow": 131072,
      "maxTokens": 65536,
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
    }
  ]
}
```

> **Dica**: Se o seu agente de codificação ou Web UI estiver rodando em uma máquina diferente da plataforma Halo, você precisará encaminhar a porta 8000 via SSH:
> ```bash
> ssh -L 0.0.0.0:8000:localhost:8000 <halo-host-ip>
> ```

## Próximos Passos

- **Clustering multi-node**: Se você tiver dois dispositivos Halo, o ds4 oferece suporte à distribuição do modelo Q4 (~153 GB) entre as duas máquinas via paralelismo de pipeline. Consulte a [documentação do ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) para instruções de configuração.
- **Decodificação especulativa (MTP)**: Baixe os pesos do MTP (~3,6 GB) e passe `--mtp` para o servidor para obter uma velocidade de geração mais rápida.
- **Offloading de cache KV para disco**: Para fluxos de trabalho de agentes de codificação, habilite `--kv-disk-dir` para que prompts de sistema repetidos sejam restaurados a partir do SSD em vez de serem recalculados a cada vez.

Para mais informações, consulte o [repositório do ds4](https://github.com/antirez/ds4) e o [toolbox ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).