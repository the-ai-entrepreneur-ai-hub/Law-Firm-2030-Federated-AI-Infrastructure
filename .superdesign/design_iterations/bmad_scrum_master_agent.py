#!/usr/bin/env python3
"""
BMAD-SCRUM-MASTER Agent
Advanced Scrum Master AI Agent for BMAD-METHOD Framework

This agent excels at sprint planning, backlog management, team coordination,
and agile process optimization within the BMAD framework ecosystem.
"""

import json
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SprintStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StoryStatus(Enum):
    BACKLOG = "backlog"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    BLOCKED = "blocked"

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class StoryPoint:
    """Story point estimation with confidence intervals"""
    estimate: int
    confidence: float  # 0-1 scale
    complexity_factors: Dict[str, int] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)

@dataclass
class DevelopmentStory:
    """Enhanced development story from BMAD context engineering"""
    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    story_points: Optional[StoryPoint] = None
    priority: Priority = Priority.MEDIUM
    status: StoryStatus = StoryStatus.BACKLOG
    assignee: Optional[str] = None
    epic_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    technical_requirements: Dict[str, Any] = field(default_factory=dict)
    context_tags: List[str] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)

@dataclass
class Sprint:
    """Sprint configuration and tracking"""
    id: str
    name: str
    goal: str
    start_date: datetime.date
    end_date: datetime.date
    status: SprintStatus = SprintStatus.PLANNING
    stories: List[str] = field(default_factory=list)  # Story IDs
    capacity: int = 0  # Total story points capacity
    committed_points: int = 0
    completed_points: int = 0
    team_members: List[str] = field(default_factory=list)
    retrospective_notes: Dict[str, List[str]] = field(default_factory=dict)

@dataclass
class TeamMember:
    """Team member with capacity and skills"""
    id: str
    name: str
    role: str
    capacity: int  # Story points per sprint
    skills: List[str] = field(default_factory=list)
    availability: float = 1.0  # 0-1 scale
    current_workload: int = 0

@dataclass
class ProjectMetrics:
    """Project health and performance metrics"""
    velocity: List[int] = field(default_factory=list)  # Historical velocity
    burndown_data: Dict[str, List[int]] = field(default_factory=dict)
    cycle_time: Dict[str, float] = field(default_factory=dict)
    defect_rate: float = 0.0
    team_satisfaction: float = 0.0
    stakeholder_satisfaction: float = 0.0

