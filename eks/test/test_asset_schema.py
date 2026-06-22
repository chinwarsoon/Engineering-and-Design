"""
Standalone test runner for asset schema tests (T1.20, R39).
Runs without fitz/PyMuPDF dependency.
"""
import unittest
import json
import sys
from pathlib import Path

# Resolve config dir
CONFIG_DIR = Path('eks/config/schemas')
if not CONFIG_DIR.exists():
    CONFIG_DIR = Path('eks/config')
if not CONFIG_DIR.exists():
    CONFIG_DIR = Path('config/schemas')
if not CONFIG_DIR.exists():
    CONFIG_DIR = Path('config')

class TestAssetSchema(unittest.TestCase):

    def test_asset_schema_files_exist(self):
        """T1.20: All 3 asset schema files must exist."""
        for fname in ['eks_asset_base_schema.json', 'eks_asset_setup_schema.json', 'eks_asset_config.json']:
            self.assertTrue((CONFIG_DIR / fname).exists(), f"Missing: {fname}")

    def test_asset_base_schema_fragments(self):
        """T1.20: eks_asset_base_schema.json must contain all 13 fragment definitions."""
        schema = json.load(open(CONFIG_DIR / 'eks_asset_base_schema.json', encoding='utf-8'))
        defs = set(schema.get('definitions', {}).keys())
        expected = {
            'item_core', 'process_conditions', 'manufacturer', 'asset_lifecycle',
            'control_system', 'piping_connection', 'valve_internals', 'actuator',
            'rotating_equipment', 'instrumentation', 'pipeline_route',
            'specialist_equipment', 'motor_control'
        }
        self.assertEqual(defs, expected, f"Fragment mismatch.\nExpected: {sorted(expected)}\nFound:    {sorted(defs)}")

    def test_asset_schema_validation(self):
        """T1.20 / R39: eks_asset_config.json validates against eks_asset_setup_schema.json."""
        from referencing import Registry
        from referencing.jsonschema import DRAFT7
        from jsonschema import validate

        base   = json.load(open(CONFIG_DIR / 'eks_asset_base_schema.json',  encoding='utf-8'))
        setup  = json.load(open(CONFIG_DIR / 'eks_asset_setup_schema.json', encoding='utf-8'))
        config = json.load(open(CONFIG_DIR / 'eks_asset_config.json',        encoding='utf-8'))

        resources = {s['$id']: DRAFT7.create_resource(s) for s in [base, setup] if '$id' in s}
        registry = Registry().with_resources(resources.items())
        validate(instance=config, schema=setup, registry=registry)

    def test_r39_conditional_fragments_structure(self):
        """R39: conditional_fragments must be present and well-formed for AT_EQUIP."""
        config  = json.load(open(CONFIG_DIR / 'eks_asset_config.json', encoding='utf-8'))
        at_reg  = config.get('asset_type_registry', {})
        at_equip = at_reg.get('AT_EQUIP', {})
        self.assertIn('conditional_fragments', at_equip)
        rule = at_equip['conditional_fragments'][0]
        self.assertEqual(rule['fragment'], 'specialist_equipment')
        self.assertEqual(rule['when'], 'device_type_code')
        self.assertIsInstance(rule['in'], list)
        self.assertGreater(len(rule['in']), 0)

    def test_r39_motor_control_fragment(self):
        """R39: AT_MOTOR must include motor_control in its fragments list."""
        config = json.load(open(CONFIG_DIR / 'eks_asset_config.json', encoding='utf-8'))
        at_motor = config['asset_type_registry'].get('AT_MOTOR', {})
        self.assertIn('motor_control', at_motor.get('fragments', []))

    def test_r39_all_config_fragments_in_base(self):
        """R39: Every fragment name referenced in config must exist in base schema definitions."""
        base   = json.load(open(CONFIG_DIR / 'eks_asset_base_schema.json', encoding='utf-8'))
        config = json.load(open(CONFIG_DIR / 'eks_asset_config.json',       encoding='utf-8'))
        base_frags = set(base.get('definitions', {}).keys())
        for at_code, entry in config.get('asset_type_registry', {}).items():
            for f in entry.get('fragments', []):
                self.assertIn(f, base_frags, f"{at_code}: fragment '{f}' not defined in base schema")
            for rule in entry.get('conditional_fragments', []):
                self.assertIn(rule['fragment'], base_frags,
                    f"{at_code}: conditional fragment '{rule['fragment']}' not defined in base schema")

    def test_r39_all_at_types_present(self):
        """R39: All 14 AT_ tag types must be registered in asset_type_registry."""
        config   = json.load(open(CONFIG_DIR / 'eks_asset_config.json', encoding='utf-8'))
        at_types = set(config.get('asset_type_registry', {}).keys())
        expected = {
            'AT_EQUIP','AT_EQPMP','AT_EQTNK','AT_EQVES','AT_EQEXC',
            'AT_INCOMP','AT_INST_','AT_INST_CS','AT_INST_FLO',
            'AT_MOTOR','AT_PROCESS','AT_CVALVE','AT_PSV','AT_HVALVE'
        }
        self.assertEqual(at_types, expected, f"AT_ type mismatch.\nMissing: {expected - at_types}\nExtra:   {at_types - expected}")

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromTestCase(TestAssetSchema)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
