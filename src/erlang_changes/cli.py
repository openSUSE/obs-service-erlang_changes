import argparse
import os.path
import shutil
from six.moves import urllib
import erlang_changes
from .changes import Changes
from .spec import Spec
from .github import get_github_version


ERLANG_SPEC_FILENAME = 'erlang.spec'


try:
	FileNotFoundError
except NameError:
	FileNotFoundError = IOError

class MajorUpdateRequested(Exception):
	def __init__(self, prev_version, version):
		message = "Major update from {} to {} is not supported.".format(prev_version, version)
		super(MajorUpdateRequested, self).__init__(message)

class OTPVersionMismatch(Exception):
	def __init__(self, otp_version, source_otp_version):
		message = "Expected version {}, while {} is found in the source file".format(otp_version, source_otp_version)
		super(OTPVersionMismatch, self).__init__(message)

def get_current_version(filename = ERLANG_SPEC_FILENAME):
	erlang_spec = Spec(filename)
	return erlang_spec.version

def get_spec_sources(filename = ERLANG_SPEC_FILENAME):
	erlang_spec = Spec(filename)
	return erlang_spec.sources

def major_version(version):
	return version.split(".")[0]

parser = argparse.ArgumentParser(prog='otp-service_erlang_changes')
parser.add_argument('--outdir', help='osc service parameter for internal use only', required=True)

def execute_from_commandline(argv=None):
	args = parser.parse_args(argv)

	prev_otp_version = get_current_version()
	prev_otp_major_version = major_version(prev_otp_version)
	otp_version = get_github_version(prev_otp_major_version)

	if prev_otp_version == otp_version:
		return

	if prev_otp_major_version != major_version(otp_version):
		raise MajorUpdateRequested(prev_otp_version, otp_version)

	tmp_spec_filename = os.path.join(args.outdir, ERLANG_SPEC_FILENAME)
	shutil.copyfile(ERLANG_SPEC_FILENAME, tmp_spec_filename)
	Spec.set_version(tmp_spec_filename, otp_version)

	for source in get_spec_sources(tmp_spec_filename):
		url = urllib.parse.urlparse(source)
		if not url.scheme:
			continue
		filename = os.path.basename(urllib.request.url2pathname(url.path))
		if os.path.exists(filename):
			continue
		urllib.request.urlretrieve(source, filename)

	otp_src_filename = "OTP-{version}.tar.gz".format(version = otp_version)
	otp_src = erlang_changes.OTPSrc.from_file(otp_src_filename)

	if otp_version != otp_src.otp_version:
		raise OTPVersionMismatch(otp_version, otp_src.otp_version)

	new_changes = Changes.from_otp_src(otp_src, prev_otp_version)
	for path, changes in Changes.find_changes():
		tmp_changes = os.path.join(args.outdir, changes)
		shutil.copyfile(os.path.join(path, changes), tmp_changes)
		new_changes.write(tmp_changes)

if __name__ == "__main__":
	import sys

	execute_from_commandline(sys.argv[1:])
