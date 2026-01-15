## Overview

Large language models (LLMs) are neural networks trained on vast amounts of text data to understand and generate human language. Running these models locally gives you full control, privacy, and the ability to experiment without API rate limits or costs. Your STX Halo™ GPU with ROCm acceleration makes running even 20B parameter models practical on consumer hardware.

This tutorial teaches you how to load and run LLMs using PyTorch with ROCm acceleration, with document summarization as a practical example.

## What You'll Learn

- How to set up PyTorch with ROCm for LLM inference
- Loading and running large language models locally
- Understanding model parameters and memory requirements
- Optimizing inference with efficient attention
- Building a practical document summarization pipeline

## Prerequisites

Before starting, ensure you have:

- **Python 3.10 or newer**
- **16GB+ GPU memory** (24GB+ recommended for 20B models)
- **50GB+ free disk space** for model storage
- **Basic Python knowledge**

## Setting Up Your Environment

<!-- @os:linux -->
### Create a Virtual Environment

```bash
python3 -m venv llm-env
source llm-env/bin/activate
```

### Install PyTorch with ROCm Support

Install PyTorch 2.8+ with ROCm 7.2 support:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm7.2
```

### Install Additional Dependencies

```bash
pip install transformers accelerate sentencepiece protobuf
```

> **Note**: Your STX Halo™ GPU uses AMD ROCm 7.2. The PyTorch 2.8 ROCm build provides native GPU acceleration for tensor operations and model inference.
<!-- @os:end -->

## Example Scripts

This playbook includes ready-to-use Python scripts in the `assets/` folder. You can run them directly or use them as templates for your own projects.

| Script | Description | Example Commands |
|--------|-------------|------------------|
| **run_llm.py** | Basic LLM loading and text generation | `python assets/run_llm.py` |
| **summarizer.py** | Document summarizer with model selection | `python assets/summarizer.py`<br>`python assets/summarizer.py --model gptoss` |

The `summarizer.py` script supports `--model {mistral,gptoss}` for flexibility.

## Understanding LLM Fundamentals

Before running your first model, it's helpful to understand what's happening under the hood.

### Model Architecture Components

Modern LLMs consist of several key components that work together:

| Component | Role |
|-----------|------|
| **Tokenizer** | Converts text into numeric tokens the model understands |
| **Embedding Layer** | Maps tokens to high-dimensional vector representations |
| **Transformer Blocks** | Process sequences using self-attention mechanisms |
| **Language Modeling Head** | Predicts the next token given previous context |

When you run inference, text flows through these components: text → tokens → embeddings → transformer layers → output predictions.

### Model Size and Memory

Model size directly impacts memory requirements and performance:

| Model Size | Parameters | Memory (FP16) | Best For |
|------------|-----------|---------------|----------|
| **7B** | 7 billion | ~14GB | Fast inference, most tasks |
| **13B** | 13 billion | ~26GB | Better quality, complex tasks |
| **20B** | 20 billion | ~40GB | High quality, specialized tasks |

Your STX Halo™ can efficiently run models up to 20B parameters with proper optimization.

## Loading Your First LLM

Let's start with Mistral 7B, an excellent model for understanding the basics.

> **Using the Example Script**: A complete version of this code is available in `assets/run_llm.py`. You can run it directly with `python assets/run_llm.py` or follow along to understand how it works.

Here's the core code (`assets/run_llm.py`):

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Verify ROCm is available
print(f"ROCm available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Load model and tokenizer
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
print(f"Loading {model_name}...")

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

print("Model loaded successfully!")
```

Run the script:

```bash
python assets/run_llm.py
```

You should see output confirming ROCm availability and the model loading. The first run will download the model (~14GB), which takes a few minutes.

> **Success Indicator**: You'll see "✓ Model loaded successfully!" when everything is working correctly.

## Generating Your First Text

The `assets/run_llm.py` script includes text generation. Here's how the generation code works:

