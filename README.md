# FeatBit OpenFeature Provider for Python Server SDK

Thin OpenFeature provider backed by an existing FeatBit Python Server SDK client.
The provider converts OpenFeature evaluation contexts and resolution details; feature
flag synchronization, local evaluation, and insight events remain owned by
`fb-python-sdk`.

## Installation

```shell
pip install featbit-openfeature-server
```

The initial implementation requires a FeatBit Python SDK release that exposes
`EvalDetail.variation_id` (planned as `fb-python-sdk>=1.1.8`).

## Usage

```python
from fbclient.client import FBClient
from fbclient.config import Config
from openfeature import api
from openfeature.evaluation_context import EvaluationContext

from featbit_openfeature import FeatBitProvider

fb_client = FBClient(
    Config(
        "server-side-environment-secret",
        event_url="https://app-eval.featbit.co",
        streaming_url="wss://app-eval.featbit.co",
    ),
    start_wait=0,
)

api.set_provider_and_wait(FeatBitProvider(fb_client))
client = api.get_client()

details = client.get_boolean_details(
    "new-checkout",
    False,
    EvaluationContext(
        targeting_key="user-123",
        attributes={"name": "Alice", "plan": "beta"},
    ),
)

print(details.value, details.reason, details.variant)

api.shutdown()
fb_client.stop()
```

The application owns the injected `FBClient`. Calling `api.shutdown()` removes
provider listeners but does not stop the FeatBit client; call `fb_client.stop()`
afterward so queued events are flushed and background resources are released.

## Supported mappings

- Boolean, string, integer, float, and object resolution.
- OpenFeature targeting key and scalar attributes to a FeatBit user dictionary.
- FeatBit reasons and failures to OpenFeature `Reason` and `ErrorCode`.
- FeatBit variation ID to OpenFeature `variant`.
- FeatBit flag changes to `PROVIDER_CONFIGURATION_CHANGED`.
- OpenFeature tracking value to `FBClient.track_metric()`.

Structured evaluation-context attributes and tracking custom attributes are not
supported by the current FeatBit user and metric schemas. They are ignored rather
than represented inaccurately.

## Development tests

Unit tests use mocks, and the integration test uses FeatBit offline data. Neither
requires a FeatBit account.
