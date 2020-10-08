import os
import sys
import pytest
import solvebio as sb
import recipes.sync_recipes as sync_recipes
import mock
from click.testing import CliRunner


def get_input(name):
    return os.path.join(os.path.dirname(__file__), "test_inputs", name)


@pytest.fixture
def mock_dataset_template_retrieve(monkeypatch):
    def mock(*args, **kwargs):
        ds = sb.DatasetTemplate(id="fake")

    monkeypatch.setattr(sync_recipes.sb.DatasetTemplate, "retrieve", mock)
    monkeypatch.setattr(sync_recipes.sb.DatasetTemplate, "delete", mock)
    monkeypatch.setattr(sync_recipes.sb.DatasetTemplate, "create", mock)
    monkeypatch.setattr(sync_recipes.sb.DatasetTemplate, "all", mock)


runner = CliRunner()


@pytest.fixture
def mock_user_retrieve(monkeypatch):
    def retrieve(*args, **kwargs):
        usr = sb.User(id="fake", full_name="Name", domain="Domain", account="Account")
        usr.full_name = "full name"
        usr.id = "3851"
        return usr
    monkeypatch.setattr(sync_recipes.sb.User, "retrieve", retrieve)

@pytest.mark.skipif(sys.version_info < (3,0), reason="requires python3")
def test_sync_recipe(mock_dataset_template_retrieve,
                     mock_user_retrieve):
    with pytest.raises(SystemExit) as e:
        sync_recipes.sync_recipes(["--help"])
    assert e.value.code == 0

    mock.patch('Solvebio.login', mock.MagicMock())

    # Invalid file
    with pytest.raises(SystemExit) as e:
        config = get_input("non_existing_file.yml")
        sync_recipes.sync(["--name", "cDNA Change (v1.0.2)", config])
    assert e.value.code == 2

    # Valid commands
    config = get_input("valid.yml")
    result = runner.invoke(sync_recipes.sync,
                           args=["--name", "cDNA Change (v1.0.2)", config],
                           input="y")
    assert result.exit_code == 0
    assert "create cDNA Change (v1.0.2)" in result.output

    result = runner.invoke(sync_recipes.delete,
                           args=["--name", "cDNA Change (v1.0.2)", config],
                           input="y")
    assert result.exit_code == 0
    assert "Requested recipe cDNA Change (v1.0.2) doesn't exist in SolveBio!" in result.output

    result = runner.invoke(sync_recipes.sync,
                           args=["--all", config],
                           input="N")
    assert result.exit_code == 0
    assert "create cDNA Change (v1.0.2)" in result.output
    assert "Aborted" in result.output

    result = runner.invoke(sync_recipes.delete,
                           args=["--all", config],
                           input="y")
    assert result.exit_code == 0
    assert "Requested recipe cDNA Change (v1.0.2) doesn't exist in SolveBio!" in result.output

    config2 = get_input("valid2.yml")
    result = runner.invoke(sync_recipes.sync,
                           args=["--all", config2],
                           input="y")

    assert result.exit_code == 0
    assert "create Gene (v1.0.3)" in result.output
    assert "create Protein Change (v1.0.4)" in result.output

    result = runner.invoke(sync_recipes.delete,
                           args=["--all", config2],
                           input="y")
    assert result.exit_code == 0
    assert "Requested recipe Gene (v1.0.3) doesn't exist in SolveBio!" in result.output
    assert "Requested recipe Protein Change (v1.0.4) doesn't exist in SolveBio!" in result.output

    yml_export_file = get_input("export.yml")
    # Test export mode with public/account recipes
    result = runner.invoke(sync_recipes.export,
                           args=["--public-recipes", yml_export_file])
    os.remove(yml_export_file)
    assert "Exporting all public recipes" in result.output
