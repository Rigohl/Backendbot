import os
import sys
import json

# Ensure src is importable (consistent with other tests)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backendbot.staging_automation import (
    schedule_optimizations,
    list_recommended_powershell_commands,
    prepare_background_command,
    optimize_ram,
    perform_disk_cleanup_preview,
    write_plan_to_file,
    run_preview_workflow,
)


def test_schedule_optimizations_dry_run():
    plan = schedule_optimizations(dry_run=True)
    assert plan["dry_run"] is True
    assert "task" in plan


def test_powershell_commands():
    cmds = list_recommended_powershell_commands()
    assert isinstance(cmds, list)
    assert any("Start-Job" in c or "Register-ScheduledTask" in c for c in cmds)


def test_prepare_background_command():
    cmd = prepare_background_command("scripts/start_staging.ps1")
    assert "Start-Process" in cmd
    assert "start_staging.ps1" in cmd


def test_optimize_ram_preview():
    plan = optimize_ram(dry_run=True)
    assert plan["dry_run"] is True
    assert "candidates" in plan


def test_disk_cleanup_preview(tmp_path):
    d = tmp_path / "tmpdir"
    d.mkdir()
    f = d / "a.txt"
    f.write_text("hello")
    preview = perform_disk_cleanup_preview([str(d)], dry_run=True)
    assert preview["preview"][0]["exists"] is True


def test_write_plan_to_file(tmp_path):
    plan = {"a": 1}
    out = tmp_path / "plan.json"
    path = write_plan_to_file(plan, str(out))
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["a"] == 1


def test_run_preview_workflow(tmp_path):
    out = tmp_path / "staging_plan.json"
    plan = run_preview_workflow(str(out))
    assert "scheduled" in plan
    assert os.path.exists(str(out))
