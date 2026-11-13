from policy_assistant.core.config import get_settings

settings = get_settings()

assert settings.gemini_api_key.get_secret_value()
assert settings.gemini_model == "gemini-3.5-flash-lite"

print("Configuration loaded successfully.")
print("Gemini API key detected:", bool(settings.gemini_api_key.get_secret_value()))
print("Gemini model:", settings.gemini_model)