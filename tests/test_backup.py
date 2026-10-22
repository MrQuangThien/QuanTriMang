def test_backup_import():
    from core.backup import backup_one, backup_all
    assert callable(backup_one)
    assert callable(backup_all)
