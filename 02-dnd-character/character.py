#!/usr/bin/env python3
"""
D&D Character Class

Implements a fully featured D&D character with:
- Personality-driven decisions
- Hierarchical memory (NPCs, locations, events)
- Class-specific behavior patterns
- Learning and growth

Used by Example 2: D&D Character
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class CharacterClass(Enum):
    """D&D Character classes."""
    FIGHTER = "Fighter"
    ROGUE = "Rogue"
    WIZARD = "Wizard"
    CLERIC = "Cleric"
    RANGER = "Ranger"
    BARBARIAN = "Barbarian"
    BARD = "Bard"
    DRUID = "Druid"
    MONK = "Monk"
    PALADIN = "Paladin"
    SORCERER = "Sorcerer"
    WARLOCK = "Warlock"


class Alignment(Enum):
    """D&D Alignments."""
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"


class ScenarioType(Enum):
    """Types of scenarios in D&D."""
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    PUZZLE = "puzzle"
    INVESTIGATION = "investigation"
    DIPLOMACY = "diplomacy"
    STEALTH = "stealth"


@dataclass
class CharacterStats:
    """Ability scores."""
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def get_modifier(self, stat: str) -> int:
        """Get ability modifier."""
        value = getattr(self, stat.lower(), 10)
        return (value - 10) // 2

    def get_save_dc(self, stat: str, proficiency_bonus: int = 3) -> int:
        """Get save DC for a stat."""
        return 8 + proficiency_bonus + self.get_modifier(stat)


@dataclass
class Personality:
    """Big Five personality traits (0.0 - 1.0)."""
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5


@dataclass
class NPCMemory:
    """Memory of an NPC."""
    name: str
    location: str
    relationship: str  # friend, enemy, neutral, unknown
    notes: List[str] = field(default_factory=list)
    last_seen: Optional[str] = None
    trust_level: float = 0.5  # 0 = distrusts, 1 = trusts


@dataclass
class LocationMemory:
    """Memory of a location."""
    name: str
    type: str  # tavern, dungeon, town, wilderness, etc.
    visited_count: int = 1
    events: List[str] = field(default_factory=list)
    loot_found: List[str] = field(default_factory=list)
    dangers: List[str] = field(default_factory=list)


@dataclass
class CombatMemory:
    """Memory of a combat encounter."""
    enemies: List[str]
    location: str
    victory: bool
    tactics_used: List[str]
    lessons_learned: List[str]
    difficulty: float  # 0 = easy, 1 = nearly fatal


class DnDCharacter:
    """
    A fully-featured D&D character with personality, memory, and
    class-specific decision patterns.
    """

    def __init__(
        self,
        name: str,
        char_class: CharacterClass,
        race: str,
        level: int = 1,
        stats: Optional[CharacterStats] = None,
        personality: Optional[Personality] = None,
        alignment: Alignment = Alignment.TRUE_NEUTRAL,
        background: str = "",
        backstory: str = "",
        goals: Optional[List[str]] = None,
    ):
        """
        Initialize the character.

        Args:
            name: Character name
            char_class: Character class
            race: Character race
            level: Character level (1-20)
            stats: Ability scores
            personality: Big Five personality traits
            alignment: D&D alignment
            background: Character background
            backstory: Character backstory
            goals: List of character goals
        """
        self.name = name
        self.char_class = char_class
        self.race = race
        self.level = level
        self.alignment = alignment
        self.background = background
        self.backstory = backstory
        self.goals = goals or []

        # Initialize components
        self.stats = stats or CharacterStats()
        self.personality = personality or Personality()

        # Memory systems
        self.npcs: Dict[str, NPCMemory] = {}
        self.locations: Dict[str, LocationMemory] = {}
        self.combat_history: List[CombatMemory] = []

        # Derived stats
        self.proficiency_bonus = 2 + (level // 4)
        self.hit_points = self._calculate_hp()

    def _calculate_hp(self) -> int:
        """Calculate hit points based on class and level."""
        hit_dice = {
            CharacterClass.FIGHTER: 10,
            CharacterClass.ROGUE: 8,
            CharacterClass.WIZARD: 6,
            CharacterClass.CLERIC: 8,
            CharacterClass.RANGER: 10,
            CharacterClass.BARBARIAN: 12,
            CharacterClass.BARD: 8,
            CharacterClass.DRUID: 8,
            CharacterClass.MONK: 8,
            CharacterClass.PALADIN: 10,
            CharacterClass.SORCERER: 6,
            CharacterClass.WARLOCK: 8,
        }

        hit_die = hit_dice.get(self.char_class, 8)
        con_mod = self.stats.get_modifier("constitution")

        # Max at first level, average after
        hp = hit_die + con_mod
        for _ in range(1, self.level):
            hp += (hit_die // 2) + 1 + con_mod

        return max(1, hp)

    def get_initiative(self) -> int:
        """Get initiative bonus."""
        return self.stats.get_modifier("dexterity")

    def get_passive_perception(self) -> int:
        """Get passive perception."""
        return 10 + self.stats.get_modifier("wisdom")

    def get_passive_investigation(self) -> int:
        """Get passive investigation."""
        return 10 + self.stats.get_modifier("intelligence")

    def meet_npc(self, name: str, location: str, first_impression: str = "") -> None:
        """
        Record meeting a new NPC.

        Args:
            name: NPC name
            location: Where they met
            first_impression: Initial notes about the NPC
        """
        if name not in self.npcs:
            self.npcs[name] = NPCMemory(
                name=name,
                location=location,
                relationship="unknown",
                notes=[first_impression] if first_impression else [],
                trust_level=0.5,
            )

    def update_npc_relationship(self, name: str, relationship: str, trust_delta: float = 0.0) -> None:
        """
        Update relationship with an NPC.

        Args:
            name: NPC name
            relationship: New relationship (friend, enemy, ally, etc.)
            trust_delta: Change in trust level
        """
        if name in self.npcs:
            self.npcs[name].relationship = relationship
            self.npcs[name].trust_level = max(0, min(1, self.npcs[name].trust_level + trust_delta))

    def visit_location(self, name: str, location_type: str, event: str = "") -> None:
        """
        Record visiting a location.

        Args:
            name: Location name
            location_type: Type of location
            event: Event that occurred
        """
        if name not in self.locations:
            self.locations[name] = LocationMemory(name=name, type=location_type)

        self.locations[name].visited_count += 1
        if event:
            self.locations[name].events.append(event)

    def record_combat(
        self,
        enemies: List[str],
        location: str,
        victory: bool,
        tactics: List[str],
        lessons: List[str],
        difficulty: float,
    ) -> None:
        """
        Record a combat encounter.

        Args:
            enemies: List of enemy names
            location: Where combat occurred
            victory: Whether the party won
            tactics: Tactics used
            lessons: Lessons learned
            difficulty: Encounter difficulty
        """
        combat = CombatMemory(
            enemies=enemies,
            location=location,
            victory=victory,
            tactics_used=tactics,
            lessons_learned=lessons,
            difficulty=difficulty,
        )
        self.combat_history.append(combat)

    def get_decision_context(
        self,
        scenario: ScenarioType,
        description: str,
        urgency_ms: Optional[int] = None,
        allies_present: bool = True,
        hp_ratio: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Get decision context for escalation engine.

        Args:
            scenario: Type of scenario
            description: Situation description
            urgency_ms: Time constraint
            allies_present: Whether allies are present
            hp_ratio: Current HP ratio (0-1)

        Returns:
            Context dictionary for decision making
        """
        # Base urgency by scenario type
        base_urgency = {
            ScenarioType.COMBAT: 500,
            ScenarioType.SOCIAL: 2000,
            ScenarioType.EXPLORATION: 1000,
            ScenarioType.PUZZLE: 5000,
            ScenarioType.INVESTIGATION: 3000,
            ScenarioType.DIPLOMACY: 2000,
            ScenarioType.STEALTH: 1000,
        }

        # Class-specific adjustments
        class_urgency_mod = {
            CharacterClass.FIGHTER: -200,  # Fighters act faster
            CharacterClass.ROGUE: 0,       # Rogues are balanced
            CharacterClass.WIZARD: 500,    # Wizards take time to think
        }

        final_urgency = urgency_ms or base_urgency.get(scenario, 1000)
        final_urgency += class_urgency_mod.get(self.char_class, 0)

        # Calculate stakes based on HP and scenario
        stakes = 0.5
        if scenario == ScenarioType.COMBAT:
            stakes = 0.5 + (1.0 - hp_ratio) * 0.4  # Higher stakes when hurt
        elif scenario == ScenarioType.SOCIAL:
            stakes = 0.3 + self.personality.extraversion * 0.2
        elif scenario == ScenarioType.DIPLOMACY:
            stakes = 0.6 + self.personality.agreeableness * 0.2

        return {
            "character_id": self.name,
            "scenario_type": scenario.value,
            "situation_description": description,
            "stakes": min(1.0, stakes),
            "urgency_ms": max(100, final_urgency),
            "character_hp_ratio": hp_ratio,
            "allies_present": allies_present,
            "class": self.char_class.value,
            "personality": {
                "openness": self.personality.openness,
                "conscientiousness": self.personality.conscientiousness,
                "extraversion": self.personality.extraversion,
                "agreeableness": self.personality.agreeableness,
                "neuroticism": self.personality.neuroticism,
            },
        }

    def get_class_response(self, scenario: ScenarioType, context: str) -> str:
        """
        Generate a class-specific response.

        Args:
            scenario: Type of scenario
            context: Additional context

        Returns:
            Character's response/action
        """
        if self.char_class == CharacterClass.FIGHTER:
            return self._fighter_response(scenario, context)
        elif self.char_class == CharacterClass.ROGUE:
            return self._rogue_response(scenario, context)
        elif self.char_class == CharacterClass.WIZARD:
            return self._wizard_response(scenario, context)
        else:
            return self._generic_response(scenario, context)

    def _fighter_response(self, scenario: ScenarioType, context: str) -> str:
        """Fighter-specific responses."""
        if scenario == ScenarioType.COMBAT:
            if self.stats.strength >= 14:
                return f"{self.name} draws their weapon and charges forward with a battle cry!"
            else:
                return f"{self.name} assumes a defensive fighting stance, shield ready."

        elif scenario == ScenarioType.SOCIAL:
            if self.personality.extraversion > 0.6:
                return f"{self.name} speaks bluntly but with good intent."
            else:
                return f"{self.name} remains quiet, observing the room."

        elif scenario == ScenarioType.DIPLOMACY:
            return f"{self.name} stands firm, guided by a strong sense of honor."

        return f"{self.name} considers the situation carefully."

    def _rogue_response(self, scenario: ScenarioType, context: str) -> str:
        """Rogue-specific responses."""
        if scenario == ScenarioType.COMBAT:
            if "surprise" in context.lower():
                return f"{self.name} uses the element of surprise to strike from the shadows!"
            else:
                return f"{self.name} looks for tactical advantages and flanking opportunities."

        elif scenario == ScenarioType.STEALTH:
            return f"{self.name} moves silently through the shadows, unnoticed."

        elif scenario == ScenarioType.SOCIAL:
            return f"{self.name} watches for opportunities and assesses who might have information."

        return f"{self.name} calculates the risks and potential rewards."

    def _wizard_response(self, scenario: ScenarioType, context: str) -> str:
        """Wizard-specific responses."""
        if scenario == ScenarioType.COMBAT:
            return f"{self.name} assesses the enemies' weaknesses and prepares an appropriate spell."

        elif scenario == ScenarioType.PUZZLE:
            return f"{self.name} studies the puzzle carefully, recalling arcane knowledge."

        elif scenario == ScenarioType.INVESTIGATION:
            return f"{self.name} uses keen intellect to piece together clues."

        elif scenario == ScenarioType.SOCIAL:
            return f"{self.name} speaks with precision and scholarly authority."

        return f"{self.name} contemplates the situation with magical curiosity."

    def _generic_response(self, scenario: ScenarioType, context: str) -> str:
        """Generic responses for other classes."""
        return f"{self.name} approaches the {scenario.value} scenario thoughtfully."

    def get_summary(self) -> Dict[str, Any]:
        """Get a character summary."""
        return {
            "name": self.name,
            "race": self.race,
            "class": self.char_class.value,
            "level": self.level,
            "alignment": self.alignment.value,
            "hp": self.hit_points,
            "npcs_met": len(self.npcs),
            "locations_visited": len(self.locations),
            "combats": len(self.combat_history),
            "combats_won": sum(1 for c in self.combat_history if c.victory),
            "personality": {
                "openness": self.personality.openness,
                "conscientiousness": self.personality.conscientiousness,
                "extraversion": self.personality.extraversion,
                "agreeableness": self.personality.agreeableness,
                "neuroticism": self.personality.neuroticism,
            },
        }
