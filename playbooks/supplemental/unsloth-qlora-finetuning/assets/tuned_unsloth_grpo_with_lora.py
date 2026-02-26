#!/usr/bin/env python
"""
Train your own R1 reasoning model with Unsloth GRPO
Based on: https://rocm.docs.amd.com/projects/ai-developer-hub/en/latest/notebooks/fine_tune/unsloth_Llama3_1_8B_GRPO.html

This script demonstrates how to fine-tune the Llama-3.1 8B large language model (LLM) 
on AMD ROCm GPUs by leveraging Unsloth for Group Relative Policy Optimization (GRPO).
"""

import os
import re
import time
import subprocess
from unsloth import FastLanguageModel

import torch
from datasets import load_dataset
from trl import GRPOConfig, GRPOTrainer

# CRITICAL: Import Unsloth FIRST before any transformers/peft/trl imports
# This ensures all optimizations are applied correctly

# UnslothZoo is optional - not all versions have it
try:
    from unsloth_zoo import UnslothZoo
except (ImportError, AttributeError):
    UnslothZoo = None

# vLLM is optional - we'll use standard PyTorch generation if not available
try:
    from vllm import SamplingParams
    HAS_VLLM = True
except ImportError:
    HAS_VLLM = False
    SamplingParams = None

# ============================================================================
# Set the parameters
# ============================================================================

max_seq_length = 512  # Reduced sequence length for faster training/dev
dtype = None  # None for auto detection. Float16 for Tesla T4, V100, Bfloat16 for Ampere+
load_in_4bit = False # Use 4bit quantization to reduce memory usage. Can be False.
lora_rank = 16  # LoRA rank parameter

# ============================================================================
# Data preparation
# ============================================================================

SYSTEM_PROMPT = """
Respond in the following format:
<reasoning>
...
</reasoning>
<answer>
...
</answer>
"""

XML_COT_FORMAT = """\
<reasoning>
{reasoning}
</reasoning>
<answer>
{answer}
</answer>
"""

def extract_xml_answer(text: str) -> str:
    """Extract answer from XML tags."""
    answer = text.split("<answer>")[-1]
    answer = answer.split("</answer>")[0]
    return answer.strip()

def extract_hash_answer(text: str) -> str | None:
    """Extract answer from GSM8K format (#### answer)."""
    if "####" not in text:
        return None
    return text.split("####")[1].strip()

# Load and prepare GSM8K dataset
def get_gsm8k_questions(split="train"):
    """Load and format GSM8K dataset for GRPO training."""
    data = load_dataset('openai/gsm8k', 'main')[split].select(range(1000)) # Temporarily 1000 samples
    data = data.map(lambda x: {
        'prompt': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': x['question']}
        ],
        'answer': extract_hash_answer(x['answer'])
    })
    return data

# Load dataset (use subset for faster iteration during development)
# 
dataset = get_gsm8k_questions(split="train")  # Use first 1000 examples

# ============================================================================
# Load model with Unsloth
# ============================================================================

# Load the model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="/models/Llama-3.1-8B-Instruct",  # Unsloth pre-quantized model
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,  # Use 4bit quantization to reduce memory usage
    fast_inference=False,  # Enable vLLM fast inference
    max_lora_rank=lora_rank,
    gpu_memory_utilization=0.6,  # Reduce if out of memory
   # enforce_eager=True,  # Use eager mode
   # compilation_config={'cudagraph_mode': 'NONE'},  # Disable cudagraph mode
)

# Add LoRA adapters for training (required for quantized models)
# Unsloth's get_peft_model is optimized for training
model = FastLanguageModel.get_peft_model(
    model,
    r=lora_rank,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=3407,
    use_rslora=False,
    loftq_config=None,
)

# Enable gradient checkpointing and other optimizations
FastLanguageModel.for_training(model)  # Enable gradient checkpointing, etc.

# ============================================================================
# Reward functions
# ============================================================================

def correctness_reward_func(prompts, completions, answer, **kwargs) -> list[float]:
    """Reward function that checks if the completion is correct."""
    responses = [completion[0]['content'] for completion in completions]
    q = prompts[0][-1]['content']
    extracted_responses = [extract_xml_answer(r) for r in responses]
    print('-'*20, f"Question:\n{q}", f"\nAnswer:\n{answer[0]}", f"\nResponse:\n{responses[0]}", f"\nExtracted:\n{extracted_responses[0]}")
    return [2.0 if r == a else 0.0 for r, a in zip(extracted_responses, answer)]

def int_reward_func(completions, **kwargs) -> list[float]:
    """Reward function that checks if the response is an integer."""
    responses = [completion[0]['content'] for completion in completions]
    extracted_responses = [extract_xml_answer(r) for r in responses]
    return [0.5 if r.isdigit() else 0.0 for r in extracted_responses]

def strict_format_reward_func(completions, **kwargs) -> list[float]:
    """Reward function that checks if the completion has a specific format."""
    pattern = r"^<reasoning>\n.*?\n</reasoning>\n<answer>\n.*?\n</answer>\n$"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r) for r in responses]
    return [0.5 if match else 0.0 for match in matches]

def soft_format_reward_func(completions, **kwargs) -> list[float]:
    """Reward function that checks if the completion has a specific format."""
    pattern = r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>"
    responses = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, r) for r in responses]
    return [0.5 if match else 0.0 for match in matches]

def count_xml(text) -> float:
    """Count XML tags and reward proper formatting."""
    count = 0.0
    if text.count("<reasoning>\n") == 1:
        count += 0.125
    if text.count("\n</reasoning>\n") == 1:
        count += 0.125
    if text.count("\n<answer>\n") == 1:
        count += 0.125
        count -= len(text.split("\n</answer>\n")[-1])*0.001
    if text.count("\n</answer>") == 1:
        count += 0.125
        count -= (len(text.split("\n</answer>")[-1]) - 1)*0.001
    return count

