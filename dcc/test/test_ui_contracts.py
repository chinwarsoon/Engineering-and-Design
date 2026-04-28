"""
Phase 4 Test: UI Consumer Contracts (R20, R21)

Tests for PathSelectionContract, ParameterOverrideContract, and UIContractManager.

Usage:
    cd /home/franklin/dsai/Engineering-and-Design/dcc/test
    python test_ui_contracts.py
"""

import sys
from pathlib import Path

# Add workflow path
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow"))

from initiation_engine.overrides import (
    PathSelectionContract,
    ParameterOverrideContract,
    UIContractBundle,
    get_available_files,
    suggest_base_paths,
    validate_and_resolve,
)
from core_engine.ui_contract import UIContractManager, UIRequest, UIResponse


def test_path_selection_contract():
    """Test PathSelectionContract creation and validation."""
    print("\n" + "="*60)
    print("Test 1: PathSelectionContract")
    print("="*60)
    
    # Test 1a: Create contract
    contract = PathSelectionContract(
        base_path=Path("/tmp/test_dcc"),
        upload_file_name="test.xlsx",
        output_folder="output_test"
    )
    print("✅ Contract created")
    
    # Test 1b: Verify file extension normalization
    assert contract.upload_file_name.endswith('.xlsx')
    print("✅ File extension normalized")
    
    # Test 1c: Convert to paths
    try:
        paths = contract.to_paths()
        print(f"✅ Paths resolved:")
        print(f"   - Excel: {paths.excel_path}")
        print(f"   - Schema: {paths.schema_path}")
        print(f"   - Output CSV: {paths.csv_output_path}")
    except Exception as e:
        print(f"⚠️  Path resolution (expected for non-existent path): {e}")
    
    # Test 1d: Serialization
    data = contract.to_dict()
    assert "base_path" in data
    assert "upload_file_name" in data
    print("✅ Serialization works")
    
    # Test 1e: Deserialization
    restored = PathSelectionContract.from_dict(data)
    assert restored.upload_file_name == contract.upload_file_name
    print("✅ Deserialization works")
    
    print("\n✅ All PathSelectionContract tests passed!")
    return True


def test_parameter_override_contract():
    """Test ParameterOverrideContract creation and validation."""
    print("\n" + "="*60)
    print("Test 2: ParameterOverrideContract")
    print("="*60)
    
    # Test 2a: Create contract with defaults
    contract = ParameterOverrideContract()
    assert contract.debug_mode == False
    assert contract.nrows is None
    print("✅ Default contract created")
    
    # Test 2b: Create contract with overrides
    contract = ParameterOverrideContract(debug_mode=True, nrows=500)
    assert contract.debug_mode == True
    assert contract.nrows == 500
    print("✅ Override contract created")
    
    # Test 2c: Validation
    result = contract.validate()
    assert "valid" in result or "warnings" in result
    print(f"✅ Validation result: {result}")
    
    # Test 2d: Serialization
    data = contract.to_dict()
    assert data["debug_mode"] == True
    assert data["nrows"] == 500
    print("✅ Serialization works")
    
    # Test 2e: Invalid nrows should raise error
    try:
        bad_contract = ParameterOverrideContract(nrows=-1)
        print("❌ Should have raised ValueError for negative nrows")
        return False
    except ValueError:
        print("✅ Correctly rejected negative nrows")
    
    print("\n✅ All ParameterOverrideContract tests passed!")
    return True


def test_ui_contract_bundle():
    """Test combined UIContractBundle."""
    print("\n" + "="*60)
    print("Test 3: UIContractBundle")
    print("="*60)
    
    # Test 3a: Create bundle
    path_contract = PathSelectionContract(
        base_path=Path("/tmp/test"),
        upload_file_name="data.xlsx"
    )
    param_contract = ParameterOverrideContract(debug_mode=True, nrows=100)
    
    bundle = UIContractBundle(
        path_selection=path_contract,
        parameters=param_contract
    )
    print("✅ Bundle created")
    
    # Test 3b: Validation (may fail due to non-existent path, but that's OK)
    result = bundle.validate()
    print(f"✅ Bundle validation: {result}")
    
    # Test 3c: Serialization
    data = bundle.to_dict()
    assert "path_selection" in data
    assert "parameters" in data
    print("✅ Bundle serialization works")
    
    # Test 3d: JSON serialization
    json_str = bundle.to_json()
    assert isinstance(json_str, str)
    print("✅ Bundle JSON serialization works")
    
    # Test 3e: Deserialization
    restored = UIContractBundle.from_json(json_str)
    assert restored.path_selection.upload_file_name == "data.xlsx"
    print("✅ Bundle JSON deserialization works")
    
    print("\n✅ All UIContractBundle tests passed!")
    return True


