import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


patch = module('apply_game_patch')
layouts = module('merge_touch_presets')
logs = module('log_summary')
fonts = module('register_fonts32')


class SafetyTests(unittest.TestCase):
    def recipe(self):
        return {'format': 1, 'input_bytes': 6, 'output_bytes': 7,
                'input_sha256': hashlib.sha256(b'abcdef').hexdigest(),
                'output_sha256': hashlib.sha256(b'abXYef!').hexdigest(),
                'edits': [{'offset': 2, 'before': '6364', 'after': '5859'}], 'append': '21'}

    def test_patch_rejects_wrong_build(self):
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            patch.transform(b'ABCDEF', self.recipe())

    def test_patch_rejects_context_and_overlap(self):
        recipe = self.recipe()
        recipe['edits'][0]['before'] = '0000'
        with self.assertRaisesRegex(ValueError, 'context'):
            patch.transform(b'abcdef', recipe)
        recipe = self.recipe()
        recipe['edits'].append({'offset': 3, 'before': '64', 'after': '59'})
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            patch.transform(b'abcdef', recipe)

    def test_patch_checks_final_hash(self):
        recipe = self.recipe()
        recipe['output_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'Output verification'):
            patch.transform(b'abcdef', recipe)

    def test_patch_keeps_input_and_applies_expected_change(self):
        original = b'abcdef'
        self.assertEqual(patch.transform(original, self.recipe()), b'abXYef!')
        self.assertEqual(original, b'abcdef')

    def test_layout_merge_preserves_custom_and_refuses_conflict(self):
        current = {'version': 1, 'presets': [{'id': 'custom', 'name': '我的布局', 'controls': []}]}
        incoming = json.loads((ROOT / 'configs/touch-presets.json').read_text())
        merged = layouts.merge(current, incoming)
        self.assertEqual(merged['presets'][0], current['presets'][0])
        self.assertEqual(len(current['presets']), 1)
        self.assertEqual(layouts.merge(merged, incoming), merged)
        conflict = {'version': 1, 'presets': [{'id': 'custom', 'name': '同一ID的新布局', 'controls': []}]}
        with self.assertRaises(ValueError):
            layouts.merge(current, conflict)

    def test_log_output_never_echoes_private_payloads(self):
        text = ('token=FAKE_SECRET account=FAKE_USER\n'
                '[steam-cloud] app=4870960 cloud-files=5 same=5 differ=0 unmapped=0 | plan download=0 upload=0 ask=0 token=FAKE_SECRET\n'
                'session-authenticated-online=1\nlaunch-client-error=0\n')
        summary = logs.summarize(text)
        rendered = json.dumps(summary)
        self.assertNotIn('FAKE_', rendered)
        self.assertTrue(summary['online_authenticated'])
        self.assertEqual(summary['cloud']['4870960']['upload'], 0)
        self.assertFalse(summary['game_window_observed'])

    def test_font_registration_preserves_other_sections_and_is_idempotent(self):
        text = ('WINE REGISTRY Version 2\n\n' + fonts.SOURCE + '\n'
                '"Microsoft YaHei"="msyh.ttc"\n\n' + fonts.TARGET + '\n'
                '"Existing"="existing.ttf"\n\n[Unrelated]\n"Keep"="yes"\n')
        updated, count = fonts.update(text)
        self.assertEqual(count, 1)
        self.assertIn('[Unrelated]\n"Keep"="yes"', updated)
        self.assertIn('"Existing"="existing.ttf"', updated)
        self.assertEqual(fonts.update(updated), (updated, 0))
        conflict = text.replace('"Existing"="existing.ttf"', '"Microsoft YaHei"="different.ttf"')
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            fonts.update(conflict)


if __name__ == '__main__':
    unittest.main()
