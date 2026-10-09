# Translation quality report

Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.

| Locale | Files | Mean | Min | Judge |
|--------|-------|------|-----|-------|
| ar | 100 | 93.5 | 82 | Claude-Opus-4.8 |
| cs-CZ | 100 | 93.2 | 82 | Claude-Opus-4.8 |
| da-DK | 100 | 93.5 | 82 | Claude-Opus-4.8 |
| de-DE | 100 | 94.4 | 82 | Claude-Opus-4.8 |
| el-GR | 100 | 92.7 | 78 | Claude-Opus-4.8 |
| es-LA | 100 | 93.5 | 82 | Claude-Opus-4.8 |
| fi-FI | 100 | 92.2 | 70 | Claude-Opus-4.8 |
| fr-CA | 100 | 91.5 | 78 | Claude-Opus-4.8 |
| fr-FR | 100 | 93.7 | 78 | Claude-Opus-4.8 |
| he | 100 | 92.6 | 60 | Claude-Opus-4.8 |
| hu-HU | 100 | 92.2 | 72 | Claude-Opus-4.8 |
| it-IT | 100 | 94.5 | 72 | Claude-Opus-4.8 |
| ja-JP | 100 | 93.5 | 20 | Claude-Opus-4.8 |
| ko-KR | 100 | 93.9 | 72 | Claude-Opus-4.8 |
| nb-NO | 100 | 92.3 | 82 | Claude-Opus-4.8 |
| nl-NL | 100 | 92.8 | 72 | Claude-Opus-4.8 |
| pl-PL | 100 | 93.4 | 78 | Claude-Opus-4.8 |
| pt-BR | 100 | 94.6 | 85 | Claude-Opus-4.8 |
| pt-PT | 100 | 93.6 | 82 | Claude-Opus-4.8 |
| ro-RO | 100 | 93.1 | 78 | Claude-Opus-4.8 |
| ru-RU | 100 | 93.0 | 88 | Claude-Opus-4.8 |
| sk-SK | 100 | 92.2 | 78 | Claude-Opus-4.8 |
| sl-SI | 100 | 91.2 | 72 | Claude-Opus-4.8 |
| sr-Latn | 100 | 91.5 | 78 | Claude-Opus-4.8 |
| sv-SE | 100 | 93.4 | 78 | Claude-Opus-4.8 |
| th-TH | 100 | 93.3 | 70 | Claude-Opus-4.8 |
| tr-TR | 100 | 92.9 | 72 | Claude-Opus-4.8 |
| uk-UA | 100 | 93.0 | 78 | Claude-Opus-4.8 |
| zh-CN | 100 | 93.9 | 72 | Claude-Opus-4.8 |
| zh-TW | 100 | 93.9 | 78 | Claude-Opus-4.8 |

## Files below 85 (97)

