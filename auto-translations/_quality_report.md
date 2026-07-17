# Translation quality report

Automated MQM/GEMBA adequacy+fluency scores (0-100) per locale. No human review.

| Locale | Files | Mean | Min | Judge |
|--------|-------|------|-----|-------|
| ar | 68 | 93.4 | 82 | Claude-Opus-4.6 |
| cs-CZ | 68 | 93.7 | 82 | Claude-Opus-4.6 |
| da-DK | 68 | 93.4 | 72 | Claude-Opus-4.6 |
| de-DE | 68 | 94.0 | 85 | Claude-Opus-4.6 |
| el-GR | 68 | 92.0 | 72 | Claude-Opus-4.6 |
| es-LA | 68 | 93.7 | 82 | Claude-Opus-4.6 |
| fi-FI | 68 | 92.0 | 75 | Claude-Opus-4.6 |
| fr-FR | 68 | 93.7 | 72 | Claude-Opus-4.6 |
| he | 68 | 93.3 | 72 | Claude-Opus-4.6 |
| hu-HU | 68 | 92.6 | 82 | Claude-Opus-4.6 |
| it-IT | 68 | 93.2 | 72 | Claude-Opus-4.6 |
| ja-JP | 68 | 95.0 | 82 | Claude-Opus-4.6 |
| ko-KR | 68 | 95.2 | 88 | Claude-Opus-4.6 |
| nb-NO | 68 | 93.1 | 82 | Claude-Opus-4.6 |
| nl-NL | 68 | 91.7 | 0 | Claude-Opus-4.6 |
| pl-PL | 68 | 93.7 | 78 | Claude-Opus-4.6 |
| pt-BR | 68 | 93.8 | 78 | Claude-Opus-4.6 |
| ro-RO | 68 | 92.7 | 78 | Claude-Opus-4.6 |
| ru-RU | 68 | 94.2 | 82 | Claude-Opus-4.6 |
| sk-SK | 68 | 93.7 | 82 | Claude-Opus-4.6 |
| sl-SI | 68 | 89.5 | 72 | Claude-Opus-4.6 |
| sr-Latn | 68 | 92.5 | 82 | Claude-Opus-4.6 |
| sv-SE | 68 | 93.7 | 82 | Claude-Opus-4.6 |
| th-TH | 68 | 93.6 | 82 | Claude-Opus-4.6 |
| tr-TR | 68 | 94.4 | 88 | Claude-Opus-4.6 |
| uk-UA | 68 | 93.4 | 78 | Claude-Opus-4.6 |
| zh-CN | 68 | 94.2 | 75 | Claude-Opus-4.6 |
| zh-TW | 68 | 94.7 | 88 | Claude-Opus-4.6 |

## Files below 85 (78)

