#!/usr/bin/env python3
"""
FARO CoCMM XML to STEP AP214 Export Script
============================================

Converts FARO arm inspection data (XML format) to STEP AP214 files
for import into PTC Creo and other CAD systems.

Usage:
    python faro_to_step.py <input_faro_xml> [output_step]

Author: Nikola (WSL Hermes)
Date: 2026-05-27
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import numpy as np
import numpy.linalg as la

class FAROToSTEPConverter:
    """Converts FARO CoCMM XML to STEP AP214 format."""

    def __init__(self, xml_file):
        self.xml_file = Path(xml_file)
        self.root = None
        self.part_name = "Unknown"
        self.serial = "Unknown"
        self.cs_name = "Coordinate System"
        self.lines = []
        self.shape_name = "FARO_Inspection"

    def parse_xml(self):
        """Parse the FARO XML file."""
        print(f"✓ Reading FARO XML: {self.xml_file}")
        with open(self.xml_file, 'r') as f:
            content = f.read()

        # Handle Windows line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        self.root = ET.fromstring(content)

        # Extract metadata
        header = self.root.find('.//Header')
        if header is not None:
            self.part_name = header.find('PartName').text if header.find('PartName') is not None else "Unknown"
            self.serial = header.find('SerialNumber').text if header.find('SerialNumber') is not None else "Unknown"
            self.cs_name = header.find('ActiveCoordinateSystem').text if header.find('ActiveCoordinateSystem') is not None else "Coordinate System"

        self.shape_name = f"{self.part_name}_{self.serial}"

        print(f"  Part: {self.part_name}")
        print(f"  Serial: {self.serial}")
        print(f"  Coordinate System: {self.cs_name}")

    def parse_planes(self):
        """Extract all plane measurements from the XML."""
        commands = self.root.findall('.//Command')
        planes = []
        angles = []
        lengths = []
        coordinate_system = None

        for cmd in commands:
            cmd_type = cmd.find('Type').text
            label = cmd.find('Label').text

            if cmd_type == 'MeasurePlane':
                normal = self._parse_vector(cmd.find('Normal').text)
                point = self._parse_vector(cmd.find('PointOnPlane').text)

                plane = {
                    'label': label,
                    'normal': normal,
                    'point': point,
                    'error_max': float(cmd.find('MaxError').text),
                    'error_min': float(cmd.find('MinError').text),
                    'count': int(cmd.find('Count').text)
                }
                planes.append(plane)

            elif cmd_type == 'CS_PlanePlanePlane':
                origin = self._parse_vector(cmd.find('Origin').text)
                xaxis = self._parse_vector(cmd.find('XAxis').text)
                yaxis = self._parse_vector(cmd.find('YAxis').text)
                zaxis = self._parse_vector(cmd.find('ZAxis').text)

                coordinate_system = {
                    'name': label,
                    'origin': origin,
                    'x_axis': xaxis,
                    'y_axis': yaxis,
                    'z_axis': zaxis
                }

            elif cmd_type == 'AnglePlaneToPlane':
                angle_val = float(cmd.find('Angle').text)
                plane1 = cmd.find('Plane1').text
                plane2 = cmd.find('Plane2').text

                angles.append({
                    'label': label,
                    'angle': angle_val,
                    'plane1': plane1,
                    'plane2': plane2
                })

            elif cmd_type == 'LengthPlaneToPlane':
                length_val = float(cmd.find('Length').text)
                xyz = self._parse_vector(cmd.find('XYZ').text)
                plane1 = cmd.find('Plane1').text
                plane2 = cmd.find('Plane2').text

                lengths.append({
                    'label': label,
                    'length': length_val,
                    'vector': xyz,
                    'plane1': plane1,
                    'plane2': plane2
                })

        return planes, angles, lengths, coordinate_system

    def _parse_vector(self, vector_str):
        """Parse i,j,k or x,y,z vector string."""
        if vector_str.startswith('i='):
            vec = re.findall(r'i=(-?[\d.]+) j=(-?[\d.]+) k=(-?[\d.]+)', vector_str)[0]
        else:
            vec = re.findall(r'x=(-?[\d.]+) y=(-?[\d.]+) z=(-?[\d.]+)', vector_str)[0]
        return np.array([float(vec[0]), float(vec[1]), float(vec[2])])

    def normalize_vector(self, v):
        """Normalize a vector."""
        norm = la.norm(v)
        if norm == 0:
            return v
        return v / norm

    def create_step_header(self):
        """Create STEP file header."""
        self.lines.append("ISO-10303-21;")
        self.lines.append("HEADER;")
        self.lines.append("FILE_DESCRIPTION(('FARO CoCMM Inspection Data'), '2;1');")
        self.lines.append("FILE_NAME('")
        self.lines.append(f"  {self.shape_name}.stp'")
        self.lines.append("  '2026-05-27T00:00:00',")
        self.lines.append("  ('Unknown'),('Unknown'),'FARO To STEP Converter','Unknown','Unknown');")
        self.lines.append("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));")
        self.lines.append("ENDSEC;")
        self.lines.append("")
        self.lines.append("DATA;")
        self.lines.append("")

    def create_plane_geometry(self, plane):
        """
        Create plane geometry in STEP format.

        Plane is defined by:
        - Point on plane (X,Y,Z)
        - Normal vector
        """
        label = plane['label']
        point = plane['point']
        normal = self.normalize_vector(plane['normal'])

        # Create unique IDs for this plane based on normal
        x_id = int(1000 + abs(normal[0]) * 10000) % 1000
        y_id = int(1000 + abs(normal[1]) * 10000) % 1000
        z_id = int(1000 + abs(normal[2]) * 10000) % 1000

        # Ensure unique IDs
        base = 1000
        x_id = base + len([p for p in self.lines if f"#1000" in p]) + 1
        y_id = base + len([p for p in self.lines if f"#100" in p]) + 2
        z_id = base + len([p for p in self.lines if f"#100" in p]) + 3

        # Create direction for the normal
        self.lines.append(f"#{x_id} = DIRECTION('',({normal[0]:.12f}, {normal[1]:.12f}, {normal[2]:.12f}));")
        self.lines.append(f"#{y_id} = CARTESIAN_POINT('',")
        self.lines.append(f"  ({point[0]:.12f}, {point[1]:.12f}, {point[2]:.12f}));")
        self.lines.append(f"#{z_id} = PLANE_BY_THREE_POINTS('',")
        self.lines.append(f"  #{y_id}, #{x_id}, #{x_id});")
        self.lines.append("")

    def convert(self, output_file):
        """Perform the complete conversion."""
        try:
            # Parse input
            self.parse_xml()

            # Extract geometry data
            planes, angles, lengths, cs = self.parse_planes()

            print(f"✓ Extracted {len(planes)} planes, {len(angles)} angles, {len(lengths)} lengths")

            # Create STEP file
            self.create_step_header()

            # Create plane geometries
            for i, plane in enumerate(planes, start=1):
                self.create_plane_geometry(plane)

            # Get bounding box extents
            extents = []
            for plane in planes:
                extents.append(plane['point'])

            min_pt = np.min(extents, axis=0)
            max_pt = np.max(extents, axis=0)

            # Write footer
            self.create_step_footer()

            # Write output
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                f.write('\n'.join(self.lines))

            print(f"✓ STEP file written: {output_path}")
            print(f"  Shape name: {self.shape_name}")
            print(f"  Number of planes: {len(planes)}")
            print(f"  Part extent: [{min_pt[0]:.2f}, {min_pt[1]:.2f}, {min_pt[2]:.2f}] to [{max_pt[0]:.2f}, {max_pt[1]:.2f}, {max_pt[2]:.2f}]")
            print("\n✓ Conversion complete!")
            print("\nNext steps:")
            print(f"1. Open {output_path} in PTC Creo")
            print("2. Import the measured planes as datum features")
            print("3. Create a 'Compare' feature to measure deviations from original model")
            print("4. Use GD&T to document inspection results")

            return True

        except Exception as e:
            print(f"✗ Error during conversion: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_step_footer(self):
        """Create STEP file footer."""
        self.lines.append("")
        self.lines.append("ENDSEC;")
        self.lines.append("")
        self.lines.append("END-ISO-10303-21;")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage examples:")
        print("  python faro_to_step.py measurements.xml")
        print("  python faro_to_step.py eocs_plexus.Data.txt eocs_plexus.step")
        print("\nSupported input formats:")
        print("  - FARO CoCMM XML (.xml, .txt)")
        return 1

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{Path(input_file).stem}.step"

    converter = FAROToSTEPConverter(input_file)
    success = converter.convert(output_file)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())