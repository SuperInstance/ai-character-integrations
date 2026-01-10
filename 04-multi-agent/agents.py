"""
Multi-Agent System - Agent Definitions

Defines specialized agent classes that work together
to accomplish complex tasks.
"""

from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import random


class AgentRole(Enum):
    """Roles that agents can have."""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"


class TaskStatus(Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELEGATED = "delegated"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """A task that can be assigned to an agent."""
    task_id: str
    description: str
    required_role: AgentRole
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Any] = None
    subtasks: List["Task"] = field(default_factory=list)
    created_by: Optional[str] = None
    estimated_effort: float = 1.0  # 0-10 scale

    def can_start(self, completed_tasks: Set[str]) -> bool:
        """Check if task can start (dependencies met)."""
        return all(dep in completed_tasks for dep in self.dependencies)


@dataclass
class AgentCapability:
    """A capability that an agent possesses."""
    name: str
    proficiency: float  # 0-1
    description: str


class BaseAgent:
    """
    Base class for all agents in the multi-agent system.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: AgentRole,
        capabilities: Optional[List[AgentCapability]] = None,
        personality: Optional[Dict[str, float]] = None,
    ):
        """
        Initialize an agent.

        Args:
            agent_id: Unique identifier
            name: Human-readable name
            role: Agent's primary role
            capabilities: List of capabilities
            personality: Personality traits (0-1)
        """
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.personality = personality or {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.3,
        }

        # Agent state
        self.current_task: Optional[Task] = None
        self.completed_tasks: List[Task] = []
        self.messages: List[Dict] = []

    def can_handle(self, task: Task) -> float:
        """
        Determine if this agent can handle a task.

        Returns:
            Confidence score (0-1)
        """
        if task.required_role == self.role:
            return 0.9

        # Check for relevant capabilities
        task_desc = task.description.lower()
        capability_match = 0.0
        for cap in self.capabilities:
            if cap.name.lower() in task_desc:
                capability_match = max(capability_match, cap.proficiency)

        return capability_match

    def receive_task(self, task: Task) -> bool:
        """
        Receive a task assignment.

        Returns:
            True if task accepted
        """
        if self.current_task is not None:
            return False

        self.current_task = task
        task.assigned_to = self.agent_id
        task.status = TaskStatus.IN_PROGRESS
        return True

    def complete_task(self, result: Any = None) -> Task:
        """Complete the current task."""
        if self.current_task is None:
            raise RuntimeError("No task to complete")

        self.current_task.status = TaskStatus.COMPLETED
        self.current_task.result = result
        completed = self.current_task
        self.completed_tasks.append(completed)
        self.current_task = None
        return completed

    def delegate_task(self, task: Task, target_role: AgentRole) -> Task:
        """Delegate a task to another role."""
        task.required_role = target_role
        task.status = TaskStatus.DELEGATED
        return task

    def send_message(self, to: str, content: str, message_type: str = "info") -> None:
        """Send a message to another agent."""
        self.messages.append({
            "from": self.agent_id,
            "to": to,
            "content": content,
            "type": message_type,
        })

    def get_response(self, prompt: str) -> str:
        """Generate a response based on agent's personality."""
        responses = []

        # Role-based responses
        if self.role == AgentRole.COORDINATOR:
            responses = [
                f"I'll coordinate this task. Let me assess the requirements and delegate appropriately.",
                f"Received. I'm analyzing the optimal approach for this task.",
                f"I'll oversee this. Let me ensure all resources are properly allocated.",
            ]
        elif self.role == AgentRole.RESEARCHER:
            responses = [
                f"I'll research this thoroughly. Let me gather relevant information.",
                f"Interesting query. I'll investigate and provide comprehensive findings.",
                f"I'll analyze the available data and synthesize key insights.",
            ]
        elif self.role == AgentRole.PLANNER:
            responses = [
                f"I'll develop a structured plan for this. Let me break it down into steps.",
                f"Planning mode activated. I'll create a roadmap with milestones.",
                f"I'll assess requirements and create an actionable strategy.",
            ]
        elif self.role == AgentRole.EXECUTOR:
            responses = [
                f"On it. I'll execute this task efficiently.",
                f"Executing. I'll focus on practical implementation.",
                f"I'll get this done. Let me take action now.",
            ]
        elif self.role == AgentRole.REVIEWER:
            responses = [
                f"I'll review this carefully. Let me check for quality and completeness.",
                f"I'll validate the work against requirements.",
                f"I'll provide feedback and ensure standards are met.",
            ]

        base = random.choice(responses)

        # Add personality touches
        if self.personality["openness"] > 0.7:
            base += " I'm open to alternative approaches if needed."
        if self.personality["conscientiousness"] > 0.7:
            base += " I'll ensure all details are covered."

        return base


