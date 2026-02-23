---
name: validate-game
description: Validate game JSON data files for correctness and cross-reference integrity
disable-model-invocation: true
allowed-tools: Bash, Read, Grep
argument-hint: "[game-dir]"
---

Validate adventure game data files for correctness.

If `$ARGUMENTS` is empty, default to `games/zork1/`.

Run this Python validation script:
```bash
python3 -c "
from engine.loader import GameLoader, Validator

game_dir = '$0' if '$0' else 'games/zork1/'
print(f'Validating game data in: {game_dir}')
print()

loader = GameLoader(game_dir)
data = loader.load()

print(f'Config: {data.config.title} v{data.config.version}')
print(f'Rooms: {len(data.rooms)}')
print(f'Objects: {len(data.objects)}')
print(f'NPCs: {len(data.npcs)}')
print(f'Verbs: {len(data.verbs)}')
print(f'Events: {len(data.events)}')
print()

validator = Validator()
errors = validator.validate(data)
if errors:
    print(f'ERRORS FOUND: {len(errors)}')
    for e in errors:
        print(f'  - {e.message}')
else:
    print('All cross-references valid.')
print()

# Check for orphaned objects (no location and no parent)
for obj in data.objects:
    if not obj.location and not obj.parent_object:
        print(f'  Warning: Object \"{obj.id}\" has no location or parent')

# List rooms and their exit connectivity
print('Room connectivity:')
for room in data.rooms:
    exits = ', '.join(f'{e.direction.value}->{e.target_room}' for e in room.exits)
    dark = ' [DARK]' if room.is_dark else ''
    print(f'  {room.id}{dark}: {exits}')
"
```

Report a clear summary of the validation results including any errors or warnings.
