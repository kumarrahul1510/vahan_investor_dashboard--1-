
import importlib

def test_imports():
    assert importlib.import_module("etl")
    assert importlib.import_module("app")
