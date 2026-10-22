def test_core_imports():
    from core.connector import load_devices, get_running_config
    from core.backup import backup_one, backup_all
    from core.diff_engine import diff_latest
    from core.monitor import collect_metrics
    from core.restore import safe_restore
    assert callable(load_devices)
    assert callable(get_running_config)
    assert callable(backup_one)
    assert callable(backup_all)
    assert callable(diff_latest)
    assert callable(collect_metrics)
    assert callable(safe_restore)
