from pathlib import Path

from unlock_pressure.__main__ import main


def test_cli_fixture_mode(tmp_path, capsys):
    exit_code = main(["run", "--mode", "fixture", "--output-dir", str(tmp_path)])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Unlock Pressure" in output
    assert "HIGH" in output
    assert "TOKEN-A" in output or "TOKEN-B" in output or "TOKEN-C" in output
    assert (Path(tmp_path) / "strategy-card.yaml").exists()
    assert (Path(tmp_path) / "strategy-card.md").exists()
