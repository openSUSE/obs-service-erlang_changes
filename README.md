[![Build Status](https://github.com/openSUSE/obs-service-erlang_changes/actions/workflows/python-package.yml/badge.svg)](https://github.com/openSUSE/obs-service-erlang_changes/actions/workflows/python-package.yml)
[![PyPI version](https://badge.fury.io/py/obs-service-erlang-changes.svg)](https://badge.fury.io/py/obs-service-erlang_changes)

# erlang_changes (OBS service)
This is the git repository for obs-service-erlang_changes, which provides [erlang](https://www.erlang.org/) changelog formating service for the [Open Build Service](http://openbuildservice.org/).

The service looks over `notes.xml` or `notes.md` in Erlang/OTP release tarball and produces formatted `erlang.changes` file for RPM packaging.

[![asciicast](https://asciinema.org/a/710828.svg)](https://asciinema.org/a/710828?autoplay=1)

## `_service` example

```xml
<services>
	<service name="erlang_changes" mode="disabled" />
	<service name="refresh_patches" mode="disabled">
		<param name="changesgenerate">enable</param>
	</service>
</services>
```
