from collections import OrderedDict
import itertools
import re
from six import viewkeys

class OTPVersionsTable(object):
	_app_re = re.compile(r'(\w+)-((\d+)(\.\d+)*)')

	@staticmethod
	def _proc_otp_version_line(x):
		otp_token, app_token, _ = x.split(":", 2)

		otp_version_match = OTPVersionsTable._app_re.search(otp_token)
		otp_version = otp_version_match.group(2)

		new_apps = itertools.chain(*[x.split() for x in app_token.split("#")])
		apps_version_matches = [OTPVersionsTable._app_re.search(x) for x in new_apps]
		apps = dict([(x.group(1), x.group(2)) for x in apps_version_matches])

		return (otp_version, apps)

	@staticmethod
	def from_file(source):
		if not hasattr(source, "readlines"):
			source = open(source, "r")

		applications = [OTPVersionsTable._proc_otp_version_line(x.decode('ascii')) for x in source.readlines() if x.strip()]

		return OTPVersionsTable(applications)

	def __init__(self, applications):
		versions, self._applications = zip(*applications)
		self._versions = OrderedDict(((ver, idx) for idx, ver in enumerate(versions)))

	@property
	def otp_versions(self):
		return self._versions.keys()

	def __getitem__(self, version):
		return self._applications[self._versions[version]]

	def slice(self, version_begin, version_end):
		idx_begin = self._versions[version_begin] if version_begin else None
		idx_end = self._versions[version_end] if version_end else None

		return itertools.islice(self._versions.keys(), idx_end, idx_begin)

	def diff(self, version):
		idx = self._versions[version]

		apps = self._applications[idx]
		apps_prev = self._applications[idx+1] if (idx+1) < len(self._applications) else dict([])

		keys = viewkeys(apps)
		keys_prev = viewkeys(apps_prev)

		keys_deleted = keys_prev - keys
		keys_added = keys - keys_prev
		keys_common = keys & keys_prev

		changes = ([(k, (apps_prev[k], None)) for k in keys_deleted] + [(k, (None, apps[k])) for k in keys_added] + [(k, (apps_prev[k], apps[k])) for k in keys_common])

		return dict(changes)
