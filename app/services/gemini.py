import os
from dotenv import load_dotenv
import google.generativeai as genai
import openai
import itertools

# Load environment variables
load_dotenv()

# ====================== API KEYS ======================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not any([GEMINI_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY]):
    raise ValueError("No API keys found in .env (GEMINI_API_KEY, GROQ_API_KEY, or OPENROUTER_API_KEY)")

# ====================== GEMINI SETUP (unchanged logic) ======================
gemini_model_name = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

    # List available models and pick the best free one
    available_models = list(genai.list_models())
    available_model_names = [m.name.split('/')[-1] for m in available_models]

    DEFAULT_TEXT_MODELS = [
        "gemini-2.5-flash-lite",   # fastest
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    gemini_model_name = next(
        (m for m in DEFAULT_TEXT_MODELS if m in available_model_names),
        None
    )
    if not gemini_model_name:
        raise RuntimeError(f"No Gemini model found. Available: {available_model_names}")

# ====================== GROQ SETUP (OpenAI-compatible, free tier) ======================
groq_client = None
groq_model = None
if GROQ_API_KEY:
    groq_client = openai.OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    # Best free/high-performance Groq models in 2026 (fast + generous limits)
    groq_model = "llama-3.3-70b-versatile"   # excellent balance of speed/quality

# ====================== OPENROUTER SETUP (free tier, many open models) ======================
openrouter_client = None
openrouter_model = None
if OPENROUTER_API_KEY:
    openrouter_client = openai.OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        # extra_headers optional but recommended for OpenRouter analytics
        # extra_headers={"HTTP-Referer": "https://your-app.com", "X-Title": "Your App"}
    )
    # Strong free-tier model on OpenRouter (different from Groq/Gemini)
    openrouter_model = "deepseek/deepseek-r1"   # excellent reasoning + free tier

# ====================== BUILD ROTATIONAL LIST ======================
active_providers = []

if gemini_model_name:
    active_providers.append({
        "provider": "gemini",
        "model": gemini_model_name,
    })

if groq_model:
    active_providers.append({
        "provider": "groq",
        "model": groq_model,
    })

if openrouter_model:
    active_providers.append({
        "provider": "openrouter",
        "model": openrouter_model,
    })

if not active_providers:
    raise RuntimeError("No providers could be initialized")

print("✅ Rotational LLM system ready!")
print("   Active providers (round-robin):")
for i, p in enumerate(active_providers, 1):
    print(f"   {i}. {p['provider'].upper()} → {p['model']}")

# Create infinite cycle for round-robin rotation
provider_cycle = itertools.cycle(active_providers)


# ====================== UNIFIED CALL FUNCTION ======================
def call_gemini(prompt: str, temperature: float = 0.2) -> str:
    """
    Calls the next LLM in the rotation (Gemini → Groq → OpenRouter → repeat).
    Automatically distributes load and respects free-tier rate limits better.
    """
    config = next(provider_cycle)
    provider = config["provider"]
    model = config["model"]

    print(f"🔄 Using {provider.upper()} | Model: {model}")  # remove in production if you want

    try:
        if provider == "gemini":
            model_obj = genai.GenerativeModel(model)
            response = model_obj.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            return response.text.strip()

        elif provider == "groq":
            response = groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=2048,          # safe default
            )
            return response.choices[0].message.content.strip()

        elif provider == "openrouter":
            response = openrouter_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=2048,
            )
            return response.choices[0].message.content.strip()

    except Exception as e:
        # Optional: graceful fallback to next provider on rate-limit/error
        print(f"⚠️  {provider} failed: {e}. Trying next provider...")
        return call_gemini(prompt, temperature)  # recursive retry with next in cycle

    raise RuntimeError("Unexpected provider")


# ====================== EXAMPLE USAGE ======================
if __name__ == "__main__":
    prompt = "Write a single strong resume bullet for Python backend experience."
    
    for _ in range(6):   # demo rotation
        result = call_gemini(prompt, temperature=0.3)
        print(f"\n{'='*60}\n{result}\n{'='*60}")