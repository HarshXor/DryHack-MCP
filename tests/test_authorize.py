import os
import unittest
from unittest.mock import patch

from dryhack_mcp.tools.authorize import authorize


class AuthorizeTests(unittest.TestCase):
    def test_matching_scope(self):
        for target, scope in [('https://api.lab.example/login', ['lab.example']),
                              ('10.0.0.5', ['10.0.0.0/24'])]:
            result = authorize(target, 'Review headers', scope)
            self.assertIn('IN SCOPE — CALLER DECLARED', result)
            self.assertIn('PERMISSION NOT VERIFIED', result)

    def test_missing_or_nonmatching_scope(self):
        for scope in [[], ['other.example'], ['evil-lab.example']]:
            self.assertIn('[OUT OF SCOPE]', authorize('lab.example', 'recon', scope))

    def test_environment_ignored_and_no_scope_leak(self):
        with patch.dict(os.environ, {'DRYHACK_SCOPE': 'lab.example'}):
            self.assertIn('[OUT OF SCOPE]', authorize('lab.example', 'recon', []))
        authorize('lab.example', 'recon', ['lab.example'])
        self.assertIn('[OUT OF SCOPE]', authorize('lab.example', 'recon', []))

    def test_scope_required(self):
        with self.assertRaises(TypeError):
            authorize('lab.example', 'recon')


if __name__ == '__main__':
    unittest.main()
