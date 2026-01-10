"""
Multi-Agent Coordinator

Orchestrates multiple agents to work together on tasks.
"""

from typing import List, Dict, Any, Optional, Set
from collections import deque
import time

try:
    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory
except ImportError:
    import sys
    from pathlib import Path

    escalation_path = Path(__file__).parent.parent.parent / "escalation-engine"
    memory_path = Path(__file__).parent.parent.parent / "hierarchical-memory"

    if str(escalation_path) not in sys.path:
        sys.path.insert(0, str(escalation_path))
    if str(memory_path / "src") not in sys.path:
        sys.path.insert(0, str(memory_path / "src"))

    from escalation_engine import EscalationEngine, DecisionContext, DecisionResult, DecisionSource
    from hierarchical_memory import HierarchicalMemory

from agents import (
    BaseAgent,
    CoordinatorAgent,
    Task,
    TaskStatus,
    TaskPriority,
    AgentRole,
    create_agent_team,
)


class MultiAgentCoordinator:
    """
    Coordinates multiple agents to work together on tasks.

    Features:
    - Task routing and delegation
    - Agent utilization tracking
    - Shared knowledge base
    - Inter-agent communication
    """

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the coordinator."""
        # Create agent team
        self.agents: List[BaseAgent] = create_agent_team()
        self.coordinator: CoordinatorAgent = self.agents[0]

        # Task management
        self.task_queue: deque[Task] = deque()
        self.completed_tasks: List[Task] = []
        self.completed_task_ids: Set[str] = set()

        # Shared memory
        self.memory = HierarchicalMemory(
            character_id="multi_agent_team",
        )

        # Escalation engine for decision routing
        self.escalation = EscalationEngine()

        # Metrics
        self.total_tasks = 0
        self.delegation_count = 0

    def submit_task(
        self,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        required_role: Optional[AgentRole] = None,
        estimated_effort: float = 1.0,
    ) -> Task:
        """
        Submit a new task to the team.

        Args:
            description: Task description
            priority: Task priority
            required_role: Required agent role (if any)
            estimated_effort: Estimated effort (0-10)

        Returns:
            Created task
        """
        self.total_tasks += 1
        task = Task(
            task_id=f"task-{self.total_tasks:04d}",
            description=description,
            required_role=required_role or AgentRole.EXECUTOR,
            priority=priority,
            estimated_effort=estimated_effort,
            created_by="user",
        )
        self.task_queue.append(task)

        # Store in shared memory
        self.memory.store_working(
            f"New task submitted: {description}",
            importance=5.0 + priority.value,
        )

        return task

    def process_next_task(self) -> Optional[Task]:
        """
        Process the next task in the queue.

        Returns:
            Completed task or None if no tasks
        """
        if not self.task_queue:
            return None

        task = self.task_queue.popleft()

        # Check dependencies
        if not task.can_start(self.completed_task_ids):
            # Put back in queue
            self.task_queue.append(task)
            return None

        # Route task to appropriate agent
        return self._route_and_execute(task)

    def _route_and_execute(self, task: Task) -> Task:
        """Route task to agent and execute."""
        # Get coordinator's assessment
        assessment = self.coordinator.assess_task(task, self.agents)

        # Find best agent
        best_agent = None
        if task.required_role:
            best_agent = self._get_agent_by_role(task.required_role)
        elif assessment["recommended_agent"]:
            best_agent = self._get_agent_by_id(assessment["recommended_agent"])

        if not best_agent:
            best_agent = self._get_available_agent()

        if not best_agent:
            # No agent available, queue for later
            self.task_queue.appendleft(task)
            return None

        # Execute task
        result = self._execute_with_agent(best_agent, task)

        # Store in memory
        self.memory.store_episodic(
            f"Agent {best_agent.name} completed task: {task.description}",
            importance=6.0,
            participants=[best_agent.name],
        )

        return result

    def _execute_with_agent(self, agent: BaseAgent, task: Task) -> Task:
        """Execute a task with a specific agent."""
        agent.receive_task(task)

        # Simulate work based on agent role
        if agent.role == AgentRole.RESEARCHER:
            result = agent.research(task.description)
        elif agent.role == AgentRole.PLANNER:
            subtasks = agent.create_plan(task)
            task.subtasks = subtasks
            result = {"subtasks_created": len(subtasks)}
        elif agent.role == AgentRole.EXECUTOR:
            result = agent.execute(task)
        elif agent.role == AgentRole.REVIEWER:
            result = agent.review(task, task.description)
        else:
            result = {"status": "coordinated"}

        agent.complete_task(result)
        self.completed_task_ids.add(task.task_id)
        self.completed_tasks.append(task)

        return task

    def _get_agent_by_role(self, role: AgentRole) -> Optional[BaseAgent]:
        """Get an available agent by role."""
        for agent in self.agents:
            if agent.role == role and agent.current_task is None:
                return agent
        return None

    def _get_agent_by_id(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID."""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def _get_available_agent(self) -> Optional[BaseAgent]:
        """Get any available agent."""
        for agent in self.agents:
            if agent.current_task is None:
                return agent
        return None

    def process_all(self) -> List[Task]:
        """Process all tasks in the queue."""
        results = []
        max_iterations = len(self.task_queue) * 2  # Prevent infinite loops

        while self.task_queue and max_iterations > 0:
            max_iterations -= 1
            result = self.process_next_task()
            if result:
                results.append(result)

        return results

    def get_team_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        return {
            agent.agent_id: {
                "name": agent.name,
                "role": agent.role.value,
                "current_task": agent.current_task.description if agent.current_task else None,
                "completed_tasks": len(agent.completed_tasks),
                "capabilities": [c.name for c in agent.capabilities],
            }
            for agent in self.agents
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of team performance."""
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.task_queue),
            "delegations": self.delegation_count,
            "team_utilization": self._calculate_utilization(),
        }

    def _calculate_utilization(self) -> float:
        """Calculate team utilization."""
        active = sum(1 for a in self.agents if a.current_task is not None)
        return active / len(self.agents)

    def consolidate_memory(self) -> None:
        """Run memory consolidation."""
        from hierarchical_memory import ConsolidationEngine

        engine = ConsolidationEngine()
        if self.memory.should_consolidate_reflection():
            result = engine.consolidate(self.memory, strategy="reflection", force=True)
            print(f"  Consolidated {result.output_count} reflection memories")

        if self.memory.should_consolidate_episodic():
            result = engine.consolidate(self.memory, strategy="episodic_semantic", force=True)
            print(f"  Consolidated {result.input_count} episodes into {result.output_count} patterns")
