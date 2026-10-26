# Translation quality report

Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.

| Locale | Files | Mean | Min | Judge |
|--------|-------|------|-----|-------|
| ar | 78 | 93.0 | 82 | Claude-Opus-4.8 |
| cs-CZ | 78 | 92.4 | 78 | Claude-Opus-4.8 |
| da-DK | 78 | 92.4 | 78 | Claude-Opus-4.8 |
| de-DE | 78 | 93.1 | 78 | Claude-Opus-4.8 |
| el-GR | 78 | 92.4 | 78 | Claude-Opus-4.8 |
| es-LA | 78 | 92.9 | 78 | Claude-Opus-4.8 |
| fi-FI | 78 | 91.7 | 70 | Claude-Opus-4.8 |
| fr-CA | 78 | 90.6 | 72 | Claude-Opus-4.8 |
| fr-FR | 78 | 93.2 | 78 | Claude-Opus-4.8 |
| he | 78 | 92.7 | 72 | Claude-Opus-4.8 |
| hu-HU | 78 | 91.9 | 78 | Claude-Opus-4.8 |
| it-IT | 78 | 93.9 | 78 | Claude-Opus-4.8 |
| ja-JP | 78 | 92.3 | 20 | Claude-Opus-4.8 |
| ko-KR | 78 | 93.5 | 82 | Claude-Opus-4.8 |
| nb-NO | 78 | 91.9 | 82 | Claude-Opus-4.8 |
| nl-NL | 78 | 92.5 | 78 | Claude-Opus-4.8 |
| pl-PL | 78 | 93.1 | 78 | Claude-Opus-4.8 |
| pt-BR | 78 | 93.7 | 78 | Claude-Opus-4.8 |
| pt-PT | 78 | 92.7 | 82 | Claude-Opus-4.8 |
| ro-RO | 78 | 92.4 | 78 | Claude-Opus-4.8 |
| ru-RU | 78 | 92.9 | 88 | Claude-Opus-4.8 |
| sk-SK | 78 | 91.6 | 78 | Claude-Opus-4.8 |
| sl-SI | 78 | 90.5 | 68 | Claude-Opus-4.8 |
| sr-Latn | 78 | 90.8 | 78 | Claude-Opus-4.8 |
| sv-SE | 78 | 93.0 | 88 | Claude-Opus-4.8 |
| th-TH | 78 | 92.4 | 70 | Claude-Opus-4.8 |
| tr-TR | 78 | 92.6 | 80 | Claude-Opus-4.8 |
| uk-UA | 78 | 92.6 | 78 | Claude-Opus-4.8 |
| zh-CN | 78 | 93.4 | 78 | Claude-Opus-4.8 |
| zh-TW | 78 | 93.3 | 78 | Claude-Opus-4.8 |

## Files below 85 (94)

