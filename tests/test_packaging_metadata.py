from pathlib import Path


ROOT = Path(__file__).parent.parent


def test_project_license_matches_repository_license():
    pyproject = ROOT.joinpath("pyproject.toml").read_text(encoding="utf-8")
    license_text = ROOT.joinpath("LICENSE").read_text(encoding="utf-8")

    assert 'license = "Apache-2.0"' in pyproject
    assert "Apache License" in license_text
    assert "Version 2.0" in license_text
