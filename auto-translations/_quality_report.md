# Translation quality report

Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.

| Locale | Files | Mean | Min | Judge |
|--------|-------|------|-----|-------|
| ar | 80 | 93.2 | 88 | Claude-Opus-4.8 |
| cs-CZ | 80 | 92.5 | 78 | Claude-Opus-4.8 |
| da-DK | 80 | 92.4 | 82 | Claude-Opus-4.8 |
| de-DE | 80 | 93.5 | 82 | Claude-Opus-4.8 |
| el-GR | 80 | 92.3 | 78 | Claude-Opus-4.8 |
| es-LA | 80 | 93.4 | 82 | Claude-Opus-4.8 |
| fi-FI | 80 | 91.9 | 72 | Claude-Opus-4.8 |
| fr-CA | 80 | 90.7 | 72 | Claude-Opus-4.8 |
| fr-FR | 80 | 93.3 | 78 | Claude-Opus-4.8 |
| he | 80 | 92.2 | 60 | Claude-Opus-4.8 |
| hu-HU | 80 | 91.6 | 82 | Claude-Opus-4.8 |
| it-IT | 80 | 93.9 | 72 | Claude-Opus-4.8 |
| ja-JP | 80 | 93.7 | 78 | Claude-Opus-4.8 |
| ko-KR | 80 | 93.7 | 88 | Claude-Opus-4.8 |
| nb-NO | 80 | 91.8 | 82 | Claude-Opus-4.8 |
| nl-NL | 80 | 92.0 | 78 | Claude-Opus-4.8 |
| pl-PL | 80 | 93.0 | 78 | Claude-Opus-4.8 |
| pt-BR | 80 | 93.7 | 78 | Claude-Opus-4.8 |
| pt-PT | 80 | 92.5 | 78 | Claude-Opus-4.8 |
| ro-RO | 80 | 93.0 | 82 | Claude-Opus-4.8 |
| ru-RU | 80 | 92.9 | 88 | Claude-Opus-4.8 |
| sk-SK | 80 | 91.6 | 82 | Claude-Opus-4.8 |
| sl-SI | 80 | 90.5 | 62 | Claude-Opus-4.8 |
| sr-Latn | 80 | 91.1 | 78 | Claude-Opus-4.8 |
| sv-SE | 80 | 92.5 | 82 | Claude-Opus-4.8 |
| th-TH | 80 | 93.0 | 78 | Claude-Opus-4.8 |
| tr-TR | 80 | 92.3 | 72 | Claude-Opus-4.8 |
| uk-UA | 80 | 92.7 | 82 | Claude-Opus-4.8 |
| zh-CN | 80 | 92.9 | 60 | Claude-Opus-4.8 |
| zh-TW | 80 | 93.2 | 82 | Claude-Opus-4.8 |

## Files below 85 (89)

