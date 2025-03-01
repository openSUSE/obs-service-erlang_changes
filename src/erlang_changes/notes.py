import re
from collections import OrderedDict
import itertools
import mistune
from mistune.renderers.markdown import MarkdownRenderer
import lxml.etree as ET


def unfold(iterable, headerfun):
	sections = []
	stack = [sections]

	for item in iterable:

		if (level := headerfun(item)) is not None:
			current_level = len(stack) - 1

			if current_level >= level:
				drop = current_level - level + 1
				stack = stack[:-drop]

			stack[-1].append([])
			stack.append(stack[-1][-1])
			for _ in range(current_level, level - 1):
				stack[-1].append([])
				stack.append(stack[-1][-1])

		stack[-1].append(item)

	return sections


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
	def from_md(source):
		markdown = mistune.create_markdown(renderer=None)
		renderer = PlainRenderer()
		state = mistune.core.BlockState()

		ast = markdown(source.read().decode("utf-8"))
		ast = unfold(ast, lambda tok: tok['attrs']['level'] if tok['type'] == 'heading' else None)

		islist = lambda tok: isinstance(tok, list)
		sections = next(filter(islist, ast))

		change_list = []
		for section in filter(islist, sections):
			heading = renderer.render_children(section[0], state)
			version_match = Notes._VERSION_RE.search(heading)
			if not version_match:
				continue

			version = version_match.group(0)
			changes = []

			for subsection in filter(islist, section):
				heading = renderer.render_children(subsection[0], state)
				if not heading in Notes._TITLE_LIST:
					continue

				for tok in filter(lambda tok: tok['type'] == 'list', subsection):

					for item in tok['children']:
						if not ('children' in item and len(item['children'])):
							continue

						text = renderer([item['children'][0]], state).strip()
						changes.append(text)

			change_list.append((version, list(changes)))

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