class CoordinatorAgent(BaseAgent):
    """Coordinates tasks between other agents."""

    def __init__(self, agent_id: str = "coordinator"):
        capabilities = [
            AgentCapability("task_delegation", 0.95, "Assign tasks to appropriate agents"),
            AgentCapability("prioritization", 0.9, "Prioritize tasks effectively"),
            AgentCapability("monitoring", 0.85, "Track progress of all tasks"),
            AgentCapability("communication", 0.9, "Facilitate agent communication"),
        ]
        super().__init__(
            agent_id=agent_id,
            name="Coordinator",
            role=AgentRole.COORDINATOR,
            capabilities=capabilities,
            personality={
                "openness": 0.6,
                "conscientiousness": 0.9,
                "extraversion": 0.7,
                "agreeableness": 0.6,
                "neuroticism": 0.2,
            },
        )

    def assess_task(self, task: Task, available_agents: List[BaseAgent]) -> Dict[str, Any]:
        """
        Assess a task and determine how to route it.

        Returns:
            Assessment dict with routing recommendations
        """
        # Find best agent for this task
        best_agent = None
        best_score = 0.0

        for agent in available_agents:
            if agent.agent_id == self.agent_id:
                continue
            score = agent.can_handle(task)
            if score > best_score:
                best_score = score
                best_agent = agent

        # Check if task needs to be broken down
        complexity = task.estimated_effort
        needs_breakdown = complexity > 5.0

        return {
            "task_id": task.task_id,
            "recommended_agent": best_agent.agent_id if best_agent else None,
            "confidence": best_score,
            "needs_breakdown": needs_breakdown,
            "estimated_duration": complexity * 2,  # hours
        }


class ResearcherAgent(BaseAgent):
    """Gathers and synthesizes information."""

    def __init__(self, agent_id: str = "researcher"):
        capabilities = [
            AgentCapability("research", 0.95, "Gather information from sources"),
            AgentCapability("analysis", 0.9, "Analyze data and findings"),
            AgentCapability("synthesis", 0.85, "Synthesize insights from data"),
            AgentCapability("fact_checking", 0.9, "Verify facts and sources"),
        ]
        super().__init__(
            agent_id=agent_id,
            name="Researcher",
            role=AgentRole.RESEARCHER,
            capabilities=capabilities,
            personality={
                "openness": 0.9,
                "conscientiousness": 0.8,
                "extraversion": 0.4,
                "agreeableness": 0.6,
                "neuroticism": 0.3,
            },
        )

    def research(self, topic: str) -> Dict[str, Any]:
        """Perform research on a topic."""
        # Simulate research process
        findings = {
            "topic": topic,
            "sources_consulted": random.randint(5, 15),
            "key_points": [
                f"Key finding about {topic}",
                f"Important aspect of {topic}",
                f"Critical consideration for {topic}",
            ],
            "confidence": random.uniform(0.7, 0.95),
        }
        return findings


