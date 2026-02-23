---
name: test
description: Run the adventure game test suite, optionally targeting a specific subsystem
disable-model-invocation: true
allowed-tools: Bash
argument-hint: "[subsystem]"
---

Run tests for the Adventure Game engine.

If `$ARGUMENTS` is empty, run the full test suite:
```bash
python3 -m pytest tests/ -v
```

If `$ARGUMENTS` is provided, map it to the right test file and run it:
- `models` → `tests/test_models.py`
- `loader` → `tests/test_loader.py`
- `state` → `tests/test_game_state.py`
- `world` → `tests/test_world.py`
- `actions` → `tests/test_actions.py`
- `parser` → `tests/test_parser.py`
- `engine` → `tests/test_engine.py`
- `darkness` → `tests/test_darkness.py`
- `combat` → `tests/test_combat.py`
- `scoring` → `tests/test_scoring.py`
- `coverage` → run full suite with `--cov=engine --cov-report=term-missing`

```bash
python3 -m pytest tests/test_$0.py -v
```

If the argument is `coverage`:
```bash
python3 -m pytest tests/ -v --cov=engine --cov-report=term-missing
```

Report results clearly: how many passed, failed, and any error details.
