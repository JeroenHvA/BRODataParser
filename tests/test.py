
from parser.core import parse_gmw_wells, xml_append_well_observations, Well
import unittest
from pathlib import Path
from os import path

THIS_DIR = Path(__file__).parent



class TestWellParsing(unittest.TestCase):
    def test_parse_gmw_wells(self):
        well = parse_gmw_wells(path.join("tests/data/GMW000000015409.xml"))
        self.assertIsInstance(well, Well)
        self.assertEqual(well.well_id, "GMW000000015409")
        self.assertGreater(len(well.well_observations), 0)

    def test_xml_append_well_observations(self):
        well = parse_gmw_wells("tests/data/GMW000000015409.xml")
        updated_well = xml_append_well_observations("tests/data/GMW000000083930.xml", well)
        self.assertEqual(len(updated_well.well_observations), len(well.well_observations) + 1)

# if __name__ == "__main__":



#     from os import listdir, path

#     _path = r"~"

#     files = listdir(_path)

#     for file in files:
#         if file[:3] == "GMW":
#             _well_path = file

#     well = parse_gmw_wells(path.join(_path, _well_path))

#     for i in files:
#         if i != _well_path:
#             well = xml_append_well_observations(path.join(_path, i), well)

#     print(well.well_observations[2])
#     print(well.well_observations[2].dataset)

