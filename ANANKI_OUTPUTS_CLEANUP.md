# Ananki Outputs Folder - Final Cleanup (Nov 12, 2025)

## What Happened

The `data/ananki_outputs/` folder has been **completely reorganized and removed**. All files have been moved to their proper locations based on their purpose.

## File Relocations

### Visualization Data → `code/web/data/visualization/`
These JSON files support the web visualization interface:
- `vibe_coordinates.json` - X/Y positions for vibe nodes
- `vibe_coordinates_v2.json` - Updated coordinate system
- `central_vibe_map.json` - Main vibe mapping data
- `central_vibe_relationships.json` - How vibes connect
- `relationships_only.json` - Simplified relationship graph
- `vibe_categories_extracted.json` - Categorization data
- `subvibes_for_analysis.json` - Sub-vibe list for analysis
- `subvibes_with_real_data.json` - Sub-vibes with actual songs
- `discovered_structure.json` - Auto-discovered vibe patterns

### Web Scripts → `code/web/lib/visualization-scripts/`
Python scripts for generating/updating visualization assets:
- `generate_tooltip_data.py` - Creates tooltip content
- `gen_real_tooltips.py` - Generates real-data tooltips
- `update_map_tooltips.py` - Updates interactive map tooltips

### Web Assets → `code/web/public/`
Visual assets for the web app:
- `interactive_tapestry_map.html` - Interactive vibe visualization
- `emotional_manifold_visualization.png` - Static vibe map image

### Utility Scripts → `analysis/`
General-purpose analysis tools:
- `balance_tapestry.py` - Balance vibe distribution
- `archive_overflow.py` - Archive management tool

### Old Files → `archive/old_processing_files/`
Legacy processing artifacts (kept for reference):
- `ananki_outputs_README.md` - Old documentation
- `ananki_v1_recategorized.csv` - Old batch processing
- `ananki_v2_with_implicit_deltas.csv` - Old batch processing
- `ananki_v3_with_anchors.csv` - Old batch processing
- `merged_v4v5.csv` - Old merged data
- `sub_vibe_map.json` - Legacy sub-vibe mapping
- `tapestry_map.json` - Legacy tapestry structure
- `tapestry_map_with_subvibes.json` - Legacy structure

## Why This Organization?

### Before (Confusing):
```
data/ananki_outputs/
├── [visualization files mixed with scripts]
├── [web assets mixed with processing data]
└── [utility scripts mixed with old artifacts]
```

**Problems:**
- Web-related files buried in data folder
- Visualization scripts not with web code
- Unclear what's current vs. obsolete
- Easy to accidentally use old/corrupted data

### After (Clear):
```
code/web/
├── data/visualization/     # Vibe mapping data for visualization
├── lib/visualization-scripts/  # Scripts to generate/update maps
└── public/                 # HTML/images served to users

analysis/                   # Utility scripts for analysis

archive/old_processing_files/  # Old artifacts (reference only)
```

**Benefits:**
- All web-related files together in `code/web/`
- Clear separation by purpose
- Old files safely archived
- Impossible to confuse current vs. legacy data

## Current Status

✅ **COMPLETE** - The `data/ananki_outputs/` folder no longer exists.

All files are now in their proper locations:
- Web visualization: `code/web/`
- Analysis tools: `analysis/`
- Legacy data: `archive/`

## If You Need These Files

### For Web Development:
```bash
cd code/web/data/visualization/  # Vibe data
cd code/web/lib/visualization-scripts/  # Generation scripts
cd code/web/public/  # HTML/images
```

### For Data Analysis:
```bash
cd analysis/  # Utility scripts
```

### For Reference (Old System):
```bash
cd archive/old_processing_files/  # Legacy artifacts
```

## Related Documentation

- See `PROJECT_STRUCTURE.md` for complete project layout
- See `REORGANIZATION_COMPLETE.md` for previous cleanup details
- See `code/web/README.md` for web app documentation (if exists)

---

**This cleanup completes the full project reorganization!** 🎉
