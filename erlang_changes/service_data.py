import lxml.etree as ET

try:
	FileNotFoundError
except NameError:
	FileNotFoundError = IOError

class ServiceDataEmpty(Exception):
	pass

class ServiceData(object):
	def __init__(self, source):
		self._servicedata = source if isinstance(source, ET._ElementTree) else ET.parse(source)
		self._otp_version = self._servicedata.find("./service[@name='erlang_changes']/param[@name='otp_version']")
		if self._otp_version is None:
			raise ServiceDataEmpty()

	@property
	def otp_version(self):
		return self._otp_version.text

	def set_otp_version(self, otp_version):
		self._otp_version.text = otp_version

	def write(self, sink):
		return self._servicedata.write(sink)

	@staticmethod
	def init_servicedata(source, otp_version):
		try:
			xml = ET.parse(source)
			root = xml.getroot()
		except FileNotFoundError:
			root = ET.fromstring("<servicedata/>")
			xml = ET.ElementTree(root)

		service = root.find("./service[@name='erlang_changes']")
		if service is None:
			service = ET.fromstring("<service name='erlang_changes'/>")
			root.append(service)

		otp_version_node = service.find("./param[@name='otp_version']")
		if otp_version_node is None:
			otp_version_node = ET.fromstring("<param name='otp_version'/>")
			service.append(otp_version_node)

		otp_version_node.text = otp_version

		return ServiceData(xml)
