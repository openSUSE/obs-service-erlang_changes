from setuptools import setup
from setuptools.command.install import install

OBS_SERVICE_PATH='/usr/lib/obs/service'

class InstallCmd(install, object):
	def finalize_options(self):
		self.install_scripts = OBS_SERVICE_PATH
		super(InstallCmd, self).finalize_options()

setup(name='obs-service-erlang_changes',
	version='0.2.1',
	description='Erlang changelog formatting OBS service',
	url='http://github.com/matwey/obs-service-erlang_changes',
	author='Matwey V. Kornilov',
	author_email='matwey.kornilov@gmail.com',
	license='GPL-2.0',
	packages=['erlang_changes'],
	test_suite='tests',
	entry_points={
		'console_scripts': ['erlang_changes = erlang_changes.cli:execute_from_commandline']
	},
	data_files=[
		(OBS_SERVICE_PATH, ['service/erlang_changes.service']),
	],
	zip_safe=False,
	cmdclass={
		'install': InstallCmd
	}
)
