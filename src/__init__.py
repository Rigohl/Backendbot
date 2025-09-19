# shim to allow imports like `src.backendbot` during tests
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
