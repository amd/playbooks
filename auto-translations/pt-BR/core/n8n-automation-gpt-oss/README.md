<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Este playbook usa tags especiais que o GitHub não consegue renderizar. Visite [amd.com/playbooks](https://amd.com/playbooks) para visualizar este conteúdo corretamente.
<!-- @github-only:end -->

## Visão Geral

<!-- @device:stx,krk,rx7900xt,rx9070xt,r9700 -->
> [!NOTE]
> Este playbook requer um mínimo de **32GB** de memória do sistema.
<!-- @device:end -->

n8n é uma plataforma de automação de fluxos de trabalho que permite conectar aplicativos e serviços usando um editor visual baseado em nós.

Este playbook ensina como configurar um resumidor de notícias financeiras com inteligência artificial que coleta dados da seção de negócios do AP News, extrai manchetes principais e usa um LLM local em execução no seu sistema para gerar um resumo voltado para investidores.

## O Que Você Vai Aprender

- Como instalar e iniciar o n8n
- Importar e configurar um fluxo de trabalho pré-construído
- Conectar ao Lemonade usando a integração nativa do n8n
- Entender os nós do fluxo de trabalho e o fluxo de dados

## O Que é o Lemonade?

[Lemonade](https://lemonade-server.ai) é uma plataforma local de serviço de LLM criada para hardware AMD. Ela fornece uma API compatível com OpenAI que roda inteiramente na sua máquina — seus dados nunca saem do seu dispositivo.

Neste playbook, usamos o Lemonade para servir um LLM local ao qual o n8n se conecta para tarefas com inteligência artificial.

O n8n inclui um **nó nativo do Lemonade** (`Lemonade Chat Model`) que oferece uma integração de primeira classe — sem necessidade de configuração manual. Isso torna simples a conexão do seu LLM local a fluxos de trabalho de automação.

## Configurando a Configuração de Memória

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Verificar Atualizações de Software

<!-- @require:software-update -->
<!-- @device:end -->

## Instalando Pré-requisitos de Software
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

## Instalando o n8n
<!-- @os:windows -->
Instale o n8n globalmente usando npm.

> **Nota**: Você pode ver alguns avisos do npm. Isso é esperado.

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
> **Dica**: Usuários do Windows podem precisar modificar a Política de Execução do PowerShell (por exemplo,
> definindo-a como RemoteSigned ou Unrestricted) antes de executar alguns comandos do PowerShell.
<!-- @os:end -->


<!-- @os:windows -->
> **Problema com PATH**: Se `n8n --version` indicar que o comando não foi encontrado, certifique-se de que o diretório bin global do npm está no `PATH` do usuário. O caminho de instalação usual é `C:\Users\<username>\AppData\Roaming\npm`.
> Adicione isso ao caminho do usuário (Editar as variáveis de ambiente do sistema > Variáveis de Ambiente > Editar Caminho do Usuário) e recarregue o terminal.

<!-- @os:end -->

<!-- @os:linux -->
Agora vamos usar o serviço Podman para containerizar nossa instalação do n8n.

Por favor, baixe o seguinte em um diretório de sua escolha: [compose.yml](assets/compose.yml)

Nesse diretório, execute o seguinte comando:
```bash
podman compose up -d
```

Isso deve instalar o n8n e gravar em um armazenamento persistente.

Inicie o n8n digitando `localhost:5678` na barra de endereços do seu navegador.
<!-- @os:end -->

<!-- @os:windows -->
## Iniciando o n8n

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
O n8n inicia um servidor web local. Pressione `'o'` ou abra seu navegador em `http://localhost:5678` para acessar o editor.
<!-- @os:end -->


> **Dica**: Mantenha a janela do terminal aberta enquanto usa o n8n. Fechá-la pode parar o servidor.

## Iniciando o Lemonade

O Lemonade é o servidor local que executará um modelo e se conectará ao n8n.

<!-- @os:linux -->
Abra a interface gráfica do Lemonade clicando no ícone do Lemonade na barra de tarefas. Você pode navegar por modelos, backends e carregar os modelos pré-instalados a partir daqui.
<!-- @os:end -->

<!-- @os:windows -->
Abra a interface gráfica do Lemonade clicando no ícone do Lemonade. Clique com o botão direito no ícone da bandeja para abrir o aplicativo. Em seguida, você pode adicionar modelos, backends e carregar os modelos pré-instalados.
<!-- @os:end -->

>**Dica**: Uma vez em execução, a interface gráfica do Lemonade também está acessível em http://localhost:13305

Alternativamente, você pode abrir um terminal e executar `lemonade list` para ver quais modelos estão instalados. Em seguida, execute:

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


## Configurando o Fluxo de Trabalho

### Passo 1: Cadastre-se ou Faça Login no n8n

Quando você abrir o n8n pela primeira vez, será solicitado que crie uma conta ou faça login:

1. Abra `http://localhost:5678` no seu navegador
2. Crie uma nova conta local com seu e-mail, ou faça login se já tiver uma
3. Após o login, você verá o painel do n8n

> **Dica**: Se estiver bloqueado fora da sua conta, tente `n8n user-management:reset`

### Passo 2: Importar o Fluxo de Trabalho

Fornecemos um fluxo de trabalho pré-construído que você pode importar diretamente:

1. Baixe o seguinte arquivo de fluxo de trabalho: [financial-news-workflow.json](assets/financial-news-workflow.json)
2. Clique em **Start from Scratch** para abrir o editor de fluxo de trabalho. Alternativamente, clique no botão + no canto superior esquerdo e depois em **Add workflow**.
3. Clique no menu **...** (três pontos) na barra superior direita e selecione **Import from file**
4. Selecione o arquivo `financial-news-workflow.json` baixado
5. O fluxo de trabalho aparecerá na tela


### Passo 3: Entendendo o Fluxo de Trabalho

O fluxo de trabalho importado contém 9 nós conectados:

<p align="center">
  <img src="assets/workflow-overview.png" alt="n8n Financial News Workflow" width="800"/>
</p>

| Nó | Finalidade |
|------|---------|
| **When clicking 'Execute workflow'** | Gatilho manual para iniciar o fluxo de trabalho |
| **Fetch Financial News Webpage** | Requisição HTTP GET para `https://apnews.com/business` |
| **Delay to Ensure Page Load** | Nó de espera para garantir que o conteúdo da página seja totalmente carregado |
| **Extract News Headlines & Text** | Nó HTML que extrai manchetes, destaques do editor, principais notícias e notícias regionais usando seletores CSS |
| **Clean Extracted News Data** | Nó Set que combina todos os dados extraídos em um único campo de texto |
| **AI Financial News Summarizer** | Agente de IA que processa as notícias com um prompt de sistema de analista financeiro |
| **Lemonade Chat Model** | Conecta ao seu servidor Lemonade local que executa o LLM |
| **Structured Output Parser** | Formata a saída da IA como JSON estruturado |
| **Convert to File** | Converte o resumo em um arquivo para download |

### Passo 4: Configurar as Credenciais do Lemonade

Antes de executar o fluxo de trabalho, você precisa conectá-lo ao seu servidor Lemonade local:

1. Clique duas vezes no nó **Lemonade Chat Model** no n8n
2. No menu suspenso **Credential to connect with**, selecione **Create New Credential**
3. Insira os valores na tabela abaixo e clique em salvar.
4. Escolha o modelo relevante que você carregou no Lemonade Server.

  | Campo | Valor |
  |-------|-------|
  | **Base URL** | `http://localhost:13305/api/v1` |
  | **API Key** | `lemonade` |

> **Nota**: Antes de testar, execute `lemonade status` em um terminal para confirmar que o servidor Lemonade está em execução.
<!-- @device:halo_box -->
> Este fluxo de trabalho usa GPT-OSS-120B e ele vem pré-instalado no Lemonade. Você pode alterá-lo para outros modelos carregados nas configurações do nó Lemonade Chat Model.
<!-- @device:end -->

### Passo 5: Testar o Fluxo de Trabalho

1. Certifique-se de que o Lemonade está em execução com um modelo carregado
2. Clique em **Execute workflow** na parte inferior central da tela
3. Observe cada nó sendo executado da esquerda para a direita — eles ficam verdes quando concluídos
4. Clique duas vezes no nó **AI Financial News Summarizer** para ver o resumo gerado no painel inferior.
5. Clique duas vezes no nó **Convert to File** para baixar o arquivo de texto correspondente no painel inferior.

## Entendendo o Agente de IA

O AI Financial News Summarizer usa um prompt de sistema projetado para análise financeira:

```
You are an AI financial analyst. Your role is to read, understand, and
summarize key financial news from today. The goal is to provide investors
with a clear and concise market overview to support better investment decisions.

Investor Outlook
Today's news points to [bullish/bearish/neutral] sentiment. Watch for
[economic event/earnings report] tomorrow, which could influence market direction.
```

O agente recebe os dados de notícias processados e gera um resumo estruturado com o sentimento do mercado.

### Salvando Seu Fluxo de Trabalho

Clique no nome do fluxo de trabalho no topo e renomeie-o se desejar. Os fluxos de trabalho são salvos automaticamente enquanto você trabalha.

## Próximos Passos

- **Agendar automação**: Substitua o Gatilho Manual por um **Schedule Trigger** para executar diariamente
- **Enviar notificações**: Adicione um nó do **Discord**, **Slack** ou **Email** para receber resumos
- **Experimentar modelos diferentes**: Altere o modelo no nó Lemonade Chat Model para experimentar diferentes LLMs
- **Personalizar a extração**: Modifique os seletores CSS do nó HTML Extract para direcionar diferentes seções de notícias
- **Experimentar backends diferentes**: O n8n também suporta [Ollama](https://n8n.io/workflows/?integrations=Ollama+Chat+Model), LM Studio e outros backends de LLM local

### Explorar Templates do n8n

O n8n possui centenas de templates de fluxos de trabalho pré-construídos. Navegue pela biblioteca oficial de templates em:

**[https://n8n.io/workflows/](https://n8n.io/workflows/)**

Pesquise por "AI", "LLM" ou "automation" para encontrar fluxos de trabalho que você pode importar e personalizar.

Para mais informações, consulte a [Documentação do n8n](https://docs.n8n.io/).