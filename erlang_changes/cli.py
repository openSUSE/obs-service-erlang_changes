import argparse
import os.path
import glob
import shutil
import erlang_changes
from erlang_changes.changes import Changes
from erlang_changes.service_data import ServiceData, ServiceDataEmpty

try:
	FileNotFoundError
except NameError:
	FileNotFoundError = IOError

class MajorUpdateRequested(Exception):
	def __init__(self, prev_version, version):
		message = "Major update from {} to {} is not supported.".format(prev_version, version)
		super(MajorUpdateRequested, self).__init__(message)

parser = argparse.ArgumentParser(prog='otp-service_erlang_changes')
parser.add_argument('--otp_sources', metavar='FILENAME', help='Path to OTP/Erlang sources tarball', required=True)
parser.add_argument('--outdir', help='osc service parameter for internal use only', required=True)

def major_version(version):
	return version.split(".")[0]

def execute_from_commandline(argv=None):
	args = parser.parse_args(argv)

	otp_src_filename = sorted(glob.glob(args.otp_sources), reverse=True)[0]
	otp_src = erlang_changes.OTPSrc.from_file(otp_src_filename)

	otp_version = otp_src.otp_version

	servicedata_filename = "_servicedata"
	tmp_servicedata_filename = os.path.join(args.outdir, "_servicedata")

	try:
		servicedata = ServiceData(servicedata_filename)
	except (ServiceDataEmpty, FileNotFoundError):
		servicedata = ServiceData.init_servicedata(servicedata_filename, otp_version)
		servicedata.write(servicedata_filename)

	prev_otp_version = servicedata.otp_version

	if prev_otp_version == otp_version:
		return

	if major_version(prev_otp_version) != major_version(otp_version):
		raise MajorUpdateRequested(prev_otp_version, otp_version)

	new_changes = Changes.from_otp_src(otp_src, prev_otp_version)
	for path, changes in Changes.find_changes():
		tmp_changes = os.path.join(args.outdir, changes)
		shutil.copyfile(os.path.join(path, changes), tmp_changes)
		new_changes.write(tmp_changes)

	servicedata.set_otp_version(otp_version)
	servicedata.write(tmp_servicedata_filename)

	shutil.move(tmp_servicedata_filename, servicedata_filename)

	for path, changes in Changes.find_changes():
		tmp_changes = os.path.join(args.outdir, changes)
		shutil.move(tmp_changes, os.path.join(path, changes))

if __name__ == "__main__":
	import sys

	execute_from_commandline(sys.argv[1:])
