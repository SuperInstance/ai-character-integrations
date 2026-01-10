#!/usr/bin/env python3
"""
Multi-Agent Team - Integration Example 4

A coordinated system showing:
- Multiple specialized agents working together
- Task delegation based on capabilities
- Shared knowledge base
- Collaborative problem solving

Run: python main.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from coordinator import MultiAgentCoordinator
from agents import Task, TaskPriority, AgentRole
from shared.utils import print_section, print_subsection, simulate_delay


def demonstrate_basic_tasks(coordinator: MultiAgentCoordinator) -> None:
    """Demonstrate basic task handling."""
    print_subsection("Basic Task Execution")

    # Submit various tasks
    tasks = [
        ("Research the latest AI trends", TaskPriority.HIGH, AgentRole.RESEARCHER, 3.0),
        ("Plan a project timeline", TaskPriority.MEDIUM, AgentRole.PLANNER, 4.0),
        ("Execute data processing", TaskPriority.MEDIUM, AgentRole.EXECUTOR, 2.0),
        ("Review the documentation", TaskPriority.LOW, AgentRole.REVIEWER, 1.5),
    ]

    for desc, priority, role, effort in tasks:
        task = coordinator.submit_task(desc, priority, role, effort)
        print(f"  Submitted: {desc} (Priority: {priority.name})")

    print()
    coordinator.process_all()


def demonstrate_complex_workflow(coordinator: MultiAgentCoordinator) -> None:
    """Demonstrate a complex multi-step workflow."""
    print_subsection("Complex Workflow: Product Launch")

    # A product launch requires multiple agents
    workflow_tasks = [
        ("Research market conditions", TaskPriority.HIGH, AgentRole.RESEARCHER, 3.0),
        ("Analyze competitor strategies", TaskPriority.HIGH, AgentRole.RESEARCHER, 3.0),
        ("Develop launch strategy", TaskPriority.CRITICAL, AgentRole.PLANNER, 5.0),
        ("Create marketing materials", TaskPriority.MEDIUM, AgentRole.EXECUTOR, 4.0),
        ("Review launch plan", TaskPriority.HIGH, AgentRole.REVIEWER, 2.0),
        ("Execute launch campaign", TaskPriority.CRITICAL, AgentRole.EXECUTOR, 5.0),
        ("Monitor launch results", TaskPriority.MEDIUM, AgentRole.RESEARCHER, 2.0),
    ]

    for desc, priority, role, effort in workflow_tasks:
        coordinator.submit_task(desc, priority, role, effort)

    print(f"  Submitted {len(workflow_tasks)} tasks for product launch")
    print()
    coordinator.process_all()


def demonstrate_delegation(coordinator: MultiAgentCoordinator) -> None:
    """Demonstrate task delegation."""
    print_subsection("Task Delegation")

    # Submit a large task that requires coordination
    task = coordinator.submit_task(
        "Implement new feature with research, planning, and review",
        TaskPriority.HIGH,
        AgentRole.COORDINATOR,
        estimated_effort=8.0,
    )

    print(f"  Submitted complex task requiring coordination")
    print()
    coordinator.process_all()


def show_agent_communication(coordinator: MultiAgentCoordinator) -> None:
    """Show communication between agents."""
    print_subsection("Agent Communication")

    for agent in coordinator.agents:
        if agent.messages:
            print(f"  {agent.name}:")
            for msg in agent.messages[:3]:
                print(f"    To {msg['to']}: {msg['content'][:60]}...")
            print()


def main():
    """Main entry point."""
    print_section("Multi-Agent Team - Integration Example 4")

    # Initialize coordinator
    print("Initializing multi-agent team...")
    coordinator = MultiAgentCoordinator("config.yaml")

    print("  Team Members:")
    for agent in coordinator.agents:
        print(f"    - {agent.name} ({agent.role.value})")
        print(f"      Capabilities: {', '.join(c.name for c in agent.capabilities)}")
    print()

    # Run demonstrations
    print_section("Demonstration 1: Basic Tasks")
    demonstrate_basic_tasks(coordinator)
    show_agent_communication(coordinator)

    simulate_delay()

    print_section("Demonstration 2: Complex Workflow")
    demonstrate_complex_workflow(coordinator)

    simulate_delay()

    print_section("Demonstration 3: Task Delegation")
    demonstrate_delegation(coordinator)

    # Show team status
    print_section("Team Status")

    status = coordinator.get_team_status()
    for agent_id, agent_status in status.items():
        print(f"  {agent_status['name']} ({agent_status['role']})")
        print(f"    Tasks Completed: {agent_status['completed_tasks']}")
        print(f"    Current Task: {agent_status['current_task'] or 'None'}")
        print()

    # Show summary
    print_section("Performance Summary")

    summary = coordinator.get_summary()
    print(f"  Total Tasks Submitted: {summary['total_tasks']}")
    print(f"  Tasks Completed: {summary['completed_tasks']}")
    print(f"  Tasks Pending: {summary['pending_tasks']}")
    print(f"  Team Utilization: {summary['team_utilization']:.1%}")
    print()

    # Show completed tasks by agent
    print_subsection("Tasks by Agent")
    for agent in coordinator.agents:
        if agent.completed_tasks:
            print(f"  {agent.name}:")
            for task in agent.completed_tasks[:3]:
                print(f"    - {task.description[:50]}...")
            if len(agent.completed_tasks) > 3:
                print(f"    ... and {len(agent.completed_tasks) - 3} more")
            print()

    # Run consolidation
    print_subsection("Memory Consolidation")
    coordinator.consolidate_memory()

    # Show shared knowledge
    print()
    print_subsection("Team Knowledge")
    important = coordinator.memory.get_important(threshold=5.0, top_k=5)
    for mem in important:
        print(f"  [{mem.importance:.1f}] {mem.content[:70]}...")

    # Show escalation stats
    print()
    print_subsection("Decision Routing")
    e_stats = coordinator.escalation.get_global_stats()
    print(f"  Total Decisions: {e_stats['total_decisions']}")
    print(f"  Success Rate: {e_stats['success_rate']:.1%}")

    print()
    print_section("Example Complete!")


if __name__ == "__main__":
    main()
