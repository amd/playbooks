<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **Μηχανική μετάφραση.** Αυτή η σελίδα μεταφράστηκε αυτόματα από τα Αγγλικά και δεν έχει ελεγχθεί από άνθρωπο. Ενδέχεται να περιέχει σφάλματα, και ορισμένες οδηγίες, εντολές, στοιχεία λήψης, διαθεσιμότητα προϊόντων ή άλλο περιεχόμενο ενδέχεται να διαφέρουν ανάλογα με τη γλώσσα ή την περιοχή. Σε περίπτωση οποιασδήποτε ασυμφωνίας ή απόκλισης, υπερισχύει η πρωτότυπη αγγλική έκδοση του playbook.
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses AMD Playbooks comment tags that are interpreted by the
> AMD Playbooks site. GitHub renders the Markdown content, but not the device,
> OS, variable, or hidden-test directives.
<!-- @github-only:end -->

## Επισκόπηση

Οι προγραμματιστές αφιερώνουν πολύ χρόνο σε μικρούς επαναλαμβανόμενους βρόχους:
έλεγχο επισημασμένων pull requests, απάντηση σε σχόλια GitHub, ταξινόμηση νέων
issues, μετατροπή νημάτων Slack σε σημειώσεις standup ή παρακολούθηση
συμβάντων, και παρακολούθηση σημάτων έκδοσης ή έρευνας. Κάθε βρόχος είναι
οικείος, αλλά εξακολουθεί να απαιτεί κρίση: συλλογή του σωστού πλαισίου,
απόφαση για το τι έχει σημασία, και δημοσίευση μιας σαφούς ενημέρωσης εκεί
όπου ήδη εργάζεται η ομάδα.

