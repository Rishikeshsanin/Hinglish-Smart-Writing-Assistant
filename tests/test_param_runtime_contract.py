"""Mocked adapter tests only: these NEVER establish pretrained model quality."""
from types import SimpleNamespace
import pytest
from indicwrite.param_rewrite import (
    BharatGenRewriter, RewriteError, build_messages, _stop_ids, MAX_INPUT_TOKENS,
)


def test_remote_code_requires_explicit_opt_in():
    with pytest.raises(RewriteError, match="Review"):
        BharatGenRewriter.load()


@pytest.mark.parametrize("text", ["।", "१२३", "\u093e", "hello ।"])
def test_punctuation_digits_and_marks_are_not_hindi_letters(text):
    with pytest.raises(ValueError):
        build_messages(text)


def test_preserves_all_official_stop_tokens():
    model = SimpleNamespace(generation_config=SimpleNamespace(eos_token_id=[256001, 3]))
    assert _stop_ids(model, SimpleNamespace(eos_token_id=256001)) == [3, 256001]


def fake_engine(ids, decoded="सीता स्कूल जाती है।", input_length=4):
    torch = pytest.importorskip("torch")
    class Batch(dict):
        def to(self, device):
            return self
    class Tokenizer:
        eos_token_id, pad_token_id = 256001, 256002
        def apply_chat_template(self, *args, **kwargs):
            assert kwargs["return_dict"] is True
            return Batch(input_ids=torch.ones((1, input_length), dtype=torch.long),
                         attention_mask=torch.ones((1, input_length), dtype=torch.long))
        def decode(self, tokens, skip_special_tokens):
            return decoded
    class Model:
        config = SimpleNamespace(max_position_embeddings=8192)
        generation_config = SimpleNamespace(eos_token_id=[256001, 3])
        def get_input_embeddings(self):
            return SimpleNamespace(weight=torch.zeros(1))
        def generate(self, **kwargs):
            assert kwargs["eos_token_id"] == [3, 256001]
            assert kwargs["use_cache"] is False
            assert "attention_mask" in kwargs
            return torch.cat((kwargs["input_ids"], torch.tensor([ids])), dim=1)
    return BharatGenRewriter(Tokenizer(), Model())


def test_second_eos_and_prompt_slicing():
    result = fake_engine([15, 3]).generate_record("सीता स्कूल जाता है।")
    assert result["generated_token_ids"] == [15, 3]
    assert result["runtime_candidate_ok"]
    assert result["meaning_preservation"] == "NOT_EVALUATED"


def test_truncated_candidate_is_retained_for_audit_but_not_displayed():
    engine = fake_engine([15] * 120)
    result = engine.generate_record("सीता स्कूल जाता है।")
    assert result["checks"]["hit_token_limit_without_eos"]
    assert result["candidate"]
    with pytest.raises(RewriteError):
        engine.rewrite("सीता स्कूल जाता है।")


def test_token_budget_rejects_without_truncating():
    with pytest.raises(ValueError, match="budget"):
        fake_engine([3], input_length=MAX_INPUT_TOKENS + 1).generate_record("हिंदी")


@pytest.mark.parametrize("decoded", ["", "English only", "।"])
def test_empty_or_non_hindi_candidates_rejected(decoded):
    with pytest.raises(RewriteError):
        fake_engine([3], decoded=decoded).rewrite("हिंदी")


def test_loader_pins_and_checks_code_before_model_load(monkeypatch, tmp_path):
    import hashlib
    torch = pytest.importorskip("torch")
    transformers = pytest.importorskip("transformers")
    hub = pytest.importorskip("huggingface_hub")
    import indicwrite.param_rewrite as runtime
    fixture = tmp_path / 'reviewed.py'
    fixture.write_bytes(b'# test fixture, never executed\n')
    digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
    monkeypatch.setattr(runtime, 'CODE_SHA256', {'reviewed.py': digest})
    calls = []
    def download(*args, **kwargs):
        assert kwargs['revision'] == runtime.MODEL_REVISION
        assert kwargs['token'] is False
        calls.append('hash')
        return str(fixture)
    monkeypatch.setattr(hub, 'hf_hub_download', download)
    tokenizer = SimpleNamespace(chat_template='fixture')
    monkeypatch.setattr(transformers.AutoTokenizer, 'from_pretrained', lambda *a, **k: tokenizer)
    model = SimpleNamespace(generate=lambda: None)
    model.eval = lambda: model
    def load(*args, **kwargs):
        assert calls == ['hash']
        assert kwargs['revision'] == kwargs['code_revision'] == runtime.MODEL_REVISION
        assert kwargs['dtype'] is torch.float32
        assert kwargs['device_map'] == {'': 'cpu'}
        assert kwargs['use_safetensors'] is True
        return model
    monkeypatch.setattr(transformers.AutoModelForCausalLM, 'from_pretrained', load)
    engine = runtime.BharatGenRewriter.load(allow_remote_code=True, device='cpu')
    assert engine.model is model
    fixture.write_bytes(b'# changed source\n')
    with pytest.raises(RewriteError, match='hash mismatch'):
        runtime.BharatGenRewriter.load(allow_remote_code=True, device='cpu')
