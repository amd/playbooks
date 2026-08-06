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

# Desenvolvimento Remoto com o AMD Sync

## Visão Geral

O **AMD Sync** transforma seu laptop em um cockpit remoto para o AMD Ryzen™ AI Halo. Elimine a configuração manual de SSH, chaves e IDE — instale o AMD Sync e tenha acesso com um clique a um terminal remoto, VS Code, JupyterLab e um painel ao vivo de GPU/CPU/memória no Ryzen AI Halo.

Sua máquina local permanece familiar; todo comando, notebook e modelo é executado no Ryzen AI Halo.

> **Dica**: Esta página conterá quaisquer novas atualizações do AMDSync. 

## O Que Você Vai Aprender

- Habilitar o SSH no Ryzen AI Halo e conectar-se a ele a partir do AMD Sync
- Iniciar VS Code, Terminal, JupyterLab e Métricas ao Vivo no Ryzen AI Halo com um clique
- Organizar o trabalho remoto usando as pastas de projeto gerenciadas do AMD Sync

---

## Conceitos Fundamentais

O AMD Sync tem dois lados: um **cliente** (seu laptop, executando o aplicativo AMD Sync) e um **servidor** (o Ryzen AI Halo, executando um servidor SSH pelo qual o AMD Sync cria um túnel). Tudo o que você inicia a partir do AMD Sync — VS Code, um terminal, um notebook — abre localmente, mas é executado no Ryzen AI Halo.

> **Clientes suportados:** Windows 11 e Linux. macOS não é suportado.

---

## Etapa 1 — Habilitar o SSH no Ryzen AI Halo


> **Observação:** No Windows, o Ryzen AI Halo vem com o servidor SSH *desativado por padrão*. No Linux, ele vem com o servidor SSH *ativado por padrão*.

1. No Ryzen AI Halo, abra o **AMD Ryzen™ AI Developer Center**.
2. Vá até a aba **Remote**.
3. Ative a opção **SSH Server**.
4. Anote o **IP Address**, a **Port** e o **Username** exibidos em **Server Information** — você vai colá-los no AMD Sync.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **Observação:** Este é o AMD Developer Center para Windows. O do Linux pode ter uma interface diferente, mas com funcionalidades remotas semelhantes.

> **Dica:** O AMD Sync solicita a **senha de login do SO** desse usuário, não uma senha do Developer Center.

---

## Etapa 2 — Instalar o AMD Sync no Seu Cliente

O AMD Sync é executado no Windows 11 e no Linux. Baixe o instalador do seu sistema operacional e siga as etapas abaixo. Após a instalação, clique em **Accept & Install** na tela **Get Started** — o AMD Sync é iniciado automaticamente ao concluir.

### Windows

