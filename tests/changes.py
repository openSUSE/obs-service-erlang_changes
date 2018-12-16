from erlang_changes.changes import Changes
from freezegun import freeze_time
import io
import unittest

class TestChanges(unittest.TestCase):
	@freeze_time("2010-01-01")
	def test_changes1(self):
		expected = b'''-------------------------------------------------------------------
Fri Jan 01 00:00:00 UTC 2010 - a@b.com


'''

		i = io.BytesIO()
		c = Changes("a@b.com", [])
		c.write(i)
		self.assertEqual(i.getvalue(), expected)

	@freeze_time("2010-01-01")
	def test_changes2(self):
		expected = b'''-------------------------------------------------------------------
Fri Jan 01 00:00:00 UTC 2010 - a@b.com

- Changes for 42.0.1:
  * erts: Update
  * kernel: Up1
  * kernel: Up2

'''

		i = io.BytesIO()
		c = Changes("a@b.com", [("42.0.1", [("erts", ["Update"]), ("kernel", ["Up1","Up2"])])])
		c.write(i)
		self.assertEqual(i.getvalue(), expected)
	@freeze_time("2010-01-01")

	@freeze_time("2010-01-01")
	def test_changes3(self):
		expected = b'''-------------------------------------------------------------------
Fri Jan 01 00:00:00 UTC 2010 - a@b.com

- Changes for 42.0.1:
  * erts: Update
- Changes for 41.0.1:
  * erts: Update

'''

		i = io.BytesIO()
		c = Changes("a@b.com", [("42.0.1", [("erts", ["Update"])]), ("41.0.1", [("erts", ["Update"])])])
		c.write(i)
		self.assertEqual(i.getvalue(), expected)

	@freeze_time("2010-01-01")
	def test_changes4(self):
		origin = b'''-------------------------------------------------------------------
Tue Dec 31 00:00:00 UTC 2009 - a@b.com
'''

		expected = b'''-------------------------------------------------------------------
Fri Jan 01 00:00:00 UTC 2010 - a@b.com

- Changes for 42.0.1:
  * erts: Update
- Changes for 41.0.1:
  * erts: Update

-------------------------------------------------------------------
Tue Dec 31 00:00:00 UTC 2009 - a@b.com
'''

		i = io.BytesIO(origin)
		c = Changes("a@b.com", [("42.0.1", [("erts", ["Update"])]), ("41.0.1", [("erts", ["Update"])])])
		c.write(i)
		self.assertEqual(i.getvalue(), expected)
