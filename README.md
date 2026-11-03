# FeatBit OpenFeature Provider for Python Server SDK

Thin OpenFeature provider backed by an existing FeatBit Python Server SDK client.
The provider converts OpenFeature evaluation contexts and resolution details; feature
flag synchronization, local evaluation, and insight events remain owned by
`fb-python-sdk`.

## Installation

```shell
pip install featbit-openfeature-server
```

The provider supports Python 3.10–3.14 and requires `fb-python-sdk>=1.2.0`,
which exposes variation IDs and data-update status listeners.

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
```

The provider owns the injected `FBClient`. Calling `api.shutdown()` removes
provider listeners and stops the FeatBit client so queued events are flushed
and background resources are released.

## Supported mappings

- Boolean, string, integer, float, and object resolution.
- OpenFeature targeting key and scalar attributes to a FeatBit user dictionary.
- FeatBit reasons and failures to OpenFeature `Reason` and `ErrorCode`.
- FeatBit variation ID to OpenFeature `variant`.
- FeatBit flag changes to `PROVIDER_CONFIGURATION_CHANGED`.
- FeatBit runtime data-source status to OpenFeature provider status.
- OpenFeature tracking value to `FBClient.track_metric()`.

Structured evaluation-context attributes and tracking custom attributes are not
supported by the current FeatBit user and metric schemas. They are ignored rather
than represented inaccurately.

## Provider status

Applications can read the status through the standard OpenFeature client:

```python
from openfeature.provider import ProviderStatus

status = client.get_provider_status()
assert status in {
    ProviderStatus.NOT_READY,
    ProviderStatus.READY,
    ProviderStatus.STALE,
    ProviderStatus.ERROR,
    ProviderStatus.FATAL,
}
```

FeatBit states are mapped as follows:

| FeatBit state | OpenFeature status |
| --- | --- |
| initializing | `NOT_READY` during provider initialization |
| OK | `READY` |
| interrupted | `STALE` |
| off observed while provider is active | `FATAL` |

After `api.shutdown()`, OpenFeature removes this provider and installs its default
no-op provider. Status after that point belongs to the OpenFeature SDK rather than
to FeatBit.

The included `py.typed` marker declares this package as PEP 561 typed, allowing
type checkers to use the annotations shipped with the provider after install.

## Development tests

Unit tests use mocks, and the integration test uses FeatBit offline data. Neither
requires a FeatBit account.

```shell
python -m pytest -q
python -m flake8 featbit_openfeature tests
python -m build
```

## Release

Publishing is handled by `.github/workflows/release.yml` when a GitHub Release
is published. The build and publish jobs are separated so package build code
never receives an OpenID Connect token. The publish job uses PyPI Trusted
Publishing and does not store a long-lived PyPI password in GitHub.

Before the first release, configure the PyPI trusted publisher with owner
`featbit`, repository `openfeature-provider-python-server`, workflow
`release.yml`, and GitHub environment `pypi`.
