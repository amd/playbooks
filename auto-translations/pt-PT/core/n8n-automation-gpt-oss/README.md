<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Tradução automática.** Esta página foi traduzida automaticamente a partir do inglês e não foi revista por um humano. Pode conter erros, e determinadas instruções, comandos, transferências, disponibilidade de produtos ou outro conteúdo podem variar consoante o idioma ou a região. Em caso de qualquer inconsistência ou discrepância, prevalece a versão original em inglês do playbook.
<!-- auto-translated-disclaimer:end -->

# <!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

## Visão geral

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este playbook requer, no mínimo, **32GB** de memória do sistema.
<!-- @device:end -->

O n8n é uma plataforma de automação de fluxos de trabalho que permite conectar aplicações e serviços através de um editor visual baseado em nós.

Este playbook ensina-o a configurar um resumidor de notícias financeiras com IA que recolhe as últimas manchetes de negócios de um feed RSS de notícias e utiliza um LLM local em execução no seu sistema para gerar um resumo orientado para investidores.

## O que vai aprender

- Como instalar e iniciar o n8n
- Importar e configurar um fluxo de trabalho pré-criado
- Ligar ao Lemonade utilizando a integração nativa do n8n
- Compreender os nós do fluxo de trabalho e o fluxo de dados

## O que é o Lemonade?