class PlannerAgent(BaseAgent):
    """Develops plans and strategies."""

    def __init__(self, agent_id: str = "planner"):
        capabilities = [
            AgentCapability("planning", 0.95, "Create detailed plans"),
            AgentCapability("scheduling", 0.9, "Schedule tasks and milestones"),
            AgentCapability("resource_allocation", 0.85, "Allocate resources efficiently"),
            AgentCapability("risk_assessment", 0.8, "Identify and mitigate risks"),
        ]
        super().__init__(
            agent_id=agent_id,
            name="Planner",
            role=AgentRole.PLANNER,
            capabilities=capabilities,
            personality={
                "openness": 0.5,
                "conscientiousness": 0.95,
                "extraversion": 0.3,
                "agreeableness": 0.7,
                "neuroticism": 0.4,
            },
        )

    def create_plan(self, task: Task) -> List[Task]:
        """Create a plan with subtasks."""
        subtasks = []
        steps = [
            ("Analyze requirements", AgentRole.RESEARCHER, 1.0),
            ("Develop approach", AgentRole.PLANNER, 2.0),
            ("Execute implementation", AgentRole.EXECUTOR, 3.0),
            ("Review and validate", AgentRole.REVIEWER, 1.0),
        ]

        for i, (desc, role, effort) in enumerate(steps):
            subtask = Task(
                task_id=f"{task.task_id}.sub{i+1}",
                description=f"{desc} for: {task.description}",
                required_role=role,
                priority=task.priority,
                estimated_effort=effort,
                created_by=self.agent_id,
            )
            subtasks.append(subtask)

        return subtasks


class ExecutorAgent(BaseAgent):
    """Executes tasks and takes action."""

    def __init__(self, agent_id: str = "executor"):
        capabilities = [
            AgentCapability("execution", 0.95, "Execute tasks efficiently"),
            AgentCapability("implementation", 0.9, "Implement solutions"),
            AgentCapability("troubleshooting", 0.8, "Resolve issues as they arise"),
            AgentCapability("optimization", 0.75, "Optimize processes"),
        ]
        super().__init__(
            agent_id=agent_id,
            name="Executor",
            role=AgentRole.EXECUTOR,
            capabilities=capabilities,
            personality={
                "openness": 0.4,
                "conscientiousness": 0.85,
                "extraversion": 0.6,
                "agreeableness": 0.5,
                "neuroticism": 0.3,
            },
        )

    def execute(self, task: Task) -> Dict[str, Any]:
        """Execute a task."""
        return {
            "task_id": task.task_id,
            "status": "completed",
            "result": f"Executed: {task.description}",
            "time_taken": task.estimated_effort * random.uniform(0.8, 1.2),
        }


class ReviewerAgent(BaseAgent):
    """Reviews and validates work."""

    def __init__(self, agent_id: str = "reviewer"):
        capabilities = [
            AgentCapability("review", 0.95, "Review work thoroughly"),
            AgentCapability("validation", 0.9, "Validate against requirements"),
            AgentCapability("quality_assurance", 0.85, "Ensure quality standards"),
            AgentCapability("feedback", 0.9, "Provide constructive feedback"),
        ]
        super().__init__(
            agent_id=agent_id,
            name="Reviewer",
            role=AgentRole.REVIEWER,
            capabilities=capabilities,
            personality={
                "openness": 0.6,
                "conscientiousness": 0.95,
                "extraversion": 0.3,
                "agreeableness": 0.6,
                "neuroticism": 0.5,
            },
        )

    def review(self, work: Any, requirements: str) -> Dict[str, Any]:
        """Review work against requirements."""
        issues_found = random.randint(0, 3)
        return {
            "passed": issues_found == 0,
            "issues": [f"Issue {i+1}" for i in range(issues_found)],
            "suggestions": [
                "Consider optimizing for performance",
                "Documentation could be clearer",
            ][:random.randint(0, 2)],
            "approval": "approved" if issues_found == 0 else "needs_revision",
        }


def create_agent_team() -> List[BaseAgent]:
    """Create a team of specialized agents."""
    return [
        CoordinatorAgent(),
        ResearcherAgent(),
        PlannerAgent(),
        ExecutorAgent(),
        ReviewerAgent(),
    ]
