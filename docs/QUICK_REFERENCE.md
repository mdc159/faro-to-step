# FARO to STEP - Quick Reference

## Send Me These Files to Convert:

```bash
# Run this once to create a symbolic link for easy access
ln -s ~/projects/comfy/local-practice/faro_to_step.py ~/bin/

# Then from now on, just run:
faro_to_step.py <your_faro_xml_file> output.step
```

## Your Original FARO Files Should Contain:

- XML version header: `<Version>1.8.XXXXX.26066</Version>`
- Part name: `<PartName>eocs</PartName>`
- Serial number: `<SerialNumber>plexus</SerialNumber>`
- Multiple `<Command>` entries with:
  - `<Type>MeasurePlane</Type>` - planar measurements
  - `<Type>AnglePlaneToPlane</Type>` - angle measurements
  - `<Type>LengthPlaneToPlane</Type>` - length measurements

## I Generate:

✅ STEP AP214 file (ISO 10303 standard)
✅ 11 plane geometries with normal vectors
✅ 4 angle measurements
✅ 2 length measurements
✅ Bounding box and reference system
✅ Complete inspection metadata

## You Do in Creo:

1. **File → Open** → Select the `.step` file
2. **Import tolerance**: ~0.01 mm (adjust based on your precision)
3. **Verify planes** → Rename datum features to match your assembly
4. **Add your original CAD model** as reference
5. **Create "Compare" feature** → Measure deviations
6. **Document** → Use GD&T annotations for inspection report

## File Location After Conversion:

```
~/projects/comfy/local-practice/
├── faro_to_step.py          # Conversion script
├── README_FARO_TO_STEP.md   # Full documentation
└── eocs_plexus.step         # Your converted file
```

## Example Workflow:

```bash
# 1. Receive FARO file via Telegram
# 2. Save to ~/projects/comfy/local-practice/
# 3. Run conversion
cd ~/projects/comfy/local-practice
python faro_to_step.py measurements.xml my_assembly.step

# 4. Send me the .step file back to import into your model
# 5. I can also extract more geometry if needed
```

## What I Cannot Extract:

❌ Complete solid model (only measured features)
❌ Original CAD source or constraints
❌ Assemblies or subcomponents (unless explicitly defined)

## What I Can Extract Next Time:

If you need more geometry:
- ✅ Add probe point measurements (`.xml` with `<MeasurePoint>` tags)
- ✅ Add circular measurements (`.xml` with `<MeasureCircle>` tags)
- ✅ Add cylindrical measurements (`.xml` with `<MeasureCylinder>` tags)
- ✅ Add file naming convention and I'll build extraction for those

---

**Ready to use**: Just send me the FARO XML files and I'll return .step files for Creo import!