def xmlcount_reward_func(completions, **kwargs) -> list[float]:
    """Reward function based on XML tag counting."""
    contents = [completion[0]["content"] for completion in completions]
    return [count_xml(c) for c in contents]

# ============================================================================
# Train the model
# ============================================================================

max_prompt_length = 256

# Set up GRPO training configuration
training_args = GRPOConfig(
    learning_rate=5e-6,
    adam_beta1=0.9,
    adam_beta2=0.99,
    weight_decay=0.1,
    warmup_ratio=0.1,
    lr_scheduler_type="cosine",
    optim="paged_adamw_8bit",
    logging_steps=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,  # Increase to 4 for smoother training
    num_generations=2,  # Decrease if out of memory
    max_prompt_length=max_prompt_length,
    max_completion_length=max_seq_length - max_prompt_length,
    # num_train_epochs=1,  # Set to 1 for a full training run
    max_steps=250,
    save_steps=250,
    max_grad_norm=0.1,
    report_to="none",  # Can use Weights & Biases
    output_dir="outputs",
)

# Create the GRPO trainer
trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[
        xmlcount_reward_func,
        soft_format_reward_func,
        strict_format_reward_func,
        int_reward_func,
        correctness_reward_func,
    ],
    args=training_args,
    train_dataset=dataset,
)

# ============================================================================
# GPU Monitoring Helper
# ============================================================================

def print_gpu_status():
    """Print current GPU status"""
    if torch.cuda.is_available():
        print(f"\n{'='*50}")
        print(f"GPU Status:")
        print(f"  Device: {torch.cuda.get_device_name(0)}")
        print(f"  Memory Allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
        print(f"  Memory Reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
        print(f"  Max Memory Allocated: {torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB")
        
        # Try to get rocm-smi output if available
        try:
            # Try rocm-smi first (ROCm 6.4 and earlier)
            result = subprocess.run(['rocm-smi', '--showuse', '--showmemuse'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print(f"\nROCm-SMI Output:")
                print(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            try:
                # Try amd-smi (ROCm 6.5+)
                result = subprocess.run(['amd-smi'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    print(f"\nAMD-SMI Output:")
                    print(result.stdout)
            except:
                pass
        print(f"{'='*50}\n")

# Train the model
print("Starting GRPO training...")
print("You might have to wait for 150 to 200 steps to see any action.")
print("You probably won't get any reward for the first 100 steps. Please be patient!")

# Print initial GPU status
print_gpu_status()

trainer.train()

# Print final GPU status
print_gpu_status()

# ============================================================================
# Inference
# ============================================================================

print("\n" + "="*50)
print("Testing the model without GRPO training:")
print("="*50)

# Test without GRPO training
text = tokenizer.apply_chat_template([
    {"role": "user", "content": "Calculate pi."},
], tokenize=False, add_generation_prompt=True)

if HAS_VLLM:
    # Use vLLM fast generation if available
    sampling_params = SamplingParams(
        temperature=0.8,
        top_p=0.95,
        max_tokens=1024,
    )
    output = model.fast_generate(
        [text],
        sampling_params=sampling_params,
        lora_request=None,
    )[0].outputs[0].text
else:
    # Use standard PyTorch generation
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.8,
            top_p=0.95,
            do_sample=True,
        )
    output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the generated part (after the prompt)
    output = output[len(text):].strip()

print("Output without GRPO:", output)

# Save the LoRA adapter
print("\nSaving LoRA adapter...")
model.save_lora("grpo_saved_lora")

# Test with GRPO training
print("\n" + "="*50)
print("Testing the model with GRPO training:")
print("="*50)

text = tokenizer.apply_chat_template([
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Calculate pi."},
], tokenize=False, add_generation_prompt=True)

if HAS_VLLM:
    # Use vLLM fast generation if available
    output = model.fast_generate(
        text,
        sampling_params=sampling_params,
        lora_request=model.load_lora("grpo_saved_lora"),
    )[0].outputs[0].text
else:
    # Use standard PyTorch generation with LoRA
    # Note: You may need to load the LoRA weights into the model first
    # For now, we'll generate without LoRA (you can add LoRA loading if needed)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1024,
            temperature=0.8,
            top_p=0.95,
            do_sample=True,
        )
    output = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the generated part (after the prompt)
    output = output[len(text):].strip()

print("Output with GRPO:", output)

# ============================================================================
# Saving the model (for use with vLLM or standard inference)
# ============================================================================

# Uncomment the following lines to save the model in different formats:

# Merge to 16bit
# model.save_pretrained_merged("model", tokenizer, save_method="merged_16bit")
# model.push_to_hub_merged("hf/model", tokenizer, save_method="merged_16bit", token="")

# Merge to 4bit
# model.save_pretrained_merged("model", tokenizer, save_method="merged_4bit")
# model.push_to_hub_merged("hf/model", tokenizer, save_method="merged_4bit", token="")

# Just LoRA adapters
# model.save_pretrained_merged("model", tokenizer, save_method="lora")
# model.push_to_hub_merged("hf/model", tokenizer, save_method="lora", token="")

print("\n" + "="*50)
print("Training complete!")
print("="*50)
print("\nIf you have any questions about Unsloth, need help, or want to keep updated:")
print("- Discord channel: https://discord.gg/unsloth")
print("- GitHub: https://github.com/unslothai/unsloth")
print("- Documentation: https://unsloth.ai")
