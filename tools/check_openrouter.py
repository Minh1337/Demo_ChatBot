"""Minimal OpenRouter check; prints no key, messages or account information."""
from pathlib import Path
import re
import sys

from dotenv import dotenv_values
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rag.generation import GenerationError, ensure_free_configuration, free_routing


def main():
    settings = dotenv_values(Path(__file__).resolve().parents[1] / '.env')
    key = (settings.get('LLM_API_KEY') or '').strip()
    model = (settings.get('LLM_MODEL') or '').strip()
    if not key or not model:
        print('CONFIG_MISSING: set LLM_API_KEY and LLM_MODEL in .env')
        return 1
    try:
        model, base_url = ensure_free_configuration(model, settings.get('LLM_BASE_URL') or 'https://openrouter.ai/api/v1')
        with OpenAI(api_key=key, base_url=base_url, timeout=35, max_retries=0) as client:
            result = client.chat.completions.create(model=model, messages=[{'role':'user', 'content':'Reply with OK.'}], max_tokens=512, extra_body=free_routing())
        print('HTTP: 200')
        print('MODEL:', result.model)
        has_text = bool(result.choices and result.choices[0].message.content and result.choices[0].message.content.strip())
        print('TEXT_RESPONSE:', has_text)
        if result.choices:
            print('FINISH_REASON:', result.choices[0].finish_reason)
        return 0 if has_text else 1
    except GenerationError as exc:
        print('CONFIG_BLOCKED:', exc.code)
        print('DETAIL:', str(exc))
        return 1
    except Exception as exc:
        print('ERROR_TYPE:', type(exc).__name__)
        print('HTTP:', getattr(exc, 'status_code', None))
        detail = str(exc).replace(key, '[REDACTED]')
        detail = re.sub(r'sk-[A-Za-z0-9_-]+', '[REDACTED]', detail)
        print('DETAIL:', detail[:600])
        cause = exc.__cause__
        if cause:
            print('CAUSE:', re.sub(r'sk-[A-Za-z0-9_-]+', '[REDACTED]', str(cause).replace(key, '[REDACTED]'))[:300])
        return 1


if __name__ == '__main__':
    sys.exit(main())
