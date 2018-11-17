from erlang_changes.service_data import ServiceData, ServiceDataEmpty
import io
import tempfile
import unittest
import xml.etree.ElementTree as ET

class TestServiceData(unittest.TestCase):
	def assertXMLEqual(self, first, second):
		return self.assertEqual(ET.tostring(first.getroot()), ET.tostring(second.getroot()))

	def test_parse1(self):
		s = u"""<servicedata><service name="erlang_changes"><param name="otp_version">17.0</param></service></servicedata>"""

		c = ServiceData(io.StringIO(s))

		self.assertEqual(c.otp_version, "17.0")

	def test_parse2(self):
		s = u"""<servicedata/>"""

		with self.assertRaises(ServiceDataEmpty):
			c = ServiceData(io.StringIO(s))

	def test_parse3(self):
		s = u"""<servicedata/>"""

		c = ServiceData.init_servicedata(io.StringIO(s), "21.0")

		self.assertEqual(c.otp_version, "21.0")

	def test_parse4(self):
		s = u"""<servicedata><service name="erlang_changes"/></servicedata>"""

		c = ServiceData.init_servicedata(io.StringIO(s), "21.0")

		self.assertEqual(c.otp_version, "21.0")

	def test_parse5(self):
		s = u"""<servicedata><service name="erlang_changes"><param name="otp_version"/></service></servicedata>"""

		c = ServiceData.init_servicedata(io.StringIO(s), "21.0")

		self.assertEqual(c.otp_version, "21.0")

	def test_write1(self):
		s = u"""<servicedata><service name="erlang_changes"><param name="otp_version">17.0</param></service></servicedata>"""
		expected = u"""<servicedata><service name="erlang_changes"><param name="otp_version">21.0</param></service></servicedata>"""

		c = ServiceData(io.StringIO(s))

		c.set_otp_version("21.0")
		self.assertEqual(c.otp_version, "21.0")

		o = io.BytesIO()
		c.write(o)
		self.assertXMLEqual(
			ET.parse(io.BytesIO(o.getvalue())),
			ET.parse(io.StringIO(expected))
		)

if __name__ == '__main__':
	unittest.main()
