#!/usr/bin/env python3
import sys

def load_exclusions(file_path):
    """Load package names to exclude from inference-non-requirements.txt"""
    exclusions = set()
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, ~=, etc.)
                    pkg_name = line.split('==')[0].split('>=')[0].split('~=')[0].split('<=')[0].split('!=')[0]
                    exclusions.add(pkg_name.strip())
    except FileNotFoundError:
        print(f"Warning: {file_path} not found, no packages will be excluded")
    return exclusions

def filter_requirements(req_files, exclusion_file, output_file):
    """Filter requirements files by removing excluded packages"""
    exclusions = load_exclusions(exclusion_file)
    
    all_requirements = []
    for req_file in req_files:
        try:
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pkg_name = line.split('==')[0].split('>=')[0].split('~=')[0].split('<=')[0].split('!=')[0]
                        if pkg_name.strip() not in exclusions:
                            all_requirements.append(line)
        except FileNotFoundError:
            print(f"Warning: {req_file} not found")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_requirements = []
    for req in all_requirements:
        if req not in seen:
            seen.add(req)
            unique_requirements.append(req)
    
    with open(output_file, 'w') as f:
        for req in sorted(unique_requirements):
            f.write(req + '\n')
    
    print(f"Filtered requirements written to {output_file}")
    print(f"Excluded packages: {sorted(exclusions)}")
    excluded_count = len(exclusions)
    included_count = len(unique_requirements)
    print(f"Total packages: included={included_count}, excluded={excluded_count}")

if __name__ == '__main__':
    filter_requirements(
        ['./main_requirements.txt', './filtered_submodule_reqs.txt'],
        './inference_non_requirements.txt',
        './inference_requirements.txt'
    ) # requirement[s], exclusion, output 