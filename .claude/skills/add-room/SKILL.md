---
name: add-room
description: Scaffold a new room definition for the adventure game
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
argument-hint: <room-id>
---

Create a new room for the adventure game. The room ID is `$0`.

Follow these steps:

1. **Gather details** — Ask the user:
   - Room name (display name like "West of House")
   - Full description (what the player sees on first visit)
   - Short description (for revisits)
   - Is it dark? (requires a light source)
   - Exits: which directions lead where (use existing room IDs)

2. **Check existing rooms** — Read the game data to understand what rooms exist and ensure the room ID doesn't conflict:
```bash
python3 -c "
from engine.loader import GameLoader
data = GameLoader('games/zork1/').load()
for r in data.rooms:
    exits = ', '.join(f'{e.direction.value}->{e.target_room}' for e in r.exits)
    print(f'{r.id}: {exits}')
"
```

3. **Determine file placement** — Check which JSON file in `games/zork1/rooms/` the room belongs in based on location:
   - `above_ground.json` — outdoor/surface rooms
   - `house.json` — rooms inside the white house
   - `underground.json` — cellar and below
   - Or create a new file if it's a distinct area

4. **Create the room JSON** — Follow this format:
```json
{
  "id": "room_id",
  "name": "Room Name",
  "description": "Full description.",
  "short_description": "Short description.",
  "is_dark": false,
  "exits": [
    {"direction": "north", "target_room": "other_room_id"}
  ]
}
```

Add it to the appropriate JSON array file.

5. **Add return exits** — Update the connecting rooms so they have exits back to the new room.

6. **Validate** — Run the validator to confirm all cross-references are correct:
```bash
python3 -c "
from engine.loader import GameLoader, Validator
data = GameLoader('games/zork1/').load()
errors = Validator().validate(data)
if errors:
    for e in errors:
        print(f'ERROR: {e.message}')
else:
    print('Validation passed.')
"
```

7. **Report** — Show the user the new room and its connections.
