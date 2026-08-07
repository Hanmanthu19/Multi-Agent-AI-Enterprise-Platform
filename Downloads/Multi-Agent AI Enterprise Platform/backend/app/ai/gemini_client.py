from google import genai
from app.config import settings

print("=" * 60)
print("Loaded Gemini Key:", settings.GEMINI_API_KEY)
print("=" * 60)

client = genai.Client(api_key=settings.GEMINI_API_KEY)