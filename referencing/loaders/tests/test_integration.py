from unittest import TestCase


class TestLoaders(TestCase):
    def test_it_imports(self):
        import referencing.loaders  # noqa: F401
