<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão Geral

[DeepSeek V4 Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) é a variante focada em eficiência da família DeepSeek V4 — um modelo Mixture of Experts com 284 mil milhões de parâmetros e 13 mil milhões de parâmetros ativos. De acordo com o [relatório técnico da DeepSeek](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash), obtém uma pontuação de 79% no SWE-bench Verified e 91,6% no LiveCodeBench.

O [ds4 (Dwarf Star 4)](https://github.com/antirez/ds4) é um motor de inferência dedicado, criado especificamente para esta arquitetura de modelo. Em vez de ser um runtime de uso geral, o ds4 tem como alvo diretamente a família DeepSeek V4, com otimizações de kernel específicas da arquitetura para o software AMD ROCm™. É atualmente uma das implementações com melhor desempenho do DeepSeek V4 Flash no Strix Halo.

Este tutorial mostra como usar o `ai-toolbox-cockpit`, uma TUI (interface de utilizador em terminal), para configurar o ds4, transferir os pesos do modelo e começar a servir o DeepSeek V4 Flash localmente na AMD Ryzen™ AI Halo Developer Platform.

## O Que Vai Aprender

- Como instalar e iniciar a TUI de terminal `ai-toolbox-cockpit`
- Como criar o contentor toolbox ds4 ROCm
- Transferir a quantização recomendada para um único nó Halo
- Iniciar o servidor de inferência ds4 e expor um endpoint compatível com OpenAI
- Ligar uma Web UI ou um agente de programação ao servidor local

## Definir a Configuração de Memória

<!-- @require:memory-config -->

## Instalar os Pré-requisitos de Software

<!-- @require = dependency docs rendered on the website; @prereq = CI-only, validated and auto-installed before tests (never rendered) -->
<!-- @prereq:podman,distrobox,ds4-cockpit,ds4-toolbox-image -->

> **Requisitos de sistema para esta configuração (IQ2_XXS de nó único a um contexto de 126k):**
> - Um sistema Strix Halo com **pelo menos 128 GB de memória unificada**.
> - **VRAM dedicada da BIOS (frame buffer UMA) definida para o mínimo**, para que o pool de memória partilhada possa ser o maior possível.
> - O pool de memória partilhada da GPU **definido para pelo menos 110 GB**: execute `amd-ttm --set 110` (ver o passo de configuração de memória acima) e reinicie. Valores inferiores podem falhar por falta de memória quando o modelo é carregado com um contexto de 126k. Se o seu sistema tiver menos memória disponível, reduza antes o valor de **Contexto** no Modo Servidor.
>
> **Nota:** Experimente definir o **pool de memória partilhada da GPU** para **110 GB** como ponto de partida. Se encontrar erros de falta de memória, aumente o pool de memória partilhada ou reduza o tamanho do contexto.

O ai-toolbox-cockpit usa toolboxes em contentores para executar o motor ds4. Instale o `podman`, o `distrobox` e o `pipx`:

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

O autor do ds4 disponibiliza várias versões quantizadas do DeepSeek V4 Flash em formato GGUF. Todos os modelos abaixo usam calibração por matriz de importância (imatrix), que preserva uma precisão mais elevada nas partes do modelo que mais importam para tarefas de programação e de raciocínio.

| Quantização | Tamanho | Descrição |
|-------------|------|-------------|
| [IQ2_XXS imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~80,8 GB | Recomendado para um único nó de 128 GB |
| [Híbrido Q2/Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~97 GB | Mantém as camadas 37–42 em precisão Q4 para melhor exatidão. Cabe em 128 GB, mas deixa menos espaço para o contexto |
| [Q4 imatrix](https://huggingface.co/antirez/deepseek-v4-gguf) | ~153 GB | Maior qualidade. Requer dois nós Halo através de agrupamento multi-nó |
| [Descodificação Especulativa MTP](https://huggingface.co/antirez/deepseek-v4-gguf) | ~3,6 GB | Extensão opcional para descodificação especulativa, de forma a melhorar a velocidade de geração |

O modelo **IQ2_XXS imatrix** é um bom ponto de partida. Cabe confortavelmente num único nó e deixa memória suficiente para uma janela de contexto razoável.

## Instalar o ai-toolbox-cockpit

O [ai-toolbox-cockpit](https://github.com/kyuz0/ai-toolbox-cockpit) é uma TUI de terminal leve que facilita a instalação de vários backends de IA. Vamos usá-lo para tratar da criação do nosso contentor ds4, da transferência dos pesos do modelo e do arranque dos servidores. Instale-o com o `pipx`:

<!-- @test:id=ds4-cockpit-install-linux timeout=300 -->
```bash
pipx install git+https://github.com/kyuz0/ai-toolbox-cockpit.git
```
<!-- @test:end -->

Inicie o cockpit:
```bash
ai-toolbox-cockpit
```

<!-- @test:id=ds4-cockpit-linux timeout=60 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
# Verify the pipx-installed cockpit entry point is on PATH (do NOT launch the TUI).
command -v ai-toolbox-cockpit
echo "OK: ai-toolbox-cockpit is installed and on PATH"
```
<!-- @test:end -->

## Passo 1: Criar a Toolbox

No separador **Interactive Toolboxes**, selecione a toolbox mais recente disponível/estável para o ds4 (por exemplo, `ds4-rocm-10.0`) e clique em **Create/Update**. Isto descarrega a imagem do contentor e cria o ambiente de toolbox.


<p align="center">
  <img src="assets/ai-toolbox-cockpit-toolboxes.png" alt="Selecting the ds4 toolbox in ai-toolbox-cockpit" width="800"/>
</p>

<!-- @test:id=ds4-toolbox-image-linux timeout=120 hidden=True -->
```bash
set -euo pipefail
export PATH="$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

# The toolbox version changes over time, so match the image family, not a fixed tag.
if ! podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit (Interactive Toolboxes tab) first."
  exit 1
fi
echo "OK: ds4 toolbox container image is present"
```
<!-- @test:end -->

## Passo 2: Transferir o Modelo

Vá ao separador **Models**. Primeiro, selecione o backend (ds4). Em seguida, selecione **IQ2_XXS imatrix (~80.8 GB)** na lista pendente e clique em **Download**. Os ficheiros do modelo serão guardados por predefinição em `~/ds4` (pode alterar o caminho de armazenamento).

> **Nota:** O modelo IQ2_XXS tem cerca de 80 GB, pelo que a transferência pode demorar algum tempo, consoante a sua ligação. Pode continuar assim que terminar.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-models.png" alt="Selecting and downloading the IQ2_XXS model" width="800"/>
</p>

<!-- @test:id=ds4-model-downloaded-linux timeout=60 hidden=True -->
```bash
set -euo pipefail

# ai-toolbox-cockpit saves model weights to ~/ds4 by default
model_dir="$HOME/ds4"

if [ ! -d "$model_dir" ]; then
  echo "Model directory $model_dir does not exist. Download the model in ai-toolbox-cockpit (Model Manager tab) first."
  exit 1
fi

if ! find "$model_dir" -maxdepth 2 -iname '*.gguf' | grep -q .; then
  echo "No .gguf model files found under $model_dir. Download the IQ2_XXS imatrix model in ai-toolbox-cockpit first."
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

## Passo 3: Iniciar o Servidor

Vá ao separador **Server Mode**. Selecione o modelo transferido e a toolbox e, em seguida, configure o tamanho do contexto, o anfitrião (host) e a porta. Quando estiver pronto, clique em **Start ds4-server**.

> **Sugestão:** Um tamanho de contexto de `126000` é um valor inicial razoável que deverá caber num único nó — pode aumentá-lo se tiver memória de sobra, ou reduzi-lo se encontrar erros de falta de memória. A porta (`8000` neste guia) é arbitrária; escolha qualquer porta livre.

> **Cache de KV em disco (opcional).** Ativar a opção **KV Disk Cache** descarrega a cache de KV para disco (em **Host Cache Dir**, por predefinição `~/.cache/ds4-kv`), de modo a que as instruções de sistema repetidas sejam restauradas a partir do SSD em vez de serem recalculadas. Trata-se de uma otimização de desempenho para fluxos de trabalho de agentes de programação com instruções longas e repetidas, e **não é necessária** para executar o servidor.

<p align="center">
  <img src="assets/ai-toolbox-cockpit-server.png" alt="Configuring and starting the ds4 server" width="800"/>
</p>

O servidor vai iniciar e ficar à escuta na porta 8000, expondo um endpoint de API compatível com OpenAI em `http://localhost:8000/v1`.

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
  echo "No .gguf model found under $MODEL_DIR. Download it in ai-toolbox-cockpit first."
  exit 1
fi
model_name="$(basename "$model_file")"

# Pick the toolbox image (version-agnostic).
image="$(podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox' | head -1)"
if [ -z "$image" ]; then
  echo "No strix-halo-ds4-toolbox image found. Create the toolbox in ai-toolbox-cockpit first."
  exit 1
fi

# Always stop/remove the server on exit so it never holds GPU memory afterwards.
cleanup() {
  podman stop -t 10 "$CONTAINER" >/dev/null 2>&1 || true
  podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# keep-id maps the calling user into the container. Root does not need it, and as root it cannot
# be combined with --ipc=host (crun fails to mount /dev/mqueue), so root keeps the host user namespace.
userns=keep-id
if [ "$(id -u)" -eq 0 ]; then
  userns=host
fi

# Remove any stale instance, then start ds4-server detached (same flags ai-toolbox-cockpit uses, with -d instead of -it).
podman rm -f "$CONTAINER" >/dev/null 2>&1 || true
podman run -d --name "$CONTAINER" \
  --device /dev/dri --device /dev/kfd \
  --group-add keep-groups \
  --security-opt seccomp=unconfined \
  --ipc=host \
  --cap-add=SYS_PTRACE \
  --security-opt label=disable \
  --userns="$userns" \
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
## Ligar uma Interface Web

Pode ligar qualquer interface de chat que suporte o formato da API OpenAI. Por exemplo, para usar o HuggingFace ChatUI:

```bash
docker run --network=host \
  -e PORT=3000 \
  -e OPENAI_BASE_URL=http://localhost:8000/v1 \
  -e OPENAI_API_KEY=dummy \
  -v chat-ui-data:/data \
  ghcr.io/huggingface/chat-ui-db
```

Abra `http://localhost:3000` no seu navegador para começar a conversar.

> **Nota:** `--network=host` coloca a Interface Web na rede do anfitrião para que possa alcançar o servidor ds4 em `localhost` diretamente. Isto mantém o servidor ds4 vinculado ao loopback (não é necessário expô-lo noutras interfaces).

> **Dica:** A porta da Interface Web (`3000` aqui, definida através de `PORT`) é arbitrária — escolha qualquer porta livre se `3000` já estiver em uso e abra essa porta no seu navegador em vez disso. Certifique-se de que a porta em `OPENAI_BASE_URL` corresponde à porta em que o seu servidor ds4 está a ser executado.

## Ligar um Agente de Programação

O servidor ds4 expõe endpoints compatíveis com OpenAI e Anthropic, pelo que a maioria dos agentes de programação se pode ligar a ele diretamente. Por exemplo, para o adicionar ao agente de programação `pi`, adicione o seguinte bloco a `~/.pi/agent/models.json`:

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

> **Dica**: Se o seu agente de programação ou Interface Web estiver a ser executado numa máquina diferente da plataforma Halo, terá de encaminhar a porta do servidor (`8000` aqui) via SSH:
> ```bash
> ssh -L 8000:localhost:8000 <halo-host-ip>
> ```

## Próximos Passos

- **Clustering multi-nó**: Se tiver dois dispositivos Halo, o ds4 suporta a distribuição do modelo Q4 (~153 GB) por ambas as máquinas através de paralelismo de pipeline. Consulte a [documentação do ds4-toolbox](https://github.com/kyuz0/strix-halo-ds4-toolbox#distributed-inference-pipeline-parallelism) para instruções de configuração.
- **Descodificação especulativa (MTP)**: Transfira os pesos MTP (~3.6 GB) e passe `--mtp` ao servidor para uma velocidade de geração mais rápida.
- **Descarregamento da cache KV para disco**: Para fluxos de trabalho de agentes de programação, ative `--kv-disk-dir` para que os prompts de sistema repetidos sejam restaurados a partir do SSD em vez de serem recalculados de cada vez.

Para mais informações, consulte o [repositório ds4](https://github.com/antirez/ds4) e a [toolbox ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox).