"""
Hiring data models and operations.
Handles hiring position data structures and calculations.
"""

from typing import List, Tuple, Dict, Any
from src.config.settings import BASE_STAGES


class HiringPosition:
    """Represents a single hiring position with all its stages and metadata."""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a HiringPosition instance.
        
        Args:
            data: Dictionary containing position data
        """
        self.division = data.get("Division", "")
        self.job_position = data.get("Job Position", "")
        self.pic = data.get("PIC", "")
        self.notes = data.get("Notes", "")
        self.last_updated = data.get("Last Updated", "")
        self.has_skill_test = data.get("Has Skill Test", True)
        self.hire_type = data.get("Hire Type", "Additional")
        self.replacement_for = data.get("Replacement For", "")
        
        # Stage completion status
        self.stages = {stage: data.get(stage, False) for stage in BASE_STAGES}
    
    def get_active_stages(self) -> List[str]:
        """
        Get list of active stages for this position.
        Excludes Skill Test if not required.
        
        Returns:
            List of active stage names
        """
        if self.has_skill_test:
            return BASE_STAGES
        else:
            return [s for s in BASE_STAGES if s != "Skill Test"]
    
    def calculate_progress(self) -> float:
        """
        Calculate completion progress percentage.
        
        Returns:
            Progress percentage (0-100)
        """
        active_stages = self.get_active_stages()
        if len(active_stages) > 0:
            completed = sum([1 for stage in active_stages if self.stages.get(stage, False)])
            return (completed / len(active_stages)) * 100
        return 0.0


def calculate_position_progress(row: Dict[str, Any], stages: List[str]) -> float:
    """
    Calculate progress percentage for a position, accounting for Has Skill Test flag.
    
    Args:
        row: Dictionary or DataFrame row containing position data
        stages: List of all possible stages
        
    Returns:
        Progress percentage (0-100)
    """
    if row.get('Has Skill Test', True):
        active_stages = stages
    else:
        active_stages = [s for s in stages if s != "Skill Test"]
    
    if len(active_stages) > 0:
        completed = sum([1 for stage in active_stages if row.get(stage, False)])
        return (completed / len(active_stages)) * 100
    return 0


def get_hire_type_display(row: Dict[str, Any]) -> str:
    """
    Returns formatted hire type display string.
    
    Args:
        row: Dictionary or DataFrame row containing position data
        
    Returns:
        Formatted hire type string
    """
    hire_type = row.get("Hire Type", "Additional")
    if hire_type == "Replacement":
        replacement_for = row.get("Replacement For", "").strip()
        if replacement_for:
            return f"Replacement_{replacement_for}"
    return "Additional"


def format_skill_test(row: Dict[str, Any]) -> str:
    """
    Format skill test display based on Has Skill Test flag.
    
    Args:
        row: Dictionary or DataFrame row containing position data
        
    Returns:
        Formatted skill test status ("✓", "—", or "")
    """
    if not row.get('Has Skill Test', True):
        return ""  # Empty string if position doesn't require skill test
    else:
        return "✓" if row.get('Skill Test', False) else "—"  # Check mark if done, dash if not


def get_progress_badge(progress_pct: float) -> Tuple[str, str]:
    """
    Get CSS badge class and display text based on progress percentage.
    
    Args:
        progress_pct: Progress percentage (0-100)
        
    Returns:
        Tuple of (badge_class, badge_text)
    """
    if progress_pct == 100:
        return "badge-complete", "Complete"
    elif progress_pct >= 70:
        return "badge-high", f"{progress_pct:.0f}%"
    elif progress_pct >= 40:
        return "badge-medium", f"{progress_pct:.0f}%"
    else:
        return "badge-low", f"{progress_pct:.0f}%"
