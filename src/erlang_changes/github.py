import re
import requests


_re_refs_tags = re.compile(r'refs/tags/(.*)')
_re_OTP = re.compile(r'OTP-(.*)')


def get_github_tags(prefix, owner="erlang", repo="otp"):
	url = "https://api.github.com/repos/{}/{}/git/matching-refs/tags/{}".format(owner, repo, prefix)
	req = requests.get(url)
	req.raise_for_status()
	return [_re_refs_tags.match(x['ref']).groups(1)[0] for x in req.json()]

def get_github_version(major):
	prefix = "OTP-{}".format(major)
	return _re_OTP.match(get_github_tags(prefix)[-1]).groups(1)[0]
