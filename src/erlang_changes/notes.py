import re
from collections import OrderedDict
import itertools
import more_itertools
import mistune
from mistune.renderers.markdown import MarkdownRenderer
import lxml.etree as ET


class PlainRenderer(MarkdownRenderer):
	def __init__(self):
		super(PlainRenderer, self).__init__()

	def heading(self, token, state):
		return self.render_children(token, state)

	def emphasis(self, token, state):
		return self.render_children(token, state)

	def strong(self, token, state):
		return self.render_children(token, state)

	def codespan(self, token, state):
		return token['raw']

	def softbreak(self, token, state):
		return ' '

class Notes(object):
	_VERSION_RE = re.compile(r'((\d+)(\.\d+)*)$')
	_TITLE_LIST = ['Fixed Bugs and Malfunctions', 'Improvements and New Features', 'Known Bugs and Problems']

	@staticmethod
	def _is_md_version_header(token):
		return token['type'] == 'heading' and int(token['attrs']['level']) == 2

	@staticmethod
	def _is_md_changes_header(token):
		return token['type'] == 'heading' and int(token['attrs']['level']) == 3

	@staticmethod
	def from_md(source):
		markdown = mistune.create_markdown(renderer=None)
		renderer = PlainRenderer()
		state = mistune.core.BlockState()

		ast = markdown(source.read().decode("utf-8"))

		change_list = []
		for section in more_itertools.split_before(ast, Notes._is_md_version_header):
			head, *tail = section
			if head['type'] != 'heading':
				continue

			heading = renderer.render_children(head, state)

			version_match = Notes._VERSION_RE.search(heading)
			if not version_match:
				continue

			version = version_match.group(0)
			changes = []

			headings_and_lists = filter(lambda token: token['type'] in ['heading', 'list'], tail)
			split_headings_and_lists = more_itertools.split_before(headings_and_lists, Notes._is_md_changes_header)
			changes_lists = more_itertools.filter_map(lambda tokens: tokens[1:] if (tokens[0]['type'] == 'heading'
				and renderer.render_children(tokens[0], state).strip() in Notes._TITLE_LIST) else None, split_headings_and_lists)
			changes_lists_flatten = itertools.chain.from_iterable(changes_lists)
			changes_items = map(lambda token: token['children'], changes_lists_flatten)
			changes_items_flatten = itertools.chain.from_iterable(changes_items)
			text_changes = more_itertools.filter_map(lambda token: ''.join(renderer([token['children'][0],], state).splitlines()) if len(token['children']) else None, changes_items_flatten)

			change_list.append((version, list(text_changes)))

		return Notes(change_list)

	@staticmethod
	def from_xml(source, parser=None):
		if parser is None:
			parser = ET.XMLParser()

		root = ET.parse(source, parser=parser)
		change_list = []

		for x in root.findall('./section[title]'):
			version_match = Notes._VERSION_RE.search(x.find("title").text)
			if not version_match:
				continue

			version = version_match.group(0)
			entries = []
			for item in itertools.chain.from_iterable([x.findall("./section[title='{}']/list/item[p]".format(title)) for title in Notes._TITLE_LIST]):
				entries.append(" ".join(itertools.chain.from_iterable(["".join(y.itertext()).split() for y in item.xpath("./p[position()<last()]")])))

			change_list.append((version, entries))

		return Notes(change_list)

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
