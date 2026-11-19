# Contributing

Small corrections to documentation, parsers, tests, and figure scripts are
welcome. Please open an issue before changing a published numerical table or
the interpretation of an electronic-state assignment.

Before submitting a change:

```bash
python -m ruff check scripts tests
python -m pytest -q
python scripts/verify_key_numbers.py
```

Do not add `POTCAR`, `WAVECAR`, full `CHGCAR` volumes, credentials, local
absolute paths, or third-party papers.
