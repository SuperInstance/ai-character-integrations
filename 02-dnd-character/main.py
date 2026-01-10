#!/usr/bin/env python3
"""
D&D Character - Integration Example 2

A complete RPG character demonstrating:
- Personality-driven decisions
- Memory of adventures and NPCs
- Learning from combat and social encounters
- Identity persistence across sessions

Run: python main.py [fighter|rogue|wizard]
"""

import sys
import os
import argparse
import yaml
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Try to import from installed packages
    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory, ConsolidationEngine, IdentityPersistence
except ImportError:
    # If not installed, try to import from local paths
    escalation_path = Path(__file__).parent.parent.parent / "escalation-engine"
    memory_path = Path(__file__).parent.parent.parent / "hierarchical-memory"

    if str(escalation_path) not in sys.path:
        sys.path.insert(0, str(escalation_path))
    if str(memory_path / "src") not in sys.path:
        sys.path.insert(0, str(memory_path / "src"))

    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory, ConsolidationEngine, IdentityPersistence

from character import (
    DnDCharacter,
    CharacterClass,
    Personality,
    Alignment,
    ScenarioType,
    CharacterStats,
)
from shared.utils import (
    load_config,
    print_section,
    print_subsection,
    print_memory,
    simulate_delay,
)
from shared.mock_llm import MockLLMFactory, LLMProviderType


class DnDCharacterAgent:
    """
    Combines D&D character mechanics with hierarchical memory and
    intelligent decision routing.
    """

    def __init__(self, config_path: str = "character.yaml"):
        """Initialize the character agent."""
        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        char_config = self.config["character"]

        # Create character
        stats = CharacterStats(**char_config["stats"])
        personality = Personality(**char_config["personality"])

        self.character = DnDCharacter(
            name=char_config["name"],
            char_class=CharacterClass(char_config["class"].upper()),
            race=char_config["race"],
            level=char_config["level"],
            stats=stats,
            personality=personality,
            alignment=Alignment[char_config["alignment"].upper().replace(" ", "_")],
            background=char_config["background"],
            backstory=char_config["backstory"],
            goals=char_config["goals"],
        )

        # Initialize memory system
        self.memory = HierarchicalMemory(
            character_id=self.character.name.lower().replace(" ", "_"),
        )

        # Store character identity
        self.memory.store_semantic(
            f"I am {self.character.name}, a {self.character.race} {self.character.char_class.value}.",
            importance=10.0,
        )
        self.memory.store_semantic(
            f"Background: {self.character.backstory}",
            importance=9.0,
        )

        # Initialize escalation engine
        self.escalation = EscalationEngine()

        # Initialize LLM
        llm_config = self.config.get("llm", {})
        self.llm = MockLLMFactory.get_provider(
            provider=LLMProviderType.MOCK,
            model="gpt-4",
        )

        # Session tracking
        self.session_count = 0

    def process_scenario(
        self,
        scenario_type: ScenarioType,
        description: str,
        allies_present: bool = True,
        hp_ratio: float = 1.0,
        location: Optional[str] = None,
    ) -> tuple:
        """
        Process a game scenario.

        Returns:
            (decision_source, response, memory_created)
        """
        self.session_count += 1

        # Get decision context
        context_data = self.character.get_decision_context(
            scenario=scenario_type,
            description=description,
            allies_present=allies_present,
            hp_ratio=hp_ratio,
        )

        # Route decision through escalation engine
        context = DecisionContext(**context_data)
        decision = self.escalation.route_decision(context)

        # Generate response
        response = self.character.get_class_response(scenario_type, description)

        # Store memory
        memory_importance = 5.0 + context_data["stakes"] * 3
        self.memory.store_episodic(
            f"{scenario_type.value.title()}: {description}",
            importance=memory_importance,
            emotional_valence=0.5 if allies_present else -0.2,
        )

        # Record outcome
        result = DecisionResult(
            decision_id=f"dec_{self.session_count}",
            source=decision.source,
            action=response,
            confidence=decision.confidence_required,
            time_taken_ms=100,
            cost_estimate=0.0,
        )
        self.escalation.record_decision(result)
        self.escalation.record_outcome(result.decision_id, success=True)

        return decision.source, response, memory_importance

    def meet_npc(self, name: str, location: str, impression: str = "") -> None:
        """Record meeting an NPC."""
        self.character.meet_npc(name, location, impression)

        # Store in memory
        self.memory.store_episodic(
            f"Met {name} at {location}" + (f": {impression}" if impression else ""),
            importance=6.0,
            emotional_valence=0.3,
            participants=[name],
            location=location,
        )

    def record_combat(
        self,
        enemies: list,
        location: str,
        victory: bool,
        tactics: list,
        lessons: list,
        difficulty: float,
    ) -> None:
        """Record a combat encounter."""
        self.character.record_combat(enemies, location, victory, tactics, lessons, difficulty)

        # Store in memory
        outcome = "victory" if victory else "defeat"
        importance = 8.0 + difficulty * 2
        valence = 0.8 if victory else -0.5

        self.memory.store_episodic(
            f"Combat at {location}: Fought {', '.join(enemies)}. Result: {outcome}.",
            importance=importance,
            emotional_valence=valence,
            location=location,
        )

        # Store lessons learned
        for lesson in lessons:
            self.memory.store_semantic(
                f"Combat lesson: {lesson}",
                importance=6.0,
                emotional_valence=0.3,
            )

    def visit_location(self, name: str, location_type: str, event: str = "") -> None:
        """Record visiting a location."""
        self.character.visit_location(name, location_type, event)

        self.memory.store_episodic(
            f"Visited {name} ({location_type})" + (f": {event}" if event else ""),
            importance=5.0,
            emotional_valence=0.2,
            location=name,
        )

    def reflect(self) -> None:
        """Run consolidation and reflect on experiences."""
        engine = ConsolidationEngine()

        if self.memory.should_consolidate_reflection():
            result = engine.consolidate(self.memory, strategy="reflection", force=True)
            print(f"  → Consolidated {result.output_count} reflections")

        if self.memory.should_consolidate_episodic():
            result = engine.consolidate(self.memory, strategy="episodic_semantic", force=True)
            print(f"  → Consolidated {result.input_count} episodes into {result.output_count} patterns")

    def get_character_sheet(self) -> str:
        """Get a formatted character sheet."""
        c = self.character
        sheet = f"""
╔════════════════════════════════════════════════════════════╗
║                      CHARACTER SHEET                       ║
╠════════════════════════════════════════════════════════════╣
║  Name: {c.name:<40} Race: {c.race:<10} ║
║  Class: {c.char_class.value:<15} Level: {c.level:<5} Alignment: {c.alignment.value:<15} ║
╠════════════════════════════════════════════════════════════╣
║  STR  DEX  CON  INT  WIS  CHA                              ║
║  {c.stats.strength:>3}   {c.stats.dex:>3}   {c.stats.con:>3}   {c.stats.int:>3}   {c.stats.wis:>3}   {c.stats.cha:>3}                                          ║
╠════════════════════════════════════════════════════════════╣
║  HP: {c.hit_points:<50} Proficiency: +{c.proficiency_bonus:<3}          ║
║  Initiative: +{c.get_initiative():<43} Passive Per: {c.get_passive_perception():<3}       ║
╠════════════════════════════════════════════════════════════╣
║  BACKGROUND: {c.background:<34}                    ║
║                                                          ║
║  GOALS:                                                  ║
"""
        for i, goal in enumerate(c.goals, 1):
            sheet += f"║    {i}. {goal:<50} ║\n"

        sheet += "╚════════════════════════════════════════════════════════════╝"
        return sheet


