import pathlib
import sys
import unittest


def _bytes_from_hex_lines(hex_lines: str) -> bytes:
    return bytes.fromhex("".join(line.strip() for line in hex_lines.splitlines() if line.strip()))


class TestXmpParsing(unittest.TestCase):
    def test_xmp_frequency_matches_reference_tools(self):
        # This SPD sample previously decoded as 3603 MT/s due to treating byte +4 as a tCK fine offset.
        # Reference tools (CPU-Z / Thaiphoon Burner) decode it as XMP-4000 (2000 MHz).
        spd_bytes = _bytes_from_hex_lines(
            """
            23100c028629000800000003090300000000080cffff03006c6c6c1108743011
            f00a200800a81e2b2b0000000000000000000000000000000000000016361636
            1636163600002b0c2b0c2b0c2b0c000000000000000000000000000000000000
            000000000000000000000000000000000000000000edb5ce0000000000c265a6
            1111010100000000000000000000000000000000000000000000000000000000
            0000000000000000000000000000000000000000000000000000000000000000
            0000000000000000000000000000000000000000000000000000000000000000
            000000000000000000000000000000000000000000000000000000000000de27
            0000000000000000000000000000000000000000000000000000000000000000
            0000000000000000000000000000000000000000000000000000000000000000
            029e00000000000000434d345833324743333230304331364b3245000000802c
            0000000000000000000000000000000000000000000000000000000000000000
            0c4a01200000000000a300000437ff030050616110ba223011f00a200800b01e
            2d00000000000000000000f6f6f6f60000000000000000000000000000000000
            0000000000000000000000000000000000000000000000000000000000000000
            0000000000000000000000000000000000000000000000000000000000000000
            """
        )

        # Keep imports local so test discovery doesn't require GUI deps.
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        from src.core.parser.ddr4 import DDR4Parser

        parser = DDR4Parser(list(spd_bytes))
        self.assertTrue(parser.is_valid())

        xmp = parser.parse_xmp()
        self.assertTrue(xmp["supported"])
        self.assertEqual(xmp["version"], "2.0")
        self.assertEqual(len(xmp["profiles"]), 1)

        p1 = xmp["profiles"][0]
        self.assertEqual(p1["frequency"], 4000)
        self.assertAlmostEqual(p1["voltage"], 1.35, places=3)
        self.assertEqual(p1["tRC"], 73)
        self.assertEqual(p1["tRFC1"], 1100)
        self.assertEqual(p1["tRFC2"], 700)
        self.assertEqual(p1["tRFC4"], 520)
        self.assertEqual(p1["tFAW"], 44)
        self.assertEqual(p1["tRRD_S"], 8)
        self.assertEqual(p1["tRRD_L"], 12)
        self.assertNotIn("tWTR_S", p1)
        self.assertNotIn("tWTR_L", p1)
        self.assertNotIn("tCCD_L", p1)
        self.assertEqual(p1["timings"], "CL20-25-25-47-73")

    def test_xmp_tck_fine_offset_affects_frequency_and_timings(self):
        # Same SPD sample, but simulate an edited profile where tCK uses MTB+FTB (e.g., ~DDR4-3600).
        spd_bytes = bytearray(
            _bytes_from_hex_lines(
                """
                23100c028629000800000003090300000000080cffff03006c6c6c1108743011
                f00a200800a81e2b2b0000000000000000000000000000000000000016361636
                1636163600002b0c2b0c2b0c2b0c000000000000000000000000000000000000
                000000000000000000000000000000000000000000edb5ce0000000000c265a6
                1111010100000000000000000000000000000000000000000000000000000000
                0000000000000000000000000000000000000000000000000000000000000000
                0000000000000000000000000000000000000000000000000000000000000000
                000000000000000000000000000000000000000000000000000000000000de27
                0000000000000000000000000000000000000000000000000000000000000000
                0000000000000000000000000000000000000000000000000000000000000000
                029e00000000000000434d345833324743333230304331364b3245000000802c
                0000000000000000000000000000000000000000000000000000000000000000
                0c4a01200000000000a300000437ff030050616110ba223011f00a200800b01e
                2d00000000000000000000f6f6f6f60000000000000000000000000000000000
                0000000000000000000000000000000000000000000000000000000000000000
                0000000000000000000000000000000000000000000000000000000000000000
                """
            )
        )

        repo_root = pathlib.Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        from src.core.parser.ddr4 import DDR4Parser
        from src.utils.constants import SPD_BYTES, XMP_PROFILE_OFFSETS

        # Encode tCK = 556ps (4*125 + 56) -> ~3597 MT/s, should snap to 3600 MT/s.
        spd_bytes[SPD_BYTES.XMP_PROFILE1_START + XMP_PROFILE_OFFSETS.TCK_FTB] = 0x38

        parser = DDR4Parser(list(spd_bytes))
        self.assertTrue(parser.is_valid())

        xmp = parser.parse_xmp()
        self.assertTrue(xmp["supported"])
        self.assertEqual(len(xmp["profiles"]), 1)

        p1 = xmp["profiles"][0]
        self.assertEqual(p1["frequency"], 3600)
        self.assertEqual(p1["timings"], "CL18-22-22-42-66")

    def test_ddr4_base_timing_twtr_is_12bit_with_shared_high_nibbles(self):
        # Regression: tWTR_S / tWTR_L are 12-bit values with a shared high-nibble byte.
        repo_root = pathlib.Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        from src.core.parser.ddr4 import DDR4Parser
        from src.utils.constants import SPD_BYTES, DDR4_TYPE

        spd = bytearray([0] * 512)
        spd[SPD_BYTES.DRAM_TYPE] = DDR4_TYPE

        # Set a valid tCK so parse_timings has a sane baseline.
        spd[SPD_BYTES.TCK_MIN] = 4
        spd[SPD_BYTES.TCK_MIN_FTB] = 0

        # tWTR_S = 0x123, tWTR_L = 0x456
        spd[SPD_BYTES.TWTR_MIN_HIGH] = 0x41  # high nibble=0x4 (L), low nibble=0x1 (S)
        spd[SPD_BYTES.TWTR_S_MIN] = 0x23
        spd[SPD_BYTES.TWTR_L_MIN] = 0x56

        parser = DDR4Parser(list(spd))
        self.assertTrue(parser.is_valid())

        timing = parser.parse_timings()
        self.assertAlmostEqual(timing.tWTR_S, 0x123 * 0.125, places=3)
        self.assertAlmostEqual(timing.tWTR_L, 0x456 * 0.125, places=3)


if __name__ == "__main__":
    unittest.main()
