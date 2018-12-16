from setuptools import setup

setup(name='obs-service-erlang_changes',
	version='0.1.0',
	description='Erlang changelog formatting OBS service',
	url='http://github.com/matwey/obs-service-erlang_changes',
	author='Matwey V. Kornilov',
	author_email='matwey.kornilov@gmail.com',
	license='GPL-2.0',
	packages=['erlang_changes'],
	test_suite='tests',
	data_files=[
		('/usr/lib/obs/service', [
			'service/erlang_changes',
			'service/erlang_changes.service']),
	],
	zip_safe=False)
