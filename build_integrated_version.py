#!/usr/bin/env python3
"""
Build the fully integrated trading_signal_analyzer.py v0.93
with Enhanced Dark Flow Scanner market scanning capability
"""

print("Building fully integrated version...")

# Read the enhanced Dark Flow scanner code
with open('enhanced_dark_flow_scanner.py', 'r') as f:
    enhanced_code = f.read()

# Extract just the class and functions we need
import re

# Find the EnhancedDarkFlowScanner class
class_match = re.search(r'class EnhancedDarkFlowScanner:.*?(?=\n(?:class|def|if __name__))', 
                        enhanced_code, re.DOTALL)

if class_match:
    enhanced_class = class_match.group(0)
    print(f"Extracted Enhanced Dark Flow Scanner class: {len(enhanced_class)} characters")
else:
    print("Could not extract class")
    
# Find the display functions
display_scan_match = re.search(r'def display_dark_flow_scan_results.*?(?=\n\ndef )', 
                               enhanced_code, re.DOTALL)
display_analysis_match = re.search(r'def display_dark_flow_analysis.*?(?=\n\ndef )', 
                                   enhanced_code, re.DOTALL)

if display_scan_match:
    display_scan = display_scan_match.group(0)
    print(f"Extracted display_scan function: {len(display_scan)} characters")
    
if display_analysis_match:
    display_analysis = display_analysis_match.group(0)
    print(f"Extracted display_analysis function: {len(display_analysis)} characters")

print("\nExtraction complete. Now we need to integrate into the main file...")
print("This requires the original trading_signal_analyzer.py content.")