def run_adventure(character: DnDCharacterAgent) -> None:
    """Run a sample adventure with the character."""
    print_section("Starting Adventure")

    # Scene 1: Arriving at town
    print_subsection("Scene 1: Arrival at Crossroads Inn")
    character.visit_location("Crossroads Inn", "tavern", "First stop on the journey")
    source, response, imp = character.process_scenario(
        ScenarioType.SOCIAL,
        "You enter the Crossroads Inn. It's bustling with activity.",
        allies_present=False,
    )
    print(f"  Action ({source.value}): {response}")

    character.meet_npc("Goblin Keeper", "Crossroads Inn", "Gruff but friendly innkeeper")
    character.meet_npc("Mysterious Stranger", "Crossroads Inn", "Hooded figure in corner")

    simulate_delay()

    # Scene 2: Information gathering
    print_subsection("Scene 2: Gathering Information")
    source, response, imp = character.process_scenario(
        ScenarioType.INVESTIGATION,
        "You hear rumors of goblin attacks on nearby trade routes.",
        allies_present=False,
    )
    print(f"  Action ({source.value}): {response}")

    simulate_delay()

    # Scene 3: Combat encounter
    print_subsection("Scene 3: Goblin Ambush!")
    character.visit_location("Forest Trail", "wilderness", "Ambush site")

    source, response, imp = character.process_scenario(
        ScenarioType.COMBAT,
        "Goblins jump out from the bushes! There are four of them.",
        allies_present=True,
        hp_ratio=1.0,
    )
    print(f"  Action ({source.value}): {response}")

    # Record combat
    character.record_combat(
        enemies=["Goblin Scout", "Goblin Warrior", "Goblin Archer", "Goblin Shaman"],
        location="Forest Trail",
        victory=True,
        tactics=["Used sword and shield", "Protected allies"],
        lessons=["Goblins attack from ambush", "Always be ready"],
        difficulty=0.4,
    )

    simulate_delay()

    # Scene 4: Post-combat
    print_subsection("Scene 4: Aftermath")
    source, response, imp = character.process_scenario(
        ScenarioType.SOCIAL,
        "The party catches their breath and tends to wounds.",
        allies_present=True,
        hp_ratio=0.8,
    )
    print(f"  Action ({source.value}): {response}")

    simulate_delay()

    # Scene 5: Finding treasure
    print_subsection("Scene 5: Discovery")
    source, response, imp = character.process_scenario(
        ScenarioType.EXPLORATION,
        "You find a hidden chest in the goblin camp.",
        allies_present=True,
    )
    print(f"  Action ({source.value}): {response}")

    character.visit_location("Goblin Camp", "dungeon", "Found treasure")

    simulate_delay()

    # Scene 6: Diplomacy
    print_subsection("Scene 6: Return to Town")
    source, response, imp = character.process_scenario(
        ScenarioType.DIPLOMACY,
        "You report the goblin threat to the town guard.",
        allies_present=False,
    )
    print(f"  Action ({source.value}): {response}")

    simulate_delay()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="D&D Character Example")
    parser.add_argument(
        "character",
        nargs="?",
        choices=["fighter", "rogue", "wizard"],
        default="fighter",
        help="Character class to play",
    )
    args = parser.parse_args()

    print_section("D&D Character - Integration Example 2")

    # Update config based on character choice
    with open("character.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Set the character class
    config["character"]["class"] = args.character.title()

    # Adjust stats based on class
    if args.character == "fighter":
        config["character"]["stats"] = {
            "strength": 16, "dexterity": 12, "constitution": 14,
            "intelligence": 10, "wisdom": 13, "charisma": 14,
        }
        config["character"]["personality"] = {
            "openness": 0.6, "conscientiousness": 0.8,
            "extraversion": 0.7, "agreeableness": 0.6, "neuroticism": 0.3,
        }
    elif args.character == "rogue":
        config["character"]["stats"] = {
            "strength": 10, "dexterity": 16, "constitution": 12,
            "intelligence": 12, "wisdom": 12, "charisma": 14,
        }
        config["character"]["personality"] = {
            "openness": 0.8, "conscientiousness": 0.5,
            "extraversion": 0.4, "agreeableness": 0.4, "neuroticism": 0.5,
        }
    elif args.character == "wizard":
        config["character"]["stats"] = {
            "strength": 8, "dexterity": 12, "constitution": 12,
            "intelligence": 16, "wisdom": 14, "charisma": 12,
        }
        config["character"]["personality"] = {
            "openness": 0.9, "conscientiousness": 0.8,
            "extraversion": 0.3, "agreeableness": 0.5, "neuroticism": 0.4,
        }

    # Save updated config
    with open("character.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Initialize character
    print(f"Initializing {args.character.title()} character...")
    character = DnDCharacterAgent("character.yaml")

    print(character.get_character_sheet())

    # Run adventure
    run_adventure(character)

    # Show summary
    print_section("Adventure Summary")

    summary = character.character.get_summary()
    print(f"  Character: {summary['name']}")
    print(f"  NPCs Met: {summary['npcs_met']}")
    print(f"  Locations Visited: {summary['locations_visited']}")
    print(f"  Combats: {summary['combats']} (Victories: {summary['combats_won']})")
    print()

    # Show decisions
    escalation_stats = character.escalation.get_global_stats()
    print("  Decisions Made:")
    print(f"    Bot (Rules):   {escalation_stats['bot_decisions']}")
    print(f"    Brain (LLM):   {escalation_stats['brain_decisions']}")
    print(f"    Human (API):   {escalation_stats['human_decisions']}")

    # Show memories
    print()
    print_subsection("Important Memories")
    important = character.memory.get_important(threshold=5.0, top_k=5)
    for mem in important:
        print_memory(mem, show_details=True)

    # Show NPCs
    print()
    print_subsection("NPCs Met")
    for name, npc in character.character.npcs.items():
        trust = ""
        if npc.trust_level > 0.7:
            trust = ""
        elif npc.trust_level < 0.3:
            trust = ""
        print(f"  {name}: {npc.relationship} {trust}")

    # Show locations
    print()
    print_subsection("Locations Visited")
    for name, loc in character.character.locations.items():
        print(f"  {name} ({loc.type}) - Visited {loc.visited_count}x")

    # Run consolidation
    print()
    print_subsection("Memory Consolidation")
    character.reflect()

    # Generate narrative
    print()
    print_subsection("Character's Adventure Narrative")
    narrative = character.memory.generate_narrative()
    print(f"  Coherence: {narrative.coherence_score:.2f}")
    print(f"  Themes: {', '.join(narrative.key_themes)}")
    print()
    for line in narrative.narrative.split("\n")[:8]:
        print(f"  {line}")

    print()
    print_section("Adventure Complete!")


if __name__ == "__main__":
    main()
