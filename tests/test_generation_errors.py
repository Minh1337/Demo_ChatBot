"""Error reporting checks with mocked provider calls, never real credentials/network."""
import os
import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from app import ChatRequest, chat
from rag.generation import GenerationError, describe_failure, draft


class ProviderFailure(Exception):
    def __init__(self, status):
        self.status_code = status
        super().__init__('private-provider-detail unit-test-only')


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'LLM_API_KEY':'unit-test-only', 'LLM_MODEL':'openrouter/free', 'LLM_BASE_URL':'https://openrouter.ai/api/v1'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_http_codes_remain_distinct_and_safe(self):
        expected = {401:'authentication', 402:'credits', 403:'permission', 404:'model_unavailable', 429:'rate_limit', 400:'invalid_request', 422:'invalid_request', 503:'provider_unavailable'}
        for status, code in expected.items():
            with self.subTest(status=status):
                failure = describe_failure(ProviderFailure(status))
                self.assertEqual(failure.code, code)
                self.assertNotIn('private-provider-detail', str(failure))

    def test_missing_config(self):
        with patch.dict(os.environ, {'LLM_API_KEY':''}), self.assertRaises(GenerationError) as caught:
            draft('Hello', [])
        self.assertEqual(caught.exception.code, 'config_missing')

    def test_logs_never_include_provider_detail_or_key(self):
        with patch('openai.OpenAI') as sdk:
            sdk.return_value.chat.completions.create.side_effect = ProviderFailure(429)
            with self.assertLogs('rag.generation', level='WARNING') as logs, self.assertRaises(GenerationError):
                draft('Hello', [])
        self.assertNotIn('unit-test-only', '\n'.join(logs.output))
        self.assertNotIn('private-provider-detail', '\n'.join(logs.output))

    def test_empty_and_truncated_outputs(self):
        for reason, code in [('stop','empty_response'), ('length','output_limit')]:
            with self.subTest(reason=reason), patch('openai.OpenAI') as sdk:
                sdk.return_value.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=''), finish_reason=reason)])
                with self.assertRaises(GenerationError) as caught:
                    draft('Hello', [])
                self.assertEqual(caught.exception.code, code)

    def test_success_retains_multi_turn_context(self):
        history = [{'role':'user', 'content':'Learn Python'}, {'role':'assistant', 'content':'Sure'}]
        with patch('openai.OpenAI') as sdk:
            sdk.return_value.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='  Answer  '))])
            self.assertEqual(draft('Next', [], history), 'Answer')
            messages = sdk.return_value.chat.completions.create.call_args.kwargs['messages']
            self.assertEqual(messages[1:3], history)
            self.assertEqual(messages[-1]['content'], 'Next')
            self.assertEqual(sdk.return_value.chat.completions.create.call_args.kwargs['extra_body'], {'provider': {'max_price': {'prompt':0, 'completion':0, 'request':0, 'image':0}}})

    def test_paid_model_and_alternate_endpoint_are_blocked_before_any_connection(self):
        cases = [('openrouter/auto', 'https://openrouter.ai/api/v1', 'free_only_model'), ('openai/gpt-4o', 'https://openrouter.ai/api/v1', 'free_only_model'), ('google/gemma:free:online', 'https://openrouter.ai/api/v1', 'free_only_model'), ('openrouter/free', 'https://example.com/api/v1', 'free_only_endpoint')]
        for model, base_url, code in cases:
            with self.subTest(model=model, base_url=base_url), patch.dict(os.environ, {'LLM_MODEL':model, 'LLM_BASE_URL':base_url}), patch('openai.OpenAI') as sdk:
                with self.assertRaises(GenerationError) as caught:
                    draft('Hello', [])
                self.assertEqual(caught.exception.code, code)
                sdk.assert_not_called()

    def test_verified_free_model_can_be_selected(self):
        with patch.dict(os.environ, {'LLM_MODEL':'google/gemma-4-31b-it:free'}), patch('openai.OpenAI') as sdk:
            sdk.return_value.chat.completions.create.return_value = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='OK'))])
            self.assertEqual(draft('Hello', []), 'OK')
            self.assertEqual(sdk.return_value.chat.completions.create.call_args.kwargs['model'], 'google/gemma-4-31b-it:free')

    def test_diagnostic_tool_does_not_connect_for_paid_model(self):
        from tools import check_openrouter
        settings = {'LLM_API_KEY':'unit-test-only', 'LLM_MODEL':'openrouter/auto', 'LLM_BASE_URL':'https://openrouter.ai/api/v1'}
        with patch.object(check_openrouter, 'dotenv_values', return_value=settings), patch.object(check_openrouter, 'OpenAI') as sdk, redirect_stdout(io.StringIO()):
            self.assertEqual(check_openrouter.main(), 1)
            sdk.assert_not_called()

    def test_app_returns_specific_error(self):
        with patch('app.draft', side_effect=GenerationError('rate_limit', 'OpenRouter giới hạn lượt gọi (429).')), patch('app.retrieve', return_value=[]):
            result = chat(ChatRequest(question='Xin chào'))
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['error_code'], 'rate_limit')
        self.assertIn('429', result['answer'])


if __name__ == '__main__':
    unittest.main()
