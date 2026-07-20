<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> Tento playbook používá speciální značky, které GitHub neumí zobrazit. Pro správné zobrazení tohoto obsahu prosím navštivte [amd.com/playbooks](https://amd.com/playbooks).
<!-- @github-only:end -->


## Přehled

vLLM je vysoce výkonný inferenční engine navržený pro velké jazykové modely (LLM). Poskytuje optimalizované obsluhování s průběžným dávkováním pro vysokou propustnost a API kompatibilní s OpenAI pro bezproblémovou integraci aplikací. Díky tomu je vLLM skvělou volbou pro produkční nasazení, kde jsou rychlost a efektivní využití zdrojů klíčové.

Tento playbook vás naučí, jak obsluhovat LLM pomocí kontejnerizovaného vLLM na integrovaném GPU a jak komunikovat s modely prostřednictvím Python API kompatibilního s OpenAI.

## Co se naučíte

- Jak nastavit a spustit server vLLM s podporou AMD ROCm™
- Jak komunikovat s modely přes koncové body API kompatibilního s OpenAI
- Jak odesílat výzvy (prompty) na lokální server pomocí `vllm-prompt`

## Nastavení konfigurace paměti

<!-- @require:memory-config -->

<!-- @device:halo_box -->
## Kontrola aktualizací softwaru

> **Poznámka**: Pokud VS Code není nainstalováno, můžete jej nainstalovat pomocí AMD Ryzen™ AI Developer Center.

<!-- @require:software-update -->
<!-- @device:end -->

## Instalace softwarových předpokladů

Tento playbook používá předpřipravený obraz kontejneru, který zahrnuje vLLM, podporu ROCm a pomocné skripty potřebné ke spuštění serveru. Není potřeba ručně instalovat PyTorch, vLLM ani lokální skripty playbooku.

Neexistuje žádný krok instalace vLLM na hostitelském systému. Spusťte vLLM pomocí:

```bash
vllm-launch
```

Spouštěč (launcher) spustí kontejner, zacílí na integrované GPU a zpřístupní lokální server vLLM kompatibilní s OpenAI. Alternativně klikněte na ikonu vLLM na hlavním panelu.

## Rychlý start

### 1. Ověřte, že server vLLM běží

Spuštění `vllm-launch` může trvat pár minut, než se vše inicializuje. Jakmile se server spustí, je dostupný na adrese `http://localhost:8001`. Terminál se spouštěcím příkazem nechte otevřený, protože server běží na popředí, a pro zbývající kroky otevřete samostatný terminál. Níže uvedené příklady používají `Qwen/Qwen3-1.7B`; pokud je váš spouštěč nakonfigurován pro jiný model, v požadavcích nahraďte odpovídající ID modelu.

### 2. Odešlete výzvu (prompt)

Pomocí přiloženého skriptu `vllm-prompt` odešlete požadavek na lokální server vLLM kompatibilní s OpenAI:

```bash
vllm-prompt "Tell me a story"
```

### 3. Konverzace s modelem pomocí Python API OpenAI

Jelikož vLLM poskytuje API kompatibilní s OpenAI, můžete k interakci s ním použít Python balíček `openai`.

Nejprve vytvořte virtuální prostředí Pythonu:

<!-- @os:linux -->
<!-- @device:halo_box -->
```bash
sudo apt install -y python3-venv
python3 -m venv vllm-env
source vllm-env/bin/activate
```
<!-- @device:end -->

Nainstalujte balíček OpenAI
```bash
pip install openai
```

Vytvořte klienta `OpenAI` směřujícího na lokální server vLLM namísto serverů OpenAI. Klient vyžaduje `api_key`, ale vLLM jej neověřuje, takže funguje libovolný řetězec:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="EMPTY",
)
```

Poté odešlete požadavek na dokončení konverzace (chat completion). Používá se stejný formát zpráv jako u API OpenAI — seznam zpráv s rolemi jako `"user"` a `"assistant"`. Nastavení `stream=True` znamená, že odpověď bude přicházet postupně místo najednou:

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-1.7B",
    messages=[
        {"role": "user", "content": "Tell me a short story"},
    ],
    max_tokens=2048,  # Maximum number of tokens the model will generate in its response
    stream=True,
)
```

Nakonec projděte streamované úseky (chunky) a vypište každou část textu, jakmile dorazí:

```python
for chunk in response:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

Přiložený skript [chat_with_model.py](assets/chat_with_model.py) obsahuje celý příklad a lze jej stáhnout.


## Řešení problémů

### Odmítnuté připojení (connection refused)

Ujistěte se, že server běží:
```bash
curl http://localhost:8001/health
```

## Shrnutí

V tomto playbooku jste se naučili, jak:

- Spustit kontejnerizované vLLM s podporou ROCm na integrovaném GPU
- Spustit server vLLM s koncovými body API kompatibilního s OpenAI na portu 8001
- Odesílat výzvy pomocí `vllm-prompt`
- Volat API serveru vLLM pomocí streamovaných i nestreamovaných požadavků
- Řešit běžné problémy se spuštěním serveru, pamětí a připojením klienta

Nyní máte k dispozici kontejnerizované nasazení vLLM pro obsluhu velkých jazykových modelů s optimalizovaným výkonem na integrovaném GPU.

## Další kroky

- **Vyzkoušejte různé modely** — Vyměňte model v konfiguraci `vllm-launch` a experimentujte s různými LLM a porovnávejte výkon.
- **Vytvořte aplikaci** — Použijte API kompatibilní s OpenAI k integraci vLLM do Python aplikace, chatbota nebo automatizovaného pracovního postupu.
- **Doladění a nasazení** — Doladěte model pomocí LoRA nebo QLoRA a poté jej nasaďte pomocí vLLM pro optimalizovanou inferenci.

## Další zdroje

- **[Oficiální dokumentace vLLM](https://docs.vllm.ai/)** — Podrobné návody a reference API
- **[Repozitář vLLM na GitHubu](https://github.com/vllm-project/vllm)** — Zdrojový kód, problémy a diskuze komunity