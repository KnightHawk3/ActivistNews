import unittest
from click.testing import CliRunner
from manage import fetch, add

class TestManage(unittest.TestCase):
    def test_fetch(self):
        runner = CliRunner()
        result = runner.invoke(fetch)
        assert result.exit_code == 0
        assert result.output == ""

    def test_add(self):
        runner = CliRunner()
        result = runner.invoke(add, ["--feed", "https://redflag.org.au/all/rss"])
        assert result.output == ""
        assert result.exit_code == 0

if __name__ == '__main__':
    unittest.main()
