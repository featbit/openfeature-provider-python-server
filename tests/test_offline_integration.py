from pathlib import Path

from fbclient.client import FBClient
from fbclient.config import Config
from fbclient.status_types import State
from openfeature import api
from openfeature.evaluation_context import EvaluationContext
from openfeature.flag_evaluation import Reason
from openfeature.provider import ProviderStatus

from featbit_openfeature import FeatBitProvider


def test_openfeature_client_evaluates_with_real_featbit_sdk_offline():
    data = Path(__file__).parent.joinpath("fixtures", "bootstrap.json").read_text(
        encoding="utf-8"
    )
    config = Config("offline-secret", "http://offline", "http://offline", offline=True)
    fb_client = FBClient(config, start_wait=0)
    try:
        assert fb_client.initialize_from_external_json(data)
        assert fb_client.initialize

        api.set_provider_and_wait(FeatBitProvider(fb_client))
        client = api.get_client()
        details = client.get_string_details(
            "python-app-release",
            "v1",
            EvaluationContext(
                "employee-001", {"name": "Employee", "plan": "standard"}
            ),
        )

        assert details.value == "v2"
        assert details.reason == Reason.TARGETING_MATCH
        assert details.variant == "variation-v2"
        assert details.error_code is None

        fb_client.update_status_provider.update_state(State.ok_state())
        fb_client.update_status_provider.update_state(
            State.interrupted_state("network", "connection lost")
        )
        assert client.get_provider_status() == ProviderStatus.STALE

        fb_client.update_status_provider.update_state(State.ok_state())
        assert client.get_provider_status() == ProviderStatus.READY
    finally:
        api.shutdown()