[Baixar AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. Dê um duplo clique em `AMDSyncInstaller.exe`.
2. Clique em **Accept & Install**.

> Se o Firewall do Windows solicitar permissão, permita o acesso do AMD Sync à rede para que ele possa alcançar o Ryzen AI Halo via SSH.

### Linux

Clique no link para baixar o formato de sua preferência:

| Formato | Download | Comando de instalação |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **Observação:** O Ubuntu App Center pode sinalizar um `.deb` aberto localmente como *"Potencialmente inseguro."* Esse é o alerta padrão para qualquer instalador local de terceiros. Se o duplo clique no `.deb` falhar, use o comando de terminal acima.

---

## Etapa 3 — Conectar-se ao Seu Ryzen AI Halo

Na primeira execução, o AMD Sync exibe o formulário **Add a Remote Device**. Preencha-o usando os valores da aba **Remote** do Developer Center.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| Campo | Observações |
|-------|-------|
| **Device Name** *(opcional)* | Um rótulo amigável como `Ryzen AI Halo`. O padrão é `Device 1`, `Device 2`, … |
| **Hostname or IP** | Da aba Remote |
| **SSH Port** | Da aba Remote (somente números) |
| **Username** | O nome da sua conta de sistema operacional no Ryzen AI Halo |
| **Password** | Sua senha de login do sistema operacional — mascarada enquanto você digita |

Clique em **Add Device**. Após uma breve tela de carregamento, você verá **"Connection Successful"** e chegará à visualização inicial, que fica na bandeja do sistema. Clique fora da janela para fechá-la; o AMD Sync continua em execução e fica a um clique de distância.

> **Se a conexão falhar,** o AMD Sync retorna ao formulário com seus valores preservados. As causas mais comuns são o SSH desativado no Ryzen AI Halo, senha incorreta ou os dois dispositivos estarem em redes diferentes.

---

## Etapa 4 — Iniciar Sua Primeira Ferramenta Remota

A visualização inicial oferece cinco componentes de um clique — todos disponíveis independentemente do sistema operacional em que o cliente e o Ryzen AI Halo estão sendo executados.

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| Componente | O que faz |
|-----------|--------------|
| **Directory** | Seleciona a pasta no Ryzen AI Halo em que o VS Code, o Terminal e o JupyterLab serão abertos. O padrão é um espaço de trabalho gerenciado `Documents/AMD_Sync`. |
| **VS Code** | Abre o VS Code localmente com um túnel SSH para a pasta selecionada. |
| **Terminal** | Abre um terminal local conectado via SSH ao Ryzen AI Halo, na pasta selecionada. |
| **JupyterLab** | Inicia um projeto de notebook conectado via SSH ao Ryzen AI Halo, restrito à pasta selecionada. |
| **Live Metrics** | Visualização em tempo real da utilização de GPU, memória e CPU no Ryzen AI Halo. |

### Experimente o VS Code

Para sua primeira execução, experimente o **VS Code**.

1. Deixe **Directory** com o valor padrão `~/Documents/AMD_Sync`.
2. Clique em **VS Code**.
3. O AMD Sync cria `Documents/AMD_Sync/Project_1` no Ryzen AI Halo e abre o VS Code localmente, com túnel para essa pasta.

Agora você está editando arquivos que residem no Ryzen AI Halo com sua configuração local do VS Code. Crie `helloworld.py`, adicione `print("hello world")`, abra o terminal integrado (`` Ctrl + ` ``) e execute-o:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

A barra de status exibe **SSH: Linux** — prova de que seu código está sendo executado no Ryzen AI Halo, e não no seu laptop.
### Experimente o Terminal

Clique em **Terminal** para acessar a mesma pasta via SSH sem sair do teclado.

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

No Windows, o terminal padrão é o **PowerShell** — mude para **Windows Command Prompt** no menu Settings, se preferir. No Linux, o AMD Sync usa o terminal padrão do sistema.

---

## Como o Directory Funciona

O menu suspenso **Directory** é o controle mais importante do AMD Sync — ele decide onde cada ferramenta que você inicia é colocada no Ryzen AI Halo.

- **`~/Documents/AMD_Sync` (padrão)** — Iniciar o VS Code ou o JupyterLab a partir daqui cria automaticamente uma nova pasta de projeto (`Project_1`, `Project_2`, … para o VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … para o JupyterLab).
- **Pastas de projeto existentes** — Qualquer subpasta imediata de `AMD_Sync` (incluindo pastas que você cria manualmente no Ryzen AI Halo) aparece no menu suspenso. A última pasta usada se torna o padrão na próxima vez.
- **Caminhos personalizados** — Digite qualquer caminho absoluto para abrir uma pasta em outro local do Ryzen AI Halo. O AMD Sync apenas *abre* essa pasta — ele não cria pastas fora de `AMD_Sync`, e caminhos personalizados não são salvos entre sessões.

Se um caminho personalizado não funcionar, o AMD Sync informa o motivo: sintaxe inválida, a pasta não existe ou o caminho aponta para um arquivo.

---

## Live Metrics e JupyterLab

- **Live Metrics** — Um painel em tempo real de uso de GPU, memória e CPU. A forma mais rápida de confirmar que uma execução de treinamento remota está realmente utilizando o hardware.
- **JupyterLab** — Um projeto de notebook completo conectado via SSH ao Ryzen AI Halo, com seu próprio terminal integrado para combinar células de notebook e comandos de shell sem sair da interface.

---

## Settings e Múltiplos Dispositivos

O menu **Settings** tem três abas:

| Aba | O que abrange |
|-----|----------------|
| **Devices** | Lista todos os Ryzen AI Halo aos quais você já se conectou com sucesso. Reconecte, edite credenciais ou adicione um novo dispositivo. |
| **Information** | Links para documentação e suporte do fórum. |
| **Customize** | Reposicione o aplicativo na sua área de trabalho, altere o tipo de terminal (somente Windows) e verifique atualizações do AMD Sync. |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **Tipo de terminal (Windows)** — Escolha entre **PowerShell** (padrão) e **Windows Command Prompt**.
- **Tipo de terminal (Linux)** — Apenas o terminal padrão do sistema está disponível.
- **Atualizações do aplicativo** — Esta aba é o local certo para verificar e instalar novas versões do AMD Sync diretamente pela interface; não é necessário um atualizador separado.

> Um dispositivo só aparece em **Devices** após uma primeira conexão bem-sucedida, então tentativas malsucedidas não poluem a lista.

---

## Solução de Problemas

- **A conexão falha imediatamente** — Confirme se o servidor SSH está habilitado na aba **Remote** do Ryzen AI Halo, no Developer Center.
- **Erro de senha incorreta** — Use a **senha de login do sistema operacional** no Ryzen AI Halo, não senhas obtidas no Developer Center.
- **O botão do VS Code não faz nada** — Instale o VS Code na sua máquina cliente em [code.visualstudio.com](https://code.visualstudio.com).
- **Ícone do AMD Sync ausente na bandeja (Linux/GNOME)** — Instale e habilite a extensão AppIndicator.
- **O arquivo `.deb` não abre pelo gerenciador de arquivos** — Use `sudo apt install ./AMDSyncInstaller.deb` em um terminal.

---