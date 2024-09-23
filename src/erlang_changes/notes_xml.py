import re
from collections import OrderedDict
import itertools
import lxml.etree as ET

class NotesXML(object):
	_version_re = re.compile(r'((\d+)(\.\d+)*)$')
	_title_list = ['Fixed Bugs and Malfunctions', 'Improvements and New Features', 'Known Bugs and Problems']

	@staticmethod
	def from_xml(source, parser=None):
		if parser is None:
			parser = ET.XMLParser()

		root = ET.parse(source, parser=parser)
		change_list = []

		for x in root.findall('./section[title]'):
			version_match = NotesXML._version_re.search(x.find("title").text)
			if not version_match:
				continue

			version = version_match.group(0)
			entries = []
			for item in itertools.chain.from_iterable([x.findall("./section[title='{}']/list/item[p]".format(title)) for title in NotesXML._title_list]):
				entries.append(" ".join(itertools.chain.from_iterable(["".join(y.itertext()).split() for y in item.xpath("./p[position()<last()]")])))

			change_list.append((version, entries))

		return NotesXML(change_list)

	def __init__(self, changelog):
		versions, self._changes = zip(*changelog)
		self._versions = OrderedDict(((ver, idx) for idx, ver in enumerate(versions)))

	@property
	def app_versions(self):
		return self._versions.keys()

	def __getitem__(self, version):
		return self._changes[self._versions[version]]

	def slice(self, version_begin, version_end):
		idx_begin = self._versions[version_begin] if version_begin else None
		idx_end = self._versions[version_end] if version_end else None

		return itertools.islice(self._changes, idx_end, idx_begin)
