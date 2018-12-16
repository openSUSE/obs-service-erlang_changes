import datetime
import glob
import itertools
import os
import os.path
import textwrap

DEFAULT_AUTHOR = 'opensuse-packaging@opensuse.org'

class Changes(object):
	wrapper = textwrap.TextWrapper(width=67, initial_indent='  * ', subsequent_indent='    ')

	@staticmethod
	def find_changes(path=None):
		if path is None:
			path = os.getcwd()
		return [os.path.split(x) for x in glob.glob(os.path.join(path, "*.changes"))]

	@staticmethod
	def from_otp_src(otp_src, base_otp_version, author=None):
		if author is None:
			author = DEFAULT_AUTHOR

		otp_version = otp_src.otp_version
		otp_versions_table = otp_src.otp_versions_table

		if base_otp_version == otp_version:
			return Changes(author, [])

		def proc_app(app, prev_ver, next_ver):
			if next_ver is None:
				return (app, ["Application {} deleted".format(app)])

			changes = itertools.chain.from_iterable(otp_src.app_notes_xml[app].slice(prev_ver, next_ver))
			return (app, list(changes))

		def proc_version(ver):
			changelog = [proc_app(app, *vpair) for (app, vpair) in otp_versions_table.diff(ver).items() if vpair[0] != vpair[1]]
			return (ver, changelog)

		changelog = [proc_version(ver) for ver in otp_versions_table.slice(base_otp_version, otp_version)]

		return Changes(author, changelog)

	def _generate_changelog(self, changelog, author):
		lines = [str('-' * 67), str("%s - %s" % (datetime.datetime.utcnow().strftime('%a %b %d %H:%M:%S UTC %Y'), author)), str("")]

		for version, apps in changelog:
			lines.append("- Changes for {}:".format(version))
			for (app, changes) in apps:
				for x in changes:
					lines.extend(Changes.wrapper.wrap(app + ": " + x))

		lines.extend(["",]*2)

		self._content = "\n".join(lines).encode("utf-8")

	def __init__(self, changelog, author):
		self._content = b""
		self._generate_changelog(author, changelog)

	def write(self, sink):
		if not hasattr(sink, "write"):
			sink = open(sink, "r+b")

		existing_content = sink.read()
		sink.seek(0)
		sink.write(self._content + existing_content)
