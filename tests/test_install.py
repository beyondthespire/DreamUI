"""Exercise deployment against isolated temporary homes, never the real desktop."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('manage',ROOT/'scripts/manage.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Installation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source=self.root/'source'
        self.source.mkdir()
        self.manager=m.Manager(self.root/'data',self.root/'config',self.root/'state')
        (self.source/'theme').write_bytes(b'new')

    def test_first_install_update_uninstall_restores_original(self):
        target=self.root/'data/theme'; target.parent.mkdir()
        target.write_bytes(b'original'); target.chmod(0o640)
        self.manager.install(self.source)
        (self.source/'theme').write_bytes(b'updated')
        self.manager.install(self.source)
        self.assertEqual(target.read_bytes(),b'updated')
        self.manager.uninstall()
        self.assertEqual(target.read_bytes(),b'original')
        self.assertEqual(target.stat().st_mode&0o777,0o640)

    def test_modified_assets_block_update_and_uninstall(self):
        self.manager.install(self.source)
        (self.root/'data/theme').write_bytes(b'my edits')
        with self.assertRaisesRegex(RuntimeError,'changed or removed'): self.manager.install(self.source)
        with self.assertRaisesRegex(RuntimeError,'changed or removed'): self.manager.uninstall()
        self.assertEqual((self.root/'data/theme').read_bytes(),b'my edits')

    def test_dry_run_makes_no_directories(self):
        self.manager.install(self.source,dry=True)
        self.assertFalse((self.root/'data').exists())
        self.assertFalse((self.root/'state').exists())

    def test_symlink_escape_rejected(self):
        (self.root/'data').mkdir()
        (self.root/'outside').write_bytes(b'keep')
        (self.root/'data/theme').symlink_to(self.root/'outside')
        with self.assertRaisesRegex(RuntimeError,'symlink'): self.manager.install(self.source)
        self.assertEqual((self.root/'outside').read_bytes(),b'keep')

    def test_stale_files_restored(self):
        self.manager.install(self.source)
        (self.source/'theme').unlink()
        (self.source/'replacement').write_bytes(b'next')
        self.manager.install(self.source)
        self.assertFalse((self.root/'data/theme').exists())
        self.manager.uninstall()
        self.assertFalse((self.root/'data/replacement').exists())

    def test_failure_rolls_back_assets_and_ledger(self):
        self.manager.install(self.source)
        before=self.manager.ledger_path.read_bytes()
        (self.source/'theme').write_bytes(b'update')
        (self.source/'z-fail').write_bytes(b'fail')
        real=m.atomic_write
        def fail_once(path,content,mode=0o644):
            if path.name=='z-fail' and content==b'fail': raise OSError('disk failure')
            return real(path,content,mode)
        with patch.object(m,'atomic_write',side_effect=fail_once):
            with self.assertRaises(OSError): self.manager.install(self.source)
        self.assertEqual((self.root/'data/theme').read_bytes(),b'new')
        self.assertEqual(self.manager.ledger_path.read_bytes(),before)
        self.assertFalse((self.root/'state/pending.json').exists())

    def test_settings_backed_up_once_and_explicit_restore(self):
        self.manager.install(self.source)
        cfg=self.root/'config/kdeglobals'; cfg.parent.mkdir(); cfg.write_bytes(b'personal')
        self.manager.backup_settings()
        cfg.write_bytes(b'dream')
        self.manager.backup_settings()
        with self.assertRaisesRegex(RuntimeError,'Log out'): self.manager.uninstall()
        with patch.object(m.subprocess,'run') as run:
            run.return_value.returncode=1
            self.manager.uninstall(restore_settings=True)
        self.assertEqual(cfg.read_bytes(),b'personal')

    def test_running_plasma_blocks_restore(self):
        self.manager.install(self.source)
        self.manager.backup_settings()
        with patch.object(m.subprocess,'run') as run:
            run.return_value.returncode=0
            with self.assertRaisesRegex(RuntimeError,'Log out'): self.manager.uninstall(True)
        self.assertTrue((self.root/'data/theme').exists())

    def test_xdg_path_change_rejected(self):
        self.manager.install(self.source)
        with self.assertRaisesRegex(RuntimeError,'XDG paths changed'):
            m.Manager(self.root/'other',self.root/'config',self.root/'state')

    def test_path_traversal_rejected(self):
        for path in ('../escape','/tmp/escape'):
            with self.assertRaises(RuntimeError): m.safe_path(self.root,path)

    def test_crash_recovery_restores_files_and_ledger(self):
        self.manager.install(self.source)
        original_ledger=self.manager.ledger_path.read_bytes()
        (self.source/'theme').write_bytes(b'next')
        # Simulate a process exit after writing assets but before committing state.
        with patch.object(self.manager,'save',side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt): self.manager.install(self.source)
        self.assertTrue((self.root/'state/pending.json').exists())
        # CLI uses STATE_HOME/dreamui, so use a parallel recovery manager via a
        # correctly named state directory for the full recovery path.
        state_home=self.root/'state-home'; state_home.mkdir()
        (self.root/'state').rename(state_home/'dreamui')
        with patch.object(m.os,'geteuid',return_value=1000), patch.dict(m.os.environ,{
            'XDG_DATA_HOME':str(self.root/'data'), 'XDG_CONFIG_HOME':str(self.root/'config'),
            'XDG_STATE_HOME':str(state_home)}), patch.object(m.sys,'argv',['manage.py','recover']):
            m.main()
        self.assertEqual((self.root/'data/theme').read_bytes(),b'new')
        self.assertEqual((state_home/'dreamui/installation.json').read_bytes(),original_ledger)
        self.assertFalse((state_home/'dreamui/pending.json').exists())

    def test_apply_failure_keeps_original_config_snapshot(self):
        theme=self.source/'plasma/look-and-feel/org.beyondthespire.dreamui.blue'
        theme.mkdir(parents=True); (theme/'metadata.json').write_text('{}')
        self.manager.install(self.source)
        cfg=self.root/'config/kdeglobals'; cfg.parent.mkdir(); cfg.write_bytes(b'original')
        with patch.object(m,'require_plasma'), patch.object(m.shutil,'which',return_value='/tool'), \
             patch.dict(m.os.environ,{'DBUS_SESSION_BUS_ADDRESS':'test'}), \
             patch.object(m.subprocess,'run',side_effect=m.subprocess.CalledProcessError(1,'apply')):
            with self.assertRaises(m.subprocess.CalledProcessError): m.apply(self.manager,'blue')
        self.assertEqual(m.base64.b64decode(self.manager.ledger['settings']['kdeglobals']['content']),b'original')

if __name__=='__main__': unittest.main()