O [Lemonade](https://lemonade-server.ai) é uma plataforma de disponibilização de LLM local criada para hardware AMD. Fornece uma API compatível com OpenAI que é executada inteiramente na sua máquina — os seus dados nunca saem do dispositivo.

Neste playbook, utilizamos o Lemonade para disponibilizar um LLM local ao qual o n8n se liga para tarefas de IA.

O n8n inclui um **nó Lemonade nativo** (`Lemonade Chat Model`) que fornece uma integração de primeira classe - sem necessidade de configuração manual. Isto torna simples a ligação do seu LLM local a fluxos de trabalho de automação.

<!-- @device:halo_box,halo,stx,krk -->
## Definir a configuração de memória

<!-- @require:memory-config -->
<!-- @device:end -->

<!-- @device:halo_box -->
## Verificar atualizações de software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalar os pré-requisitos de software
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
Instale o n8n globalmente utilizando o npm.

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
> **Dica**: Os utilizadores do Windows podem precisar de modificar a sua Política de Execução do PowerShell (por exemplo,
> definindo-a para RemoteSigned ou Unrestricted) antes de executar alguns comandos do Powershell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problema de PATH**: Se `n8n --version` indicar que o comando não foi encontrado, certifique-se de que o diretório bin global do npm está no `PATH` do utilizador. O caminho de instalação habitual é `C:\Users\<username>\AppData\Roaming\npm`.
> Adicione-o ao caminho do utilizador (Editar as variáveis de ambiente do sistema > Variáveis de Ambiente > Editar Caminho do Utilizador) e recarregue o terminal.

<!-- @os:end -->

<!-- @os:linux -->
Vamos agora utilizar o serviço Podman para colocar em contentor a nossa instalação do n8n.

Por favor, descarregue o seguinte para um diretório à sua escolha: [compose.yml](assets/compose.yml)

Nesse diretório, execute o seguinte comando:
```bash
podman compose up -d
```

Isto deverá instalar o n8n e gravar em armazenamento persistente.

Inicie o n8n digitando `localhost:5678` na barra de endereço do seu navegador.
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
O n8n inicia um servidor web local. Prima `'o'` ou abra o seu navegador em `http://localhost:5678` para aceder ao editor.
<!-- @os:end -->


> **Dica**: Mantenha a janela do terminal aberta enquanto utiliza o n8n. Fechá-la pode parar o servidor.

## Iniciar o Lemonade

O Lemonade é o servidor local que irá executar um modelo e ligar-se ao n8n.

<!-- @os:linux -->
Abra a GUI do Lemonade clicando no Ícone Lemonade na barra de tarefas. Aqui pode explorar modelos, backends e carregar os modelos pré-instalados.
<!-- @os:end -->

<!-- @os:windows -->
Abra a GUI do Lemonade clicando no Ícone Lemonade. Clique com o botão direito no ícone da bandeja para abrir a aplicação. Depois, pode adicionar modelos, backends e carregar os modelos pré-instalados.
<!-- @os:end -->

>**Dica**: Uma vez em execução, a GUI do Lemonade também está acessível em http://localhost:13305

Em alternativa, pode abrir um terminal e executar `lemonade list` para ver quais os modelos instalados. Depois, execute:

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


## Configurar o fluxo de trabalho

### Passo 1: Registar-se ou iniciar sessão no n8n

Quando abrir o n8n pela primeira vez, será convidado a criar uma conta ou iniciar sessão:

1. Abra `http://localhost:5678` no seu navegador
2. Crie uma nova conta local com o seu email, ou inicie sessão se já tiver uma
3. Depois de iniciar sessão, verá o painel do n8n

> **Dica**: Se ficar bloqueado fora da sua conta, tente `n8n user-management:reset`

### Passo 2: Importar o fluxo de trabalho

Disponibilizámos um fluxo de trabalho pré-criado que pode importar diretamente:

1. Descarregue o seguinte ficheiro de fluxo de trabalho: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Clique em **Start from Scratch** para abrir o editor de fluxos de trabalho. Em alternativa, clique no botão + no canto superior esquerdo e, depois, em **Add workflow**.
3. Clique no menu **...** (três pontos) na barra superior direita e selecione **Import from file**
4. Selecione o ficheiro `financial-news-workflow.json` descarregado
5. O fluxo de trabalho aparecerá na tela
### Passo 3: Compreender o Workflow

O workflow importado contém 8 nós ligados entre si:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nó | Finalidade |
|------|---------|
| **When clicking 'Execute workflow'** | Acionador manual para iniciar o workflow |
| **Fetch Financial News Feed** | Nó RSS Read que obtém as manchetes de negócios mais recentes de um feed RSS (por predefinição, o feed de Negócios do NYT, sem necessidade de chave de API) |
| **Aggregate Headlines** | Nó Aggregate que recolhe os títulos das manchetes e os resumos de cada item do feed numa única lista |
| **Clean Extracted News Data** | Nó Set que combina todas as manchetes num único campo de texto |
| **AI Financial News Summarizer** | Agente de IA que processa as notícias com uma instrução de sistema de analista financeiro |
| **Lemonade Chat Model** | Liga ao seu servidor Lemonade local que executa o LLM |
| **Structured Output Parser** | Formata a saída da IA como JSON estruturado |
| **Convert to File** | Converte o resumo num ficheiro para transferência |

> **Dica**: Para utilizar uma fonte de notícias diferente, faça duplo clique no nó **Fetch Financial News Feed** e substitua o URL por qualquer feed RSS de negócios ou mercados que prefira.

### Passo 4: Configurar as Credenciais do Lemonade

Antes de executar o workflow, precisa de o ligar ao seu servidor Lemonade local:

1. Faça duplo clique no nó **Lemonade Chat Model** no n8n
2. No menu pendente **Credential to connect with**, selecione **Create New Credential**
3. Introduza os valores na tabela abaixo e clique em guardar.
4. Escolha o modelo relevante que tem carregado no Lemonade Server.

  | Campo | Valor |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Nota**: Antes de testar, execute `lemonade status` num terminal para confirmar que o servidor Lemonade está em execução.
<!-- @device:halo_box -->
> Este workflow utiliza o GPT-OSS-120B, que já vem pré-instalado no Lemonade. Pode alterar isto para outros modelos carregados nas definições do nó Lemonade Chat Model.
<!-- @device:end -->

### Passo 5: Testar o Workflow

1. Certifique-se de que o Lemonade está em execução com um modelo carregado
2. Clique em **Execute workflow** na parte inferior central da tela
3. Observe cada nó a executar da esquerda para a direita — ficam verdes quando concluídos
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

### Guardar o Seu Workflow

Clique no nome do workflow na parte superior e mude-o de nome, se desejar. Os workflows são guardados automaticamente à medida que trabalha.

## Próximos Passos

- **Agendar automação**: Substitua o Manual Trigger por um **Schedule Trigger** para executar diariamente
- **Enviar notificações**: Adicione um nó **Discord**, **Slack** ou **Email** para receber resumos
- **Experimentar modelos diferentes**: Altere o modelo no nó Lemonade Chat Model para experimentar diferentes LLMs
- **Alterar a fonte de notícias**: Aponte o nó **Fetch Financial News Feed** para um feed RSS diferente para seguir outras secções ou publicações
- **Experimentar backends diferentes**: o n8n também suporta [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio, e outros backends de LLM locais

### Explorar os Modelos do n8n

O n8n tem centenas de modelos de workflow pré-criados. Explore a biblioteca oficial de modelos em:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Pesquise por "AI", "LLM" ou "automation" para encontrar workflows que possa importar e personalizar.

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