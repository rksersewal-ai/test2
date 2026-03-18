"""Shared runtime checks for the optional ML classifier stack."""

from importlib.util import find_spec


_REQUIRED_MODULES = (
    ('joblib', 'joblib'),
    ('numpy', 'numpy'),
    ('sklearn', 'scikit-learn'),
)


def missing_ml_dependencies() -> list[str]:
    """Return the install names for any missing optional ML dependencies."""
    return [package for module, package in _REQUIRED_MODULES if find_spec(module) is None]


def ensure_ml_dependencies() -> None:
    """Raise a clear runtime error when the optional ML stack is unavailable."""
    missing = missing_ml_dependencies()
    if not missing:
        return

    joined = ', '.join(missing)
    raise RuntimeError(
        f'ML classifier dependencies are missing: {joined}. '
        'Install them with `pip install -r requirements-optional.txt`.'
    )
