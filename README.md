# Roblox Studio to Rojo Project Setup Guide

This guide explains how to extract scripts from a Roblox place file and set up a Rojo project for syncing between your file system and Roblox Studio.

## Prerequisites

1. **Rojo** - Install via Cargo:
   ```bash
   cargo install rojo
   ```

2. **Python 3** - Should be pre-installed on most systems (used for script extraction)

3. **Rojo Plugin** - Install in Roblox Studio from the plugin marketplace

## Step-by-Step Process

### Step 1: Save Your Place as XML

1. Open your place file in Roblox Studio
2. Go to **File → Save to File As...**
3. Choose **Roblox XML Place Files (.rbxlx)** as the file type
4. Save it (e.g., `Place1_XML.rbxlx`)
5. Copy the .rbxlx file to your project directory

### Step 2: Extract Scripts with Folder Structure

1. Save the extraction script as `extract_with_structure_v2.py` (included in this project)

2. Run the extraction:
   ```bash
   python3 extract_with_structure_v2.py
   ```

   This will:
   - Create a `src/` directory
   - Extract all scripts while preserving the folder hierarchy
   - Organize scripts into:
     - `src/server/` - ServerScriptService and ServerStorage scripts
     - `src/shared/` - ReplicatedStorage scripts (accessible by both server and client)
     - `src/client/` - StarterPlayer and StarterGui scripts

   Example output:
   ```
   Extraction complete with structure preserved!
   Total scripts extracted: 49
   ```

### Step 3: Create Rojo Project Configuration

Create a `default.project.json` file:

```json
{
  "name": "your-project-name",
  "tree": {
    "$className": "DataModel",
    
    "ServerScriptService": {
      "$className": "ServerScriptService",
      "$path": "src/server"
    },
    
    "ReplicatedStorage": {
      "$className": "ReplicatedStorage",
      "$path": "src/shared"
    },
    
    "StarterPlayer": {
      "$className": "StarterPlayer",
      "StarterPlayerScripts": {
        "$className": "StarterPlayerScripts",
        "$path": "src/client"
      },
      "StarterCharacterScripts": {
        "$className": "StarterCharacterScripts",
        "$path": "src/client/StarterCharacterScripts"
      }
    }
  }
}
```

### Step 4: Test the Setup

1. Build the project to verify it works:
   ```bash
   rojo build -o test.rbxlx
   ```

2. If successful, you'll see:
   ```
   Building project 'your-project-name'
   Built project to test.rbxlx
   ```

### Step 5: Start Syncing with Studio

1. In your terminal, start the Rojo server:
   ```bash
   rojo serve
   ```
   
   You should see:
   ```
   Rojo server listening on port 34872
   ```

2. In Roblox Studio:
   - Open your original place file
   - Open the Rojo plugin
   - Click "Connect" 
   - Enter `localhost:34872` (or just click Connect if it's the default)

3. Your scripts will now sync between your file system and Studio!

## Project Structure

After extraction, your project will look like this:

```
your-project/
├── src/
│   ├── server/          # ServerScriptService scripts
│   │   ├── Gameplay/
│   │   ├── Platformer/
│   │   └── Utility/
│   ├── shared/          # ReplicatedStorage scripts
│   │   ├── Gameplay/
│   │   ├── Platformer/
│   │   └── Utility/
│   └── client/          # Client scripts
│       └── StarterCharacterScripts/
├── default.project.json  # Rojo configuration
├── extract_with_structure_v2.py  # Extraction script
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## How the Extraction Works

The Python script (`extract_with_structure_v2.py`):
1. Parses the .rbxlx XML file
2. Finds all Script, LocalScript, and ModuleScript instances
3. Preserves the folder hierarchy from Studio
4. Extracts the source code from the XML's ProtectedString fields
5. Saves each script as a .lua file in the appropriate directory

## Workflow Tips

- **Edit scripts** in your favorite code editor (VSCode, Sublime, etc.)
- **Changes sync automatically** to Studio when Rojo is connected
- **Models and assets** stay in Studio - only scripts sync
- **Version control** - You can now use Git to track script changes

## Troubleshooting

### "Place file not found"
- Make sure the .rbxlx file is in the same directory as the Python script
- Check the filename matches what's in the script (default: `Place1_XML.rbxlx`)

### Scripts not extracting
- The place file MUST be saved as `.rbxlx` (XML format), not `.rbxl` (binary format)
- Check that Python 3 is installed: `python3 --version`

### Rojo not syncing
- Ensure the Rojo server is running: `rojo serve`
- Check that the plugin is connected to the correct port (34872)
- Verify your `default.project.json` paths match your folder structure

### Folder structure doesn't match Studio
- The extraction script preserves the exact folder structure from Studio
- If folders are missing, they may not have contained any scripts

## Re-extracting Scripts

If you need to re-extract scripts from Studio:
1. Save the place as .rbxlx again
2. Run `python3 extract_with_structure_v2.py`
3. The script will clean and rebuild the `src/` directory

## Clean Up (Optional)

Once everything is working, you can optionally remove:
```bash
rm Place1_XML.rbxlx test*.rbxlx
```

Keep:
- `src/` directory with your scripts
- `default.project.json`
- `extract_with_structure_v2.py` (for future re-extraction)
- `.gitignore`
- This README

## Additional Resources

- [Rojo Documentation](https://rojo.space/docs/)
- [Python XML Documentation](https://docs.python.org/3/library/xml.etree.elementtree.html)