from typer.testing import CliRunner
from tissu_cli.main import app

runner = CliRunner()


def test_info_json():
    result = runner.invoke(app, ["info", "data/scenes/curtain.json"])
    assert result.exit_code == 0


def test_info_tissu():
    result = runner.invoke(app, ["info", "data/states/frame42.tissu"])
    assert result.exit_code == 0


def test_bake():
    result = runner.invoke(app, [
        "bake", "data/scenes/curtain.json",
        "--out", "data/animations/output.abc",
        "--start", "1",
        "--end", "24",
        "--fps", "24"
    ])
    assert result.exit_code == 0
