from context import parser
import unittest
from pathlib import Path
from os import path

THIS_DIR = Path(__file__).parent

class TestWellParsing(unittest.TestCase):
    def test_read_well(self):
        well = parser.read_well(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        self.assertIsInstance(well, parser.Well)
        self.assertEqual(well.gld_bro_id, "GMW000000015409")
        self.assertGreater(len(well.well_filter), 0)

    def test_append_filter_measurements(self):
        well = parser.read_well(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        updated_well = parser.append_filter_measurements(path.join(THIS_DIR,"data/GLD000000083930.xml"), well)
        self.assertIsInstance(updated_well, parser.Well)
        self.assertIsNotNone(updated_well.get_filters(4).get_start_date())

    def test_well_to_csv(self):
        filter = "data/GLD000000083930.xml"
        well = parser.read_well(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        well = parser.append_filter_measurements(path.join(THIS_DIR,filter), well)
        csv_file_path = path.join(THIS_DIR, f"data/test_{filter[5:-4]}.csv")
        well.filter_to_csv(4, csv_file_path)
        self.assertTrue(path.exists(csv_file_path))
        with open(csv_file_path, 'r') as f:
            content = f.read()
            self.assertIn("surface level", content)
            self.assertIn("bro id", content)

    def test_dataset(self):
        well = parser.read_well(path.join(THIS_DIR,"data/GMW000000015409.xml"))
        well = parser.append_filter_measurements(path.join(THIS_DIR,"data/GLD000000083930.xml"), well)
        filter = well.get_filters(4)
        self.assertIsNotNone(filter.get_start_date())
        self.assertIsNotNone(filter.get_end_date())
        self.assertGreater(len(filter.dataset.dataset), 0)
        filter.dataset.calculate_statistics()
        self.assertEqual(filter.dataset.mean(), filter.dataset.statistics['mean'])
        GLG = filter.GLG()
        self.assertGreater(GLG, 0.0)


if __name__ == "__main__":
    unittest.main()
