import unittest
from pathlib import Path

from tools.nacelle_esc_service import extract_board_data, validate_expected_envelope


BOARD = Path(
    "/home/steve/Documents/Vocation/Employers/Griffing.tech/designs/"
    "Open-Secure-ESC/builds/6s/50A/CAN_485_faraday/kicad/"
    "open_secure_esc_6s_50a_can485_faraday.kicad_pcb"
)


class NacelleEscServiceTest(unittest.TestCase):
    def test_committed_board_envelope_is_measured(self) -> None:
        data = extract_board_data(BOARD)
        validate_expected_envelope(data)
        self.assertEqual(data["outline_mm"]["width"], 32.0)
        self.assertEqual(data["outline_mm"]["height"], 66.1)
        self.assertEqual(data["thickness_mm"], 1.6)
        self.assertIn("component_height_envelope_not_encoded_in_pcb", data["unknowns"])

    def test_unknown_height_data_is_not_silently_resolved(self) -> None:
        data = extract_board_data(BOARD)
        self.assertIn("thermal_interface_not_encoded_in_pcb", data["unknowns"])
        self.assertEqual(data["mounting_holes"], [])


if __name__ == "__main__":
    unittest.main()