class BMADScrumMaster:
    """
    Advanced Scrum Master AI Agent for BMAD-METHOD Framework
    
    Integrates with:
    - bmad-planning-requirements (epic and story management)
    - bmad-context-engineering (development story prioritization)
    - bmad-quality-assurance (quality gates and definition of done)
    - bmad-architectural-design (technical dependency management)
    """

    def __init__(self, project_name: str, config_path: Optional[Path] = None):
        self.project_name = project_name
        self.config_path = config_path or Path(".bmad/scrum-master-config.json")
        
        # Core data structures
        self.stories: Dict[str, DevelopmentStory] = {}
        self.sprints: Dict[str, Sprint] = {}
        self.team_members: Dict[str, TeamMember] = {}
        self.project_metrics = ProjectMetrics()
        
        # Integration endpoints
        self.bmad_agents = {
            "planning_requirements": None,
            "context_engineering": None,
            "quality_assurance": None,
            "architectural_design": None
        }
        
        # Configuration
        self.config = self._load_config()
        
        logger.info(f"Initialized BMAD Scrum Master for project: {project_name}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults"""
        default_config = {
            "sprint_duration_weeks": 2,
            "story_point_scale": [1, 2, 3, 5, 8, 13, 21],
            "velocity_calculation_sprints": 3,
            "quality_gates": {
                "code_review": True,
                "automated_tests": True,
                "security_scan": True,
                "performance_test": False
            },
            "ceremonies": {
                "daily_standup": {"duration_minutes": 15},
                "sprint_planning": {"duration_hours": 4},
                "sprint_review": {"duration_hours": 2},
                "retrospective": {"duration_hours": 1.5}
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        return default_config

    # Sprint Planning & Management
    async def plan_sprint(self, sprint_name: str, goal: str, duration_weeks: Optional[int] = None) -> Sprint:
        """
        Organize and facilitate sprint planning sessions
        """
        duration = duration_weeks or self.config["sprint_duration_weeks"]
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(weeks=duration)
        
        sprint = Sprint(
            id=f"sprint_{len(self.sprints) + 1:03d}",
            name=sprint_name,
            goal=goal,
            start_date=start_date,
            end_date=end_date,
            team_members=list(self.team_members.keys())
        )
        
        # Calculate team capacity
        total_capacity = sum(member.capacity * member.availability 
                           for member in self.team_members.values())
        sprint.capacity = int(total_capacity)
        
        # AI-powered story selection and prioritization
        candidate_stories = await self._get_prioritized_backlog()
        selected_stories = await self._select_stories_for_sprint(candidate_stories, sprint.capacity)
        
        sprint.stories = [story.id for story in selected_stories]
        sprint.committed_points = sum(story.story_points.estimate for story in selected_stories 
                                    if story.story_points)
        
        self.sprints[sprint.id] = sprint
        
        logger.info(f"Sprint planned: {sprint.name} with {len(selected_stories)} stories "
                   f"({sprint.committed_points}/{sprint.capacity} points)")
        
        return sprint

    async def _get_prioritized_backlog(self) -> List[DevelopmentStory]:
        """Get prioritized backlog from BMAD context engineering"""
        # Integration with bmad-context-engineering
        backlog_stories = [story for story in self.stories.values() 
                          if story.status == StoryStatus.BACKLOG]
        
        # AI-powered prioritization based on:
        # - Business value (from planning requirements)
        # - Technical dependencies (from architectural design)
        # - Risk factors
        # - Context engineering insights
        
        priority_scores = {}
        for story in backlog_stories:
            score = await self._calculate_priority_score(story)
            priority_scores[story.id] = score
        
        # Sort by priority score (descending)
        sorted_stories = sorted(backlog_stories, 
                              key=lambda s: priority_scores[s.id], 
                              reverse=True)
        
        return sorted_stories

    async def _calculate_priority_score(self, story: DevelopmentStory) -> float:
        """Calculate AI-powered priority score for story"""
        score = 0.0
        
        # Base priority weight
        priority_weights = {
            Priority.CRITICAL: 100,
            Priority.HIGH: 75,
            Priority.MEDIUM: 50,
            Priority.LOW: 25
        }
        score += priority_weights[story.priority]
        
        # Business value factors (from planning requirements)
        if "high_business_value" in story.context_tags:
            score += 25
        if "customer_facing" in story.context_tags:
            score += 20
        if "revenue_impact" in story.context_tags:
            score += 30
        
        # Technical factors (from architectural design)
        if "foundational" in story.context_tags:
            score += 15
        if "performance_critical" in story.context_tags:
            score += 20
        
        # Risk factors (reduce score for high-risk items unless critical)
        risk_penalty = len(story.story_points.risk_factors) * 5 if story.story_points else 0
        if story.priority != Priority.CRITICAL:
            score -= risk_penalty
        
        # Dependency factors
        if not story.dependencies:  # No dependencies = higher priority
            score += 10
        
        return score

    async def _select_stories_for_sprint(self, prioritized_stories: List[DevelopmentStory], 
                                       capacity: int) -> List[DevelopmentStory]:
        """Select optimal set of stories for sprint capacity"""
        selected_stories = []
        used_capacity = 0
        
        for story in prioritized_stories:
            if not story.story_points:
                continue
                
            story_points = story.story_points.estimate
            
            # Check if story fits in remaining capacity
            if used_capacity + story_points <= capacity:
                # Check dependencies are met
                if await self._dependencies_satisfied(story, selected_stories):
                    selected_stories.append(story)
                    used_capacity += story_points
                    story.status = StoryStatus.PLANNED
        
        return selected_stories

    async def _dependencies_satisfied(self, story: DevelopmentStory, 
                                    selected_stories: List[DevelopmentStory]) -> bool:
        """Check if story dependencies are satisfied"""
        if not story.dependencies:
            return True
        
        selected_ids = {s.id for s in selected_stories}
        completed_ids = {s.id for s in self.stories.values() 
                        if s.status == StoryStatus.DONE}
        
        return all(dep_id in selected_ids or dep_id in completed_ids 
                  for dep_id in story.dependencies)

    # Backlog Management
    async def manage_backlog(self) -> Dict[str, Any]:
        """Prioritize and manage product backlog using BMAD framework outputs"""
        backlog_analysis = {
            "total_stories": len([s for s in self.stories.values() 
                                if s.status == StoryStatus.BACKLOG]),
            "epics_coverage": await self._analyze_epic_coverage(),
            "technical_debt": await self._assess_technical_debt(),
            "priority_distribution": self._get_priority_distribution(),
            "estimation_health": await self._assess_estimation_health(),
            "recommendations": await self._generate_backlog_recommendations()
        }
        
        return backlog_analysis

    async def _analyze_epic_coverage(self) -> Dict[str, Any]:
        """Analyze epic coverage and balance"""
        epic_stats = {}
        
        for story in self.stories.values():
            if story.epic_id:
                if story.epic_id not in epic_stats:
                    epic_stats[story.epic_id] = {
                        "total_stories": 0,
                        "completed_stories": 0,
                        "total_points": 0,
                        "completed_points": 0
                    }
                
                epic_stats[story.epic_id]["total_stories"] += 1
                if story.story_points:
                    epic_stats[story.epic_id]["total_points"] += story.story_points.estimate
                
                if story.status == StoryStatus.DONE:
                    epic_stats[story.epic_id]["completed_stories"] += 1
                    if story.story_points:
                        epic_stats[story.epic_id]["completed_points"] += story.story_points.estimate
        
        return epic_stats

    async def _assess_technical_debt(self) -> Dict[str, Any]:
        """Assess technical debt in backlog"""
        tech_debt_stories = [s for s in self.stories.values() 
                           if "technical_debt" in s.context_tags]
        
        return {
            "total_debt_stories": len(tech_debt_stories),
            "debt_points": sum(s.story_points.estimate for s in tech_debt_stories 
                             if s.story_points),
            "percentage_of_backlog": len(tech_debt_stories) / len(self.stories) * 100 if self.stories else 0,
            "high_priority_debt": len([s for s in tech_debt_stories 
                                     if s.priority in [Priority.CRITICAL, Priority.HIGH]])
        }

    def _get_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of story priorities"""
        distribution = {priority.value: 0 for priority in Priority}
        
        for story in self.stories.values():
            if story.status == StoryStatus.BACKLOG:
                distribution[story.priority.value] += 1
        
        return distribution

    async def _assess_estimation_health(self) -> Dict[str, Any]:
        """Assess quality of story point estimations"""
        estimated_stories = [s for s in self.stories.values() if s.story_points]
        
        if not estimated_stories:
            return {"health_score": 0, "recommendations": ["No estimated stories found"]}
        
        avg_confidence = sum(s.story_points.confidence for s in estimated_stories) / len(estimated_stories)
        high_risk_stories = len([s for s in estimated_stories 
                               if s.story_points.risk_factors])
        
        health_score = avg_confidence * 100
        recommendations = []
        
        if avg_confidence < 0.7:
            recommendations.append("Consider more detailed estimation sessions")
        if high_risk_stories > len(estimated_stories) * 0.3:
            recommendations.append("High number of risky stories - consider breaking down")
        
        return {
            "health_score": health_score,
            "average_confidence": avg_confidence,
            "high_risk_stories": high_risk_stories,
            "recommendations": recommendations
        }

    async def _generate_backlog_recommendations(self) -> List[str]:
        """Generate AI-powered backlog recommendations"""
        recommendations = []
        
        # Analyze backlog size
        backlog_size = len([s for s in self.stories.values() 
                          if s.status == StoryStatus.BACKLOG])
        
        if backlog_size > 50:
            recommendations.append("Large backlog detected. Consider archiving low-priority items.")
        
        # Analyze dependency chains
        dependency_chains = await self._analyze_dependency_chains()
        if dependency_chains["max_chain_length"] > 5:
            recommendations.append("Long dependency chains detected. Consider breaking down features.")
        
        # Analyze estimation gaps
        unestimated = len([s for s in self.stories.values() 
                         if s.status == StoryStatus.BACKLOG and not s.story_points])
        
        if unestimated > 10:
            recommendations.append(f"{unestimated} stories need estimation. Schedule grooming sessions.")
        
        return recommendations

    async def _analyze_dependency_chains(self) -> Dict[str, Any]:
        """Analyze dependency chains in backlog"""
        # Build dependency graph
        dependency_graph = {}
        for story in self.stories.values():
            dependency_graph[story.id] = story.dependencies
        
        # Find longest chains
        max_chain_length = 0
        
        def dfs_chain_length(story_id, visited=None):
            if visited is None:
                visited = set()
            
            if story_id in visited:
                return 0  # Circular dependency
            
            visited.add(story_id)
            max_length = 0
            
            for dep_id in dependency_graph.get(story_id, []):
                length = 1 + dfs_chain_length(dep_id, visited.copy())
                max_length = max(max_length, length)
            
            return max_length
        
        for story_id in dependency_graph:
            chain_length = dfs_chain_length(story_id)
            max_chain_length = max(max_chain_length, chain_length)
        
        return {
            "max_chain_length": max_chain_length,
            "total_dependencies": sum(len(deps) for deps in dependency_graph.values())
        }

    # Team Coordination
    async def coordinate_team(self, action: str, **kwargs) -> Dict[str, Any]:
        """Facilitate communication between BMAD agents and team members"""
        coordination_actions = {
            "daily_standup": self._facilitate_daily_standup,
            "blocker_resolution": self._resolve_blockers,
            "cross_team_sync": self._coordinate_cross_team,
            "capacity_planning": self._plan_team_capacity,
            "skill_gap_analysis": self._analyze_skill_gaps
        }
        
        if action in coordination_actions:
            return await coordination_actions[action](**kwargs)
        else:
            raise ValueError(f"Unknown coordination action: {action}")

    async def _facilitate_daily_standup(self) -> Dict[str, Any]:
        """Generate daily standup agenda and insights"""
        current_sprint = self._get_current_sprint()
        if not current_sprint:
            return {"error": "No active sprint found"}
        
        standup_data = {
            "sprint_progress": {
                "days_remaining": (current_sprint.end_date - datetime.date.today()).days,
                "completed_points": current_sprint.completed_points,
                "committed_points": current_sprint.committed_points,
                "progress_percentage": (current_sprint.completed_points / current_sprint.committed_points * 100) 
                                     if current_sprint.committed_points else 0
            },
            "team_updates": await self._generate_team_updates(),
            "blockers": await self._identify_current_blockers(),
            "at_risk_stories": await self._identify_at_risk_stories(),
            "achievements": await self._identify_recent_achievements()
        }
        
        return standup_data

    async def _generate_team_updates(self) -> Dict[str, Dict[str, Any]]:
        """Generate team member updates for standup"""
        updates = {}
        
        for member_id, member in self.team_members.items():
            member_stories = [s for s in self.stories.values() 
                            if s.assignee == member_id and s.status in 
                            [StoryStatus.IN_PROGRESS, StoryStatus.REVIEW, StoryStatus.TESTING]]
            
            updates[member.name] = {
                "current_stories": [{"id": s.id, "title": s.title, "status": s.status.value} 
                                  for s in member_stories],
                "workload_percentage": (member.current_workload / member.capacity * 100) 
                                     if member.capacity else 0,
                "suggested_focus": await self._suggest_member_focus(member, member_stories)
            }
        
        return updates

    async def _suggest_member_focus(self, member: TeamMember, 
                                  current_stories: List[DevelopmentStory]) -> List[str]:
        """AI-powered suggestions for team member focus"""
        suggestions = []
        
        # Check for overcommitment
        if member.current_workload > member.capacity:
            suggestions.append("Consider moving some work to next sprint - overcommitted")
        
        # Check for blocked items
        blocked_stories = [s for s in current_stories if s.status == StoryStatus.BLOCKED]
        if blocked_stories:
            suggestions.append(f"Focus on unblocking {len(blocked_stories)} stories")
        
        # Check for review items
        review_stories = [s for s in current_stories if s.status == StoryStatus.REVIEW]
        if review_stories:
            suggestions.append("Prioritize getting reviews completed")
        
        # Check for skill alignment
        skill_mismatches = await self._check_skill_alignment(member, current_stories)
        if skill_mismatches:
            suggestions.append("Consider pairing on stories outside expertise")
        
        return suggestions

    async def _check_skill_alignment(self, member: TeamMember, 
                                   stories: List[DevelopmentStory]) -> List[str]:
        """Check if stories align with member skills"""
        mismatches = []
        
        for story in stories:
            required_skills = story.technical_requirements.get("required_skills", [])
            if required_skills and not any(skill in member.skills for skill in required_skills):
                mismatches.append(story.id)
        
        return mismatches

    async def _identify_current_blockers(self) -> List[Dict[str, Any]]:
        """Identify current blockers across the team"""
        blocked_stories = [s for s in self.stories.values() if s.status == StoryStatus.BLOCKED]
        
        blockers = []
        for story in blocked_stories:
            blocker_info = {
                "story_id": story.id,
                "story_title": story.title,
                "assignee": story.assignee,
                "blocker_type": await self._classify_blocker(story),
                "suggested_resolution": await self._suggest_blocker_resolution(story)
            }
            blockers.append(blocker_info)
        
        return blockers

    async def _classify_blocker(self, story: DevelopmentStory) -> str:
        """Classify type of blocker"""
        # This would integrate with actual blocker tracking
        # For now, infer from context and dependencies
        
        if story.dependencies:
            return "dependency"
        elif "external_dependency" in story.context_tags:
            return "external"
        elif "technical_research" in story.context_tags:
            return "research"
        else:
            return "unknown"

    async def _suggest_blocker_resolution(self, story: DevelopmentStory) -> str:
        """Suggest resolution for blocker"""
        blocker_type = await self._classify_blocker(story)
        
        suggestions = {
            "dependency": "Review dependency status and prioritize blocking stories",
            "external": "Escalate to stakeholders or find alternative approach",
            "research": "Time-box research and make decision with available information",
            "unknown": "Schedule focused discussion to identify root cause"
        }
        
        return suggestions.get(blocker_type, "Requires manual investigation")

    # Progress Tracking
    async def track_progress(self) -> Dict[str, Any]:
        """Monitor sprint progress and identify bottlenecks"""
        current_sprint = self._get_current_sprint()
        if not current_sprint:
            return {"error": "No active sprint found"}
        
        progress_data = {
            "sprint_health": await self._assess_sprint_health(current_sprint),
            "burndown_analysis": await self._generate_burndown_analysis(current_sprint),
            "velocity_trend": await self._analyze_velocity_trend(),
            "bottleneck_analysis": await self._identify_bottlenecks(current_sprint),
            "quality_metrics": await self._assess_quality_metrics(current_sprint),
            "risk_indicators": await self._identify_risk_indicators(current_sprint)
        }
        
        return progress_data

    def _get_current_sprint(self) -> Optional[Sprint]:
        """Get the currently active sprint"""
        active_sprints = [s for s in self.sprints.values() if s.status == SprintStatus.ACTIVE]
        return active_sprints[0] if active_sprints else None

    async def _assess_sprint_health(self, sprint: Sprint) -> Dict[str, Any]:
        """Assess overall sprint health"""
        days_elapsed = (datetime.date.today() - sprint.start_date).days
        total_days = (sprint.end_date - sprint.start_date).days
        
        expected_progress = days_elapsed / total_days if total_days > 0 else 0
        actual_progress = sprint.completed_points / sprint.committed_points if sprint.committed_points > 0 else 0
        
        health_score = min(100, max(0, (actual_progress / max(expected_progress, 0.1)) * 100))
        
        health_status = "excellent" if health_score >= 90 else \
                       "good" if health_score >= 75 else \
                       "warning" if health_score >= 50 else "critical"
        
        return {
            "health_score": health_score,
            "health_status": health_status,
            "expected_progress": expected_progress * 100,
            "actual_progress": actual_progress * 100,
            "days_remaining": (sprint.end_date - datetime.date.today()).days
        }

    async def _generate_burndown_analysis(self, sprint: Sprint) -> Dict[str, Any]:
        """Generate burndown chart data and analysis"""
        # This would integrate with actual time tracking
        # For demonstration, generate synthetic burndown data
        
        days_elapsed = (datetime.date.today() - sprint.start_date).days
        total_days = (sprint.end_date - sprint.start_date).days
        
        ideal_burndown = []
        actual_burndown = []
        
        for day in range(total_days + 1):
            ideal_remaining = sprint.committed_points * (1 - day / total_days)
            ideal_burndown.append(max(0, ideal_remaining))
            
            # Simulate actual burndown with some variance
            if day <= days_elapsed:
                actual_remaining = sprint.committed_points - sprint.completed_points
                actual_burndown.append(actual_remaining)
            else:
                actual_burndown.append(None)
        
        return {
            "ideal_burndown": ideal_burndown,
            "actual_burndown": actual_burndown,
            "projection": await self._project_sprint_completion(sprint),
            "trend_analysis": await self._analyze_burndown_trend(actual_burndown)
        }

    async def _project_sprint_completion(self, sprint: Sprint) -> Dict[str, Any]:
        """Project sprint completion based on current velocity"""
        current_velocity = await self._calculate_current_velocity()
        remaining_points = sprint.committed_points - sprint.completed_points
        days_remaining = (sprint.end_date - datetime.date.today()).days
        
        projected_completion = remaining_points / max(current_velocity, 1) if current_velocity > 0 else float('inf')
        
        completion_likelihood = "high" if projected_completion <= days_remaining else \
                              "medium" if projected_completion <= days_remaining * 1.2 else "low"
        
        return {
            "projected_days_to_completion": projected_completion,
            "completion_likelihood": completion_likelihood,
            "remaining_points": remaining_points,
            "current_velocity": current_velocity
        }

    async def _calculate_current_velocity(self) -> float:
        """Calculate current sprint velocity (points per day)"""
        current_sprint = self._get_current_sprint()
        if not current_sprint:
            return 0
        
        days_elapsed = max(1, (datetime.date.today() - current_sprint.start_date).days)
        return current_sprint.completed_points / days_elapsed

    # Scrum Ceremonies
    async def facilitate_ceremony(self, ceremony_type: str, **kwargs) -> Dict[str, Any]:
        """Organize and facilitate scrum ceremonies"""
        ceremonies = {
            "daily_standup": self._facilitate_daily_standup,
            "sprint_planning": self._facilitate_sprint_planning,
            "sprint_review": self._facilitate_sprint_review,
            "retrospective": self._facilitate_retrospective,
            "backlog_grooming": self._facilitate_backlog_grooming
        }
        
        if ceremony_type in ceremonies:
            return await ceremonies[ceremony_type](**kwargs)
        else:
            raise ValueError(f"Unknown ceremony type: {ceremony_type}")

    async def _facilitate_sprint_planning(self, **kwargs) -> Dict[str, Any]:
        """Facilitate sprint planning ceremony"""
        planning_data = {
            "agenda": [
                "Review sprint goal and objectives",
                "Review team capacity and availability",
                "Prioritize and estimate backlog items",
                "Select stories for sprint commitment",
                "Identify dependencies and risks",
                "Finalize sprint backlog"
            ],
            "team_capacity": await self._calculate_team_capacity(),
            "prioritized_backlog": await self._get_prioritized_backlog(),
            "estimation_guidelines": self._get_estimation_guidelines(),
            "risk_assessment": await self._assess_planning_risks()
        }
        
        return planning_data

    async def _facilitate_sprint_review(self, sprint_id: str) -> Dict[str, Any]:
        """Facilitate sprint review ceremony"""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return {"error": f"Sprint {sprint_id} not found"}
        
        completed_stories = [self.stories[story_id] for story_id in sprint.stories 
                           if self.stories[story_id].status == StoryStatus.DONE]
        
        review_data = {
            "sprint_summary": {
                "goal_achievement": await self._assess_goal_achievement(sprint),
                "completed_stories": len(completed_stories),
                "completed_points": sprint.completed_points,
                "committed_points": sprint.committed_points
            },
            "demo_agenda": [{"story": s.title, "demo_notes": s.description} 
                          for s in completed_stories],
            "stakeholder_feedback": await self._prepare_feedback_collection(),
            "retrospective_prep": await self._prepare_retrospective_topics(sprint)
        }
        
        return review_data

    async def _facilitate_retrospective(self, sprint_id: str) -> Dict[str, Any]:
        """Facilitate retrospective ceremony with AI insights"""
        sprint = self.sprints.get(sprint_id)
        if not sprint:
            return {"error": f"Sprint {sprint_id} not found"}
        
        retrospective_data = {
            "what_went_well": await self._analyze_positive_patterns(sprint),
            "what_can_improve": await self._identify_improvement_areas(sprint),
            "action_items": await self._generate_action_items(sprint),
            "team_sentiment": await self._assess_team_sentiment(sprint),
            "process_insights": await self._generate_process_insights(sprint),
            "continuous_improvement": await self._suggest_improvements(sprint)
        }
        
        return retrospective_data

    async def _analyze_positive_patterns(self, sprint: Sprint) -> List[str]:
        """AI analysis of what went well in the sprint"""
        positive_patterns = []
        
        # Analyze completion rate
        completion_rate = sprint.completed_points / sprint.committed_points if sprint.committed_points > 0 else 0
        if completion_rate >= 0.9:
            positive_patterns.append("Excellent sprint completion rate - good estimation and execution")
        
        # Analyze story flow
        stories_completed = len([s for s in sprint.stories 
                               if self.stories[s].status == StoryStatus.DONE])
        if stories_completed >= len(sprint.stories) * 0.8:
            positive_patterns.append("Strong story completion rate - effective task breakdown")
        
        # Analyze blocker resolution
        blocked_stories = [s for s in sprint.stories 
                         if self.stories[s].status == StoryStatus.BLOCKED]
        if not blocked_stories:
            positive_patterns.append("No blocked stories - effective dependency management")
        
        return positive_patterns

    async def _identify_improvement_areas(self, sprint: Sprint) -> List[str]:
        """AI identification of improvement opportunities"""
        improvements = []
        
        # Analyze velocity variance
        historical_velocity = self.project_metrics.velocity[-3:] if len(self.project_metrics.velocity) >= 3 else []
        if historical_velocity:
            avg_velocity = sum(historical_velocity) / len(historical_velocity)
            current_velocity = sprint.completed_points
            
            if current_velocity < avg_velocity * 0.8:
                improvements.append("Velocity below average - investigate capacity or estimation issues")
        
        # Analyze cycle time
        long_running_stories = [s for s in sprint.stories 
                              if (datetime.datetime.now() - self.stories[s].updated_at).days > 5]
        if long_running_stories:
            improvements.append(f"{len(long_running_stories)} stories took longer than expected - consider smaller tasks")
        
        # Analyze quality issues
        if self.project_metrics.defect_rate > 0.1:
            improvements.append("Higher than expected defect rate - review quality practices")
        
        return improvements

    # Velocity & Metrics Management
    async def manage_velocity(self) -> Dict[str, Any]:
        """Track team velocity and make predictions for future sprints"""
        velocity_data = {
            "current_velocity": await self._calculate_team_velocity(),
            "velocity_trend": await self._analyze_velocity_trend(),
            "capacity_planning": await self._calculate_team_capacity(),
            "predictive_analytics": await self._generate_velocity_predictions(),
            "performance_insights": await self._generate_performance_insights()
        }
        
        return velocity_data

    async def _calculate_team_velocity(self) -> Dict[str, Any]:
        """Calculate various velocity metrics"""
        completed_sprints = [s for s in self.sprints.values() if s.status == SprintStatus.COMPLETED]
        
        if not completed_sprints:
            return {"error": "No completed sprints found"}
        
        recent_sprints = completed_sprints[-self.config["velocity_calculation_sprints"]:]
        velocities = [sprint.completed_points for sprint in recent_sprints]
        
        return {
            "average_velocity": sum(velocities) / len(velocities),
            "velocity_range": {"min": min(velocities), "max": max(velocities)},
            "velocity_variance": await self._calculate_variance(velocities),
            "trend_direction": await self._calculate_trend_direction(velocities),
            "prediction_confidence": await self._calculate_prediction_confidence(velocities)
        }

    async def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of velocity values"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    async def _calculate_trend_direction(self, velocities: List[int]) -> str:
        """Calculate velocity trend direction"""
        if len(velocities) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        recent_avg = sum(velocities[-2:]) / 2
        older_avg = sum(velocities[:-2]) / max(1, len(velocities) - 2) if len(velocities) > 2 else velocities[0]
        
        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    async def _generate_velocity_predictions(self) -> Dict[str, Any]:
        """Generate predictive analytics for future sprints"""
        velocity_stats = await self._calculate_team_velocity()
        
        if "error" in velocity_stats:
            return velocity_stats
        
        avg_velocity = velocity_stats["average_velocity"]
        variance = velocity_stats["velocity_variance"]
        
        # Confidence intervals for next sprint
        confidence_80 = {
            "lower": max(0, avg_velocity - variance * 0.8),
            "upper": avg_velocity + variance * 0.8
        }
        
        confidence_95 = {
            "lower": max(0, avg_velocity - variance * 1.2),
            "upper": avg_velocity + variance * 1.2
        }
        
        return {
            "next_sprint_prediction": avg_velocity,
            "confidence_intervals": {
                "80_percent": confidence_80,
                "95_percent": confidence_95
            },
            "capacity_recommendations": await self._generate_capacity_recommendations(avg_velocity)
        }

    # Risk Management
    async def manage_risks(self) -> Dict[str, Any]:
        """Identify project risks and facilitate mitigation strategies"""
        risk_data = {
            "current_risks": await self._identify_current_risks(),
            "risk_matrix": await self._generate_risk_matrix(),
            "mitigation_strategies": await self._suggest_mitigation_strategies(),
            "early_warning_indicators": await self._monitor_early_warnings(),
            "contingency_plans": await self._develop_contingency_plans()
        }
        
        return risk_data

    async def _identify_current_risks(self) -> List[Dict[str, Any]]:
        """Identify current project risks using AI analysis"""
        risks = []
        
        # Velocity risk
        velocity_trend = await self._analyze_velocity_trend()
        if velocity_trend.get("trend_direction") == "decreasing":
            risks.append({
                "type": "velocity",
                "severity": "medium",
                "description": "Decreasing velocity trend detected",
                "impact": "Sprint commitments may not be met",
                "probability": 0.7
            })
        
        # Dependency risk
        dependency_analysis = await self._analyze_dependency_chains()
        if dependency_analysis["max_chain_length"] > 5:
            risks.append({
                "type": "dependency",
                "severity": "high",
                "description": "Long dependency chains increase delivery risk",
                "impact": "Cascading delays from blocked dependencies",
                "probability": 0.6
            })
        
        # Team capacity risk
        overcommitted_members = [m for m in self.team_members.values() 
                               if m.current_workload > m.capacity]
        if overcommitted_members:
            risks.append({
                "type": "capacity",
                "severity": "high",
                "description": f"{len(overcommitted_members)} team members overcommitted",
                "impact": "Burnout and quality issues",
                "probability": 0.8
            })
        
        # Quality risk
        if self.project_metrics.defect_rate > 0.15:
            risks.append({
                "type": "quality",
                "severity": "medium",
                "description": "High defect rate detected",
                "impact": "Increased rework and customer dissatisfaction",
                "probability": 0.9
            })
        
        return risks

    # Integration with BMAD Agents
    async def integrate_with_bmad_agents(self):
        """Setup integration with other BMAD framework agents"""
        
        # Integration with bmad-planning-requirements
        await self._setup_planning_integration()
        
        # Integration with bmad-context-engineering
        await self._setup_context_integration()
        
        # Integration with bmad-quality-assurance
        await self._setup_quality_integration()
        
        # Integration with bmad-architectural-design
        await self._setup_architecture_integration()

    async def _setup_planning_integration(self):
        """Setup integration with planning requirements agent"""
        # This would establish communication channels with planning agent
        # for epic management, requirement prioritization, etc.
        logger.info("Setting up integration with bmad-planning-requirements")

    async def _setup_context_integration(self):
        """Setup integration with context engineering agent"""
        # This would establish communication channels with context engineering
        # for story prioritization, context analysis, etc.
        logger.info("Setting up integration with bmad-context-engineering")

    async def _setup_quality_integration(self):
        """Setup integration with quality assurance agent"""
        # This would establish communication channels with QA agent
        # for quality gates, definition of done, etc.
        logger.info("Setting up integration with bmad-quality-assurance")

    async def _setup_architecture_integration(self):
        """Setup integration with architectural design agent"""
        # This would establish communication channels with architecture agent
        # for technical dependency management, etc.
        logger.info("Setting up integration with bmad-architectural-design")

    # Story Point Estimation
    async def estimate_story_points(self, story_id: str, estimation_session: Dict[str, Any]) -> StoryPoint:
        """AI-powered story point estimation with confidence intervals"""
        story = self.stories.get(story_id)
        if not story:
            raise ValueError(f"Story {story_id} not found")
        
        # Analyze complexity factors
        complexity_factors = await self._analyze_story_complexity(story)
        
        # Calculate base estimate using AI model
        base_estimate = await self._calculate_base_estimate(story, complexity_factors)
        
        # Adjust for team experience and historical data
        adjusted_estimate = await self._adjust_for_team_factors(base_estimate, story)
        
        # Calculate confidence based on factors
        confidence = await self._calculate_estimation_confidence(story, complexity_factors)
        
        # Identify risk factors
        risk_factors = await self._identify_estimation_risks(story, complexity_factors)
        
        story_point = StoryPoint(
            estimate=adjusted_estimate,
            confidence=confidence,
            complexity_factors=complexity_factors,
            risk_factors=risk_factors
        )
        
        story.story_points = story_point
        story.updated_at = datetime.datetime.now()
        
        return story_point

    async def _analyze_story_complexity(self, story: DevelopmentStory) -> Dict[str, int]:
        """Analyze story complexity factors"""
        factors = {}
        
        # UI complexity
        if "ui" in story.context_tags or "frontend" in story.context_tags:
            factors["ui_complexity"] = len(story.acceptance_criteria)
        
        # Backend complexity
        if "backend" in story.context_tags or "api" in story.context_tags:
            factors["backend_complexity"] = len(story.dependencies) + 1
        
        # Integration complexity
        if "integration" in story.context_tags:
            factors["integration_complexity"] = 3
        
        # Data complexity
        if "database" in story.context_tags or "data" in story.context_tags:
            factors["data_complexity"] = 2
        
        return factors

    # Utility Methods
    def add_story(self, story: DevelopmentStory):
        """Add a new development story"""
        self.stories[story.id] = story
        logger.info(f"Added story: {story.id} - {story.title}")

    def add_team_member(self, member: TeamMember):
        """Add a new team member"""
        self.team_members[member.id] = member
        logger.info(f"Added team member: {member.name}")

    def update_story_status(self, story_id: str, new_status: StoryStatus):
        """Update story status and trigger related updates"""
        if story_id not in self.stories:
            raise ValueError(f"Story {story_id} not found")
        
        old_status = self.stories[story_id].status
        self.stories[story_id].status = new_status
        self.stories[story_id].updated_at = datetime.datetime.now()
        
        # Update sprint metrics if story is in current sprint
        current_sprint = self._get_current_sprint()
        if current_sprint and story_id in current_sprint.stories:
            self._update_sprint_metrics(current_sprint.id)
        
        logger.info(f"Updated story {story_id} status: {old_status.value} -> {new_status.value}")

    def _update_sprint_metrics(self, sprint_id: str):
        """Update sprint metrics based on current story statuses"""
        sprint = self.sprints[sprint_id]
        
        completed_points = 0
        for story_id in sprint.stories:
            story = self.stories[story_id]
            if story.status == StoryStatus.DONE and story.story_points:
                completed_points += story.story_points.estimate
        
        sprint.completed_points = completed_points

    async def generate_report(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Generate comprehensive project reports"""
        reports = {
            "sprint_summary": self._generate_sprint_summary_report,
            "team_performance": self._generate_team_performance_report,
            "project_health": self._generate_project_health_report,
            "stakeholder_update": self._generate_stakeholder_report,
            "retrospective_insights": self._generate_retrospective_insights_report
        }
        
        if report_type in reports:
            return await reports[report_type](**kwargs)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    async def _generate_project_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive project health report"""
        current_sprint = self._get_current_sprint()
        
        health_report = {
            "executive_summary": await self._generate_executive_summary(),
            "sprint_status": await self._assess_sprint_health(current_sprint) if current_sprint else None,
            "team_metrics": await self.manage_velocity(),
            "quality_metrics": {
                "defect_rate": self.project_metrics.defect_rate,
                "team_satisfaction": self.project_metrics.team_satisfaction,
                "stakeholder_satisfaction": self.project_metrics.stakeholder_satisfaction
            },
            "risk_assessment": await self.manage_risks(),
            "recommendations": await self._generate_health_recommendations()
        }
        
        return health_report

    async def _generate_executive_summary(self) -> str:
        """Generate AI-powered executive summary"""
        current_sprint = self._get_current_sprint()
        backlog_analysis = await self.manage_backlog()
        velocity_data = await self.manage_velocity()
        
        summary_points = []
        
        # Sprint progress
        if current_sprint:
            health = await self._assess_sprint_health(current_sprint)
            summary_points.append(f"Current sprint is {health['health_status']} with {health['actual_progress']:.0f}% completion")
        
        # Velocity trend
        if "error" not in velocity_data:
            trend = velocity_data.get("velocity_trend", {}).get("trend_direction", "stable")
            summary_points.append(f"Team velocity is {trend}")
        
        # Quality status
        if self.project_metrics.defect_rate < 0.05:
            summary_points.append("Quality metrics are excellent")
        elif self.project_metrics.defect_rate < 0.1:
            summary_points.append("Quality metrics are good")
        else:
            summary_points.append("Quality metrics need attention")
        
        return ". ".join(summary_points) + "."


# Example usage and integration
if __name__ == "__main__":
    async def main():
        # Initialize the BMAD Scrum Master
        scrum_master = BMADScrumMaster("Law Firm Vision 2030")
        
        # Add some sample team members
        scrum_master.add_team_member(TeamMember(
            id="dev001",
            name="Alice Johnson",
            role="Senior Developer",
            capacity=10,
            skills=["Python", "React", "AWS"],
            availability=1.0
        ))
        
        scrum_master.add_team_member(TeamMember(
            id="dev002",
            name="Bob Smith",
            role="Full Stack Developer",
            capacity=8,
            skills=["Node.js", "Vue.js", "PostgreSQL"],
            availability=0.8
        ))
        
        # Add some sample stories
        story1 = DevelopmentStory(
            id="story001",
            title="Implement AI document analysis",
            description="Create AI-powered document analysis for legal briefs",
            acceptance_criteria=[
                "System can extract key information from PDF documents",
                "AI analysis provides confidence scores",
                "Integration with existing document management system"
            ],
            priority=Priority.HIGH,
            context_tags=["ai", "backend", "high_business_value"]
        )
        
        story2 = DevelopmentStory(
            id="story002", 
            title="Build client dashboard UI",
            description="Create responsive dashboard for client case management",
            acceptance_criteria=[
                "Dashboard shows case status and updates",
                "Mobile responsive design",
                "Real-time notifications"
            ],
            priority=Priority.MEDIUM,
            context_tags=["ui", "frontend", "customer_facing"]
        )
        
        scrum_master.add_story(story1)
        scrum_master.add_story(story2)
        
        # Estimate story points
        await scrum_master.estimate_story_points("story001", {})
        await scrum_master.estimate_story_points("story002", {})
        
        # Plan a sprint
        sprint = await scrum_master.plan_sprint(
            "Sprint 1: AI Foundation",
            "Establish core AI capabilities for document analysis"
        )
        
        print(f"Planned sprint: {sprint.name}")
        print(f"Committed points: {sprint.committed_points}/{sprint.capacity}")
        
        # Generate project health report
        health_report = await scrum_master.generate_report("project_health")
        print(f"Project health: {health_report['executive_summary']}")
    
    # Run the example
    asyncio.run(main())