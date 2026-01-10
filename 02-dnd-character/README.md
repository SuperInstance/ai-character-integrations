# Example 2: D&D Character

A complete RPG character demonstrating personality-driven decisions, memory of adventures, and learning from experience.

## What This Example Shows

- Personality-driven decision making
- Memory of adventures, NPCs, and locations
- Learning from combat and social encounters
- Identity persistence across sessions
- Class-based decision routing (Fighter vs Rogue vs Wizard)

## Character Classes

The example includes three character classes:

| Class | Play Style | Decision Pattern |
|-------|------------|------------------|
| **Fighter** | Direct, combat-focused | Quick decisions (Bot), aggressive |
| **Rogue** | Stealthy, cautious | Calculated decisions (Brain), opportunistic |
| **Wizard** | Intelligent, studied | Thoughtful decisions (Brain/Human), magical |

## Running the Example

```bash
# From the integration-examples directory
cd 02-dnd-character
python main.py

# Or choose a specific character
python main.py --character fighter
python main.py --character rogue
python main.py --character wizard
```

## Expected Output

The character will:
1. Load their personality and backstory
2. Process several game scenarios
3. Make decisions based on their class and personality
4. Remember NPCs, locations, and past events
5. Learn from combat and roleplay encounters
6. Generate a character narrative at the end

## Character Memory

Characters remember:
- **NPCs met** and their relationships
- **Locations visited** and key events
- **Combat encounters** and lessons learned
- **Loot obtained** and items used
- **Quests accepted** and completed

## Configuration

Edit `character.yaml` to customize:
- Character name, class, and stats
- Personality traits
- Backstory and goals
- Decision preferences per class
