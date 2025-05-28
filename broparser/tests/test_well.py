from .context import parser
import unittest
from pathlib import Path
from os import path

THIS_DIR = Path(__file__).parent

class TestWellParsing(unittest.TestCase):
    def test_parse_gmw_wells(self):
        well = parser.parse_gmw_wells(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        self.assertIsInstance(well, parser.Well)
        self.assertEqual(well.gld_bro_id, "GMW000000015409")
        self.assertGreater(len(well.well_filter), 0)

    def test_xml_append_well_observations(self):
        well = parser.parse_gmw_wells(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        updated_well = parser.xml_append_well_observations(path.join(THIS_DIR,"data/GLD000000083930.xml"), well)
        self.assertIsInstance(updated_well, parser.Well)

    def test_well_to_csv(self):
        filter = "data/GLD000000083930.xml"
        well = parser.parse_gmw_wells(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        well = parser.xml_append_well_observations(path.join(THIS_DIR,filter), well)
        csv_file_path = path.join(THIS_DIR, f"data/test_{filter[5:-4]}.csv")
        well.filter_to_csv(4, csv_file_path)
        self.assertTrue(path.exists(csv_file_path))
        with open(csv_file_path, 'r') as f:
            content = f.read()
            self.assertIn("surface level", content)
            self.assertIn("bro id", content)



if __name__ == "__main__":
    unittest.main()
