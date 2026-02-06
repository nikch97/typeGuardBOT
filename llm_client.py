from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 1) Use StarCoder2-3B instead of codegen
MODEL_NAME = "bigcode/starcoder2-3b"

print(f"[LLM] Loading model '{MODEL_NAME}'... this may take a bit.")

# 2) Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Some StarCoder-style models don’t have a pad token set by default,
# so we safely set pad_token = eos_token if needed.
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token

# Decide device & dtype (float16 on GPU, float32 on CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=dtype,
)
model.to(device)
model.eval()


def generate_patch(prompt: str, max_new_tokens: int = 256) -> str:
    """Call the local model with a prompt and return generated text."""
    # 3) Move tensors to the same device as the model
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.2,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )

    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Often the output is 'prompt + completion'; try to strip the prompt part
    if full_text.startswith(prompt):
        return full_text[len(prompt):].strip()
    return full_text.strip()
