<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинный перевод.** Эта страница была автоматически переведена с английского языка и не прошла проверку человеком. Она может содержать ошибки, а некоторые инструкции, команды, файлы для загрузки, сведения о доступности продуктов или иное содержимое могут отличаться в зависимости от языка или региона. В случае каких-либо несоответствий или расхождений преимущественную силу имеет оригинальная версия playbook на английском языке.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Обзор

Разработчики тратят много времени на небольшие повторяющиеся циклы: просмотр
помеченных pull request'ов, ответы на комментарии GitHub, разбор новых issue,
превращение тредов в Slack в заметки для стендапов или последующие действия
после инцидентов, а также отслеживание сигналов о релизах или исследованиях.
Каждый из этих циклов знаком, но всё равно требует суждения: собрать нужный
контекст, решить, что важно, и опубликовать понятное обновление там, где
команда уже работает.

[Автоматизации OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
превращают эти циклы в запланированные или запускаемые по событию диалоги
агента: прогоны, в которых ИИ-агент программного обеспечения может читать
контекст, вызывать инструменты и формировать обновление. Общие шаблоны
автоматизаций в каталоге расширений OpenHands следуют этой схеме для проверки
pull request'ов GitHub, мониторинга репозитория, триажа issue Linear,
разборов инцидентов, дайджестов стендапов в Slack и исследовательских
сводок: автоматизация просыпается, использует настроенные интеграции, такие
как GitHub или Slack, для получения контекста, рассуждает над этим контекстом
с помощью большой языковой модели (LLM) и записывает результат обратно.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — это локальная
плоскость управления для создания и тестирования таких автоматизаций. В этом
playbook он запускает OpenHands Agent Server, backend-процесс, который
выполняет диалоги агента, и подключает агента к внешним сервисам, таким как
GitHub и Slack.

Чтобы рабочий процесс оставался на вашей системе AMD, агент обращается к
локальной модели, обслуживаемой Lemonade Server. Lemonade предоставляет
доступ к этой модели через OpenAI-совместимый API, поэтому Agent Canvas может
настроить её как удалённую конечную точку в стиле OpenAI, при этом модель,
запрос и контекст рабочего процесса остаются локальными.

В этом playbook вы создадите одну конкретную автоматизацию: запланированный
дайджест разработки GitHub-в-Slack. Он использует GitHub для проверки
недавней активности в репозитории, Slack для публикации дайджеста, вызовы
API Agent Canvas для настройки и тестирования автоматизации, а также Lemonade
для локального запуска LLM.

![Диаграмма архитектуры, показывающая GitHub MCP, автоматизацию OpenHands, Lemonade Server и Slack MCP](assets/00-architecture-overview.png)

## Чему вы научитесь

- Как запустить Lemonade Server и убедиться, что локальная модель отвечает на
  запросы чата
- Как запустить Agent Canvas и настроить его Agent Server на локальную LLM
- Как установить серверы Model Context Protocol (MCP) для GitHub и Slack через
  API Agent Server
- Как создать и запустить запланированную автоматизацию OpenHands, которая
  публикует дайджест разработки в Slack
- Как устранять наиболее распространённые сбои локальной модели и автоматизации

## Основные концепции

| Концепция | Что это такое | Роль в этом playbook |
| --- | --- | --- |
| Lemonade Server | Локальная платформа обслуживания LLM, созданная для оборудования AMD, предоставляющая OpenAI-совместимый API. Ваши данные никогда не покидают вашу машину. | Запускает модель, которая обеспечивает работу агента. |
| OpenHands Agent Server | Backend-процесс, который выполняет диалоги агента OpenHands. | Размещает агента, его профиль LLM и его серверы MCP. |
| Agent Canvas | Локальная плоскость управления для OpenHands, которая запускает Agent Server и пользовательский интерфейс для проверки прогонов агента. | Запускает backend-процессы и предоставляет API, который вы вызываете. |
| Сервер MCP | Сервер Model Context Protocol, который предоставляет агенту инструменты для внешнего сервиса, такого как GitHub или Slack. | Позволяет агенту читать GitHub и писать в Slack. |
| Автоматизация OpenHands | Запланированный или запускаемый по событию диалог агента, который получает контекст, рассуждает над ним и записывает результат куда-либо. | Дайджест GitHub-в-Slack, который вы создаёте здесь. |

<!-- @device:stx,krk -->
> [!NOTE]
> Рабочие процессы кодирующих агентов выигрывают от более крупной модели и
> большего окна контекста. Используйте не менее 32 ГБ системной памяти и
> предпочитайте 64 ГБ и более для более крупных моделей GGUF.
<!-- @device:end -->

## Предварительные требования

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Вам потребуется:

- Lemonade Server, установленный согласно стандартному
  [руководству по установке Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 или более поздней версии и `npm`, используемые для установки
  опубликованного CLI Agent Canvas и запуска серверов MCP с помощью `npx`.
- Недавно опубликованный пакет `@openhands/agent-canvas` с
  настройками агента на основе схем, `LLMSummarizingCondenserSettings.max_tokens`
  и поддержкой `custom_tokenizer` для LLM.
- Пакет Python `transformers`, доступный в среде Agent Server.
  Он требуется для подсчёта токенов шаблона чата, когда установлен
  `custom_tokenizer`.
- Токен GitHub с правом чтения репозитория, который вы хотите суммировать.
- Токен бота Slack (`xoxb-...`) с правами `chat:write` и чтения канала.
- Идентификатор команды Slack (`T...`).
- Идентификатор канала Slack (`C...`), в который должен публиковаться дайджест.

Пригласите приложение Slack в целевой канал перед тестированием автоматизации.

## Переменные, используемые в этом playbook

<!-- @device:halo,halo_box,stx,krk -->
<!-- @var:id=lemonade_model value="Qwen3.6-35B-A3B-GGUF" -->
<!-- @device:end -->

```bash
export LEMONADE_BASE_URL="http://127.0.0.1:13305/api/v1"
export LEMONADE_MODEL="Qwen3.6-35B-A3B-GGUF"
export OPENHANDS_LLM_MODEL="openai/${LEMONADE_MODEL}"
export QWEN_CUSTOM_TOKENIZER="Qwen/Qwen3.6-35B-A3B"
export CONDENSER_MAX_TOKENS="56000"
```

Следующие значения вводятся в пользовательский интерфейс Agent Canvas на
последующих шагах. Задайте их здесь, чтобы затем скопировать:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Используйте явное значение `owner/repo` для `GITHUB_REPO_FILTER`. Широкие
шаблоны организаций могут вернуть слишком много контекста MCP для локальных
моделей.

## 1. Запуск Lemonade Server

Запустите модель из CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade предоставляет OpenAI-совместимый API по адресу:

```text
http://127.0.0.1:13305/api/v1
```

Необязательно: если Agent Canvas или исполнитель автоматизации находятся не
на той же машине, опубликуйте конечную точку Lemonade через защищённый
туннель и используйте URL-адрес HTTPS в качестве базового URL-адреса LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Проверка локальной модели

Убедитесь, что Lemonade может обслуживать выбранную модель:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Затем отправьте небольшой запрос чата:

```bash
curl -sS "${LEMONADE_BASE_URL}/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"${LEMONADE_MODEL}"'",
    "messages": [
      {"role": "user", "content": "Reply with exactly: OK"}
    ],
    "temperature": 0,
    "max_tokens": 64
  }' | python3 -m json.tool
```

Если это возвращает массив `choices`, значит Lemonade готов к работе с Agent Canvas.
## 3. Запуск Agent Canvas

Установите опубликованный пакет Agent Canvas и запустите полный стек:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Если глобальная установка npm завершится ошибкой доступа, см. раздел по
устранению проблем с правами npm ниже.

По умолчанию Agent Canvas запускается по адресу `http://localhost:8000`.
Откройте этот адрес в браузере. Локальный бэкенд по умолчанию должен
отображаться на главном экране как исправный.

Команда `agent-canvas` запускает сервер агента, автоматизационный бэкенд и
веб-фронтенд вместе. Для локального запуска OpenHands достаточно всего одной
этой команды. Остальная часть данного руководства настраивает всё через
интерфейс Agent Canvas в вашем браузере.

## 4. Настройка локальной LLM в интерфейсе

При первом запуске Agent Canvas открывает мастер первоначальной настройки. В
этом мастере:

1. Оставьте **OpenHands** выбранным в качестве агента и нажмите **Next**.
2. На экране **Set up your LLM** выберите **Advanced**.
3. Оставьте для **Authentication** значение **API key**.
4. Установите **Custom Model** равным значению `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Установите **Base URL** равным `http://127.0.0.1:13305/api/v1`.
6. В поле **API Key** введите любой непустой заполнитель, например
   `lemonade-local`. Lemonade не требует реального ключа, но клиенту
   OpenHands нужно какое-то значение для отправки.

Поля подключения должны выглядеть следующим образом. Поле API-ключа скрыто
интерфейсом.

![Первоначальные настройки LLM Advanced в Agent Canvas с моделью Lemonade и локальным базовым URL](assets/01-llm-advanced-settings.png)

Затем выберите **All** и заполните дополнительные поля локальной модели:

1. Прокрутите до **Custom Tokenizer** и установите значение
   `Qwen/Qwen3.6-35B-A3B`.
2. Прокрутите до **LiteLLM Extra Body** и установите значение
   `{"enable_thinking": true}`.
3. Нажмите **Next**.

![Вкладка All первоначальных настроек LLM в Agent Canvas с пользовательским токенизатором Qwen](assets/02-llm-all-tokenizer-settings.png)

![Вкладка All первоначальных настроек LLM в Agent Canvas с настроенным дополнительным телом LiteLLM](assets/03-llm-all-extra-body-settings.png)

Настройки LLM должны выглядеть так:

| Поле | Значение |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Префикс `openai/` указывает LiteLLM использовать формат запросов, совместимый
с OpenAI, для обращения к эндпоинту Lemonade. Пользовательский токенизатор —
это оригинальный токенизатор Hugging Face для модели в формате GGUF; он
позволяет OpenHands подсчитывать те же токены шаблона чата, которые видит
локальный сервер модели. Текущая форма настройки LLM при первом запуске не
показывает настройки конденсатора (condenser). Если в вашей сборке Agent
Canvas позже появятся настройки конденсатора в разделе **Settings > LLM**,
используйте `llm_summarizing` и установите максимальное количество токенов
ниже контекстного окна Lemonade, например `56000`.

## 5. Установка MCP-серверов GitHub и Slack

В интерфейсе Agent Canvas откройте **Customize** (или **Settings > MCP**),
чтобы добавить MCP-серверы, которые предоставляют агенту инструменты для
работы с GitHub и Slack. Значения токенов отправляются только на ваш
локальный Agent Server и сохраняются в виде зашифрованных настроек.

### MCP-сервер GitHub

Добавьте новый MCP-сервер со следующими настройками:

| Поле | Значение |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = ваш токен GitHub |

Используйте токен GitHub с правом на чтение репозитория, для которого нужно
формировать сводку.

### MCP-сервер Slack

Добавьте второй MCP-сервер со следующими настройками:

| Поле | Значение |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID вашего канала для сводки |

Установите для `SLACK_CHANNEL_IDS` ID канала для сводки (то же значение, что
и `SLACK_DIGEST_CHANNEL`), чтобы агенту не приходилось просматривать все
каналы Slack подряд.

После добавления обоих серверов используйте кнопку **Test** для каждого из
них, чтобы убедиться, что подключение работает и сервер предоставляет
инструменты. Сервер GitHub должен вывести список инструментов GitHub, а
сервер Slack — список инструментов Slack.

![Страница MCP в Agent Canvas с установленными серверами GitHub и Slack](assets/04-mcp-servers-installed.png)

## 6. Создание автоматизации сводки

В интерфейсе Agent Canvas откройте страницу **Automations** и создайте новую
автоматизацию:

1. Выберите **Create automation** и тип **Prompt preset**.
2. Установите **Name** равным `GitHub Development Digest to Slack`.
3. Установите **Prompt** равным следующему тексту, заменив заполнители
   репозитория и канала на свои значения:

   ```text
   Use the GitHub MCP server for exactly one repository: your-org/your-repo.
   Inspect recent development activity since the previous weekday, including
   merged pull requests, newly opened or reopened pull requests, notable
   commits pushed to main or release branches, new issues, important issue
   updates, releases, risks, blockers, and review requests. Keep GitHub
   lookups small: inspect the latest 3 to 5 commits, pull requests, issues,
   and releases. Use the Slack MCP server to post directly to channel ID
   C0123456789. Keep the Slack message concise: title with date range, 3 to 7
   bullets, links back to GitHub, and a Needs attention section only if
   needed. End with: This digest was generated by an AI agent (OpenHands) on
   behalf of the user. Do not include secrets, raw tokens, private
   environment variables, or unrelated Slack messages.
   ```

4. Установите **Trigger** равным **Cron** с расписанием `0 9 * * 1-5`
   (9 утра по будням) и установите **Timezone** равным вашему часовому
   поясу, например `America/New_York`.
5. Установите **Timeout** равным `900` секундам.
6. Сохраните автоматизацию.

На странице сведений об автоматизации отображается новая автоматизация с её
cron-триггером и сгенерированной точкой входа prompt-preset.

![Страница сведений об автоматизации в Agent Canvas после создания](assets/05-automation-created.png)
## 7. Тестирование автоматизации

На странице сведений об автоматизации в Agent Canvas UI:

1. Нажмите **Run now** (или **Dispatch**), чтобы немедленно запустить автоматизацию один раз.
2. Следите за списком запусков на той же странице. Последний запуск должен перейти в состояние
   `COMPLETED`.
3. Откройте целевой канал Slack. В нём должен появиться сгенерированный дайджест.

Ждать срабатывания расписания cron не нужно — **Run now** запускает выполнение
по требованию, чтобы вы могли убедиться, что промпт, подключения MCP и публикация в Slack
работают корректно, прежде чем полагаться на расписание.

![Автоматизация в Agent Canvas успешно завершила выполнение](assets/06-automation-run-completed.png)

![Канал Slack с сгенерированным дайджестом OpenHands](assets/07-slackbot-message.png)

## Устранение неполадок

- **Lemonade не работает:** перезапустите его с помощью команды
  `lemonade run "${LEMONADE_MODEL}"` из шага 1, затем повторно выполните проверку
  работоспособности.
- **`npm install -g` завершается с ошибкой доступа:** в Linux или WSL
  настройте пользовательский глобальный каталог npm, добавьте его в файл запуска
  оболочки, затем снова установите Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Если вы используете `zsh`, добавьте ту же строку `export PATH=...` в `~/.zshrc`
  вместо `~/.bashrc`.
- **Agent Canvas отклоняет настройки LLM после установки `custom_tokenizer`:**
  установите `transformers` в среде Python Agent Server, при необходимости перезапустите
  Agent Canvas и повторите попытку сохранения настроек LLM. OpenHands требует
  Transformers для загрузки шаблона чата токенизатора при установленном `custom_tokenizer`.
- **Agent Canvas не может подключиться к Lemonade:** проверьте
  `curl -fsS "${LEMONADE_BASE_URL}/health"` и убедитесь, что базовый URL, указанный
  в форме LLM при первом использовании или в **Settings > LLM**, совпадает с запущенной локальной
  конечной точкой или HTTPS-туннелем.
- **Настройки LLM не сохранились:** убедитесь, что вы нажали **Next** после
  ввода значений. Откройте снова **Settings > LLM**, чтобы убедиться, что значения
  сохранились.
- **GitHub MCP не видит приватные репозитории:** убедитесь, что токен GitHub имеет
  доступ на чтение к целевому репозиторию и что кнопка **Test** MCP в разделе
  **Customize** отображает инструменты GitHub.
- **Slack может читать каналы, но не может публиковать сообщения:** пригласите приложение Slack в
  целевой канал и убедитесь, что у бота есть право `chat:write`.
- **Автоматизация выводит слишком много каналов Slack:** используйте идентификатор канала Slack и
  установите `SLACK_CHANNEL_IDS` на сервере Slack MCP в разделе **Customize**.
- **Запуск автоматизации завершается ошибкой или превышает контекст:** убедитесь, что Lemonade был запущен
  с `ctx_size=65536`, что у LLM OpenHands установлен `custom_tokenizer`,
  и используйте конкретный репозиторий с набором результатов GitHub, ограниченным
  3–5 элементами. Если в вашей сборке Agent Canvas доступны настройки конденсатора, установите
  максимальное количество токенов конденсатора ниже контекстного окна Lemonade.

## Дальнейшие шаги

- Добавьте еженедельный дайджест только по релизам.
- Добавьте автоматизацию, запускаемую событиями GitHub, для более быстрых уведомлений о PR или push.
- Направьте тот же дайджест в Notion, Linear или другой инструмент на базе MCP.

## Ресурсы

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Документация Lemonade Server](https://lemonade-server.ai/docs)
- [Репозиторий расширений OpenHands](https://github.com/OpenHands/extensions)
- [Серверы Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Пакет Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)