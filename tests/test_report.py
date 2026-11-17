import json
import os
import tempfile
import unittest

import report


class ReportTests(unittest.TestCase):
    def test_empty_report_has_zero_count(self):
        result = report.build_report([])
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["average"], 0)

    def test_empty_report_max_is_zero(self):
        self.assertEqual(report.build_report([])["max"], 0)

    def test_single_record(self):
        result = report.build_report([{"name": "a", "value": 5}])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["average"], 5)

    def test_total(self):
        data = [{"value": 1}, {"value": 2}, {"value": 3}]
        self.assertEqual(report.build_report(data)["total"], 6)

    def test_average_rounded_to_two_digits(self):
        data = [{"value": 1}, {"value": 1}, {"value": 2}]
        self.assertEqual(report.build_report(data)["average"], 1.33)

    def test_maximum(self):
        data = [{"value": 3}, {"value": 9}, {"value": 4}]
        self.assertEqual(report.build_report(data)["max"], 9)

    def test_missing_value_is_rejected(self):
        with self.assertRaises(ValueError):
            report.build_report([{"name": "a"}])

    def test_non_numeric_value_is_rejected(self):
        with self.assertRaises(ValueError):
            report.build_report([{"value": "ten"}])

    def test_bool_value_is_rejected(self):
        with self.assertRaises(ValueError):
            report.build_report([{"value": True}])

    def test_format_report_contains_count(self):
        text = report.format_report(report.build_report([{"value": 2}]))
        self.assertIn("Records: 1", text)

    def test_load_data_reads_list(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump([{"value": 1}], f)
            self.assertEqual(len(report.load_data(path)), 1)

    def test_load_data_rejects_non_list(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"value": 1}, f)
            with self.assertRaises(ValueError):
                report.load_data(path)

    def test_main_returns_error_for_missing_file(self):
        self.assertEqual(report.main(["--input", "no_such_file.json"]), 1)

    def test_main_ok_on_example(self):
        self.assertEqual(report.main(["--input", "data.json.example"]), 0)


if __name__ == "__main__":
    unittest.main()
