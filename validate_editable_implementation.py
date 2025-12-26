#!/usr/bin/env python3
"""
Validation script for scenario_selector editable property implementation.
This script validates that the changes are correctly implemented.
"""

import sys
import os

# Add the taipy directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_core_lib_changes():
    """Test that the _GuiCoreLib.py changes are correct."""
    try:
        from taipy.gui_core._GuiCoreLib import _GuiCore
        
        gui_core = _GuiCore()
        elements = gui_core.get_elements()
        
        # Test 1: scenario_selector element exists
        assert "scenario_selector" in elements, "scenario_selector element not found"
        print("[PASS] scenario_selector element exists")
        
        # Test 2: editable property exists
        scenario_selector = elements["scenario_selector"]
        assert "editable" in scenario_selector.properties, "editable property not found"
        print("[PASS] editable property exists")
        
        # Test 3: editable property has correct default value
        editable_prop = scenario_selector.properties["editable"]
        assert editable_prop.default_value is True, f"Expected True, got {editable_prop.default_value}"
        print("[PASS] editable property defaults to True")
        
        # Test 4: editable property has correct type
        assert "dynamic_boolean" in str(editable_prop.type), f"Expected dynamic_boolean, got {editable_prop.type}"
        print("[PASS] editable property has correct type")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error testing _GuiCoreLib changes: {e}")
        return False

def test_viselements_json_changes():
    """Test that the viselements.json changes are correct."""
    try:
        import json
        
        with open("taipy/gui_core/viselements.json", "r") as f:
            viselements = json.load(f)
        
        # Find scenario_selector in controls
        scenario_selector = None
        for control in viselements["controls"]:
            if control[0] == "scenario_selector":
                scenario_selector = control[1]
                break
        
        assert scenario_selector is not None, "scenario_selector not found in viselements.json"
        print("[PASS] scenario_selector found in viselements.json")
        
        # Check editable property exists
        editable_prop = None
        for prop in scenario_selector["properties"]:
            if prop["name"] == "editable":
                editable_prop = prop
                break
        
        assert editable_prop is not None, "editable property not found in viselements.json"
        print("[PASS] editable property found in viselements.json")
        
        # Check property configuration
        assert editable_prop["type"] == "dynamic(bool)", f"Expected dynamic(bool), got {editable_prop['type']}"
        assert editable_prop["default_value"] == "True", f"Expected 'True', got {editable_prop['default_value']}"
        print("[PASS] editable property correctly configured in viselements.json")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error testing viselements.json changes: {e}")
        return False

def test_backward_compatibility():
    """Test that existing functionality is preserved."""
    try:
        from taipy.gui_core._GuiCoreLib import _GuiCore
        
        gui_core = _GuiCore()
        elements = gui_core.get_elements()
        scenario_selector = elements["scenario_selector"]
        
        # Test that all expected properties still exist
        expected_properties = [
            "id", "show_add_button", "display_cycles", "show_primary_flag",
            "value", "on_change", "height", "class_name", "show_pins",
            "on_creation", "show_dialog", "scenarios", "multiple",
            "filter", "sort", "show_search", "editable"
        ]
        
        for prop in expected_properties:
            assert prop in scenario_selector.properties, f"Property {prop} missing"
        
        print("[PASS] All expected properties present - backward compatibility maintained")
        return True
        
    except Exception as e:
        print(f"[FAIL] Error testing backward compatibility: {e}")
        return False

def main():
    """Run all validation tests."""
    print("Validating scenario_selector editable property implementation...\n")
    
    tests = [
        ("GUI Core Library Changes", test_gui_core_lib_changes),
        ("Visual Elements JSON Changes", test_viselements_json_changes),
        ("Backward Compatibility", test_backward_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Testing {test_name}:")
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"VALIDATION SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("[PASS] All tests passed! Implementation is correct.")
        return 0
    else:
        print("[FAIL] Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())