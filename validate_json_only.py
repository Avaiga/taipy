#!/usr/bin/env python3
"""
Simple validation script for JSON changes only.
"""

import json
import sys

def validate_viselements_json():
    """Validate that the viselements.json changes are correct."""
    try:
        with open("taipy/gui_core/viselements.json", "r") as f:
            viselements = json.load(f)
        
        print("JSON file loaded successfully")
        
        # Find scenario_selector in controls
        scenario_selector = None
        for control in viselements["controls"]:
            if control[0] == "scenario_selector":
                scenario_selector = control[1]
                break
        
        if scenario_selector is None:
            print("ERROR: scenario_selector not found in viselements.json")
            return False
            
        print("Found scenario_selector in controls")
        
        # Check editable property exists
        editable_prop = None
        for prop in scenario_selector["properties"]:
            if prop["name"] == "editable":
                editable_prop = prop
                break
        
        if editable_prop is None:
            print("ERROR: editable property not found in scenario_selector properties")
            return False
            
        print("Found editable property")
        
        # Check property configuration
        expected_type = "dynamic(bool)"
        expected_default = "True"
        
        if editable_prop["type"] != expected_type:
            print(f"ERROR: Expected type '{expected_type}', got '{editable_prop['type']}'")
            return False
            
        if editable_prop["default_value"] != expected_default:
            print(f"ERROR: Expected default_value '{expected_default}', got '{editable_prop['default_value']}'")
            return False
            
        print("Property configuration is correct")
        print("SUCCESS: All JSON validations passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = validate_viselements_json()
    sys.exit(0 if success else 1)