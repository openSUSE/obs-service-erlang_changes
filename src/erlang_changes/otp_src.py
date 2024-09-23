import os.path
import re
import tarfile
import lxml.etree as ET
from erlang_changes.otp_versions_table import OTPVersionsTable
from erlang_changes.notes_xml import NotesXML

class DTDResolver(ET.Resolver):
	dtd_paths = ["lib/erl_docgen/priv/dtd", "lib/erl_docgen/priv/dtd_man_entities"]

	def __init__(self, root_name, otp_src):
		self._root_name = root_name
		self._otp_src = otp_src
		self._cache = dict([])
		super(DTDResolver, self).__init__()

	def _resolve(self, name, no_cache=False):
		entry = self._cache.get(name)

		if not no_cache and entry is not None:
			return entry

		filenames = [os.path.join(self._root_name, p, name) for p in DTDResolver.dtd_paths]
		for x in filenames:
			try:
				entry = self._otp_src.extractfile(x).read()
			except KeyError:
				pass

		if not no_cache and entry is not None:
			self._cache[name] = entry

		return entry

	def resolve(self, url, _id, context):
		name = os.path.basename(url)
		entry = self._resolve(name)

		if entry is not None:
			return self.resolve_string(entry, context)

		return None

class OTPSrc(object):
	_notes_xml_re = re.compile(r'(\w+)/doc/src/notes\.xml$')

	@staticmethod
	def from_file(otp_sources_filename):
		otp_src = tarfile.open(otp_sources_filename)
		filenames = otp_src.getnames()
		root_name = filenames[0]

		otp_version = otp_src.extractfile("{}/OTP_VERSION".format(root_name)).read().decode('ascii').strip()
		otp_versions_table = OTPVersionsTable.from_file(otp_src.extractfile("{}/otp_versions.table".format(root_name)))
		apps = []

		parser = ET.XMLParser(load_dtd=True)
		parser.resolvers.add(DTDResolver(root_name, otp_src))

		for x in filenames:
			app_match = OTPSrc._notes_xml_re.search(x)
			if not app_match:
				continue
			apps.append((app_match.group(1), NotesXML.from_xml(otp_src.extractfile(x), parser=parser)))

		return OTPSrc(otp_version, otp_versions_table, apps)

	def __init__(self, otp_version, otp_versions_table, apps):
		self._otp_version = otp_version
		self._otp_versions_table = otp_versions_table
		self._apps = dict(apps)

	@property
	def otp_version(self):
		return self._otp_version

	@property
	def otp_versions_table(self):
		return self._otp_versions_table

	@property
	def app_notes_xml(self):
		return self._apps
