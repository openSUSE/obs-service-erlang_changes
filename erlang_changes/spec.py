import codecs
import re
import rpm

class Spec(object):
	def __init__(self, filename):
		#
		# Workaround for https://github.com/rpm-software-management/rpm/pull/1067
		# See also http://lists.rpm.org/pipermail/rpm-list/2020-February/002012.html
		#
		rpm.reloadConfig()

		self._spec = rpm.spec(filename)
		self._filename = filename

	@property
	def version(self):
		version_header = self._spec.sourceHeader[rpm.RPMTAG_VERSION]
		if isinstance(version_header, (bytes, bytearray)):
			return version_header.decode("ascii")
		return version_header

	@property
	def filename(self):
		return self._filename

	@property
	def sources(self):
		return [source for source,position,flag in self._spec.sources if flag == 1]

	@staticmethod
	def _replace_tag(filename, tag, string):
		with codecs.open(filename, 'r+', 'utf8') as f:
			contents = f.read()
			f.seek(0)

			contents_new, subs = re.subn(r'^{tag}:([ \t\f\v]*)[^%\n\r]*'.format(tag=tag),
				r'{tag}:\g<1>{string}'.format(tag=tag, string=string),
				contents, flags=re.MULTILINE)

			if subs > 0:
				f.truncate()
				f.write(contents_new)

	@staticmethod
	def set_version(filename, version):
		Spec._replace_tag(filename, "Version", version)
