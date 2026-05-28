# FARO CoCMM to STEP Conversion Workflow

## Overview

This directory contains tools to convert FARO arm inspection data (XML format) to STEP AP214 files for import into PTC Creo and other CAD systems.

## Files

### `faro_to_step.py`
Main conversion script that reads FARO CoCMM XML files and generates STEP files.

### Usage

```bash
# Basic usage - auto-generate output filename
python faro_to_step.py <input_faro_xml>

# Specify output filename
python faro_to_step.py <input_faro_xml> <output_step>

# Example with your file
python faro_to_step.py eocs_plexus.Data.txt eocs_plexus.step
```

### Command-Line Arguments

- `input_faro_xml`: Path to FARO CoCMM XML file (.xml, .txt)
- `output_step`: Optional path for STEP file (.step, .stp)

## Supported FARO Data Types

The converter extracts:

- **11 Planes**: Measured datum planes and feature planes with:
  - Normal vectors (i,j,k or x,y,z)
  - Reference points on plane
  - Measurement error data (max/min)

- **4 Angles**: Between measured planes (typically ~179.98° = near-parallel)
  - DATUM A, B, C (reference planes)
  - Feature planes (Plane1, Plane2, etc.)

- **2 Lengths**: Between measured planes
  - REAR TOP INVAR: ~890.2 units from LH PLATE INNER to RS TOAD MOUNT
  - TOAD PLANES: ~890.3 units from RS TOAD PLANE to LS TOAD PLANE

## Output Format

The generated STEP files contain:

- ISO 10303-21 standard header
- 11 PLANE entities with DIRECTION and CARTESIAN_POINT
- Bounding box reference location
- Valid STEP AP214 structure

## Verification

The converter outputs:

```
✓ Reading FARO XML: <file>
  Part: <part_name>
  Serial: <serial_number>
  Coordinate System: <cs_name>
✓ Extracted <N> planes, <M> angles, <P> lengths
✓ STEP file written: <output_file>
  Shape name: <shape_name>
  Number of planes: <N>
  Part extent: [min_x, min_y, min_z] to [max_x, max_y, max_z]
```

## Creo Import Workflow

### Step 1: Import STEP File

1. Open PTC Creo
2. File → Open
3. Select the generated `.step` file
4. Set import tolerance appropriately (typically 0.01-0.1 mm)

### Step 2: Create Datum Features

1. In Creo, the imported planes appear as datum features
2. They can be renamed (e.g., "DATUM_A", "DATUM_B", "Plane1")
3. Verify orientation using the normal display

### Step 3: Compare to Original Model

1. Import or reference your original CAD model
2. Use Creo's "Compare" or "Deviation Analysis" feature
3. Configure inspection points on original model
4. Generate deviation reports showing:
   - Distance from measured plane
   - Angular deviations
   - Length comparisons

### Step 4: GD&T Documentation

1. Apply GD&T annotations
2. Document measurement errors (provided in FARO data)
3. Create inspection reports

## Limitations

### Current Implementation

- **Feature-based only**: Extracts measured planes, not full solid model
- **Skeletal geometry**: Uses bounding box for visualization
- **No constraints**: Planes are independent entities

### What's Missing

- **No fillets, holes, or complex features**
- **No assembly structure**
- **No material properties**
- **No relationships to original CAD source**

### For Complete Models

If you need complete solid geometry:

1. **Use FARO SCENE software**: Import XML, export full CAD
2. **Use CAD software**: Open XML in CAM2, export STEP
3. **Contact FARO**: Query technical support for direct STEP export

## Troubleshooting

### Common Issues

**Issue**: STEP file won't import to Creo

**Solutions**:
- Check file encoding (UTF-8 with BOM)
- Verify STEP file integrity (validate with online STEPs checker)
- Adjust Creo import tolerance

**Issue**: Planes appear rotated

**Solutions**:
- Verify normal vectors in FARO data
- Check coordinate system transformation
- Manually reorient in Creo if needed

**Issue**: Too few planes for accurate inspection

**Solutions**:
- Collect more measurement features
- Use additional FARO probe points
- Create intermediate reference planes

## Next Steps

### For Regular Workflows

1. **Save this directory** as your standard tool location
2. **Create a symbolic link** for easy access:
   ```bash
   ln -s /home/mdc159/projects/comfy/local-practice/faro_to_step.py ~/bin/
   ```
3. **Test with new FARO files** regularly
4. **Document geometry characteristics** for inspection planning

### For Advanced Use

- **Extend script** to extract other feature types (circles, cylinders)
- **Add GD&T annotations** to STEP file
- **Create batch processing** for multiple files
- **Integrate with inspection automation** pipelines

## Technical Notes

### FARO CoCMM Format

- XML-based coordinate measurement data
- Version: 1.8.5820.26066 (from sample file)
- Part name and serial number in header
- Coordinate system derived from three datum planes
- Measurement units: likely millimeters

### STEP AP214

- ISO 10303 standard for CAD data exchange
- AP214 used for automotive and mechanical design
- Supports 3D geometry, assemblies, and GD&T
- Parseable by most CAD systems: Creo, SolidWorks, CATIA, Siemens NX

### Conversion Algorithm

1. Parse XML and extract plane definitions
2. Normalize normal vectors
3. Create DIRECTION and CARTESIAN_POINT entities
4. Generate PLANE_BY_THREE_POINTS geometry
5. Write ISO 10303-21 compliant header/footer

## Contact & Support

For questions or improvements:
- Original data: FARO CoCMM system
- Conversion tool: Nikola (WSL Hermes)
- Date: 2026-05-27

## Version History

- v1.0 (2026-05-27): Initial release with plane-only extraction
  - 11 plane geometries
  - Coordinate system derivation
  - STEP AP214 compliant output

---

**Last Updated**: 2026-05-27
**Python Version**: 3.12+
**Dependencies**: numpy, xml.etree.ElementTree (standard library)