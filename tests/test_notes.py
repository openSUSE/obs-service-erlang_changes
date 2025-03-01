import unittest
import io

from erlang_changes import Notes

class TestNotes(unittest.TestCase):
	def test_parse_xml(self):
		s = b"""
<chapter>
<section><title>App 1.0.1</title>

    <section><title>Fixed Bugs and Malfunctions</title>
      <list>
        <item>
          <p>Fix <c>1</c></p>
          <p>Skip this</p>
        </item>
        <item>
          <p>Fix <c>2</c></p>
          <p>Another par</p>
          <p>Skip this</p>
        </item>
      </list>
    </section>

    <section><title>Improvements and New Features</title>
      <list>
        <item>
          <p>Feature <c>2</c></p>
          <p>Skip this</p>
        </item>
      </list>
    </section>

</section>

<section><title>App 1.0</title>

    <section><title>Improvements and New Features</title>
      <list>
        <item>
          <p>Feature <c>1</c></p>
          <p>Skip this</p>
        </item>
      </list>
    </section>

</section>

</chapter>
		"""

		slice1_exp = [
			["Fix 1", "Fix 2 Another par", "Feature 2"],
		]
		slice2_exp = [
			["Fix 1", "Fix 2 Another par", "Feature 2"],
			["Feature 1"],
		]

		n = Notes.from_xml(io.BytesIO(s))

		self.assertListEqual(list(n.app_versions), ["1.0.1", "1.0"])
		self.assertListEqual(n["1.0.1"], ["Fix 1", "Fix 2 Another par", "Feature 2"])
		self.assertListEqual(n["1.0"], ["Feature 1"])
		self.assertListEqual(list(n.slice("1.0", "1.0.1")), slice1_exp)
		self.assertListEqual(list(n.slice(None, "1.0.1")), slice2_exp)
		self.assertListEqual(list(n.slice(None, None)), slice2_exp)
		self.assertListEqual(list(n.slice("1.0", None)), slice1_exp)

	def test_parse_md(self):
		s = b"""
# App Release Notes

This document describes the changes made to the App application.

## App 1.0.1

### Fixed Bugs and Malfunctions

- Fix *1*

  Skip this

- Fix *2*
  Another line

  Skip this

Skip that

### Improvements and New Features

- Feature *2* 3

  Skip this

Ship that

## App 1.0

### Improvements and New Features

- Feature *1*

  Skip this

-"""

		slice1_exp = [
			["Fix 1", "Fix 2 Another line", "Feature 2 3"],
		]
		slice2_exp = [
			["Fix 1", "Fix 2 Another line", "Feature 2 3"],
			["Feature 1"],
		]

		n = Notes.from_md(io.BytesIO(s))

		self.assertListEqual(list(n.app_versions), ["1.0.1", "1.0"])
		self.assertListEqual(n["1.0.1"], ["Fix 1", "Fix 2 Another line", "Feature 2 3"])
		self.assertListEqual(n["1.0"], ["Feature 1"])
		self.assertListEqual(list(n.slice("1.0", "1.0.1")), slice1_exp)
		self.assertListEqual(list(n.slice(None, "1.0.1")), slice2_exp)
		self.assertListEqual(list(n.slice(None, None)), slice2_exp)
		self.assertListEqual(list(n.slice("1.0", None)), slice1_exp)

if __name__ == '__main__':
	unittest.main()