| Locale | File | Score | Issues |
|--------|------|-------|--------|
| he | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 60 | Title left untranslated ('Running DeepSeek V4 Flash'); body translated well with terms intact. |
| zh-CN | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 60 | Title left untranslated in English; body translation accurate and fluent. |
| sl-SI | playbooks/supplemental/pytorch-finetuning/playbook.json | 62 | Inconsistent terminology; 'Fine-tune' left untranslated in second sentence; awkward 'Fino prilagajanje'; brand terms intact. |
| fi-FI | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 72 | Title awkward word order; second sentence has grammatical case error ('OpenClaw-autonomisen tekoälyagentin käyttö'). |
| fr-CA | playbooks/supplemental/amd-sync/playbook.json | 72 | Title translates 'AMD Sync' but body keeps it as brand; inconsistent handling of product name. |
| it-IT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Redundant 'Ottimizzazione fine-tuning'; trademark ™ misplaced from Unsloth to LLM; 'fine-tuned' rendered as generic 'ottimizzati'. |
| tr-TR | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 72 | Title mistranslation: 'Four Ryzen AI Halos' rendered as 'Dört Sistemi... (RPC)'; RPC misplaced, meaning distorted. |
| cs-CZ | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should be on Unsloth/product name); slight redundancy 'jemné doladění' vs 'doladění'. |
| cs-CZ | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 78 | Redundant 'Clustering...do klastru'; added 'AMD' brand not in source; otherwise accurate and fluent. |
| el-GR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | Inconsistent terminology: 'Βελτιστοποίηση' vs 'Συντονίστε'; hyphenated 'LLaMA-Factory' deviates from source brand naming. |
| el-GR | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Terminology inconsistency: 'Ρύθμιση ακριβείας' vs 'Συντονίστε' for fine-tune; slightly awkward but adequate. |
| el-GR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow Unsloth, not LLM); 'Fine-Tuning' terminology inconsistent between title and body. |
| fr-CA | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | Awkward 'de manière fine (« fine-tune »)'; parenthetical English redundant; 'Optimisez' less precise than 'affinez/ajustez'. |
| fr-CA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark misplaced: ™ belongs after 'fine-tuned LLMs' concept; awkward placement on 'LLM™'. Otherwise accurate, fluent. |
| fr-FR | playbooks/supplemental/pytorch-kernels/playbook.json | 78 | Inconsistent terminology: 'noyaux' vs 'kernels' for same concept across the two lines. |
| fr-FR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced (should follow LLMs, not the phrase); terminology inconsistency (Ajustement fin vs affinés). |
| he | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 78 | Title mistranslates 'Halo' as 'Max'; drops trademark symbol; 'ריכוב' unusual term for clustering. |
| ja-JP | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | "音声対音声" is awkward; "音声から音声への" or "スピーチ・トゥ・スピーチ" more natural. Otherwise accurate. |
| ja-JP | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | Trademark symbol misplaced; source has 'fine-tuned LLMs™' but translation attaches ™ to Unsloth. |
| nl-NL | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 78 | Title 'Running' left untranslated (should be 'DeepSeek V4 Flash uitvoeren'); 'inference engine' kept in English. |
| nl-NL | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 78 | Title left partly untranslated ('Clustering Four'); should be 'Vier ... clusteren'. Otherwise accurate. |
| pl-PL | playbooks/supplemental/amd-sync/playbook.json | 78 | Product name 'AMD Sync' mistranslated as 'synchronizacją AMD' in title; otherwise accurate and fluent. |
| pt-BR | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translates 'AMD Sync' as 'Sincronização AMD'—brand name should stay 'AMD Sync' consistently. |
| pt-BR | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 78 | Redundant title 'Agrupando (Clustering)...em Cluster'; awkward double clustering term; otherwise accurate and fluent. |
| pt-PT | playbooks/supplemental/amd-sync/playbook.json | 78 | Title translates 'AMD Sync' as 'Sincronização AMD' but body keeps 'AMD Sync'—inconsistent brand handling. |
| sl-SI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 78 | Inconsistent 'fine-tuning' rendering; 'Fino nastavite' awkward; otherwise accurate, terms intact. |
| sl-SI | playbooks/supplemental/cvml/playbook.json | 78 | Grammatical error: 'Lokalno računalniško vid' should be 'Lokalni računalniški vid'; otherwise accurate, terms/brands intact. |
| sr-Latn | playbooks/core/lmstudio-rocm-llms/playbook.json | 78 | Inconsistent 'pružanje/posluživanje' for serving; 'LM Studio-a' hyphenation awkward but acceptable. |
| sr-Latn | playbooks/supplemental/hermes-lemonade-server/playbook.json | 78 | Awkward 'Hermes Agent autonomnog AI agenta' redundancy; inconsistent brand casing; 'Server-a' hyphenation stylistically off. |
| th-TH | playbooks/supplemental/clustering-rccl/playbook.json | 78 | Title left partially untranslated ('Clustering Two Ryzen™ AI Halos'); body translation accurate and fluent. |
| th-TH | playbooks/supplemental/cvml/playbook.json | 78 | Title left 'Local Computer Vision' untranslated inconsistently; otherwise accurate, brands and terms intact. |
| zh-CN | playbooks/supplemental/clustering-rccl/playbook.json | 78 | Title 'AMD' added; 'clustering' rendered awkwardly as verb; 'with RCCL' misplaced (modifies clustering, not devices). |
| tr-TR | playbooks/supplemental/speech2speech-translation/platform.md | 80 | Headings left untranslated (Platform Configuration, Prerequisites, Required Models, Network Requirements); table headers untranslated. Body translation accurate and fluent. |
| cs-CZ | playbooks/supplemental/amd-sync/playbook.json | 82 | Title mistranslates 'AMD Sync' as generic 'synchronizací AMD'; otherwise accurate and fluent. |
| cs-CZ | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Anglicisms 'Clustrování', 'multi-node clusteru' unnatural; otherwise accurate, brands intact. |
| da-DK | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | "servering/betjene" awkward for serving models; better "levere/hoste". Otherwise accurate and fluent. |
| da-DK | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Gender agreement error: 'et...udviklingsoversigt' should be 'en'; otherwise accurate and fluent. |
| de-DE | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Inconsistent terminology: 'Feinabstimmung' vs 'Feintunen'; 'Feintunen' is informal/anglicism. |
| de-DE | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent terminology (Feinabstimmung vs Fine-Tuning); trademark symbol misplaced from original 'fine-tuned LLMs™'. |
| el-GR | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | 'Development Digest' left untranslated inconsistently; slightly awkward mixing of English and Greek terms. |
| es-LA | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Word order 'AMD ROCm Software' unnatural; 'lenguaje grande' should be 'gran/grande lenguaje'; otherwise accurate. |
| fi-FI | playbooks/supplemental/open-webui-chat/playbook.json | 82 | Inconsistent 'Open WebUI' declension (WebUIssa vs WebUI:ta); 'LLM-malleilla' slightly awkward but acceptable. |
| fi-FI | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent term: 'ytimien' vs 'kerneleitä'; 'PyTorch- ja...ohjelmistoa' slightly awkward compound. |
| fr-CA | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | Inconsistent 'diffusion'/'servir' for serving; 'de grands modèles' preferred over 'des grands'. Otherwise accurate. |
| fr-CA | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Inconsistent 'cluster'/'grappe' usage; title mixes English 'cluster' with French. Otherwise accurate, fluent, terms intact. |
| fr-CA | playbooks/supplemental/cvml/playbook.json | 82 | Grammatical error: 'en s'appuyant' should be 'en vous appuyant' to match 'Créez'. |
| fr-CA | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Inconsistent imperative mood (Créez vs Configurer); 'digest' rendered as 'résumé'; 'local-LLM digest' slightly ambiguous. |
| fr-CA | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Inconsistent term: 'voix-voix' vs 'voix-à-voix'; 'voix-à-voix' is anglicized calque, 'parole à parole' preferable. |
| fr-FR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | LLMs plural should be LLM in French; 'Ajustement fin' acceptable but inconsistent with 'Affinez'; minor terminology nits |
| he | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | 'Clustering' left untranslated in title; otherwise accurate, fluent, terms and numbers intact. |
| hu-HU | playbooks/supplemental/gaia-agents/playbook.json | 82 | Title mistranslates 'your first agent with GAIA' as 'GAIA's first agent'; otherwise accurate and fluent. |
| hu-HU | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Title 'Nagynyelvi' incorrect compound; inconsistent 'LLaMA Factory' vs 'LLaMA-Factory' hyphenation. |
| hu-HU | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Title awkwardly rephrased with colon; otherwise accurate, terms and brand names intact. |
| it-IT | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Title omits 'speech-to-speech' nuance; 'voce a voce' slightly awkward but acceptable; overall accurate and fluent. |
| ja-JP | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title mistranslated: 'with RCCL' modifies clustering method, rendered as noun phrase awkwardly. |
| ja-JP | playbooks/supplemental/ollama-getting-started/playbook.json | 82 | LLM incorrectly lowercased to 'llm'; otherwise accurate and fluent |
| nb-NO | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title 'Klynger av' awkward; 'Halo-er' inconsistent with 'Halo-enheter' below; otherwise accurate. |
| nb-NO | playbooks/supplemental/cvml/playbook.json | 82 | 'Lokal datasyn' gender error (should be 'lokalt'); 'oppå' awkward for 'on top of', better 'basert på'. |
| nb-NO | playbooks/supplemental/lemonade-getting-started/playbook.json | 82 | 'open source-lokal AI-server' awkward word order; 'åpen kildekode' more natural than 'open source' |
| pl-PL | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'jąder' vs 'kernele' for same term; otherwise accurate, brands/symbols intact. |
| pt-BR | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Anglicisms 'Clustering'/'workloads' left untranslated; 'multinó' awkward; otherwise accurate, brands intact. |
| pt-BR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Untranslated 'large language models' where Portuguese equivalent common; otherwise accurate, fluent, terms intact. |
| pt-PT | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Brazilian gerund 'Executando' unidiomatic in pt-PT; heading should use 'Executar'. |
| pt-PT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced (should follow Unsloth); 'eficiência de memória' slightly literal but acceptable. |
| ro-RO | playbooks/supplemental/gaia-agents/playbook.json | 82 | Inconsistent register (tău/Construiți); 'APIs' should be 'API-uri'; slightly awkward phrasing. |
| ro-RO | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Inconsistent register (Creează vs Configurați); 'Digest' kept in title but translated as 'rezumat' below—slight inconsistency. |
| sk-SK | playbooks/supplemental/amd-sync/playbook.json | 82 | Title translated 'AMD Sync' as 'synchronizáciou AMD'; inconsistent with brand name kept later. |
| sk-SK | playbooks/supplemental/open-webui-chat/playbook.json | 82 | "Rozprávanie" awkward for chatting; "chatovanie" more natural. Otherwise accurate, terms intact. |
| sk-SK | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol misplaced (should follow Unsloth, not LLM); otherwise accurate and fluent. |
| sl-SI | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | "Strežba" awkward for serving; otherwise accurate, fluent, terms/brands intact. |
| sl-SI | playbooks/supplemental/amd-sync/playbook.json | 82 | Title mistranslates 'AMD Sync' as generic 'sinhronizacijo'; inconsistent with body. Otherwise accurate, fluent, brands intact. |
| sl-SI | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent GPU terminology (GPU vs GPE); 'kernelov' anglicism; otherwise accurate, brands/terms intact. |
| sl-SI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Redundant parenthetical (fine-tuning) repeated; trademark ™ misplaced from 'LLMs' brand context; otherwise accurate, fluent. |
| sr-Latn | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'kernela' vs 'jezgra' for same term across two lines |
| sr-Latn | playbooks/supplemental/github-slack-development-digest/playbook.json | 82 | Inconsistent: 'izveštaj' vs 'digest' for same term; 'GitHub-to-Slack' left partially untranslated |
| sr-Latn | playbooks/supplemental/deepseek-v4-flash-ds4/playbook.json | 82 | Untranslated 'inference engine'; 'primenite' slightly off for deploy; otherwise accurate, brands intact. |
| sv-SE | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | 'serva'/'tillhandahålla' inconsistent for 'serve'; slightly informal 'serva' but overall accurate. |
| sv-SE | playbooks/supplemental/cvml/playbook.json | 82 | Grammar: 'Lokal datorseende' should be 'Lokalt datorseende' (neuter agreement). |
| th-TH | playbooks/core/comfyui-image-gen/playbook.json | 82 | Title mistranslated as progressive 'กำลังสร้าง' instead of gerund 'การสร้าง'; otherwise accurate. |
| uk-UA | playbooks/supplemental/amd-sync/playbook.json | 82 | Title translates 'AMD Sync' as 'синхронізацією AMD', inconsistent with brand term kept in body. |
| uk-UA | playbooks/supplemental/clustering-rpc-server-4-node/playbook.json | 82 | 'висновок' is wrong term for inference; should be 'інференс'; otherwise accurate, brands/numbers intact. |
| zh-CN | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Second line awkward; trademark symbol misplaced (belongs to LLM brand, not translation); slightly literal phrasing. |
| zh-TW | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Added '教學' not in source; comma should be full-width; otherwise accurate and fluent. |
| zh-TW | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | Title translation awkward/unclear ('叢集運算 RPC' omits 'with'); body accurate and fluent. |
| zh-TW | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | ™ symbol misplaced (belongs to Unsloth, not LLM); otherwise accurate and fluent. |
| fr-FR | playbooks/core/lmstudio-rocm-llms/playbook.json | 84 | 'Diffusion' and 'servir' for serving are suboptimal; 'de grands modèles' preferred over 'des grands'. |
| hu-HU | playbooks/supplemental/clustering-rccl/playbook.json | 84 | Inconsistent term: 'klaszterezése' vs 'fürt'; 'Multi-node' left untranslated; added 'AMD' not in source. |
| ro-RO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 84 | Trademark symbol misplaced (belongs to LLMs, not memory phrase); slightly awkward phrasing but accurate. |
| uk-UA | playbooks/supplemental/cvml/playbook.json | 84 | Redundant '(perception)' gloss unnecessary; otherwise accurate, fluent, terms and brands intact. |