| Locale | File | Score | Issues |
|--------|------|-------|--------|
| nl-NL | playbooks/dependencies/memoryconfig.md | 0 | judge error: Extra data: line 3 column 1 (char 807) |
| da-DK | playbooks/supplemental/open-webui-chat/playbook.json | 72 | Title mixes English 'Chatting' with Danish; should be fully translated, e.g. 'Chat med LLM'er' or 'Snak med LLM'er'. |
| el-GR | playbooks/supplemental/pytorch-finetuning/playbook.json | 72 | Fine-tuning translated as Βελτιστοποίηση (optimization) instead of correct Μικρο-ρύθμιση or Λεπτή ρύθμιση; mistranslation of key technical term. |
| fr-FR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | Inconsistent acronym (LLMs vs LLM™). 'mémoire efficace' is awkward; should be 'efficaces en mémoire'. Trademark placement shifted from 'fine-tuned LLMs™' to 'LLM™'. |
| he | playbooks/supplemental/pytorch-kernels/playbook.json | 72 | Inconsistent translation: 'software' left untranslated; 'kernels' not capitalized consistently; mixing Hebrew and English awkwardly; 'GPU Kernels' should be consistent throughout. |
| it-IT | playbooks/supplemental/pytorch-finetuning/playbook.json | 72 | "Ottimizzazione fine" is awkward; standard Italian uses "Fine-tuning" as loanword or "Messa a punto". Imperative "Ottimizza" shifts register from infinitive source. |
| it-IT | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 72 | "Ottimizzazione Fine-Tuning" is redundant. "memoria efficiente" should be "efficienza di memoria" or "memory-efficient" kept closer to source meaning. |
| sl-SI | playbooks/dependencies/memoryconfig.md | 72 | Grammar error: 'privzeta namenjena pomnilnik' (gender mismatch). 'kolesa/kolo' for 'wheels' is awkward; 'pakete' preferred. 'namenski VRAM' should be 'namenjeni VRAM'. TTM 'page setting' mistranslated |
| sl-SI | playbooks/supplemental/llama-factory-finetuning/playbook.json | 72 | Inconsistent hyphenation ('Fino nastavljanje' vs 'Fino-nastavljajte'); 'LLaMA-Factory' adds hyphen not in source; 'Fino nastavljanje' is an awkward calque rather than natural Slovenian terminology. |
| sl-SI | playbooks/supplemental/pytorch-kernels/playbook.json | 72 | Inconsistent terminology: 'jeder' (title) vs 'jedrnike' (subtitle) for 'kernels'. 'Jedrnike' is non-standard; 'jedra' is preferred throughout. |
| sl-SI | playbooks/supplemental/vllm-inference/playbook.json | 72 | "vsebnikovim" is awkward/incorrect; should be "kontejneriziranim". "sklepanje" is acceptable but "strežbo" is slightly unnatural for "serving". |
| el-GR | playbooks/supplemental/llama-factory-finetuning/playbook.json | 75 | "Fine-Tuning" inconsistently translated as "Ρύθμιση" (title) vs "Βελτιστοποιήστε" (body); should be "Λεπτομερής Ρύθμιση" or similar. "LLaMA Factory" changed to "LLaMA-Factory" (hyphenated). |
| fi-FI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 75 | "Hienosäätö LLM-malleille" should be "LLM-mallien hienosäätö Unsloth-työkalulla"; allative case incorrect for this context. |
| he | playbooks/core/lmstudio-rocm-llms/playbook.json | 75 | "מודלים של שפה גדולים" is awkward; should be "מודלי שפה גדולים". "הגשת" is a literal/awkward translation of "serving". |
| zh-CN | playbooks/supplemental/clustering-rpc-server/playbook.json | 75 | Title awkward: '集群两个...与 RPC' misparses structure; should be '通过 RPC 集群两台 Ryzen™ AI Halo' |
| it-IT | playbooks/supplemental/speech2speech-translation/playbook.json | 78 | Title drops 'speech-to-speech'; body redundantly adds 'da voce a voce' alongside 'vocale', slightly awkward phrasing. |
| pl-PL | playbooks/core/n8n-automation-gpt-oss/playbook.json | 78 | "news summarizer" translated as "agregator wiadomości z podsumowaniami" (news aggregator with summaries) instead of "narzędzie do podsumowywania wiadomości" — shifts meaning from summarizer to aggrega |
| pt-BR | playbooks/dependencies/nodejs.md | 78 | Bash code block comments left untranslated in English. Windows steps partially translated but inconsistent with Linux section. |
| ro-RO | playbooks/supplemental/cvml/playbook.json | 78 | "Computer Vision Local" is awkward; should be "Viziune Computerizată Locală" or keep English term with better word order. |
| sl-SI | playbooks/core/n8n-automation-gpt-oss/playbook.json | 78 | Awkward phrasing 's pomočjo umetne inteligence podprt povzemalnik' is clunky; more natural would be 'povzemalnik novic, podprt z UI'. |
| sl-SI | playbooks/supplemental/pytorch-finetuning/playbook.json | 78 | "Fino nastavljanje" is a calque; "natančno prilagajanje" or similar would be more natural. Inconsistent LLM/LLM-jev usage. |
| uk-UA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 78 | "пам'яттєво-ефективного" is awkward; inconsistent LLM/LLMs usage; "fine-tuned LLMs" mistranslated as "дообучення LLMs" (noun vs adjective shift). |
| ar | playbooks/supplemental/open-webui-chat/playbook.json | 82 | Inconsistent terminology: 'LLMs' translated as full phrase in title but kept as 'LLM' abbreviation in subtitle. Minor inconsistency but understandable. |
| ar | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | LLMs acronym partially translated inconsistently; 'Fine-Tuned LLMs™' brand-like phrase was paraphrased rather than kept intact. |
| ar | playbooks/supplemental/vllm-inference/playbook.json | 82 | "containerized" translated as "المُحتوى" is slightly unusual; should be "المُعبّأ في حاوية". "serving" as "الخدمة" is acceptable but could be more precise. |
| cs-CZ | playbooks/core/n8n-automation-gpt-oss/playbook.json | 82 | "AI-powered" translated as "AI" losing "powered" nuance. "news summarizer" as "zpravodajský sumarizátor" is slightly awkward; "sumarizátor zpráv" would be more natural. |
| cs-CZ | playbooks/supplemental/clustering-rccl/playbook.json | 82 | "Clustering" left untranslated in title; "vícenódový" is a calque, "víceuzlový" preferred; "workloads" simplified to "úlohy" losing nuance |
| cs-CZ | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'jader' (title) vs 'kernely' (subtitle) for 'kernels'. Should use one consistently. |
| da-DK | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | Gender agreement error: 'autonomt' should be 'autonom' to agree with 'AI-agent' (common gender). |
| el-GR | playbooks/core/vscode-qwen3-coder/playbook.json | 82 | "κωδικοποίηση" is ambiguous; "συγγραφή κώδικα" or "προγραμματισμός" would be more accurate for "coding". Title uses "VS Code" but source has "VSCode" (minor). |
| el-GR | playbooks/supplemental/clustering-rccl/playbook.json | 82 | "Clustering" translated as "Ομαδοποίηση" loses technical meaning; "Halos" changed to singular "Halo" in subtitle inconsistently. |
| el-GR | playbooks/supplemental/clustering-rpc-server/playbook.json | 82 | "Clustering" translated as "Ομαδοποίηση" instead of more precise "Συσταδοποίηση"; "inference" as "εξαγωγής συμπερασμάτων" is awkward—standard ML term is "συμπερασμός". |
| el-GR | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent terminology: 'Kernels' untranslated in title but translated as 'πυρήνες' in subtitle; 'software' left untranslated in subtitle. |
| el-GR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | "Fine-tuning" translated as "Βελτιστοποίηση" (optimization) instead of the more precise "Λεπτή ρύθμιση" or keeping "Fine-Tuning". Slight semantic shift. |
| es-LA | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | Inconsistent 'GPU'/'de GPU' usage; 'AMD ROCm™ software' left partially untranslated and awkward word order at end. |
| es-LA | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | "memory-efficient" modifies the fine-tuning process, not the LLMs; slight restructuring changes emphasis. Otherwise adequate. |
| fi-FI | playbooks/core/comfyui-image-gen/playbook.json | 82 | Minor grammatical issue: 'Luo upea' should be 'Luo upeita' (plural adjective needed to match plural noun 'kuvia'). |
| fi-FI | playbooks/dependencies/nodejs.md | 82 | Bash code block comments left untranslated in Finnish. Minor inconsistency in translation completeness. |
| fi-FI | playbooks/supplemental/open-webui-chat/playbook.json | 82 | Minor fluency issues: 'LLM:ien' is awkward inflection; 'chattailuun' is informal but acceptable. Brand name 'Open WebUI' preserved correctly. |
| fi-FI | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | "OpenClaw'n" uses awkward apostrophe for Finnish genitive; should be "OpenClaw:n". Minor fluency issues with compound word formation. |
| fi-FI | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Title uses allative 'malleille' (for models) instead of genitive/partitive; should be 'LLM-mallien hienosäätö'. Minor case inconsistency with 'PyTorch' missing suffix in body. |
| fr-FR | playbooks/dependencies/nodejs.md | 82 | Bash code comments left untranslated in French version; inconsistent with translated cmd section and note. |
| he | playbooks/core/pytorch-rocm-llms/playbook.json | 82 | Missing word: 'מודלים שפה' should be 'מודלי שפה' (construct state). Minor grammatical error. |
| hu-HU | playbooks/core/vscode-qwen3-coder/platform.md | 82 | "Helyszín" should be "Hely" or "Elérési út" for file paths. "A LM Studio" should be "Az LM Studio". Title "Platform Configuration" left untranslated. Minor capitalization inconsistencies in headings. |
| hu-HU | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Missing 'to' equivalent in 'speech-to-speech' → should be 'beszédről beszédre' or 'beszéd-beszéd közötti'. 'Build a' slightly undertranslated as 'létrehozása'. |
| it-IT | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | "LLaMA-Factory" should be "LLaMA Factory" (no hyphen). Redundant "Ottimizzazione Fine-Tuning" is awkward; mixing Italian and English in the title reduces fluency. |
| ja-JP | playbooks/core/comfyui-image-gen/playbook.json | 82 | Title inconsistency: 'Image生成' mixes English/Japanese; should be '画像生成' for natural Japanese. |
| nb-NO | playbooks/core/n8n-automation-gpt-oss/playbook.json | 82 | "KI-drevet" should be "AI-drevet" – Norwegian commonly uses "AI", not "KI". Otherwise fluent and accurate. |
| nb-NO | playbooks/supplemental/cvml/playbook.json | 82 | "datamaskinvisjon" is a literal calque; "bildegjenkjenning" or keeping "Computer Vision" would be more natural. "persepsjonskapasiteter" is awkward; "på toppen av" is a literal translation of "on top  |
| nb-NO | playbooks/supplemental/openclaw-lemonade-server/playbook.json | 82 | Gender agreement error: 'autonomt' should be 'autonom' to agree with 'AI-agent' (common gender). |
| nb-NO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent pluralization: 'LLM-er' vs 'LLMs™'. 'fine-tuned LLMs' mistranslated as 'finjustering av LLMs' (noun vs adjective). |
| nl-NL | playbooks/core/lmstudio-rocm-llms/playbook.json | 82 | "bedienen" and "serveren" are awkward for "serving"; better: "aanbieden" or "hosten". Minor fluency issues. |
| pl-PL | playbooks/dependencies/nodejs.md | 82 | Bash code comments left untranslated in Polish version; inconsistent translation approach between sections. |
| pt-BR | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | "grandes modelos de linguagem" should be "modelos de linguagem de grande porte" or similar; "AMD ROCm™ Software" left untranslated (acceptable for brand). |
| pt-BR | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | "AMD ROCm™ software" left partially untranslated; should be "software AMD ROCm™" for natural pt-BR word order. |
| pt-BR | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Minor fluency issue: 'LLMs ajustados com eficiência de memória' is slightly awkward; 'ajuste fino de LLMs com eficiência de memória' would be more natural. 'Fine-tuned' nuance slightly shifted. |
| ro-RO | playbooks/supplemental/gaia-agents/playbook.json | 82 | Inconsistent register: title uses informal 'tău' but body uses formal 'Construiți/Utilizați'. Minor fluency issue. |
| ro-RO | playbooks/supplemental/pytorch-kernels/playbook.json | 82 | "nuclee GPU" is an awkward translation of "GPU kernels"; "kerneluri GPU" is the standard Romanian technical term used in practice. |
| ro-RO | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Inconsistent terminology: title uses 'Vorbire-în-Vorbire' but body switches to 'vocală'. 'speech-to-speech' dropped in body. Minor fluency issues. |
| ro-RO | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Trademark symbol repositioned from after 'LLMs' to after 'LLM-uri'; slight awkwardness in phrasing but adequate. |
| ru-RU | playbooks/dependencies/nodejs.md | 82 | Bash code comments left untranslated; Windows steps translated but Linux section not translated at all. |
| sk-SK | playbooks/dependencies/nodejs.md | 82 | Bash code block comments left untranslated in Slovak; minor inconsistency with translating some UI text but not inline code comments. |
| sk-SK | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Typo: 'viacu uzlový' should be 'viacuzlový'. Missing 'Halos' plural form in title (used 'Halo' instead). |
| sl-SI | playbooks/dependencies/driver.md | 82 | UI strings 'Driver and Software' and 'Manage Updates' left untranslated (acceptable if matching app UI). 'sistemske vrstice' is awkward for 'system tray'. Minor phrasing issues. |
| sl-SI | playbooks/supplemental/amd-sync/playbook.json | 82 | "enoklični" is incorrect; should be "z enim klikom" (one-click). Minor fluency issue with mixed formal register. |
| sl-SI | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | "Fino nastavljanje" is a calque; more natural would be "Natančno prilagajanje". Trademark symbol preserved. Brand name Unsloth correctly kept. |
| sr-Latn | playbooks/supplemental/cvml/playbook.json | 82 | "na vrhu" is a literal translation of "on top of"; should be "na osnovu" or "povrh". "percepcijske" is slightly awkward; "perceptivne" is more natural. |
| sr-Latn | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | "fine-tuned LLMs" translated as "fino podešavanje LLM-ova" shifts meaning from adjective (fine-tuned models) to verb phrase (fine-tuning). Minor adequacy issue. |
| sv-SE | playbooks/dependencies/nodejs.md | 82 | Code block comments left untranslated in bash section; surrounding prose is translated but inline comments remain in English. |
| sv-SE | playbooks/supplemental/cvml/playbook.json | 82 | "Lokal datorseende" is grammatically awkward; should be "Lokalt datorseende" (neuter agreement). Otherwise accurate and fluent. |
| sv-SE | playbooks/supplemental/speech2speech-translation/playbook.json | 82 | Compound word errors: should be 'Realtids-tal-till-tal-översättning' or 'Tal-till-tal-översättning i realtid'. Awkward phrasing with 'realtids tal-till-tal'. |
| th-TH | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Inconsistent use of 'LLM' vs 'LLMs'; mixed Thai/English phrasing for 'fine-tune' vs 'การปรับแต่งอย่างละเอียด'; adequate but slightly unpolished. |
| uk-UA | playbooks/dependencies/nodejs.md | 82 | Bash code comments left untranslated. 'Node.js Downloads' link text not translated. Minor inconsistency in translation completeness. |
| uk-UA | playbooks/supplemental/llama-factory-finetuning/playbook.json | 82 | Inconsistent translation of 'fine-tuning': 'тонке налаштування' in title vs 'точне налаштування' in subtitle. 'LLaMA Factory' hyphenated as 'LLaMA-Factory' differs from source. |
| uk-UA | playbooks/supplemental/pytorch-finetuning/playbook.json | 82 | Inconsistent terminology: 'Тонке налаштування' in title vs 'Точне налаштування' in subtitle. Both translate 'Fine-Tuning' differently. |
| zh-CN | playbooks/supplemental/clustering-rccl/playbook.json | 82 | Title '集群两个 Ryzen™ AI Halo 与 RCCL' is awkward; '集群' used as verb is unnatural. Better: '使用 RCCL 对两台 Ryzen™ AI Halo 进行集群配置'. Subtitle is good. |
| zh-CN | playbooks/supplemental/gaia-agents/playbook.json | 82 | Inconsistent terminology: 'agent' translated as '智能体' in title but '代理' in body text. |
| zh-CN | playbooks/supplemental/unsloth-llms-finetuning/playbook.json | 82 | Second line slightly awkward phrasing; 'fine-tuned LLMs' mistranslated as '微调 LLMs' losing 'fine-tuned' as adjective; trademark preserved. |
