<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Машинний переклад.** Цю сторінку було автоматично перекладено з англійської мови, і вона не була перевірена людиною. Вона може містити помилки, а певні інструкції, команди, завантаження, доступність продукту чи інший вміст можуть відрізнятися залежно від мови чи регіону. У разі будь-яких невідповідностей чи розбіжностей переважну силу має оригінальна англомовна версія playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Огляд

Розробники витрачають багато часу на невеликі повторювані цикли: перегляд
позначених міток pull request, відповіді на коментарі в GitHub, сортування
нових задач, перетворення обговорень у Slack на нотатки для стендапів або
подальші дії щодо інцидентів, а також відстеження сигналів релізів чи
досліджень. Кожен такий цикл знайомий, але все одно вимагає судження: зібрати
потрібний контекст, вирішити, що важливо, і опублікувати чітке оновлення там,
де команда вже працює.

[Автоматизації OpenHands](https://docs.openhands.dev/openhands/usage/automations/overview)
перетворюють ці цикли на заплановані або запущені подіями розмови з агентом:
запуски, під час яких ШІ-агент програмного забезпечення може читати контекст,
викликати інструменти та створювати оновлення. Спільні шаблони автоматизації
в каталозі розширень OpenHands дотримуються цього шаблону для перегляду pull
request у GitHub, моніторингу репозиторію, сортування задач Linear,
ретроспектив інцидентів, дайджестів стендапів у Slack та дослідницьких
оглядів: автоматизація "прокидається", використовує налаштовані інтеграції,
такі як GitHub або Slack, для отримання контексту, обмірковує цей контекст за
допомогою великої мовної моделі (LLM) і записує результат назад.

[Agent Canvas](https://github.com/OpenHands/agent-canvas) — це локальна
панель керування для створення та тестування таких автоматизацій. У цьому
плейбуці вона запускає OpenHands Agent Server, backend-процес, який виконує
розмови з агентом, і з'єднує агента із зовнішніми сервісами, такими як GitHub
і Slack.

Щоб робочий процес залишався на вашій системі AMD, агент спілкується з
локальною моделлю, яку обслуговує Lemonade Server. Lemonade надає доступ до
цієї моделі через API, сумісний з OpenAI, тому Agent Canvas може налаштувати
її як віддалену кінцеву точку у стилі OpenAI, тоді як модель, підказка та
контекст робочого процесу залишаються локальними.

У цьому плейбуці ви створите одну конкретну автоматизацію: запланований
дайджест розробки з GitHub у Slack. Вона використовує GitHub для перевірки
нещодавньої активності репозиторію, Slack для публікації дайджесту, виклики
Agent Canvas API для налаштування й тестування автоматизації та Lemonade для
локального запуску LLM.

![Схема архітектури, що показує GitHub MCP, автоматизацію OpenHands, Lemonade Server та Slack MCP](assets/00-architecture-overview.png)

## Чого ви навчитеся

- Як запустити Lemonade Server і перевірити, чи локальна модель відповідає
  на запити чату
- Як запустити Agent Canvas і налаштувати його Agent Server на локальну LLM
- Як встановити сервери GitHub і Slack Model Context Protocol (MCP) через
  API Agent Server
- Як створити та запустити заплановану автоматизацію OpenHands, яка публікує
  дайджест розробки у Slack
- Як усунути найпоширеніші збої локальної моделі та автоматизації

## Основні поняття

| Поняття | Що це таке | Де воно застосовується в цьому плейбуці |
| --- | --- | --- |
| Lemonade Server | Локальна платформа обслуговування LLM, створена для апаратного забезпечення AMD, яка надає API, сумісний з OpenAI. Ваші дані ніколи не залишають вашу машину. | Запускає модель, яка живить агента. |
| OpenHands Agent Server | Backend-процес, який виконує розмови агента OpenHands. | Розміщує агента, його профіль LLM та його MCP-сервери. |
| Agent Canvas | Локальна панель керування для OpenHands, яка запускає Agent Server і інтерфейс для перегляду запусків агента. | Запускає backend-и та надає API, який ви викликаєте. |
| MCP-сервер | Сервер Model Context Protocol, який надає агенту інструменти для зовнішнього сервісу, такого як GitHub або Slack. | Дозволяє агенту читати GitHub і писати у Slack. |
| Автоматизація OpenHands | Запланована або запущена подіями розмова з агентом, яка отримує контекст, обмірковує його та записує результат кудись. | Дайджест з GitHub у Slack, який ви створюєте тут. |

<!-- @device:stx,krk -->
> [!NOTE]
> Робочі процеси агента з кодуванням виграють від більшої моделі та більшого
> контекстного вікна. Використовуйте щонайменше 32 ГБ системної пам'яті,
> а для більших моделей GGUF надавайте перевагу 64 ГБ або більше.
<!-- @device:end -->

## Передумови

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Вам потрібно:

- Встановлений Lemonade Server за стандартним
  [посібником з встановлення Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 або новіше та `npm`, що використовуються для встановлення
  опублікованого CLI Agent Canvas і запуску MCP-серверів за допомогою `npx`.
- Нещодавно опублікований пакет `@openhands/agent-canvas` зі
  схемо-орієнтованими налаштуваннями агента,
  `LLMSummarizingCondenserSettings.max_tokens` та підтримкою LLM
  `custom_tokenizer`.
- Пакет Python `transformers`, доступний у середовищі Agent Server.
  Він потрібен для підрахунку токенів шаблону чату, коли встановлено
  `custom_tokenizer`.
- Токен GitHub з доступом на читання до репозиторію, який потрібно
  підсумувати.
- Токен бота Slack (`xoxb-...`) з доступом `chat:write` та доступом на
  читання каналу.
- Ідентифікатор команди Slack (`T...`).
- Ідентифікатор каналу Slack (`C...`), куди має публікуватися дайджест.

Запросіть застосунок Slack до цільового каналу перед тестуванням
автоматизації.

## Змінні, використані в цьому плейбуці

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

Наступні значення вводяться в інтерфейс Agent Canvas на подальших кроках.
Задайте їх тут, щоб потім скопіювати:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Використовуйте явне значення `owner/repo` для `GITHUB_REPO_FILTER`. Широкі
шаблони для цілих організацій можуть повертати занадто багато контексту MCP
для локальних моделей.

## 1. Запустіть Lemonade Server

Запустіть модель з CLI Lemonade:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Lemonade надає API, сумісний з OpenAI, за адресою:

```text
http://127.0.0.1:13305/api/v1
```

Необов'язково: якщо Agent Canvas або виконавець автоматизації не на тій самій
машині, опублікуйте кінцеву точку Lemonade через безпечний тунель і
використайте HTTPS-URL як базову URL-адресу LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Перевірте локальну модель

Переконайтеся, що Lemonade може обслуговувати обрану модель:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Потім надішліть невеликий запит чату:

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

Якщо це повертає масив `choices`, Lemonade готовий для Agent Canvas.
## 3. Запуск Agent Canvas

Встановіть опублікований пакет Agent Canvas і запустіть повний стек:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Якщо глобальне встановлення npm завершується помилкою доступу, див. розділ
про усунення проблем із дозволами npm нижче.

За замовчуванням Agent Canvas запускається за адресою `http://localhost:8000`.
Відкрийте цю URL-адресу у своєму браузері. Локальний бекенд за замовчуванням
має відображатися як справний на головному екрані.

Команда `agent-canvas` запускає сервер агента, бекенд автоматизації та
веб-фронтенд разом. Вам потрібна лише ця одна команда для запуску OpenHands
локально. Решта цього посібника налаштовує все через інтерфейс Agent Canvas
у вашому браузері.

## 4. Налаштування локальної LLM в інтерфейсі

Під час першого запуску Agent Canvas відкриває процес початкового
налаштування. У цьому процесі:

1. Залиште **OpenHands** вибраним як агента та натисніть **Next**.
2. На екрані **Set up your LLM** виберіть **Advanced**.
3. Залиште **Authentication** зі значенням **API key**.
4. Встановіть для **Custom Model** значення `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Встановіть для **Base URL** значення `http://127.0.0.1:13305/api/v1`.
6. Для **API Key** введіть будь-яке непорожнє значення-заповнювач, наприклад
   `lemonade-local`. Lemonade не вимагає справжнього ключа, але клієнту
   OpenHands потрібне якесь значення для надсилання.

Поля підключення мають виглядати так. Поле API-ключа приховане інтерфейсом.

![Налаштування Agent Canvas першого запуску LLM Advanced з моделлю Lemonade та локальною базовою URL-адресою](assets/01-llm-advanced-settings.png)

Потім виберіть **All** і налаштуйте додаткові поля для локальної моделі:

1. Прокрутіть до **Custom Tokenizer** і встановіть значення
   `Qwen/Qwen3.6-35B-A3B`.
2. Прокрутіть до **LiteLLM Extra Body** і встановіть значення
   `{"enable_thinking": true}`.
3. Натисніть **Next**.

![Вкладка Agent Canvas першого запуску LLM All з користувацьким токенізатором Qwen](assets/02-llm-all-tokenizer-settings.png)

![Вкладка Agent Canvas першого запуску LLM All з налаштованим LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Налаштування LLM мають показувати:

| Поле | Значення |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Префікс `openai/` вказує LiteLLM використовувати сумісне з OpenAI
форматування запитів для кінцевої точки Lemonade. Користувацький токенізатор —
це оригінальний токенізатор Hugging Face для моделі GGUF; він дозволяє
OpenHands рахувати ті самі токени шаблону чату, які бачить локальний сервер
моделі. Поточна форма LLM першого запуску не показує налаштування
кондесера. Якщо ваша збірка Agent Canvas пізніше показує налаштування
кондесера в розділі **Settings > LLM**, використовуйте `llm_summarizing` і
встановіть максимальну кількість токенів нижче за контекстне вікно Lemonade,
наприклад `56000`.

## 5. Встановлення MCP-серверів GitHub і Slack

В інтерфейсі Agent Canvas відкрийте **Customize** (або **Settings > MCP**),
щоб додати MCP-сервери, які надають агенту інструменти для GitHub і Slack.
Значення токенів надсилаються лише на ваш локальний Agent Server і
зберігаються як зашифровані налаштування.

### MCP-сервер GitHub

Додайте новий MCP-сервер із такими налаштуваннями:

| Поле | Значення |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = ваш токен GitHub |

Використовуйте токен GitHub із доступом на читання до репозиторію, для якого
потрібно створювати зведення.

### MCP-сервер Slack

Додайте другий MCP-сервер із такими налаштуваннями:

| Поле | Значення |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = ID вашого каналу для зведень |

Встановіть для `SLACK_CHANNEL_IDS` значення ID каналу для зведень (те саме
значення, що й `SLACK_DIGEST_CHANNEL`), щоб агенту не потрібно було
переглядати кожен канал Slack.

Після додавання обох серверів скористайтеся кнопкою **Test** на кожному з
них, щоб переконатися, що він підключається та повідомляє про свої
інструменти. Сервер GitHub має показати список інструментів GitHub, а сервер
Slack — список інструментів Slack.

![Сторінка MCP Agent Canvas зі встановленими серверами GitHub і Slack](assets/04-mcp-servers-installed.png)

## 6. Створення автоматизації зведення

В інтерфейсі Agent Canvas відкрийте сторінку **Automations** і створіть нову
автоматизацію:

1. Виберіть **Create automation** і тип **Prompt preset**.
2. Встановіть для **Name** значення `GitHub Development Digest to Slack`.
3. Встановіть для **Prompt** такий текст, замінивши заповнювачі репозиторію
   та каналу на власні значення:

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

4. Встановіть для **Trigger** значення **Cron** із розкладом `0 9 * * 1-5`
   (9 ранку в будні дні) і встановіть для **Timezone** ваш часовий пояс,
   наприклад `America/New_York`.
5. Встановіть для **Timeout** значення `900` секунд.
6. Збережіть автоматизацію.

Сторінка деталей автоматизації показує нову автоматизацію з її cron-тригером
і згенерованою точкою входу prompt-preset.

![Сторінка деталей автоматизації Agent Canvas після створення](assets/05-automation-created.png)
## 7. Перевірка автоматизації

На сторінці деталей автоматизації в Agent Canvas UI:

1. Натисніть **Run now** (або **Dispatch**), щоб одразу запустити автоматизацію один раз.
2. Слідкуйте за списком запусків на тій самій сторінці. Останній запуск має перейти в стан
   `COMPLETED`.
3. Відкрийте свій цільовий канал Slack. Він повинен містити згенерований дайджест.

Вам не потрібно чекати на спрацювання розкладу cron — **Run now** запускає
виконання за запитом, тож ви можете підтвердити, що промт, з'єднання MCP та публікація
в Slack працюють коректно, перш ніж покладатися на розклад.

![Успішно завершений запуск автоматизації Agent Canvas](assets/06-automation-run-completed.png)

![Канал Slack із згенерованим дайджестом OpenHands](assets/07-slackbot-message.png)

## Усунення несправностей

- **Lemonade не працює:** перезапустіть його командою
  `lemonade run "${LEMONADE_MODEL}"` з кроку 1, а потім повторно виконайте перевірку
  стану.
- **Помилка прав доступу під час `npm install -g`:** у Linux або WSL
  налаштуйте глобальний каталог npm, що належить користувачу, додайте його до файлу
  запуску оболонки, а потім установіть Agent Canvas знову:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Якщо ви використовуєте `zsh`, додайте той самий рядок `export PATH=...` до
  `~/.zshrc` замість `~/.bashrc`.
- **Agent Canvas відхиляє налаштування LLM після встановлення `custom_tokenizer`:**
  встановіть `transformers` у Python-середовищі Agent Server, за потреби
  перезапустіть Agent Canvas і повторіть спробу зберегти налаштування LLM. OpenHands
  потребує Transformers для завантаження шаблону чату токенізатора, коли встановлено
  `custom_tokenizer`.
- **Agent Canvas не може підключитися до Lemonade:** перевірте виконання
  `curl -fsS "${LEMONADE_BASE_URL}/health"` і переконайтеся, що базова URL-адреса, введена в
  формі LLM при першому використанні або в **Settings > LLM**, відповідає активній локальній
  кінцевій точці або HTTPS-тунелю.
- **Налаштування LLM не зберігаються:** переконайтеся, що ви натиснули **Next** після
  введення значень. Повторно відкрийте **Settings > LLM**, щоб перевірити, чи значення
  збереглися.
- **GitHub MCP не бачить приватні репозиторії:** переконайтеся, що токен GitHub має
  доступ на читання до цільового репозиторію та що кнопка **Test** MCP у
  **Customize** повідомляє про наявність інструментів GitHub.
- **Slack може читати канали, але не може публікувати повідомлення:** запросіть застосунок Slack до
  цільового каналу та переконайтеся, що бот має право `chat:write`.
- **Автоматизація перелічує занадто багато каналів Slack:** використайте ID каналу Slack і
  встановіть `SLACK_CHANNEL_IDS` на сервері Slack MCP у **Customize**.
- **Запуск автоматизації завершується невдало або перевищує контекст:** переконайтеся, що Lemonade запущено
  з `ctx_size=65536`, переконайтеся, що для LLM OpenHands встановлено `custom_tokenizer`,
  і використовуйте явно вказаний репозиторій із набором результатів GitHub, обмеженим 3–5
  елементами. Якщо ваша збірка Agent Canvas має налаштування конденсора, встановіть максимальну кількість
  токенів конденсора нижче за розмір контекстного вікна Lemonade.

## Наступні кроки

- Додайте щотижневий дайджест лише з релізами.
- Додайте автоматизацію, що запускається подіями GitHub, для швидших сповіщень про PR або push.
- Спрямуйте той самий дайджест до Notion, Linear або іншого інструменту на базі MCP.

## Ресурси

- [Посібники AMD AI](https://developer.amd.com/playbooks/)
- [Документація Lemonade Server](https://lemonade-server.ai/docs)
- [Репозиторій розширень OpenHands](https://github.com/OpenHands/extensions)
- [Сервери Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Пакет Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)