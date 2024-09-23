import unittest
import io

from erlang_changes import OTPVersionsTable

class TestOTPVersionsTable(unittest.TestCase):
	def test_parse1(self):
		s = b"""
OTP-21.0.5 : compiler-7.2.3 crypto-4.3.1 erts-10.0.5 # asn1-5.0.6 common_test-1.16 :
OTP-21.0.4 : erts-10.0.4 # asn1-5.0.6 common_test-1.16 compiler-7.2.2 crypto-4.3 :
		"""

		vt = OTPVersionsTable.from_file(io.BytesIO(s))

		self.assertListEqual(list(vt.otp_versions), ["21.0.5", "21.0.4"])
		self.assertDictEqual(vt["21.0.5"], dict([("asn1","5.0.6"), ("common_test","1.16"), ("compiler","7.2.3"), ("crypto","4.3.1"), ("erts","10.0.5")]))
		self.assertDictEqual(vt["21.0.4"], dict([("asn1", "5.0.6"), ("common_test", "1.16"), ("compiler", "7.2.2"), ("crypto","4.3"), ("erts","10.0.4")]))
		self.assertListEqual(list(vt.slice("21.0.4", "21.0.5")), ["21.0.5",])
		self.assertDictEqual(vt.diff("21.0.4"), dict([("erts", (None, "10.0.4")), ("asn1", (None, "5.0.6")), ("common_test", (None, "1.16")), ("compiler", (None, "7.2.2")), ("crypto", (None, "4.3"))]))
		self.assertDictEqual(vt.diff("21.0.5"), dict([("erts", ("10.0.4", "10.0.5")), ("asn1", ("5.0.6", "5.0.6")), ("common_test", ("1.16", "1.16")), ("compiler", ("7.2.2", "7.2.3")), ("crypto", ("4.3", "4.3.1"))]))

if __name__ == '__main__':
	unittest.main()

