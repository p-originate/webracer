import unittest
import webracer.agent
import webracer.support

class NetlocToHostPortTest(unittest.TestCase):
    def test_host(self):
        netloc = 'foo'
        expected = ('foo', None)
        self._perform(netloc, expected)
    
    def test_host_with_port(self):
        netloc = 'foo:8080'
        expected = ('foo', 8080)
        self._perform(netloc, expected)
    
    def _perform(self, netloc, expected):
        agent = webracer.agent.Agent()
        actual = webracer.support.netloc_to_host_port(netloc)
        if isinstance(actual, list):
            actual = tuple(actual)
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    import unittest
    unittest.main()
