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

## Visão geral

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este playbook requer um mínimo de **32GB** de memória de sistema.
<!-- @device:end -->

O n8n é uma plataforma de automação de fluxos de trabalho que permite ligar aplicações e serviços através de um editor visual baseado em nós.

Este playbook ensina-o a configurar um resumidor de notícias financeiras com IA que faz scraping da secção de negócios da AP News, extrai as principais manchetes e utiliza um LLM local em execução no seu sistema para gerar um resumo orientado para investidores.

## O que vai aprender

- Como instalar e iniciar o n8n
- Importar e configurar um fluxo de trabalho pré-criado
- Ligar ao Lemonade utilizando a integração nativa do n8n
- Compreender os nós do fluxo de trabalho e o fluxo de dados

## O que é o Lemonade?

O [Lemonade](https://lemonade-server.ai) é uma plataforma de serviço de LLM local desenvolvida para hardware AMD. Fornece uma API compatível com OpenAI que funciona inteiramente na sua máquina — os seus dados nunca saem do dispositivo.

Neste playbook, utilizamos o Lemonade para servir um LLM local ao qual o n8n se liga para tarefas com IA.

O n8n inclui um **nó nativo do Lemonade** (`Lemonade Chat Model`) que fornece uma integração de primeira classe - sem necessidade de configuração manual. Isto torna simples ligar o seu LLM local a fluxos de trabalho de automação.

## Definir a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os Pré-requisitos de Software
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @var:id=lemonade_model value="gpt-oss-120b-mxfp-GGUF" -->
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
<!-- @var:id=lemonade_model value="gpt-oss-20b-mxfp4-GGUF" -->
<!-- @device:end -->


<!-- @test:id=lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-chat-windows timeout=1200 hidden=True -->
```powershell
$ErrorActionPreference = "Stop"

# Wait for server to come up
$modelsJson = $null
for ($i=0; $i -lt 120; $i++) {
  $modelsJson = curl.exe -s --max-time 2 http://127.0.0.1:13305/api/v1/models
  if ($modelsJson) { break }
  Start-Sleep -Seconds 1
}
if (-not $modelsJson) { throw "Lemonade server not ready on http://127.0.0.1:13305" }
Write-Host "OK: Lemonade server is responding"

# Now that the server is responding, check if model is downloaded in Lemonade (robust JSON parse)
$parsed = $modelsJson | ConvertFrom-Json
$entry  = $parsed.data | Where-Object { $_.id -eq "${lemonade_model}" } | Select-Object -First 1
if (-not $entry) { throw "Model ${lemonade_model} is not present in Lemonade /api/v1/models." }
if (-not $entry.downloaded) { throw "Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it." }
Write-Host "OK: ${lemonade_model} model is downloaded in Lemonade"

# Model chat test
$body = @{
  model = "${lemonade_model}"
  messages = @(@{ role = "user"; content = "Reply with exactly: OK" })
  temperature = 0
  max_tokens = 32
} | ConvertTo-Json -Depth 5

$tmpBody = Join-Path $env:TEMP "lemonade-chat-body.json"
[System.IO.File]::WriteAllText($tmpBody, $body, [System.Text.UTF8Encoding]::new($false))

try {
  $out = curl.exe -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@$tmpBody"
  if (-not $out) { throw "Empty response from Lemonade chat/completions" }
}
finally {
  Remove-Item  $tmpBody -Force -ErrorAction SilentlyContinue
}
```
<!-- @test:end -->
<!-- @os:end -->


<!-- @os:linux -->
<!-- @test:id=lemonade-chat-linux timeout=1200 hidden=True -->
```bash
set -euo pipefail

models_json=""
for i in $(seq 1 120); do
  models_json="$(curl -s --max-time 2 http://127.0.0.1:13305/api/v1/models || true)"
  if [ -n "$models_json" ]; then
    break
  fi
  sleep 1
done

if [ -z "$models_json" ]; then
  echo "Lemonade server not ready on http://127.0.0.1:13305"
  exit 1
fi
echo "OK: Lemonade server is responding"

export MODELS_JSON="$models_json"
python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["MODELS_JSON"])
entry = None
for item in data.get("data", []):
    if item.get("id") == "${lemonade_model}":
        entry = item
        break

if entry is None:
    print("Model ${lemonade_model} is not present in Lemonade /api/v1/models.")
    sys.exit(1)

if not entry.get("downloaded", False):
    print("Model ${lemonade_model} is present but not downloaded in Lemonade. Please download it.")
    sys.exit(1)

print("OK: ${lemonade_model} model is downloaded in Lemonade")
PY

body='{
  "model": "${lemonade_model}",
  "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
  "temperature": 0,
  "max_tokens": 32
}'

out="$(curl -sS --fail-with-body --max-time 300 http://127.0.0.1:13305/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$body" || true)"

if [ -z "$out" ]; then
  echo "Empty response from Lemonade chat/completions"
  exit 1
fi
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @test:id=node-npm-version timeout=60 hidden=True -->
```bash
node -v
npm -v
```
<!-- @test:end -->

## Instalar o n8n
<!-- @os:windows -->
Instale o n8n globalmente utilizando npm.

> **Nota**: Poderá ver alguns avisos do npm. Isto é esperado.

```bash
npm install -g n8n
```

<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-version timeout=60 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
n8n --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
> **Dica**: Os utilizadores de Windows podem precisar de modificar a sua Política de Execução do PowerShell (por exemplo,
> definindo-a para RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problema de PATH**: Se `n8n --version` indicar que o comando não foi encontrado, certifique-se de que o diretório binário global do npm está na `PATH` do utilizador. O caminho de instalação habitual é `C:\Users\<username>\AppData\Roaming\npm`. 
> Adicione este caminho à PATH do utilizador (Edit the system environment variables > Environment Variables > Edit User Path) e recarregue o terminal. 

<!-- @os:end -->

<!-- @os:linux -->
Vamos agora utilizar o serviço Podman para containerizar a nossa instalação do n8n.

Transfira o seguinte para um diretório à sua escolha: [compose.yml](assets/compose.yml)

Nesse diretório, execute o seguinte comando:
```bash
podman compose up -d
```

Isto deverá instalar o n8n e gravar os dados num armazenamento persistente.

Inicie o n8n digitando `localhost:5678` na barra de endereços do seu browser.
<!-- @os:end -->

<!-- @os:windows -->
## Iniciar o n8n

Inicie o n8n a partir do terminal:

```bash
n8n start
```

<!-- @test:id=n8n-start-windows timeout=300 hidden=True -->
```powershell
$N8N_CMD = "$env:APPDATA\npm\n8n.cmd"
$p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$N8N_CMD`" start" -NoNewWindow -PassThru
try {
  $ok = $false
  for ($i=0; $i -lt 120; $i++) {
    # Check HTTP status code only (body may be empty)
    $code = curl.exe -s -o NUL -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz
    if ($LASTEXITCODE -eq 0 -and $code -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 1
  }
  if (-not $ok) { throw "n8n not ready on http://127.0.0.1:5678/healthz" }
  Write-Host "OK: n8n server is responding"
} finally {
  # Kill the process actually listening on 5678
  $conn = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($conn) { Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue }
  # Also kill wrapper pid just in case
  if ($p -and -not $p.HasExited) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue }
}
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=n8n-start-linux timeout=300 hidden=True -->
```bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
p=""
cleanup() {
  if [ -n "${p:-}" ] && kill -0 "$p" 2>/dev/null; then
    kill "$p" 2>/dev/null || true
    sleep 2
    kill -9 "$p" 2>/dev/null || true
  fi
}
trap cleanup EXIT

n8n start >/tmp/n8n-test.log 2>&1 &
p=$!

ok=false
for i in $(seq 1 120); do
  code="$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://127.0.0.1:5678/healthz || true)"
  if [ "$code" = "200" ]; then
    ok=true
    break
  fi
  sleep 1
done

if [ "$ok" != "true" ]; then
  echo "n8n not ready on http://127.0.0.1:5678/healthz"
  exit 1
fi

echo "OK: n8n server is responding"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
O n8n inicia um servidor web local. Prima `'o'` ou abra o seu browser em `http://localhost:5678` para aceder ao editor.
<!-- @os:end -->


> **Dica**: Mantenha a janela do terminal aberta enquanto utiliza o n8n. Fechá-la pode parar o servidor.

## Iniciar o Lemonade

O Lemonade é o servidor local que executará um modelo e se ligará ao n8n. 

<!-- @os:linux -->
Abra a GUI do Lemonade clicando no ícone do Lemonade na barra de tarefas. Aqui pode navegar pelos modelos, backends e carregar os modelos pré-instalados.
<!-- @os:end -->

<!-- @os:windows -->
Abra a GUI do Lemonade clicando no ícone do Lemonade. Clique com o botão direito no ícone da bandeja para abrir a aplicação. Depois, pode adicionar modelos, backends e carregar os modelos pré-instalados.
<!-- @os:end -->

>**Dica**: Uma vez em execução, a GUI do Lemonade também está acessível em http://localhost:13305

Em alternativa, pode abrir um terminal e executar `lemonade list` para ver que modelos estão instalados. Depois, execute:

<!-- @device:halo_box -->
<!-- @os:linux -->
```bash
lemonade run gpt-oss-120b-Q4_K_M --llamacpp vulkan
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @os:end -->
<!-- @device:end -->

<!-- @device:halo -->
```bash
lemonade run gpt-oss-120b-GGUF --llamacpp vulkan
```
<!-- @device:end -->

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
```bash
lemonade run gpt-oss-20b-GGUF --llamacpp vulkan
```
<!-- @device:end -->


## Configurar o Fluxo de Trabalho

### Passo 1: Registar-se ou Iniciar Sessão no n8n

Quando abrir o n8n pela primeira vez, será solicitado a criar uma conta ou iniciar sessão:

1. Abra `http://localhost:5678` no seu browser
2. Crie uma nova conta local com o seu email, ou inicie sessão se já tiver uma
3. Depois de iniciar sessão, verá o painel do n8n

> **Dica**: Se ficar bloqueado fora da sua conta, tente `n8n user-management:reset`

### Passo 2: Importar o Fluxo de Trabalho

Disponibilizámos um fluxo de trabalho pré-criado que pode importar diretamente:

1. Transfira o seguinte ficheiro de fluxo de trabalho: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Clique em **Start from Scratch** para abrir o editor de fluxo de trabalho. Em alternativa, clique no botão + no canto superior esquerdo e, em seguida, em **Add workflow**.
3. Clique no menu **...** (três pontos) na barra superior direita e selecione **Import from file**
4. Selecione o ficheiro `financial-news-workflow.json` transferido
5. O fluxo de trabalho aparecerá na tela
### Passo 3: Compreender o Fluxo de Trabalho

O fluxo de trabalho importado contém 9 nós ligados entre si:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nó | Finalidade |
|------|---------|
| **When clicking 'Execute workflow'** | Acionador manual para iniciar o fluxo de trabalho |
| **Fetch Financial News Webpage** | Pedido HTTP GET para `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Nó de espera para garantir que o conteúdo da página é totalmente carregado |
| **Extract News Headlines & Text** | Nó HTML que extrai títulos, escolhas do editor, principais notícias e notícias regionais utilizando seletores CSS |
| **Clean Extracted News Data** | Nó Set que combina todos os dados extraídos num único campo de texto |
| **AI Financial News Summarizer** | Agente de IA que processa as notícias com uma instrução de sistema de analista financeiro |
| **Lemonade Chat Model** | Liga ao seu servidor Lemonade local que está a executar o LLM |
| **Structured Output Parser** | Formata a saída da IA como JSON estruturado |
| **Convert to File** | Converte o resumo num ficheiro transferível |

### Passo 4: Configurar as Credenciais do Lemonade

Antes de executar o fluxo de trabalho, é necessário ligá-lo ao seu servidor Lemonade local:

1. Faça duplo clique no nó **Lemonade Chat Model** no n8n
2. No menu suspenso **Credential to connect with**, selecione **Create New Credential**
3. Introduza os valores na tabela abaixo e clique em guardar.
4. Escolha o modelo relevante que tem carregado no Lemonade Server.

  | Campo | Valor |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Nota**: Antes de testar, execute `lemonade status` num terminal para confirmar que o servidor Lemonade está em execução.
<!-- @device:halo_box -->
> Este fluxo de trabalho utiliza o GPT-OSS-120B, que vem pré-instalado no Lemonade. Pode alterar isto para outros modelos carregados nas definições do nó Lemonade Chat Model.
<!-- @device:end -->

### Passo 5: Testar o Fluxo de Trabalho

1. Certifique-se de que o Lemonade está em execução com um modelo carregado
2. Clique em **Execute workflow** na parte inferior central da tela
3. Observe cada nó a ser executado da esquerda para a direita — ficam verdes quando concluídos
4. Faça duplo clique no nó **AI Financial News Summarizer** para ver o resumo gerado no painel inferior.
5. Faça duplo clique no nó **Convert to File** para transferir o ficheiro de texto correspondente no painel inferior.

## Compreender o Agente de IA

O AI Financial News Summarizer utiliza uma instrução de sistema concebida para análise financeira:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

O agente recebe os dados de notícias limpos e produz um resumo estruturado com o sentimento do mercado.

### Guardar o Seu Fluxo de Trabalho

Clique no nome do fluxo de trabalho na parte superior e mude o nome, se desejar. Os fluxos de trabalho guardam-se automaticamente à medida que trabalha.

## Próximos Passos

- **Agendar automação**: Substitua o Manual Trigger por um **Schedule Trigger** para executar diariamente
- **Enviar notificações**: Adicione um nó **Discord**, **Slack** ou **Email** para receber os resumos
- **Experimentar diferentes modelos**: Altere o modelo no nó Lemonade Chat Model para experimentar diferentes LLMs
- **Personalizar a extração**: Modifique os seletores CSS do nó HTML Extract para direcionar a extração para diferentes secções de notícias
- **Experimentar diferentes backends**: o n8n também suporta [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio, e outros backends de LLM locais

### Explorar Modelos do n8n

O n8n tem centenas de modelos de fluxo de trabalho pré-construídos. Navegue pela biblioteca oficial de modelos em:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Pesquise por "AI", "LLM" ou "automation" para encontrar fluxos de trabalho que pode importar e personalizar.

Para mais informações, consulte a [Documentação do n8n](https://docs.n8n.io/).

<!-- @os:linux -->
<!-- @test:id=lemonade-unload-linux timeout=60 hidden=True -->
```bash
# CI cleanup: unload the model so the GPU pool is free
lemonade unload || true
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @test:id=lemonade-unload-windows timeout=60 hidden=True -->
```powershell
# CI cleanup: unload the model so the GPU pool is free
lemonade unload
exit 0
```
<!-- @test:end -->
<!-- @os:end -->