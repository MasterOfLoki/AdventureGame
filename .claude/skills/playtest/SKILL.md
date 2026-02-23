---
name: playtest
description: Launch the adventure game for interactive playtesting
disable-model-invocation: true
allowed-tools: Bash
argument-hint: "[game-dir]"
---

Launch the adventure game for playtesting.

If `$ARGUMENTS` is empty, default to the Zork I game:
```bash
python3 -m cli.main games/zork1/ --parser fallback
```

If `$ARGUMENTS` is provided, use it as the game directory:
```bash
python3 -m cli.main $0 --parser fallback
```

To run with debug mode (shows parsed commands and state changes), add `--debug`:
```bash
python3 -m cli.main games/zork1/ --parser fallback --debug
```

If the argument is `debug`, run Zork I with debug mode enabled.