| Locale | File | Score | Issues |
|--------|------|-------|--------|
| ja-JP | playbooks/core/vscode-qwen3-coder/playbook.json | 20 | Contains garbled text 'للで', meta-commentary 'Wait, let me reconsider', and duplicated title lines; unprofessional output. |
| ja-JP | playbooks/supplemental/openhands-getting-started/playbook.json | 68 | OpenHands mistranslated as OpenHats; inconsistent spacing around terms |
| sl-SI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 68 | Redundant English parentheticals; inconsistent 'fino prilagajanje' vs 'fino nastavite'; awkward 'LLaMA-Factory' hyphenation differs from title. |
| fi-FI | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 70 | Title reverses emphasis; 'määritä käyttö' awkward; grammatical case issues with 'autonomisen tekoälyagentin'. |
| th-TH | playbooks/supplemental/cvml/playbook.json | 70 | Left 'Local Computer Vision' and 'perception' untranslated; inconsistent localization reduces fluency. |
| fr-CA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Trademark symbol misplaced (belongs to Unsloth, not LLM); 'affinés' vs 'réglage fin' terminology inconsistency; awkward phrasing. |
| he | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 72 | 'ריכוד' is incorrect term for clustering; should be 'אשכול'/'קיבוץ'. Otherwise accurate, brands/numbers intact. |
| ja-JP | playbooks/supplemental/vllm-inference/playbook.json | 72 | Added 'Ryzen AI Max+' not in source; 'integrated GPU' loosely rendered as iGPU. |
| sl-SI | playbooks/supplemental/pytorch-finetuning/playbook.json | 72 | Inconsistent terminology (fino uravnavanje vs fino prilagodite); 'Software' untranslated; awkward phrasing 'Fino'. |
| sl-SI | playbooks/supplemental/pytorch-kernels/playbook.json | 72 | Inconsistent terminology: 'jeder' vs 'kernele' for same term; 'GPU jeder po meri' awkward word order. |
| cs-CZ | playbooks/supplemental/clustering-rpc-server/playbook.json | 78 | Title omits 'with RPC'; 'Clustrování' awkward neologism; otherwise accurate, terms/numbers intact. |
| cs-CZ | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth); slight inconsistency in fine-tuning terminology; otherwise accurate. |
| da-DK | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Inconsistent term: 'Finjustering' vs 'Fine-tun'; latter is anglicism, should be 'Finjuster'. |
| de-DE | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Fine-tuning translated as 'optimieren' loses precision; 'Feinabstimmung' inconsistent with body verb. |
| de-DE | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth, not LLMs); minor stylistic awkwardness in 'feinabgestimmte'. |
| el-GR | playbooks/core/vscode-qwen3-coder/playbook.json | 78 | "LLM Coding" left partly untranslated; "Coding" awkward in Greek title, slightly unnatural phrasing. |
| el-GR | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Inconsistent terminology: 'Ρύθμιση ακριβείας' vs 'Συντονίστε' for fine-tune; parenthetical clutter but code/brands intact. |
| es-LA | playbooks/supplemental/github-slack-development-digest/playbook.json | 78 | Inconsistent formality (Cree vs Configura); 'digest' left untranslated in title while translated later as 'resumen'. |
| fr-CA | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translates 'AMD Sync' as 'synchronisation AMD' but body keeps 'AMD Sync'—inconsistent brand term handling. |
| fr-CA | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | Title drops speech-to-speech nuance; 'voix-à-voix' awkward calque, 'traduction vocale directe' preferred. |
| fr-FR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (belongs after LLMs); 'à mémoire optimisée' slightly awkward, inconsistent terminology (réglage fin vs affinés). |
| hu-HU | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | "Nagynyelvi modellek" awkward for LLMs; trademark symbol placement shifted; otherwise accurate and fluent. |
| it-IT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow LLMs). 'Fine-tuned' rendered as 'ottimizzati'; slightly imprecise but acceptable. |
| ja-JP | playbooks/supplemental/lemonade-getting-started/playbook.json | 78 | Second sentence restructured awkwardly; relative clause placement makes it read as if models are the server. |
| ja-JP | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced: source has 'LLMs™', translation attached ™ to Unsloth instead. |
| nl-NL | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | Inconsistent 'fijnafstemmen'/'verfijn'; incorrect hyphenation 'LLaMA-Factory-' alters brand; slight mistranslation of technique scope. |
| nl-NL | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 78 | Untranslated 'Running' in title; otherwise accurate and fluent. |
| pl-PL | playbooks/supplemental/amd-sync/playbook.json | 78 | Inconsistent 'AMD Sync' translation: title translates as 'synchronizacją AMD' but body keeps 'AMD Sync'; brand should stay intact. |
| pt-BR | playbooks/supplemental/amd-sync/playbook.json | 78 | Title inconsistently translated 'Sincronização da AMD' vs product name 'AMD Sync'; 'Live Metrics' translated though arguably a feature name. |
| ro-RO | playbooks/supplemental/vllm-inference/playbook.json | 78 | 'Primii' typo (should be 'Primii/Primii pași→Primii'), 'serverea' is an invented/incorrect term for 'serving'. |
| sk-SK | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translated 'AMD Sync' as 'synchronizáciou AMD', inconsistent with body; brand name should stay intact. |
| sl-SI | playbooks/supplemental/clustering-rpc-server/playbook.json | 78 | Untranslated 'Clustering'; added 'AMD' not in source; '350B+' expanded acceptably but added 'parametrov' not explicit in source. |
| sl-SI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark ™ misplaced (belongs to Unsloth/LLMs brand); inconsistent terminology 'fino prilagajanje' vs 'fino nastavljanje'. |
| sr-Latn | playbooks/supplemental/amd-sync/playbook.json | 78 | Inconsistent 'AMD Sync' rendered as 'AMD sinhronizacijom' in title; otherwise accurate and fluent. |
| sr-Latn | playbooks/supplemental/hermes-lemonade-server/playbook.json | 78 | Awkward 'Hermes Agent autonomnog AI agenta' redundancy; inconsistent brand formatting with hyphens. |
| th-TH | playbooks/core/comfyui-image-gen/playbook.json | 78 | Title 'กำลังสร้าง' implies ongoing action; should be 'การสร้าง'. Slightly awkward 'ภาพที่สร้างโดย AI'. |
| th-TH | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 78 | Title left untranslated in English ('Clustering Four Ryzen AI Halos'); otherwise accurate and fluent. |
| uk-UA | playbooks/core/n8n-automation-gpt-oss/playbook.json | 78 | "саммарайзер" is an awkward transliteration; "засіб підсумовування новин" preferred. Otherwise accurate. |
| uk-UA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark ™ misplaced (belongs to LLMs term); inconsistent terminology 'тонке'/'точне налаштування'; slightly awkward phrasing. |
| zh-CN | playbooks/supplemental/clustering-rpc-server/playbook.json | 78 | Title mistranslates 'with RPC'; 'Halos' plural lost; overall adequate but title phrasing awkward. |
| zh-CN | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced onto LLM instead of Unsloth; slight rephrasing but adequate. |
| zh-TW | playbooks/supplemental/clustering-rccl/playbook.json | 78 | Title omits 'with RCCL'; 'Clustering' left untranslated in heading, reducing fluency. |
| tr-TR | playbooks/supplemental/speech2speech-translation/platform.md | 80 | Headings left untranslated (Platform Configuration, Prerequisites, Required Models, Network Requirements); table headers untranslated. Body translation accurate and fluent. |
| ar | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Title omits 'Fine' nuance; inconsistent LLaMA Factory vs LLaMA-Factory hyphenation; otherwise accurate and fluent. |
| cs-CZ | playbooks/supplemental/amd-sync/playbook.json | 82 | Title translates 'AMD Sync' as 'synchronizací AMD' instead of keeping brand name consistent; otherwise accurate. |
| cs-CZ | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Anglicism 'Clustrování' awkward; 'Halos' plural left untranslated in title; otherwise accurate and fluent. |
| cs-CZ | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'jader' vs 'kernely' for kernels; otherwise accurate, fluent, brands intact. |
| da-DK | playbooks/supplemental/cvml/playbook.json | 82 | Grammatical gender error: 'Lokal' should be 'Lokalt' for neuter 'computersyn'. Otherwise accurate, terms/brands intact. |
| da-DK | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Gender agreement error: 'et...udviklingsoversigt' should be 'en'; 'udgiver' slightly off for 'posts'. |
| de-DE | playbooks/supplemental/lemonade-getting-started/playbook.json | 82 | Omitted 'Gen AI' (Gen KI); translated as generic 'KI-Modelle', losing generative AI specificity. |
| de-DE | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Inconsistent register (Erstelle vs Konfigurieren Sie); 'ein Digest' gender debatable, minor fluency issues |
| el-GR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent fine-tune rendering (Βελτιστοποίηση vs Συντονίστε); minor terminology awkwardness but adequate, brands/acronyms intact. |
| el-GR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark ™ likely belongs to Unsloth, not LLM; slightly awkward phrasing. Terminology otherwise accurate. |
| el-GR | playbooks/supplemental/openhands-getting-started/playbook.json | 82 | "πράκτορα κωδικοποίησης" awkward; "coding agent" better as "προγραμματισμού". Otherwise accurate, brands intact. |
| es-LA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced; 'LLMs™' brand term altered; slightly verbose but adequate and fluent. |
| fi-FI | playbooks/supplemental/lemonade-getting-started/playbook.json | 82 | Title awkward 'Aloita käytön kanssa'; otherwise accurate and fluent. |
| fr-CA | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | Inconsistent 'diffusion'/'servir' for 'serving'; 'de grands modèles' preferred over 'des grands modèles'. |
| fr-CA | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Slight inconsistency: 'Réglage fin' vs 'Ajustez avec précision' for fine-tune; otherwise accurate, fluent, terms intact. |
| fr-CA | playbooks/supplemental/vllm-inference/playbook.json | 82 | "le service" ambiguous for serving; "GPU" acceptable but "processeur graphique" preferred by OQLF. |
| fr-FR | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | 'diffusion' suboptimal for 'serving'; 'de grands modèles' more correct than 'des grands modèles' |
| fr-FR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent terminology: 'Réglage fin' vs 'Affinez'; 'de grands modèles' preferred over 'des grands'. |
| fr-FR | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'noyaux' in title vs 'kernels' in body for same term. |
| he | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark placement shifted (LLMs™ vs LLM™); 'memory-efficient' rendering slightly awkward but acceptable. |
| hu-HU | playbooks/supplemental/amd-sync/playbook.json | 82 | Title inconsistently translates 'AMD Sync' as 'AMD szinkronizálással'; body keeps brand correctly. Otherwise accurate. |
| hu-HU | playbooks/supplemental/gaia-agents/playbook.json | 82 | Title mistranslates 'first agent with GAIA' as 'GAIA's first agent'; otherwise accurate and fluent. |
| it-IT | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title omits 'speech-to-speech' nuance; 'voce-voce' awkward, 'da voce a voce' preferred. |
| ja-JP | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Awkward '音声対音声'; more natural rendering like '音声から音声への' preferred; otherwise accurate. |
| ko-KR | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Inconsistent term (음성 대 음성 vs 음성-음성); 'speech-to-speech' better as 음성 간; otherwise accurate and fluent. |
| ko-KR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Second line incomplete; source verb 'Use...for' rendered awkwardly, missing predicate. Terminology fine, ™ intact. |
| nb-NO | playbooks/supplemental/clustering-rccl/playbook.json | 82 | First line: 'To cluster' untranslated English verb; should be 'Klynge sammen' or similar Norwegian. |
| nb-NO | playbooks/supplemental/cvml/playbook.json | 82 | Gender error: 'lokal datasyn' should be 'lokalt datasyn' (neuter). Otherwise accurate, terms/brands intact. |
| nb-NO | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Gender agreement error: 'en...utviklingssammendrag' should be 'et'; otherwise accurate and fluent. |
| pt-BR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced (should be on Unsloth); redundant '(fine-tuned)' gloss slightly awkward but acceptable. |
| pt-PT | playbooks/supplemental/hermes-lemonade-server/playbook.json | 82 | Gerund 'Executando' is Brazilian; pt-PT prefers 'A executar'. 'Agente Hermes'/'Hermes Agent' inconsistent. |
| pt-PT | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Terminology inconsistency: title uses 'Fala para Fala' but body uses 'voz-a-voz'; minor fluency. |
| ro-RO | playbooks/core/vscode-qwen3-coder/playbook.json | 82 | "Codificare" awkward for coding; "asistență de cod" slightly literal but understandable; brands intact. |
| ro-RO | playbooks/supplemental/clustering-rccl/playbook.json | 82 | "Halos" left plural/untranslated in title; "Gruparea" less idiomatic than "Clustering". Otherwise accurate. |
| ro-RO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced; slightly awkward phrasing; overall accurate and fluent. |
| ro-RO | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 82 | 'Clustering' left untranslated (awkward); 'procesoare' vs source 'devices' inconsistency with later 'dispozitive'. Otherwise accurate, terms intact. |
| sl-SI | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | Title phrasing 'Lokalno zagnan' slightly awkward; gerund 'Running' better as 'Poganjanje'. Otherwise accurate, brands intact. |
| sr-Latn | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | Inconsistent terminology: 'posluživanje' vs 'servisiranje' for 'serving'; minor fluency issues. |
| sr-Latn | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | Minor: hyphenated brand suffix non-ideal; 'agent' should be accusative 'agenta' for fluency. |
| sr-Latn | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent 'kernela' vs 'jezgra' terminology; otherwise accurate, brands intact. |
| sr-Latn | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | "rasporedite" awkward for deploy; "inferentni" unusual; otherwise accurate, brands intact |
| th-TH | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title leaves 'Clustering' untranslated, slightly awkward; otherwise accurate and fluent. |
| th-TH | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | Title left 'Clustering' untranslated; added 'AMD' not in source; otherwise accurate, fluent, terms intact. |
| th-TH | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title omits speech-to-speech nuance (just 'speech translation'); otherwise accurate and fluent. |
| th-TH | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced; 'fine-tuned' rendering slightly awkward but meaning preserved and terms intact. |
| tr-TR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Minor grammar: 'ince ayar yapın' should be 'ince ayar yapın modelleri' or 'ince ayarlayın'; slightly awkward phrasing. |
| tr-TR | playbooks/supplemental/vllm-inference/playbook.json | 82 | Added 'AMD' not in source; otherwise accurate and fluent. |
| zh-CN | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title 'Clustering' rendered as verb '集群' is awkward; 'configured with RCCL' misattributes RCCL to devices rather than clustering method. |
| ro-RO | playbooks/supplemental/pytorch-kernels/playbook.json | 84 | Inconsistent 'kernele' vs 'kernel-uri' plural; otherwise accurate, fluent, terms/brands intact. |
| sl-SI | playbooks/core/lmstudio-rocm-llms/playbook.json | 84 | "strežba" is awkward for serving LLMs; "strežnik"/"gostovanje" preferred, otherwise accurate. |
| sr-Latn | playbooks/supplemental/github-slack-development-digest/playbook.json | 84 | Inconsistent term: 'sažetak' vs untranslated 'digest'; otherwise accurate and fluent. |
