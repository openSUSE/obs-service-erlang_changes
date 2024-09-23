import unittest
import io

from erlang_changes import NotesXML

class TestNotesXML(unittest.TestCase):
	def test_parse1(self):
		s = u"""
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

		n = NotesXML.from_xml(io.StringIO(s))

		self.assertListEqual(list(n.app_versions), ["1.0.1", "1.0"])
		self.assertListEqual(n["1.0.1"], ["Fix 1", "Fix 2 Another par", "Feature 2"])
		self.assertListEqual(n["1.0"], ["Feature 1"])
		self.assertListEqual(list(n.slice("1.0", "1.0.1")), slice1_exp)
		self.assertListEqual(list(n.slice(None, "1.0.1")), slice2_exp)
		self.assertListEqual(list(n.slice(None, None)), slice2_exp)
		self.assertListEqual(list(n.slice("1.0", None)), slice1_exp)

if __name__ == '__main__':
	unittest.main()
