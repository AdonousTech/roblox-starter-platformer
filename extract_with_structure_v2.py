#!/usr/bin/env python3
"""
Extract Lua scripts from Roblox .rbxlx (XML) file while preserving folder structure
"""

import xml.etree.ElementTree as ET
import os
import re
from pathlib import Path

def clean_name(name):
    """Clean name for filesystem"""
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    return name

def find_parent_service(element, root):
    """Find which service an element belongs to by traversing the tree"""
    service_names = ['ServerScriptService', 'ServerStorage', 'ReplicatedStorage', 
                    'StarterPlayer', 'StarterGui', 'Workspace']
    
    # Build a map of element to parent
    parent_map = {}
    for parent in root.iter():
        for child in parent:
            parent_map[child] = parent
    
    # Traverse up to find service
    current = element
    path = []
    
    while current is not None and current != root:
        if current.tag == 'Item':
            name_elem = current.find('./Properties/string[@name="Name"]')
            if name_elem is not None and name_elem.text:
                item_name = name_elem.text
                path.append(item_name)
                if item_name in service_names:
                    return item_name, list(reversed(path[:-1]))  # Return service and path without service name
        
        current = parent_map.get(current)
    
    return None, []

def extract_scripts_with_structure(xml_file):
    """Extract all scripts while preserving the folder structure"""
    print(f"Parsing {xml_file} with structure preservation...")
    
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Clean existing src directory
    import shutil
    if os.path.exists('src'):
        print("Cleaning existing src directory...")
        shutil.rmtree('src')
    
    # Create base directories
    os.makedirs('src/server', exist_ok=True)
    os.makedirs('src/client', exist_ok=True)
    os.makedirs('src/shared', exist_ok=True)
    
    scripts_found = []
    folder_structure = set()
    
    # Map services to their target directories
    service_mapping = {
        'ServerScriptService': 'src/server',
        'ServerStorage': 'src/server',
        'ReplicatedStorage': 'src/shared',
        'StarterPlayer': 'src/client',
        'StarterGui': 'src/client',
        'Workspace': 'src/workspace'
    }
    
    # Build parent map for navigation
    parent_map = {}
    for parent in root.iter():
        for child in parent:
            parent_map[child] = parent
    
    # Process all items
    for item in root.iter('Item'):
        item_class = item.get('class')
        name_elem = item.find('./Properties/string[@name="Name"]')
        
        if name_elem is None or not name_elem.text:
            continue
            
        item_name = name_elem.text
        
        # Find service and path
        service_name, path_from_service = find_parent_service(item, root)
        
        if not service_name or service_name not in service_mapping:
            continue
        
        base_dir = service_mapping[service_name]
        
        # Handle scripts
        if item_class in ['Script', 'LocalScript', 'ModuleScript']:
            source_elem = item.find('./Properties/ProtectedString[@name="Source"]')
            if source_elem is not None and source_elem.text:
                
                # Special handling for StarterPlayer subfolders
                if service_name == 'StarterPlayer' and len(path_from_service) > 0:
                    if path_from_service[0] == 'StarterPlayerScripts':
                        # Scripts directly in StarterPlayerScripts go to client root
                        path_from_service = path_from_service[1:]
                    elif path_from_service[0] == 'StarterCharacterScripts':
                        # Keep StarterCharacterScripts as a subfolder
                        pass
                
                # Build full file path
                if len(path_from_service) > 0:
                    # Script is in a subfolder structure
                    folder_parts = [clean_name(p) for p in path_from_service[:-1]]
                    if folder_parts:
                        folder_path = os.path.join(base_dir, *folder_parts)
                        os.makedirs(folder_path, exist_ok=True)
                        file_path = os.path.join(folder_path, clean_name(path_from_service[-1]) + '.lua')
                        folder_structure.add(os.path.dirname(file_path))
                    else:
                        file_path = os.path.join(base_dir, clean_name(path_from_service[-1]) + '.lua')
                else:
                    # Script is at root of service (shouldn't happen often)
                    file_path = os.path.join(base_dir, clean_name(item_name) + '.lua')
                
                # Handle duplicate filenames
                if os.path.exists(file_path):
                    base_path = file_path[:-4]  # Remove .lua
                    counter = 1
                    while os.path.exists(f"{base_path}_{counter}.lua"):
                        counter += 1
                    file_path = f"{base_path}_{counter}.lua"
                
                # Write the script
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(source_elem.text)
                
                scripts_found.append({
                    'name': item_name,
                    'type': item_class,
                    'path': file_path,
                    'service': service_name,
                    'full_path': '/'.join([service_name] + path_from_service)
                })
                
                rel_path = file_path.replace('src/', '')
                print(f"Extracted: {'/'.join([service_name] + path_from_service)} -> {rel_path}")
        
        # Handle folders to maintain structure
        elif item_class == 'Folder':
            if len(path_from_service) > 0:
                folder_path = os.path.join(base_dir, *[clean_name(p) for p in path_from_service])
                os.makedirs(folder_path, exist_ok=True)
                folder_structure.add(folder_path)
    
    print(f"\n{'='*60}")
    print(f"Extraction complete with structure preserved!")
    print(f"Total scripts extracted: {len(scripts_found)}")
    
    # Summary by service
    by_service = {}
    for script in scripts_found:
        service = script['service']
        if service not in by_service:
            by_service[service] = []
        by_service[service].append(script['full_path'])
    
    print(f"\nScripts by service:")
    for service, paths in sorted(by_service.items()):
        print(f"\n{service}: ({len(paths)} scripts)")
        # Group by first folder
        folders = {}
        root_scripts = []
        for path in paths:
            parts = path.split('/')
            if len(parts) > 2:  # Has subfolder
                folder = parts[1]
                if folder not in folders:
                    folders[folder] = 0
                folders[folder] += 1
            else:
                root_scripts.append(path)
        
        for folder, count in sorted(folders.items()):
            print(f"  📁 {folder}/ ({count} scripts)")
        for script in root_scripts[:3]:
            print(f"  📄 {script.split('/')[-1]}")
        if len(root_scripts) > 3:
            print(f"  ... and {len(root_scripts) - 3} more root scripts")
    
    # Show directory tree
    print(f"\nDirectory structure created:")
    print("src/")
    for root_dir, dirs, files in os.walk("src"):
        level = root_dir.replace("src", "").count(os.sep)
        indent = "  " * level
        dir_name = os.path.basename(root_dir)
        if level > 0:
            print(f"{indent}📁 {dir_name}/")
        subindent = "  " * (level + 1)
        # Show first few files in each directory
        lua_files = [f for f in files if f.endswith('.lua')]
        for f in lua_files[:2]:
            print(f"{subindent}📄 {f}")
        if len(lua_files) > 2:
            print(f"{subindent}... {len(lua_files) - 2} more files")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    extract_scripts_with_structure("starter_platformer.rbxlx")