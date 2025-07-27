#!/usr/bin/env python3
"""
BMAD Scrum Master CLI Interface
Command-line interface for the BMAD Scrum Master Agent
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Dict, Any, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from bmad_scrum_master_agent import (
    BMADScrumMaster, DevelopmentStory, TeamMember, Sprint,
    Priority, StoryStatus, SprintStatus
)

console = Console()

class BMADScrumMasterCLI:
    """CLI interface for BMAD Scrum Master Agent"""
    
    def __init__(self, project_name: str, config_path: Optional[Path] = None):
        self.project_name = project_name
        self.scrum_master = BMADScrumMaster(project_name, config_path)
        
    async def initialize(self):
        """Initialize the scrum master and integrations"""
        await self.scrum_master.integrate_with_bmad_agents()

@click.group()
@click.option('--project', '-p', default='default', help='Project name')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, project, config, verbose):
    """BMAD Scrum Master - Advanced AI-powered Scrum Master for BMAD Framework"""
    ctx.ensure_object(dict)
    ctx.obj['project'] = project
    ctx.obj['config'] = Path(config) if config else None
    ctx.obj['verbose'] = verbose
    
    if verbose:
        console.print(f"[green]Initializing BMAD Scrum Master for project: {project}[/green]")

@cli.command()
@click.pass_context
def init(ctx):
    """Initialize a new BMAD Scrum Master project"""
    project_name = ctx.obj['project']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Create project structure
        progress.add_task("Creating project structure...", total=None)
        project_dir = Path(f".bmad/{project_name}")
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create configuration files
        progress.add_task("Setting up configuration...", total=None)
        config_path = project_dir / "scrum-master-config.json"
        with open(config_path, 'w') as f:
            json.dump({
                "project_name": project_name,
                "sprint_duration_weeks": 2,
                "story_point_scale": [1, 2, 3, 5, 8, 13, 21],
                "quality_gates": {
                    "code_review": True,
                    "automated_tests": True,
                    "security_scan": True
                }
            }, f, indent=2)
        
        # Create data directories
        (project_dir / "data").mkdir(exist_ok=True)
        (project_dir / "reports").mkdir(exist_ok=True)
        (project_dir / "logs").mkdir(exist_ok=True)
    
    console.print(f"[green]✓ BMAD Scrum Master project '{project_name}' initialized successfully![/green]")
    console.print(f"[blue]Configuration saved to: {config_path}[/blue]")

@cli.group()
def sprint():
    """Sprint management commands"""
    pass

@sprint.command()
@click.option('--name', '-n', required=True, help='Sprint name')
@click.option('--goal', '-g', required=True, help='Sprint goal')
@click.option('--duration', '-d', type=int, default=2, help='Sprint duration in weeks')
@click.pass_context
def plan(ctx, name, goal, duration):
    """Plan a new sprint"""
    async def plan_sprint():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        with console.status("[bold green]Planning sprint..."):
            sprint = await cli_instance.scrum_master.plan_sprint(name, goal, duration)
        
        # Display sprint summary
        panel = Panel(
            f"[bold]Sprint: {sprint.name}[/bold]\n"
            f"Goal: {sprint.goal}\n"
            f"Duration: {sprint.start_date} to {sprint.end_date}\n"
            f"Capacity: {sprint.capacity} points\n"
            f"Committed: {sprint.committed_points} points\n"
            f"Stories: {len(sprint.stories)}",
            title="Sprint Planned Successfully",
            border_style="green"
        )
        console.print(panel)
        
        # Display selected stories
        if sprint.stories:
            table = Table(title="Selected Stories")
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Points", style="green")
            table.add_column("Priority", style="yellow")
            
            for story_id in sprint.stories:
                story = cli_instance.scrum_master.stories[story_id]
                points = str(story.story_points.estimate) if story.story_points else "TBD"
                table.add_row(story.id, story.title[:50], points, story.priority.value)
            
            console.print(table)
    
    asyncio.run(plan_sprint())

@sprint.command()
@click.pass_context
def status(ctx):
    """Show current sprint status"""
    async def show_status():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        with console.status("[bold green]Analyzing sprint status..."):
            progress_data = await cli_instance.scrum_master.track_progress()
        
        if "error" in progress_data:
            console.print(f"[red]Error: {progress_data['error']}[/red]")
            return
        
        # Sprint health
        health = progress_data["sprint_health"]
        health_color = {
            "excellent": "green",
            "good": "blue", 
            "warning": "yellow",
            "critical": "red"
        }.get(health["health_status"], "white")
        
        panel = Panel(
            f"[bold]Health Score: {health['health_score']:.1f}%[/bold]\n"
            f"Status: [{health_color}]{health['health_status'].title()}[/{health_color}]\n"
            f"Expected Progress: {health['expected_progress']:.1f}%\n"
            f"Actual Progress: {health['actual_progress']:.1f}%\n"
            f"Days Remaining: {health['days_remaining']}",
            title="Sprint Health",
            border_style=health_color
        )
        console.print(panel)
        
        # Burndown analysis
        burndown = progress_data["burndown_analysis"]
        projection = burndown["projection"]
        
        console.print(f"\n[bold]Burndown Analysis:[/bold]")
        console.print(f"Current Velocity: {projection['current_velocity']:.1f} points/day")
        console.print(f"Completion Likelihood: {projection['completion_likelihood'].title()}")
        console.print(f"Remaining Points: {projection['remaining_points']}")
    
    asyncio.run(show_status())

@cli.group()
def story():
    """Story management commands"""
    pass

@story.command()
@click.option('--id', '-i', required=True, help='Story ID')
@click.option('--title', '-t', required=True, help='Story title')
@click.option('--description', '-d', required=True, help='Story description')
@click.option('--priority', '-p', type=click.Choice(['critical', 'high', 'medium', 'low']), 
              default='medium', help='Story priority')
@click.option('--epic', '-e', help='Epic ID')
@click.option('--tags', help='Comma-separated context tags')
@click.pass_context
def add(ctx, id, title, description, priority, epic, tags):
    """Add a new story to the backlog"""
    async def add_story():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        context_tags = [tag.strip() for tag in tags.split(',')] if tags else []
        
        story = DevelopmentStory(
            id=id,
            title=title,
            description=description,
            acceptance_criteria=[],  # Can be added later
            priority=Priority(priority),
            epic_id=epic,
            context_tags=context_tags
        )
        
        cli_instance.scrum_master.add_story(story)
        
        # Auto-estimate story points
        with console.status("[bold green]Estimating story points..."):
            await cli_instance.scrum_master.estimate_story_points(id, {})
        
        story = cli_instance.scrum_master.stories[id]
        points = story.story_points.estimate if story.story_points else "TBD"
        confidence = f"{story.story_points.confidence*100:.0f}%" if story.story_points else "N/A"
        
        console.print(f"[green]✓ Story '{id}' added successfully![/green]")
        console.print(f"[blue]Estimated Points: {points} (Confidence: {confidence})[/blue]")
    
    asyncio.run(add_story())

@story.command()
@click.pass_context
def list(ctx):
    """List all stories in the backlog"""
    async def list_stories():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        if not cli_instance.scrum_master.stories:
            console.print("[yellow]No stories found in backlog[/yellow]")
            return
        
        table = Table(title="Story Backlog")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white", max_width=40)
        table.add_column("Status", style="blue")
        table.add_column("Priority", style="yellow")
        table.add_column("Points", style="green")
        table.add_column("Epic", style="magenta")
        
        for story in cli_instance.scrum_master.stories.values():
            points = str(story.story_points.estimate) if story.story_points else "TBD"
            table.add_row(
                story.id,
                story.title,
                story.status.value,
                story.priority.value,
                points,
                story.epic_id or "-"
            )
        
        console.print(table)
    
    asyncio.run(list_stories())

@story.command()
@click.argument('story_id')
@click.argument('status', type=click.Choice(['backlog', 'planned', 'in_progress', 'review', 'testing', 'done', 'blocked']))
@click.pass_context
def update_status(ctx, story_id, status):
    """Update story status"""
    async def update():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        try:
            new_status = StoryStatus(status)
            cli_instance.scrum_master.update_story_status(story_id, new_status)
            console.print(f"[green]✓ Story {story_id} status updated to {status}[/green]")
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(update())

@cli.group()
def team():
    """Team management commands"""
    pass

@team.command()
@click.option('--id', '-i', required=True, help='Team member ID')
@click.option('--name', '-n', required=True, help='Team member name')
@click.option('--role', '-r', required=True, help='Team member role')
@click.option('--capacity', '-c', type=int, default=8, help='Sprint capacity in story points')
@click.option('--skills', '-s', help='Comma-separated skills')
@click.option('--availability', '-a', type=float, default=1.0, help='Availability (0.0-1.0)')
@click.pass_context
def add_member(ctx, id, name, role, capacity, skills, availability):
    """Add a new team member"""
    async def add():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        skill_list = [skill.strip() for skill in skills.split(',')] if skills else []
        
        member = TeamMember(
            id=id,
            name=name,
            role=role,
            capacity=capacity,
            skills=skill_list,
            availability=availability
        )
        
        cli_instance.scrum_master.add_team_member(member)
        console.print(f"[green]✓ Team member '{name}' added successfully![/green]")
    
    asyncio.run(add())

@team.command()
@click.pass_context
def list_members(ctx):
    """List all team members"""
    async def list():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        if not cli_instance.scrum_master.team_members:
            console.print("[yellow]No team members found[/yellow]")
            return
        
        table = Table(title="Team Members")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Role", style="blue")
        table.add_column("Capacity", style="green")
        table.add_column("Availability", style="yellow")
        table.add_column("Skills", style="magenta", max_width=30)
        
        for member in cli_instance.scrum_master.team_members.values():
            skills_text = ", ".join(member.skills[:3])
            if len(member.skills) > 3:
                skills_text += f" (+{len(member.skills)-3} more)"
            
            table.add_row(
                member.id,
                member.name,
                member.role,
                str(member.capacity),
                f"{member.availability*100:.0f}%",
                skills_text
            )
        
        console.print(table)
    
    asyncio.run(list())

@cli.group()
def ceremony():
    """Scrum ceremony commands"""
    pass

@ceremony.command()
@click.pass_context
def standup(ctx):
    """Generate daily standup report"""
    async def daily_standup():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        with console.status("[bold green]Preparing standup report..."):
            standup_data = await cli_instance.scrum_master.coordinate_team("daily_standup")
        
        if "error" in standup_data:
            console.print(f"[red]Error: {standup_data['error']}[/red]")
            return
        
        # Sprint progress
        progress = standup_data["sprint_progress"]
        console.print(Panel(
            f"[bold]Days Remaining: {progress['days_remaining']}[/bold]\n"
            f"Progress: {progress['completed_points']}/{progress['committed_points']} points "
            f"({progress['progress_percentage']:.1f}%)",
            title="Sprint Progress",
            border_style="blue"
        ))
        
        # Team updates
        team_updates = standup_data["team_updates"]
        for member_name, update in team_updates.items():
            workload = update['workload_percentage']
            color = "green" if workload <= 100 else "yellow" if workload <= 120 else "red"
            
            console.print(f"\n[bold]{member_name}[/bold] ([{color}]{workload:.0f}% capacity[/{color}])")
            for story in update['current_stories']:
                console.print(f"  • {story['id']}: {story['title'][:40]} ({story['status']})")
            
            if update['suggested_focus']:
                console.print(f"  [yellow]Focus: {', '.join(update['suggested_focus'])}[/yellow]")
        
        # Blockers
        blockers = standup_data["blockers"]
        if blockers:
            console.print(f"\n[red]🚫 Blockers ({len(blockers)}):[/red]")
            for blocker in blockers:
                console.print(f"  • {blocker['story_id']}: {blocker['story_title'][:40]}")
                console.print(f"    Type: {blocker['blocker_type']}, Assignee: {blocker['assignee']}")
    
    asyncio.run(daily_standup())

@ceremony.command()
@click.option('--sprint-id', required=True, help='Sprint ID for retrospective')
@click.pass_context
def retrospective(ctx, sprint_id):
    """Generate retrospective insights"""
    async def retro():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        with console.status("[bold green]Analyzing sprint data..."):
            retro_data = await cli_instance.scrum_master.facilitate_ceremony("retrospective", sprint_id=sprint_id)
        
        if "error" in retro_data:
            console.print(f"[red]Error: {retro_data['error']}[/red]")
            return
        
        # What went well
        console.print(Panel(
            "\n".join(f"• {item}" for item in retro_data["what_went_well"]),
            title="What Went Well",
            border_style="green"
        ))
        
        # What can improve
        console.print(Panel(
            "\n".join(f"• {item}" for item in retro_data["what_can_improve"]),
            title="What Can Improve", 
            border_style="yellow"
        ))
        
        # AI recommendations
        console.print(Panel(
            "\n".join(f"• {item}" for item in retro_data["continuous_improvement"]),
            title="AI Recommendations",
            border_style="blue"
        ))
    
    asyncio.run(retro())

@cli.group()
def report():
    """Reporting commands"""
    pass

@report.command()
@click.option('--type', '-t', type=click.Choice(['project_health', 'team_performance', 'stakeholder_update']),
              default='project_health', help='Report type')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def generate(ctx, type, output):
    """Generate project reports"""
    async def gen_report():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        with console.status(f"[bold green]Generating {type} report..."):
            report_data = await cli_instance.scrum_master.generate_report(type)
        
        if output:
            with open(output, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            console.print(f"[green]✓ Report saved to {output}[/green]")
        else:
            # Display executive summary
            if "executive_summary" in report_data:
                console.print(Panel(
                    report_data["executive_summary"],
                    title=f"{type.replace('_', ' ').title()} Report",
                    border_style="blue"
                ))
            
            # Display key metrics
            if type == "project_health":
                sprint_status = report_data.get("sprint_status")
                if sprint_status:
                    console.print(f"\n[bold]Sprint Health:[/bold] {sprint_status['health_status'].title()}")
                    console.print(f"[bold]Health Score:[/bold] {sprint_status['health_score']:.1f}%")
                
                velocity = report_data.get("team_metrics", {})
                if velocity and "error" not in velocity:
                    avg_velocity = velocity.get("current_velocity", {}).get("average_velocity", 0)
                    console.print(f"[bold]Average Velocity:[/bold] {avg_velocity:.1f} points/sprint")
    
    asyncio.run(gen_report())

@cli.command()
@click.pass_context
def dashboard(ctx):
    """Launch interactive dashboard"""
    async def launch_dashboard():
        cli_instance = BMADScrumMasterCLI(ctx.obj['project'], ctx.obj['config'])
        await cli_instance.initialize()
        
        console.print("[bold blue]🚀 Launching BMAD Scrum Master Dashboard...[/bold blue]")
        
        # This would launch a web-based dashboard
        # For now, display a summary
        
        with console.status("[bold green]Loading dashboard data..."):
            # Get current sprint status
            progress_data = await cli_instance.scrum_master.track_progress()
            
            # Get team metrics
            velocity_data = await cli_instance.scrum_master.manage_velocity()
            
            # Get risk assessment
            risks = await cli_instance.scrum_master.manage_risks()
        
        console.print("\n" + "="*60)
        console.print(f"[bold cyan]BMAD SCRUM MASTER DASHBOARD - {ctx.obj['project'].upper()}[/bold cyan]")
        console.print("="*60)
        
        # Sprint overview
        if "error" not in progress_data:
            health = progress_data["sprint_health"]
            console.print(f"\n[bold]Current Sprint Health:[/bold] {health['health_status'].title()} ({health['health_score']:.0f}%)")
            console.print(f"[bold]Progress:[/bold] {health['actual_progress']:.0f}% (Expected: {health['expected_progress']:.0f}%)")
            console.print(f"[bold]Days Remaining:[/bold] {health['days_remaining']}")
        
        # Velocity overview
        if "error" not in velocity_data:
            current_vel = velocity_data.get("current_velocity", {})
            if current_vel:
                console.print(f"\n[bold]Team Velocity:[/bold] {current_vel.get('average_velocity', 0):.1f} points/sprint")
                trend = velocity_data.get("velocity_trend", {}).get("trend_direction", "stable")
                trend_color = {"increasing": "green", "decreasing": "red", "stable": "blue"}.get(trend, "white")
                console.print(f"[bold]Velocity Trend:[/bold] [{trend_color}]{trend.title()}[/{trend_color}]")
        
        # Risk overview
        current_risks = risks.get("current_risks", [])
        console.print(f"\n[bold]Active Risks:[/bold] {len(current_risks)}")
        for risk in current_risks[:3]:  # Show top 3 risks
            severity_color = {"high": "red", "medium": "yellow", "low": "green"}.get(risk["severity"], "white")
            console.print(f"  • [{severity_color}]{risk['type'].title()}[/{severity_color}]: {risk['description']}")
        
        console.print(f"\n[blue]Dashboard URL: http://localhost:8080/dashboard/{ctx.obj['project']}[/blue]")
        console.print("[yellow]Note: Web dashboard requires separate server startup[/yellow]")
    
    asyncio.run(launch_dashboard())

@cli.command()
@click.pass_context  
def version(ctx):
    """Show version information"""
    console.print("[bold blue]BMAD Scrum Master Agent[/bold blue]")
    console.print("Version: 1.0.0")
    console.print("Framework: BMAD-METHOD")
    console.print("Author: BMAD Framework Team")
    console.print("License: MIT")

def main():
    """Main CLI entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            import traceback
            console.print(f"\n[red]Traceback:[/red]\n{traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()