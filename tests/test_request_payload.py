from src.agent.tools.request_payload import (
    clear_request_payload,
    fetch_request_payload,
    set_request_payload,
)


def test_request_payload_round_trip():
    clear_request_payload()
    set_request_payload(["https://example.com"], "harvard")
    payload = fetch_request_payload()
    assert payload["urls"] == ["https://example.com"]
    assert payload["format"] == "harvard"
    clear_request_payload()
    try:
        fetch_request_payload()
        assert False, "Expected RuntimeError when payload missing"
    except RuntimeError:
        pass