```python
# Create a simple prompt
prompt = "Explain what a large language model is in simple terms:"

# Tokenize input
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

# Generate response
print("\nGenerating response...")
outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    temperature=0.7,
    do_sample=True,
    top_p=0.9
)

# Decode and print
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("\n" + "="*50)
print(response)
print("="*50)
```

Run it again. You should see the model generate a coherent explanation about LLMs.

### Understanding Generation Parameters

| Parameter | What It Controls | Typical Values |
|-----------|------------------|----------------|
| `max_new_tokens` | Maximum length of generated text | 50–2000 |
| `temperature` | Randomness (higher = more creative) | 0.1–1.0 |
| `top_p` | Nucleus sampling threshold | 0.9–0.95 |
| `do_sample` | Enable sampling vs greedy decoding | `True` for variety |

**Temperature** is like a creativity dial: 0.1 for focused, deterministic output; 0.7–0.9 for balanced creativity; 1.0+ for maximum randomness.

## Building a Document Summarizer

Now let's apply what we've learned to a practical task: document summarization.

> **Using the Example Script**: A complete, production-ready summarizer is available in `assets/summarizer.py`. Run it with `python assets/summarizer.py` or import it in your own code.

### The Summarizer Class

Here's the core implementation (from `assets/summarizer.py`):

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class DocumentSummarizer:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.3"):
        print(f"Loading {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("Model ready!")
    
    def summarize(self, text, max_length=200):
        """Summarize the given text."""
        prompt = f"""[INST] Summarize the following text concisely, capturing the main points:

{text}

Provide a clear, concise summary. [/INST]"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=0.3,  # Lower for more focused summaries
            do_sample=True,
            top_p=0.9
        )
        
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract just the summary (after [/INST])
        summary = full_response.split("[/INST]")[-1].strip()
        return summary

# Example usage
if __name__ == "__main__":
    summarizer = DocumentSummarizer()
    
    # Sample document
    document = """
    Large language models (LLMs) are neural networks with billions of parameters 
    trained on massive text datasets. They learn to predict the next word in a 
    sequence, developing an understanding of language patterns, facts, and reasoning. 
    Modern LLMs like GPT-4, Claude, and Llama can perform diverse tasks including 
    translation, question answering, code generation, and creative writing. The key 
    breakthrough was the transformer architecture, which uses attention mechanisms 
    to process sequences in parallel. Training these models requires enormous 
    computational resources, but once trained, they can run on consumer hardware 
    for inference tasks.
    """
    
    print("Original document:")
    print(document)
    print("\n" + "="*70 + "\n")
    
    summary = summarizer.summarize(document)
    print("Summary:")
    print(summary)
```

Run the summarizer:

```bash
python assets/summarizer.py
```

You'll see the original text and a concise summary generated by the model.

> **Tip**: The `DocumentSummarizer` class can be imported in your own projects. See `assets/README.md` for examples.

### How It Works

The summarization pipeline:

1. **Prompt Construction**: We format the input with instructions and the document text
2. **Tokenization**: Convert the prompt to token IDs
3. **Model Inference**: The transformer processes tokens and generates output
4. **Decoding**: Convert output token IDs back to human-readable text

The `[INST]` tags are instruction markers that Mistral models are trained to recognize, signaling this is a user request.

## Scaling Up: Using GPTOSS 20B

For higher quality summaries, let's try the larger GPTOSS 20B model. It provides better reasoning and more nuanced understanding.

> **Using the Example Script**: Run `python assets/summarizer.py --model gptoss` to use the GPTOSS-20B model. Requires ~40GB GPU memory.

You can also use GPTOSS-20B in your code:

```python
summarizer = DocumentSummarizer(model="gptoss")
```

The 20B model will take longer to load but produces noticeably better results for complex documents.

## Processing Multiple Documents

The `DocumentSummarizer` class includes a `summarize_batch()` method for processing multiple documents:

```python
from summarizer import DocumentSummarizer

summarizer = DocumentSummarizer(model="mistral")

documents = [
    "Your first document text here...",
    "Your second document text here...",
    "Your third document text here..."
]

summaries = summarizer.summarize_batch(documents)

for i, summary in enumerate(summaries, 1):
    print(f"\nDocument {i} Summary:")
    print(summary)
    print("-" * 70)
```

This pattern is useful for processing research papers, news articles, or large document collections.

## Performance Optimization

### Enable Flash Attention

For faster inference, install Flash Attention:

```bash
pip install flash-attn --no-build-isolation
```

Then add to your model loading:

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
    attn_implementation="flash_attention_2"  # Much faster!
)
```

### Batch Processing

Process multiple inputs at once for better GPU utilization:

```python
# Tokenize multiple prompts
inputs = tokenizer(
    [prompt1, prompt2, prompt3],
    return_tensors="pt",
    padding=True
).to("cuda")

outputs = model.generate(**inputs, max_new_tokens=200)
```

### Key Performance Metrics

| Optimization | Memory Impact | Speed Impact | Quality Impact |
|--------------|---------------|--------------|----------------|
| FP16 precision | -50% (vs FP32) | +2× | Negligible |
| Flash Attention | None | +2-3× | None |
| Batching | Slight increase | +1.5-2× | None |

## Understanding Model Behavior

### Temperature Effects

Try running the same prompt with different temperatures:

```python
for temp in [0.1, 0.5, 0.9]:
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=temp,
        do_sample=True
    )
    print(f"\nTemperature {temp}:")
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

**Temperature 0.1**: Focused, deterministic, often repetitive  
**Temperature 0.5**: Balanced, coherent, good for summaries  
**Temperature 0.9**: Creative, varied, good for brainstorming

### Prompt Engineering

The way you structure prompts significantly impacts output quality:

**Generic prompt**:
```
Summarize this text: [document]
```

**Better prompt**:
```
[INST] Summarize the following text concisely, capturing the main points:

[document]

Provide a clear, concise summary. [/INST]
```

**Best prompt** (with examples):
```
[INST] Summarize the following text. Focus on key findings and conclusions:

[document]

Summary: [/INST]
```

Experiment with prompt variations to find what works best for your use case.

## Comparing Models

Here's how different models compare for summarization:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **Mistral 7B** | 7B | Fast | Good | General summaries, high throughput |
| **Mistral 7B Instruct** | 7B | Fast | Very Good | Instruction following, structured tasks |
| **GPTOSS 20B** | 20B | Moderate | Excellent | Complex documents, nuanced understanding |

Start with Mistral 7B Instruct for learning, then scale to GPTOSS 20B when you need higher quality.

## Real-World Applications

Beyond basic summarization, you can adapt this pipeline for:

- **Research Paper Analysis**: Extract key findings from academic papers
- **News Aggregation**: Summarize multiple news articles on the same topic
- **Meeting Notes**: Condense long transcripts into action items
- **Legal Document Review**: Extract relevant clauses and obligations
- **Code Documentation**: Generate summaries of code repositories

The pattern is always the same: craft a good prompt, feed it to the model, and process the output.

## Next Steps

Now that you understand LLM inference with PyTorch and ROCm, explore further:

- **Fine-tuning**: Adapt models to your specific domain or style (see the [PyTorch Fine-tuning Playbook](../pytorch-finetuning/))
- **RAG Systems**: Combine LLMs with document retrieval for question answering
- **Multi-modal Models**: Explore models that process images and text together
- **Model Comparison**: Try different models like Llama 3, Phi-3, or Qwen
- **Production Deployment**: Use vLLM or Text Generation Inference for serving models at scale

### Resources

- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers)
- [PyTorch ROCm Documentation](https://pytorch.org/get-started/locally/)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [GPTOSS Model Card](https://huggingface.co/Writer/GPTOSS-20B)

Your STX Halo™ GPU gives you the power to run sophisticated language models locally. Experiment with different models, prompts, and parameters to discover what works best for your applications.