| Locale | File | Score | Issues |
|--------|------|-------|--------|
| ja-JP | playbooks/core/vscode-qwen3-coder/playbook.json | 20 | Contains garbled text 'للで', meta-commentary 'Wait, let me reconsider', and duplicated title lines; unprofessional output. |
| he | playbooks/supplemental/clustering-rpc-server/playbook.json | 60 | Title left mostly untranslated ('Clustering Two Ryzen AI Halos'); rest is accurate and fluent. |
| fi-FI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 70 | Second sentence mistranslated: 'fine-tune LLMs' became 'fine-tune using LLMs'; awkward phrasing, meaning distorted. |
| th-TH | playbooks/supplemental/cvml/playbook.json | 70 | Left 'Local Computer Vision' and 'perception' untranslated; inconsistent localization reduces fluency. |
| he | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 72 | Title 'AiCluster' is mistranslation/garbled; 'Clustering' not properly rendered. Rest accurate and fluent. |
| hu-HU | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Title mistranslates 'Fine-Tuning LLMs' as 'with LLMs'; trademark symbol misplaced vs source. |
| it-IT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Trademark™ misplaced (should be on Unsloth); 'fine-tuned' rendered as 'ottimizzati', slightly imprecise terminology. |
| ja-JP | playbooks/supplemental/vllm-inference/playbook.json | 72 | Added 'Ryzen AI Max+' not in source; 'integrated GPU' loosely rendered as iGPU. |
| ko-KR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Inconsistent terminology (파인튜닝 vs 미세 조정); trademark misplaced—™ belongs to Unsloth, not LLMs; awkward phrasing |
| nl-NL | playbooks/supplemental/llama-factory-finetuning/playbook.json | 72 | Inconsistent terminology: 'Fijnafstemmen' in title vs 'Fine-tune' in body; mixing creates incoherence. |
| nl-NL | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 72 | Title 'Running' left untranslated (should be 'DeepSeek V4 Flash draaien'); otherwise accurate. |
| sl-SI | playbooks/supplemental/pytorch-kernels/playbook.json | 72 | Inconsistent terminology: 'jeder' vs 'kernele' for same term; 'GPU jeder po meri' awkward word order. |
| sl-SI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Inconsistent terminology (prilagajanje vs nastavljene); awkward phrasing; trademark symbol misplaced vs source placement on LLMs. |
| tr-TR | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 72 | Title mistranslated: 'Running DeepSeek V4 Flash with ds4' reversed meaning. 'Dağıtın' slightly off for deploy. |
| zh-CN | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Second line awkward phrasing; trademark symbol misplaced; 'memory-efficient fine-tuned LLMs' rendered unnaturally in Chinese. |
| el-GR | playbooks/core/vscode-qwen3-coder/playbook.json | 78 | "LLM Coding" left partly untranslated; "Coding" awkward in Greek title, slightly unnatural phrasing. |
| el-GR | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Second sentence uses 'Βελτιστοποιήστε' (optimize) instead of fine-tune; inconsistent with title's 'Μικρορύθμιση'. |
| el-GR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth brand, not LLM); slightly awkward phrasing but adequate and intact. |
| fr-CA | playbooks/supplemental/amd-sync/playbook.json | 78 | Inconsistent: title translates 'AMD Sync' as 'synchronisation AMD' but body keeps 'AMD Sync'; 'métriques' anglicism (préfère 'mesures'). |
| fr-CA | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | Omits 'speech-to-speech' nuance (voice-to-voice); 'Traduction vocale' acceptable but slightly loses source-target speech distinction. |
| fr-CA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Inconsistent terminology: 'Réglage fin' vs 'affinés'; trademark ™ misplaced—belongs on Unsloth brand, not after 'mémoire'. |
| fr-FR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | 'Affinage/Affinez' unusual; 'Fine-tuning' typically kept or 'réglage fin'. 'des grands' should be 'de grands'. |
| fr-FR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should be after LLMs, not LLM™); 'ajustement fin' vs 'affinés' inconsistent terminology; otherwise fluent. |
| he | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 78 | Inconsistent verb forms: title uses plural, body uses singular imperative. |
| ja-JP | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | Omits 'speech-to-speech' nuance; title '音声対音声' awkward, body just '音声翻訳' loses source-to-target meaning. |
| ja-JP | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced; source has 'LLMs™' but translation moved ™ to Unsloth, altering meaning. |
| pl-PL | playbooks/supplemental/amd-sync/playbook.json | 78 | Product name 'AMD Sync' mistranslated as 'synchronizacją AMD' in title; otherwise accurate and fluent. |
| pl-PL | playbooks/supplemental/github-slack-development-digest/playbook.json | 78 | 'Digest' mistranslated as 'cyfrowy biuletyn'; 'local-LLM digest' means digest by local LLM, slightly ambiguous rendering |
| ro-RO | playbooks/supplemental/vllm-inference/playbook.json | 78 | 'Primii' typo (should be 'Primii/Primii pași→Primii'), 'serverea' is an invented/incorrect term for 'serving'. |
| sk-SK | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 78 | Title mistranslated as 'I am running' (Spúšťam); 'Nasadite' missing diacritic (should be Nasaďte). |
| sl-SI | playbooks/supplemental/amd-sync/playbook.json | 78 | Title mistranslates 'AMD Sync' brand as 'sinhronizacijo AMD'; body correctly keeps 'AMD Sync'. Inconsistency. |
| sl-SI | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Inconsistent fine-tuning rendering; 'Fino prilagajanje/nastavite' awkward; otherwise accurate, brands intact. |
| sr-Latn | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | Title omits 'speech-to-speech' nuance; 'govor u govor' slightly awkward but acceptable. |
| sr-Latn | playbooks/supplemental/github-slack-development-digest/playbook.json | 78 | Inconsistent 'digest' translation (izveštaj vs digest); 'GitHub-to-Slack' kept English, awkward phrasing. |
| sv-SE | playbooks/supplemental/lemonade-getting-started/playbook.json | 78 | 'öppen källkod-lokal AI-server' awkward; should be 'lokal AI-server med öppen källkod' |
| th-TH | playbooks/core/comfyui-image-gen/playbook.json | 78 | Title 'กำลังสร้าง' implies ongoing action; should be 'การสร้าง'. Slightly awkward 'ภาพที่สร้างโดย AI'. |
| th-TH | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 78 | Title left partly untranslated ('Running'); otherwise accurate, fluent, terms intact. |
| uk-UA | playbooks/core/n8n-automation-gpt-oss/playbook.json | 78 | "саммарайзер" is an awkward transliteration; "засіб підсумовування новин" preferred. Otherwise accurate. |
| zh-TW | playbooks/supplemental/clustering-rccl/playbook.json | 78 | Title omits 'with RCCL'; 'Clustering' left untranslated in heading, reducing fluency. |
| zh-TW | playbooks/supplemental/hermes-lemonade-server/playbook.json | 78 | Inconsistent: '本地'/'本機' mixed; 'Hermes 代理' vs 'Hermes Agent' inconsistent brand handling in title. |
| ro-RO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 80 | Trademark symbol misplaced (should follow LLMs™ brand concept); otherwise accurate and fluent. |
| tr-TR | playbooks/supplemental/speech2speech-translation/platform.md | 80 | Headings left untranslated (Platform Configuration, Prerequisites, Required Models, Network Requirements); table headers untranslated. Body translation accurate and fluent. |
| ar | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent terminology for LLMs; 'ضبط' alone underspecifies fine-tuning (ضبط دقيق preferred). Otherwise accurate, intact terms. |
| cs-CZ | playbooks/supplemental/amd-sync/playbook.json | 82 | Title translates 'AMD Sync' as 'synchronizací AMD' inconsistently; body keeps brand correctly. Minor terminology inconsistency. |
| cs-CZ | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Anglicism 'Clustrování' awkward; 'Halos' plural left untranslated in title; otherwise accurate and fluent. |
| cs-CZ | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'jader' vs 'kernely' for kernels; otherwise accurate, fluent, brands intact. |
| cs-CZ | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | '™' misplaced; redundant 'jazykových modelů LLM'; 'jemné dolaďování' slightly verbose but acceptable. |
| cs-CZ | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 82 | Added 'AMD' not in source; 'Clustrování' is awkward anglicism; otherwise accurate, terms/code intact. |
| da-DK | playbooks/supplemental/cvml/playbook.json | 82 | Grammatical gender error: 'Lokal' should be 'Lokalt' for neuter 'computersyn'. Otherwise accurate, terms/brands intact. |
| de-DE | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | LLaMA Factory hyphenated incorrectly; 'LLaMA-Factory-Techniken' misattributes Factory as technique, altering meaning slightly. |
| el-GR | playbooks/supplemental/openhands-getting-started/playbook.json | 82 | 'πράκτορα κωδικοποίησης' awkward; 'coding agent' better as 'πράκτορα προγραμματισμού/κώδικα'. Otherwise accurate, brands intact. |
| es-LA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced in translation; '™' should follow Unsloth product, not LLMs. Otherwise accurate, fluent. |
| fi-FI | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | "Running...Locally" slightly off; "OpenClaw-itsenäinen" compound awkward, better "itsenäinen OpenClaw-tekoälyagentti". |
| fi-FI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced onto LLM instead of staying with Unsloth brand per source. |
| fr-CA | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | Inconsistent 'diffusion'/'servir' for 'serving'; 'de grands modèles' preferred over 'des grands modèles'. |
| fr-CA | playbooks/supplemental/vllm-inference/playbook.json | 82 | "le service" ambiguous for serving; "GPU" acceptable but "processeur graphique" preferred by OQLF. |
| fr-FR | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | 'diffusion' suboptimal for 'serving'; 'de grands modèles' more correct than 'des grands modèles' |
| fr-FR | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'noyaux' in title vs 'kernels' in body for same term. |
| he | playbooks/supplemental/openhands-getting-started/playbook.json | 82 | Awkward 'ה-agent הקידוד' phrasing; 'מבית OpenHands' slightly off for 'OpenHands coding agent'. |
| hu-HU | playbooks/supplemental/gaia-agents/playbook.json | 82 | Title mistranslates 'first agent with GAIA' as 'GAIA's first agent'; otherwise accurate and fluent. |
| hu-HU | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Title reformatted awkwardly with colon; 'ds4-gyel' suffix unusual. Otherwise accurate, fluent, terms intact. |
| it-IT | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Title redundant 'Ottimizzazione fine-tuning'; LLaMA Factory is a tool, not a technique—phrasing slightly misleading. |
| it-IT | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Omits 'speech-to-speech' nuance; 'traduzione vocale' slightly generic but adequate and fluent. |
| ko-KR | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Inconsistent terminology: '음성 간' vs '음성 대 음성'; otherwise accurate and fluent. |
| ko-KR | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Title '실행 중' (progressive) misrenders gerund 'Running'; should be '실행하기'. |
| nb-NO | playbooks/supplemental/clustering-rccl/playbook.json | 82 | First line: 'To cluster' untranslated English verb; should be 'Klynge sammen' or similar Norwegian. |
| nb-NO | playbooks/supplemental/cvml/playbook.json | 82 | Gender error: 'lokal datasyn' should be 'lokalt datasyn' (neuter). Otherwise accurate, terms/brands intact. |
| nb-NO | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 82 | Added 'AMD' not in source; 'Clustering' left untranslated; 'Halo-er' awkward pluralization. |
| nl-NL | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced in source; 'gefinetunede' awkward neologism but understandable; otherwise accurate. |
| pt-PT | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | 'Executando' is Brazilian gerund style; pt-PT prefers 'Executar/A executar'. Otherwise accurate, fluent, terms intact. |
| ro-RO | playbooks/core/vscode-qwen3-coder/playbook.json | 82 | "Codificare" awkward for coding; "asistență de cod" slightly literal but understandable; brands intact. |
| ro-RO | playbooks/supplemental/clustering-rccl/playbook.json | 82 | "Halos" left plural/untranslated in title; "Gruparea" less idiomatic than "Clustering". Otherwise accurate. |
| ro-RO | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 82 | "Clustering" left untranslated (anglicism); "unități" odd for "Halos"; otherwise accurate, terms/code intact. |
| sk-SK | playbooks/supplemental/amd-sync/playbook.json | 82 | Title translates 'AMD Sync' as 'synchronizáciou AMD', inconsistent with brand name kept later; otherwise accurate. |
| sk-SK | playbooks/supplemental/open-webui-chat/playbook.json | 82 | Redundant 'LLM modelmi' (LLM already means model); 'Rozprávanie' slightly informal vs 'Chatovanie'. |
| sk-SK | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title omits 'speech-to-speech' nuance; otherwise accurate and fluent. |
| sk-SK | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol ™ misplaced (belongs to Unsloth, not LLM); otherwise accurate and fluent. |
| sl-SI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent 'fine-tuning' rendering between title and body; 'fino prilagajanje' awkward but acceptable; terms intact. |
| sl-SI | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title term 'govorno-govorno' awkward; rest fluent and accurate. |
| sr-Latn | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | Inconsistent terminology: 'posluživanje' vs 'servisiranje' for 'serving'; minor fluency issues. |
| sr-Latn | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent 'kernela' vs 'jezgra' terminology; otherwise accurate, brands intact. |
| sr-Latn | playbooks/supplemental/hermes-lemonade-server/playbook.json | 82 | Grammar: 'sa Lemonade Server' should be 'sa Lemonade Serverom'; otherwise accurate, fluent. |
| th-TH | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title leaves 'Clustering' untranslated, slightly awkward; otherwise accurate and fluent. |
| th-TH | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | LLaMA-Factory inconsistent hyphenation vs source; otherwise accurate and fluent. |
| tr-TR | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | "RPC server" untranslated; "çıkarım ayarı yapın" awkward for 'set up inference'; slightly stiff phrasing. |
| tr-TR | playbooks/supplemental/vllm-inference/playbook.json | 82 | Added 'AMD' not in source; otherwise accurate and fluent. |
| tr-TR | playbooks/supplemental/openhands-getting-started/playbook.json | 82 | Added 'AMD' before OpenHands (not in source); otherwise accurate and fluent. |
| uk-UA | playbooks/supplemental/amd-sync/playbook.json | 82 | Title mistranslates brand 'AMD Sync' as 'синхронізацією AMD'; otherwise accurate and fluent. |
| uk-UA | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Awkward 'мовлення-в-мовлення' parenthetical; 'Побудуйте' slightly literal but acceptable. |
| uk-UA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent terminology (доналаштування vs тонкого налаштування); trademark ™ misplaced from 'fine-tuned LLMs' to LLM |
| uk-UA | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | "механізму виведення" is suboptimal for 'inference engine'; better 'рушій інференсу'. Otherwise accurate, brands intact. |
| zh-CN | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title 'Clustering' rendered as verb '集群' is awkward; 'configured with RCCL' misattributes RCCL to devices rather than clustering method. |
| zh-CN | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | Inconsistent 'Lemonade Server' rendering (服务器 vs Server); title phrasing slightly awkward but accurate. |
| zh-TW | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | Title omits 'with RPC'; 'RPC server' left partly untranslated but acceptable; otherwise accurate. |
| fi-FI | playbooks/dependencies/ds4_toolbox_image.md | 84 | Awkward 'säilötuvan' coinage for toolbox; 'kuvan' for image acceptable but mixed terminology. Otherwise accurate, code intact. |
| ro-RO | playbooks/supplemental/pytorch-kernels/playbook.json | 84 | Inconsistent 'kernele' vs 'kernel-uri' plural; otherwise accurate, fluent, terms/brands intact. |
| sl-SI | playbooks/core/lmstudio-rocm-llms/playbook.json | 84 | "strežba" is awkward for serving LLMs; "strežnik"/"gostovanje" preferred, otherwise accurate. |