Τα [OpenHands automations](https://docs.openhands.dev/openhands/usage/automations/overview)
μετατρέπουν αυτούς τους βρόχους σε προγραμματισμένες ή βασισμένες σε συμβάντα
συνομιλίες πράκτορα: εκτελέσεις όπου ένας πράκτορας λογισμικού AI μπορεί να
διαβάσει πλαίσιο, να καλέσει εργαλεία και να παράγει μια ενημέρωση. Τα κοινά
πρότυπα αυτοματισμού στον κατάλογο επεκτάσεων OpenHands ακολουθούν αυτό το
μοτίβο για έλεγχο pull request σε GitHub, παρακολούθηση αποθετηρίων, ταξινόμηση
issues σε Linear, αναδρομές συμβάντων, ημερήσιες συνόψεις standup σε Slack και
συνοπτικές αναφορές έρευνας: ένας αυτοματισμός ενεργοποιείται, χρησιμοποιεί
διαμορφωμένες ενσωματώσεις όπως GitHub ή Slack για να ανακτήσει πλαίσιο,
συλλογίζεται πάνω σε αυτό το πλαίσιο με ένα μεγάλο γλωσσικό μοντέλο (LLM) και
γράφει πίσω ένα αποτέλεσμα.

Το [Agent Canvas](https://github.com/OpenHands/agent-canvas) είναι το τοπικό
επίπεδο ελέγχου για τη δημιουργία και τη δοκιμή αυτών των αυτοματισμών. Σε
αυτό το playbook, εκτελεί έναν OpenHands Agent Server, τη διαδικασία backend
που εκτελεί συνομιλίες πράκτορα, και συνδέει τον πράκτορα με εξωτερικές
υπηρεσίες όπως GitHub και Slack.

Για να διατηρηθεί η ροή εργασίας στο σύστημα AMD σας, ο πράκτορας επικοινωνεί
με ένα τοπικό μοντέλο που εξυπηρετείται από τον Lemonade Server. Ο Lemonade
εκθέτει αυτό το μοντέλο μέσω ενός API συμβατού με OpenAI, ώστε το Agent Canvas
να μπορεί να το διαμορφώσει όπως ένα απομακρυσμένο endpoint στυλ OpenAI, ενώ
το μοντέλο, η προτροπή και το πλαίσιο της ροής εργασίας παραμένουν τοπικά.

Σε αυτό το playbook, θα δημιουργήσετε έναν συγκεκριμένο αυτοματισμό: μια
προγραμματισμένη ημερήσια σύνοψη ανάπτυξης από GitHub προς Slack. Χρησιμοποιεί
το GitHub για να επιθεωρήσει την πρόσφατη δραστηριότητα αποθετηρίου, το Slack
για να δημοσιεύσει τη σύνοψη, κλήσεις API του Agent Canvas για να διαμορφώσει
και να δοκιμάσει τον αυτοματισμό, και τον Lemonade για να εκτελέσει το LLM
τοπικά.

![Διάγραμμα αρχιτεκτονικής που δείχνει GitHub MCP, αυτοματισμό OpenHands, Lemonade Server και Slack MCP](assets/00-architecture-overview.png)

## Τι Θα Μάθετε

- Πώς να ξεκινήσετε τον Lemonade Server και να επαληθεύσετε ότι ένα τοπικό
  μοντέλο απαντά σε αιτήματα συνομιλίας
- Πώς να εκκινήσετε το Agent Canvas και να κατευθύνετε τον Agent Server του σε
  ένα τοπικό LLM
- Πώς να εγκαταστήσετε διακομιστές Model Context Protocol (MCP) για GitHub και
  Slack μέσω του API του Agent Server
- Πώς να δημιουργήσετε και να αποστείλετε έναν προγραμματισμένο αυτοματισμό
  OpenHands που δημοσιεύει μια ημερήσια σύνοψη ανάπτυξης στο Slack
- Πώς να αντιμετωπίσετε τις πιο συνηθισμένες αποτυχίες τοπικού μοντέλου και
  αυτοματισμού

## Βασικές Έννοιες

| Έννοια | Τι είναι | Πού ταιριάζει σε αυτό το playbook |
| --- | --- | --- |
| Lemonade Server | Μια πλατφόρμα τοπικής εξυπηρέτησης LLM κατασκευασμένη για υλικό AMD που εκθέτει ένα API συμβατό με OpenAI. Τα δεδομένα σας δεν φεύγουν ποτέ από το μηχάνημά σας. | Εκτελεί το μοντέλο που τροφοδοτεί τον πράκτορα. |
| OpenHands Agent Server | Η διαδικασία backend που εκτελεί συνομιλίες πράκτορα OpenHands. | Φιλοξενεί τον πράκτορα, το προφίλ LLM του και τους MCP servers του. |
| Agent Canvas | Το τοπικό επίπεδο ελέγχου για το OpenHands που εκτελεί τον Agent Server και ένα UI για την επιθεώρηση εκτελέσεων πράκτορα. | Εκκινεί τα backends και παρέχει το API που καλείτε. |
| MCP server | Ένας διακομιστής Model Context Protocol που δίνει σε έναν πράκτορα εργαλεία για μια εξωτερική υπηρεσία όπως GitHub ή Slack. | Επιτρέπει στον πράκτορα να διαβάζει από το GitHub και να γράφει στο Slack. |
| Αυτοματισμός OpenHands | Μια προγραμματισμένη ή βασισμένη σε συμβάντα συνομιλία πράκτορα που ανακτά πλαίσιο, συλλογίζεται πάνω του και γράφει ένα αποτέλεσμα κάπου. | Η σύνοψη από GitHub προς Slack που δημιουργείτε εδώ. |

<!-- @device:stx,krk -->
> [!NOTE]
> Οι ροές εργασίας πράκτορα κωδικοποίησης επωφελούνται από ένα μεγαλύτερο
> μοντέλο και παράθυρο πλαισίου. Χρησιμοποιήστε τουλάχιστον 32 GB μνήμης
> συστήματος και προτιμήστε 64 GB ή περισσότερο για μεγαλύτερα μοντέλα GGUF.
<!-- @device:end -->

## Προαπαιτούμενα

<!-- @os:linux -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

Χρειάζεστε:

- Τον Lemonade Server εγκατεστημένο ακολουθώντας τον τυπικό
  [οδηγό εγκατάστασης Lemonade](https://lemonade-server.ai/docs/guide/install/).
- Node.js 22.12 ή νεότερη έκδοση και `npm`, που χρησιμοποιούνται για την
  εγκατάσταση του δημοσιευμένου CLI του Agent Canvas και την εκτέλεση MCP
  servers με `npx`.
- Ένα πρόσφατο δημοσιευμένο πακέτο `@openhands/agent-canvas` με
  ρυθμίσεις πράκτορα βασισμένες σε σχήμα, `LLMSummarizingCondenserSettings.max_tokens`,
  και υποστήριξη `custom_tokenizer` για LLM.
- Το πακέτο Python `transformers` διαθέσιμο στο περιβάλλον του Agent Server.
  Απαιτείται για την καταμέτρηση tokens προτύπου συνομιλίας όταν έχει οριστεί
  το `custom_tokenizer`.
- Ένα GitHub token με πρόσβαση ανάγνωσης στο αποθετήριο που θέλετε να
  συνοψίσετε.
- Ένα Slack bot token (`xoxb-...`) με πρόσβαση `chat:write` και ανάγνωσης
  καναλιού.
- Ένα Slack team ID (`T...`).
- Ένα Slack channel ID (`C...`) όπου θα δημοσιεύεται η σύνοψη.

Προσκαλέστε την εφαρμογή Slack στο κανάλι-στόχο πριν δοκιμάσετε τον
αυτοματισμό.

## Μεταβλητές Που Χρησιμοποιούνται σε Αυτό το Playbook

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

Οι παρακάτω τιμές εισάγονται στο UI του Agent Canvas σε επόμενα βήματα.
Ορίστε τις εδώ ώστε να μπορείτε να τις αντιγράψετε:

```bash
export GITHUB_REPO_FILTER="your-org/your-repo"
export SLACK_DIGEST_CHANNEL="C0123456789"
export DIGEST_TIMEZONE="America/New_York"
```

Χρησιμοποιήστε μια ρητή τιμή `owner/repo` για το `GITHUB_REPO_FILTER`. Ευρέα
wildcards οργανισμού μπορούν να επιστρέψουν υπερβολικά μεγάλο πλαίσιο MCP για
τοπικά μοντέλα.

## 1. Εκκίνηση του Lemonade Server

Ξεκινήστε το μοντέλο από το Lemonade CLI:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "${LEMONADE_MODEL}"
```

Ο Lemonade εκθέτει ένα API συμβατό με OpenAI στη διεύθυνση:

```text
http://127.0.0.1:13305/api/v1
```

Προαιρετικό: αν το Agent Canvas ή ο εκτελεστής αυτοματισμού δεν βρίσκονται στο
ίδιο μηχάνημα, δημοσιεύστε το endpoint του Lemonade μέσω ασφαλούς σήραγγας και
χρησιμοποιήστε το HTTPS URL ως τη διεύθυνση βάσης του LLM:

```bash
ngrok http 13305 --url YOUR_NGROK_DOMAIN.ngrok-free.dev
```



## 2. Επαλήθευση του Τοπικού Μοντέλου

Επιβεβαιώστε ότι ο Lemonade μπορεί να εξυπηρετήσει το επιλεγμένο μοντέλο:

```bash
curl -s "${LEMONADE_BASE_URL}/models" | python3 -m json.tool
```

Στη συνέχεια, στείλτε ένα μικρό αίτημα συνομιλίας:

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

Αν αυτό επιστρέψει έναν πίνακα `choices`, ο Lemonade είναι έτοιμος για το
Agent Canvas.
## 3. Εκκίνηση του Agent Canvas

Εγκαταστήστε το δημοσιευμένο πακέτο Agent Canvas και ξεκινήστε ολόκληρο το stack:

```bash
npm install -g @openhands/agent-canvas
agent-canvas
```

Αν η καθολική εγκατάσταση npm αποτύχει με σφάλμα δικαιωμάτων, δείτε την
καταχώρηση αντιμετώπισης προβλημάτων δικαιωμάτων npm παρακάτω.

Από προεπιλογή, το Agent Canvas ξεκινά στη διεύθυνση `http://localhost:8000`. Ανοίξτε αυτή τη διεύθυνση URL στο
πρόγραμμα περιήγησής σας. Το προεπιλεγμένο τοπικό backend θα πρέπει να εμφανίζεται ως healthy στην αρχική οθόνη.

Η εντολή `agent-canvas` ξεκινά τον agent server, το automation backend, και
το web frontend μαζί. Χρειάζεστε μόνο αυτήν την εντολή για να εκτελέσετε το OpenHands
τοπικά. Το υπόλοιπο αυτού του οδηγού διαμορφώνει τα πάντα μέσω του
Agent Canvas UI στο πρόγραμμα περιήγησής σας.

## 4. Διαμόρφωση του Τοπικού LLM στο UI

Κατά την πρώτη εκκίνηση, το Agent Canvas ανοίγει μια ροή onboarding. Σε αυτή τη ροή:

1. Διατηρήστε το **OpenHands** επιλεγμένο ως τον agent και κάντε κλικ στο **Next**.
2. Στο **Set up your LLM**, επιλέξτε **Advanced**.
3. Διατηρήστε το **Authentication** ρυθμισμένο σε **API key**.
4. Ρυθμίστε το **Custom Model** στην τιμή του `OPENHANDS_LLM_MODEL`,
   `openai/Qwen3.6-35B-A3B-GGUF`.
5. Ρυθμίστε το **Base URL** σε `http://127.0.0.1:13305/api/v1`.
6. Για το **API Key**, εισαγάγετε οποιαδήποτε μη κενή τιμή-θέση κράτησης, όπως `lemonade-local`.
   Το Lemonade δεν απαιτεί πραγματικό κλειδί, αλλά ο client του OpenHands χρειάζεται μια τιμή
   για να στείλει.

Τα πεδία σύνδεσης θα πρέπει να μοιάζουν ως εξής. Το πεδίο API key εμφανίζεται καλυμμένο από το UI.

![Ρυθμίσεις Advanced LLM κατά την πρώτη χρήση του Agent Canvas με το μοντέλο Lemonade και το τοπικό base URL](assets/01-llm-advanced-settings.png)

Στη συνέχεια, επιλέξτε **All** και ρυθμίστε τα επιπλέον πεδία τοπικού μοντέλου:

1. Μεταβείτε στο **Custom Tokenizer** και ρυθμίστε το σε `Qwen/Qwen3.6-35B-A3B`.
2. Μεταβείτε στο **LiteLLM Extra Body** και ρυθμίστε το σε
   `{"enable_thinking": true}`.
3. Κάντε κλικ στο **Next**.

![Καρτέλα All του LLM κατά την πρώτη χρήση του Agent Canvas με το προσαρμοσμένο tokenizer Qwen](assets/02-llm-all-tokenizer-settings.png)

![Καρτέλα All του LLM κατά την πρώτη χρήση του Agent Canvas με ρυθμισμένο LiteLLM extra body](assets/03-llm-all-extra-body-settings.png)

Οι ρυθμίσεις LLM θα πρέπει να δείχνουν:

| Πεδίο | Τιμή |
| --- | --- |
| Custom Model | `openai/Qwen3.6-35B-A3B-GGUF` |
| Base URL | `http://127.0.0.1:13305/api/v1` |
| Custom tokenizer | `Qwen/Qwen3.6-35B-A3B` |
| LiteLLM extra body | `{"enable_thinking": true}` |

Το πρόθεμα `openai/` υποδεικνύει στο LiteLLM να χρησιμοποιήσει μορφοποίηση αιτημάτων συμβατή με το OpenAI
έναντι του endpoint του Lemonade. Το custom tokenizer είναι το αρχικό tokenizer
Hugging Face για το μοντέλο GGUF· επιτρέπει στο OpenHands να μετράει τα ίδια
tokens chat-template που βλέπει ο τοπικός model server. Η τρέχουσα φόρμα LLM πρώτης χρήσης δεν
εμφανίζει ρυθμίσεις condenser. Αν η έκδοση του Agent Canvas σας εμφανίζει αργότερα
ρυθμίσεις condenser κάτω από **Settings > LLM**, χρησιμοποιήστε `llm_summarizing` και
ρυθμίστε τα μέγιστα tokens κάτω από το context window του Lemonade, όπως `56000`.

## 5. Εγκατάσταση των MCP Servers για GitHub και Slack

Στο Agent Canvas UI, ανοίξτε το **Customize** (ή **Settings > MCP**) για να προσθέσετε τους
MCP servers που δίνουν στον agent εργαλεία για GitHub και Slack. Οι τιμές των tokens
αποστέλλονται μόνο στον τοπικό σας Agent Server και διατηρούνται ως κρυπτογραφημένες ρυθμίσεις.

### GitHub MCP server

Προσθέστε έναν νέο MCP server με αυτές τις ρυθμίσεις:

| Πεδίο | Τιμή |
| --- | --- |
| Name | `github` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-github` |
| Env | `GITHUB_PERSONAL_ACCESS_TOKEN` = το token σας από το GitHub |

Χρησιμοποιήστε ένα GitHub token με πρόσβαση ανάγνωσης στο αποθετήριο που θέλετε να συνοψιστεί.

### Slack MCP server

Προσθέστε έναν δεύτερο MCP server με αυτές τις ρυθμίσεις:

| Πεδίο | Τιμή |
| --- | --- |
| Name | `slack` |
| Command | `npx` |
| Args | `-y @modelcontextprotocol/server-slack` |
| Env | `SLACK_BOT_TOKEN` = `xoxb-...` |
| Env | `SLACK_TEAM_ID` = `T0123456789` |
| Env | `SLACK_CHANNEL_IDS` = το ID του καναλιού digest σας |

Ρυθμίστε το `SLACK_CHANNEL_IDS` στο ID του καναλιού digest (την ίδια τιμή με το
`SLACK_DIGEST_CHANNEL`) ώστε ο agent να μη χρειάζεται να περιηγηθεί σε κάθε κανάλι
Slack.

Αφού προσθέσετε και τους δύο servers, χρησιμοποιήστε το κουμπί **Test** σε καθέναν για να επιβεβαιώσετε ότι
συνδέεται και προβάλλει εργαλεία. Ο server του GitHub θα πρέπει να εμφανίζει εργαλεία GitHub, και
ο server του Slack θα πρέπει να εμφανίζει εργαλεία Slack.

![Σελίδα MCP του Agent Canvas με εγκατεστημένους τους servers GitHub και Slack](assets/04-mcp-servers-installed.png)

## 6. Δημιουργία της Αυτοματοποίησης Digest

Στο Agent Canvas UI, ανοίξτε τη σελίδα **Automations** και δημιουργήστε μια νέα
αυτοματοποίηση:

1. Επιλέξτε **Create automation** και επιλέξτε τον τύπο **Prompt preset**.
2. Ρυθμίστε το **Name** σε `GitHub Development Digest to Slack`.
3. Ρυθμίστε το **Prompt** στο ακόλουθο κείμενο, αντικαθιστώντας τις τιμές-θέσεις κράτησης
   αποθετηρίου και καναλιού με τις δικές σας τιμές:

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

4. Ρυθμίστε το **Trigger** σε **Cron** με το πρόγραμμα `0 9 * * 1-5` (9 π.μ. τις
   καθημερινές) και ρυθμίστε το **Timezone** στη δική σας ζώνη ώρας, για παράδειγμα
   `America/New_York`.
5. Ρυθμίστε το **Timeout** σε `900` δευτερόλεπτα.
6. Αποθηκεύστε την αυτοματοποίηση.

Η σελίδα λεπτομερειών της αυτοματοποίησης εμφανίζει τη νέα αυτοματοποίηση με το cron trigger της και
το δημιουργημένο prompt-preset entrypoint.

![Λεπτομέρειες αυτοματοποίησης του Agent Canvas μετά τη δημιουργία](assets/05-automation-created.png)
## 7. Δοκιμή της Αυτοματοποίησης

Από τη σελίδα λεπτομερειών αυτοματοποίησης στο περιβάλλον χρήστη του Agent Canvas:

1. Κάντε κλικ στο **Run now** (ή **Dispatch**) για να εκτελέσετε την αυτοματοποίηση μία φορά άμεσα.
2. Παρακολουθήστε τη λίστα εκτελέσεων στην ίδια σελίδα. Η πιο πρόσφατη εκτέλεση θα πρέπει να μεταβεί σε
   `COMPLETED`.
3. Ανοίξτε το κανάλι Slack-στόχο σας. Θα πρέπει να περιέχει το δημιουργημένο digest.

Δεν χρειάζεται να περιμένετε να ενεργοποιηθεί το προγραμματισμένο cron—το **Run now** ενεργοποιεί μια
εκτέλεση κατ' απαίτηση, ώστε να μπορείτε να επιβεβαιώσετε ότι η προτροπή, οι συνδέσεις MCP και η δημοσίευση στο Slack
λειτουργούν όλα σωστά πριν βασιστείτε στο πρόγραμμα.

![Η εκτέλεση αυτοματοποίησης του Agent Canvas ολοκληρώθηκε με επιτυχία](assets/06-automation-run-completed.png)

![Κανάλι Slack που εμφανίζει το δημιουργημένο digest του OpenHands](assets/07-slackbot-message.png)

## Αντιμετώπιση Προβλημάτων

- **Το Lemonade είναι εκτός λειτουργίας:** επανεκκινήστε το με την
  εντολή `lemonade run "${LEMONADE_MODEL}"` στο βήμα 1, και έπειτα εκτελέστε ξανά τον έλεγχο
  κατάστασης υγείας.
- **Η εντολή `npm install -g` αποτυγχάνει με σφάλμα δικαιωμάτων:** σε Linux ή WSL,
  ρυθμίστε έναν καθολικό κατάλογο npm ανήκοντα στον χρήστη, προσθέστε τον στο αρχείο εκκίνησης
  του shell σας, και έπειτα εγκαταστήστε ξανά το Agent Canvas:

  ```bash
  mkdir -p ~/.npm-global
  npm config set prefix "$HOME/.npm-global"
  printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> ~/.bashrc
  export PATH="$HOME/.npm-global/bin:$PATH"
  npm install -g @openhands/agent-canvas
  ```

  Αν χρησιμοποιείτε `zsh`, προσθέστε την ίδια γραμμή `export PATH=...` στο `~/.zshrc` αντί
  του `~/.bashrc`.
- **Το Agent Canvas απορρίπτει τις ρυθμίσεις LLM μετά τη ρύθμιση του `custom_tokenizer`:**
  εγκαταστήστε το `transformers` στο περιβάλλον Python του Agent Server, επανεκκινήστε το Agent
  Canvas αν χρειάζεται, και προσπαθήστε ξανά να αποθηκεύσετε τις ρυθμίσεις LLM. Το OpenHands απαιτεί
  το Transformers για να φορτώσει το πρότυπο συνομιλίας του tokenizer όταν έχει οριστεί το `custom_tokenizer`.
- **Το Agent Canvas δεν μπορεί να επικοινωνήσει με το Lemonade:** επαληθεύστε με
  `curl -fsS "${LEMONADE_BASE_URL}/health"` και επιβεβαιώστε ότι το βασικό URL που καταχωρήθηκε στη
  φόρμα LLM κατά την πρώτη χρήση ή στο **Settings > LLM** ταιριάζει με το τρέχον τοπικό
  endpoint ή τη σήραγγα HTTPS.
- **Οι ρυθμίσεις LLM δεν αποθηκεύτηκαν:** βεβαιωθείτε ότι κάνατε κλικ στο **Next** αφού
  εισαγάγατε τις τιμές. Ανοίξτε ξανά το **Settings > LLM** για να επιβεβαιώσετε ότι οι τιμές
  διατηρήθηκαν.
- **Το GitHub MCP δεν μπορεί να δει ιδιωτικά αποθετήρια:** επιβεβαιώστε ότι το token του GitHub έχει
  δικαίωμα ανάγνωσης στο αποθετήριο-στόχο και ότι το κουμπί **Test** του MCP στο
  **Customize** εμφανίζει τα εργαλεία του GitHub.
- **Το Slack μπορεί να διαβάζει κανάλια αλλά δεν μπορεί να δημοσιεύει:** προσκαλέστε την εφαρμογή Slack στο
  κανάλι-στόχο και επιβεβαιώστε ότι το bot έχει το δικαίωμα `chat:write`.
- **Η αυτοματοποίηση εμφανίζει πάρα πολλά κανάλια Slack:** χρησιμοποιήστε ένα αναγνωριστικό καναλιού Slack και
  ορίστε το `SLACK_CHANNEL_IDS` στον διακομιστή Slack MCP στο **Customize**.
- **Η εκτέλεση της αυτοματοποίησης αποτυγχάνει ή υπερβαίνει το πλαίσιο περιεχομένου:** επιβεβαιώστε ότι το Lemonade ξεκίνησε
  με `ctx_size=65536`, επιβεβαιώστε ότι το LLM του OpenHands έχει ορισμένο το `custom_tokenizer`,
  και χρησιμοποιήστε ένα ρητά καθορισμένο αποθετήριο με τα σύνολα αποτελεσμάτων του GitHub περιορισμένα σε 3 έως 5
  στοιχεία. Αν η έκδοση του Agent Canvas που χρησιμοποιείτε εκθέτει ρυθμίσεις condenser, ορίστε το μέγιστο αριθμό tokens του condenser
  κάτω από το παράθυρο πλαισίου περιεχομένου του Lemonade.

## Επόμενα Βήματα

- Προσθέστε ένα εβδομαδιαίο digest μόνο για εκδόσεις (release).
- Προσθέστε μια αυτοματοποίηση που ενεργοποιείται από συμβάν GitHub για ταχύτερες ειδοποιήσεις PR ή push.
- Δρομολογήστε το ίδιο digest σε Notion, Linear, ή άλλο εργαλείο που υποστηρίζεται από MCP.

## Πόροι

- [AMD AI Playbooks](https://developer.amd.com/playbooks/)
- [Τεκμηρίωση Lemonade Server](https://lemonade-server.ai/docs)
- [Αποθετήριο επεκτάσεων OpenHands](https://github.com/OpenHands/extensions)
- [Διακομιστές Model Context Protocol](https://github.com/modelcontextprotocol/servers)
- [Πακέτο Slack MCP](https://www.npmjs.com/package/@modelcontextprotocol/server-slack)