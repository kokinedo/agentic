"""Credential store and login/logout flows."""

from __future__ import annotations

import json
import os
import webbrowser
from pathlib import Path

CREDENTIALS_PATH = Path.home() / ".config" / "agentic" / "credentials.json"

ENV_VARS = {
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

CONSOLE_URLS = {
    "claude": "https://console.anthropic.com/settings/keys",
    "openai": "https://platform.openai.com/api-keys",
    "gemini": "https://aistudio.google.com/apikey",
}

PROVIDER_NAMES = {
    "claude": "Anthropic (Claude)",
    "openai": "OpenAI",
    "gemini": "Google (Gemini)",
}


def load_credentials() -> dict:
    """Load credentials from disk."""
    if CREDENTIALS_PATH.exists():
        return json.loads(CREDENTIALS_PATH.read_text())
    return {"default_provider": "claude", "providers": {}}


def save_credentials(creds: dict) -> None:
    """Save credentials to disk."""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.write_text(json.dumps(creds, indent=2))
    CREDENTIALS_PATH.chmod(0o600)


def get_api_key(provider: str) -> str | None:
    """Get API key for a provider. Checks credentials file first, then env var."""
    creds = load_credentials()
    stored = creds.get("providers", {}).get(provider, {}).get("api_key")
    if stored:
        return stored
    env_var = ENV_VARS.get(provider)
    if env_var:
        return os.environ.get(env_var)
    return None


def get_default_provider() -> str:
    """Get the default provider from credentials."""
    creds = load_credentials()
    return creds.get("default_provider", "claude")


def login(provider: str) -> None:
    """Interactive login flow for a provider."""
    name = PROVIDER_NAMES.get(provider, provider)
    url = CONSOLE_URLS.get(provider)

    print(f"\n  Logging in to {name}...\n")
    if url:
        print(f"  Opening {url}")
        try:
            webbrowser.open(url)
        except Exception:
            print(f"  Could not open browser. Visit: {url}")
    print()

    api_key = input("  Paste your API key: ").strip()
    if not api_key:
        print("  No key provided. Aborting.")
        return

    creds = load_credentials()
    if "providers" not in creds:
        creds["providers"] = {}
    creds["providers"][provider] = {"api_key": api_key}
    creds["default_provider"] = provider
    save_credentials(creds)

    print(f"\n  Logged in to {name} successfully.")
    print(f"  Credentials saved to {CREDENTIALS_PATH}\n")


def logout(provider: str) -> None:
    """Remove stored credentials for a provider."""
    creds = load_credentials()
    if provider in creds.get("providers", {}):
        del creds["providers"][provider]
        save_credentials(creds)
        name = PROVIDER_NAMES.get(provider, provider)
        print(f"\n  Logged out of {name}.\n")
    else:
        print(f"\n  No stored credentials for {provider}.\n")
