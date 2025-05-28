from .context import parser
import unittest
from pathlib import Path
from os import path

THIS_DIR = Path(__file__).parent

class TestWellParsing(unittest.TestCase):
    def test_parse_gmw_wells(self):
        well = parser.parse_gmw_wells(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        self.assertIsInstance(well, parser.Well)
        self.assertEqual(well.bro_id, "GMW000000015409")
        self.assertGreater(len(well.well_filter), 0)

    def test_xml_append_well_observations(self):
        well = parser.parse_gmw_wells(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        updated_well = parser.xml_append_well_observations(path.join(THIS_DIR,"data/GLD000000083930.xml"), well)
        self.assertIsInstance(updated_well, parser.Well)



if __name__ == "__main__":
    unittest.main()