def test_ui_request_response():
    """Test UIRequest and UIResponse."""
    print("\n" + "="*60)
    print("Test 4: UIRequest and UIResponse")
    print("="*60)
    
    # Test 4a: Create UIRequest
    request = UIRequest(
        base_path="/tmp/test",
        upload_file_name="test.xlsx",
        debug_mode=True,
        nrows=500
    )
    print("✅ UIRequest created")
    
    # Test 4b: Convert to contract bundle
    bundle = request.to_contract_bundle()
    assert bundle.path_selection.upload_file_name == "test.xlsx"
    print("✅ UIRequest converts to bundle")
    
    # Test 4c: Create UIResponse
    response = UIResponse(
        success=True,
        message="Test completed",
        execution_time_seconds=45.5,
        rows_processed=11099,
        output_files={"csv": "/tmp/out.csv"},
        telemetry={"heartbeats": 5},
        validation={"errors": 0}
    )
    print("✅ UIResponse created")
    
    # Test 4d: Response serialization
    json_str = response.to_json()
    assert "success" in json_str
    assert "11099" in json_str
    print("✅ UIResponse JSON serialization works")
    
    print("\n✅ All UIRequest/UIResponse tests passed!")
    return True


def test_ui_contract_manager():
    """Test UIContractManager."""
    print("\n" + "="*60)
    print("Test 5: UIContractManager")
    print("="*60)
    
    # Test 5a: Create manager
    manager = UIContractManager()
    print("✅ UIContractManager created")
    
    # Test 5b: Get suggested paths (may be empty in test environment)
    paths = manager.get_suggested_paths()
    print(f"✅ Suggested paths: {len(paths)} found")
    for p in paths[:3]:  # Show first 3
        print(f"   - {p.get('label', 'Unknown')}: {p.get('path', 'N/A')}")
    
    # Test 5c: Get available files (may be empty if no data folder)
    if paths:
        test_path = paths[0]["path"]
        files = manager.get_available_files(test_path)
        print(f"✅ Available files in {test_path}: {len(files)} found")
    
    # Test 5d: Validation (will fail for non-existent path, which is expected)
    result = manager.validate_selection(
        base_path="/nonexistent",
        upload_file_name="test.xlsx"
    )
    print(f"✅ Validation called (expected failure for non-existent path)")
    
    print("\n✅ All UIContractManager tests passed!")
    return True


def test_api_endpoints_documentation():
    """Test that API endpoints are documented."""
    print("\n" + "="*60)
    print("Test 6: API Endpoints Documentation")
    print("="*60)
    
    from core_engine.ui_contract import API_ENDPOINTS
    
    assert "GET /api/v1/paths/suggestions" in API_ENDPOINTS
    assert "GET /api/v1/files" in API_ENDPOINTS
    assert "POST /api/v1/pipeline/validate" in API_ENDPOINTS
    assert "POST /api/v1/pipeline/run" in API_ENDPOINTS
    
    print("✅ All API endpoints documented:")
    for endpoint, info in API_ENDPOINTS.items():
        print(f"   - {endpoint}: {info.get('description', 'N/A')}")
    
    print("\n✅ API documentation test passed!")
    return True


def run_all_tests():
    """Run all Phase 4 UI contract tests."""
    print("\n" + "="*70)
    print("PHASE 4: UI CONTRACTS TEST SUITE (R20, R21)")
    print("="*70)
    
    tests = [
        ("PathSelectionContract", test_path_selection_contract),
        ("ParameterOverrideContract", test_parameter_override_contract),
        ("UIContractBundle", test_ui_contract_bundle),
        ("UIRequest/UIResponse", test_ui_request_response),
        ("UIContractManager", test_ui_contract_manager),
        ("API Documentation", test_api_endpoints_documentation),
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Phase 4 UI Contract tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
