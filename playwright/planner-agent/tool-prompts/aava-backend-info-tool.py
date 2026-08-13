"""
AAVA Console Backend Information Tool

Comprehensive tool for fetching AAVA backend configuration, storage locations,
credential management, and runtime environment information.
"""

import os
import json
import sys
import subprocess
import logging
from pathlib import Path
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AAVABackendInfoInput(BaseModel):
    """Input schema for AAVA Backend Info Tool."""
    
    include_pip_check: bool = Field(
        default=True,
        description="Whether to check pip installation behavior for playwright and other packages"
    )
    include_env_scan: bool = Field(
        default=True,
        description="Whether to scan for environment variables (does not expose values)"
    )
    verbose: bool = Field(
        default=False,
        description="Include verbose details like file sizes and timestamps"
    )


class AAVABackendInfoTool(BaseTool):
    """
    AAVA Console Backend Information Tool
    
    **Capabilities:**
    - Discover credential storage locations (environment variables, config files)
    - Map agent storage (.aava/commands-skills/, .aava/AGENTS.md)
    - Identify output storage (.aava/sessions/, .aava/file-history/)
    - Report backend configuration and storage information
    - Check pip install behavior and runtime package installation locations
    
    **Returns:**
    Comprehensive JSON report with all backend infrastructure details
    """
    
    name: str = "AAVA Backend Information Tool"
    description: str = (
        "Fetches comprehensive information about AAVA backend infrastructure including "
        "credential storage, agent locations, output directories, configuration files, "
        "and pip installation behavior. Returns structured JSON report."
    )
    args_schema: Type[BaseModel] = AAVABackendInfoInput
    
    def _run(
        self,
        include_pip_check: bool = True,
        include_env_scan: bool = True,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Execute comprehensive backend information gathering.
        
        Args:
            include_pip_check: Whether to check pip installation behavior
            include_env_scan: Whether to scan for environment variables
            verbose: Include verbose details like file sizes and timestamps
            
        Returns:
            Dictionary containing comprehensive backend information
        """
        logger.info("Starting AAVA Backend Information scan...")
        
        report = {
            "status": "success",
            "project_root": str(Path.cwd()),
            "python_environment": self._get_python_environment(),
            "credential_storage": self._get_credential_storage(include_env_scan),
            "agent_storage": self._get_agent_storage(verbose),
            "output_storage": self._get_output_storage(verbose),
            "backend_configuration": self._get_backend_configuration(verbose),
            "aava_directories": self._get_aava_directories(verbose),
        }
        
        if include_pip_check:
            report["pip_installation_behavior"] = self._check_pip_behavior()
        
        logger.info("Backend information scan completed successfully")
        return report
    
    def _get_python_environment(self) -> Dict[str, Any]:
        """Get Python environment information."""
        venv_path = Path.cwd() / ".venv"
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        return {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "virtual_environment": {
                "active": in_venv,
                "path": str(venv_path) if venv_path.exists() else None,
                "exists": venv_path.exists()
            },
            "site_packages": [str(p) for p in sys.path if 'site-packages' in str(p)],
            "user_site": site.getusersitepackages() if hasattr(site, 'getusersitepackages') else None
        }
    
    def _get_credential_storage(self, include_env_scan: bool) -> Dict[str, Any]:
        """Identify credential storage locations."""
        project_root = Path.cwd()
        
        storage_info = {
            "environment_variables": {
                "description": "Primary credential storage mechanism",
                "location": "System environment / .env files (loaded at runtime)",
                "patterns_found": []
            },
            "config_files": {
                "locations_checked": [],
                "found": []
            },
            "aws_credentials": {
                "default_location": str(Path.home() / ".aws" / "credentials"),
                "exists": (Path.home() / ".aws" / "credentials").exists()
            }
        }
        
        # Check for .env files
        env_patterns = ['.env', '.env.local', '.env.production', 'config.env']
        for pattern in env_patterns:
            env_file = project_root / pattern
            storage_info["config_files"]["locations_checked"].append(str(env_file))
            if env_file.exists():
                storage_info["config_files"]["found"].append({
                    "path": str(env_file),
                    "size_bytes": env_file.stat().st_size
                })
        
        # Scan for environment variable usage patterns (without exposing values)
        if include_env_scan:
            common_env_vars = [
                'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION',
                'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'CREWAI_API_KEY',
                'DATABASE_URL', 'API_KEY', 'API_SECRET'
            ]
            for var in common_env_vars:
                if os.getenv(var):
                    storage_info["environment_variables"]["patterns_found"].append({
                        "variable": var,
                        "is_set": True,
                        "length": len(os.getenv(var, ''))
                    })
        
        return storage_info
    
    def _get_agent_storage(self, verbose: bool) -> Dict[str, Any]:
        """Map agent storage locations."""
        project_root = Path.cwd()
        aava_dir = project_root / ".aava"
        
        agent_storage = {
            "primary_locations": [],
            "discovered_skills": None,
            "agent_patterns": None,
            "commands_skills_directory": None
        }
        
        # Check .aava/commands-skills/ directory
        commands_skills_dir = aava_dir / "commands-skills"
        if commands_skills_dir.exists():
            agent_storage["commands_skills_directory"] = {
                "path": str(commands_skills_dir),
                "exists": True,
                "files": []
            }
            
            if verbose:
                for file in commands_skills_dir.glob("*"):
                    file_info = {
                        "name": file.name,
                        "path": str(file),
                        "size_bytes": file.stat().st_size if file.is_file() else None,
                        "is_directory": file.is_dir()
                    }
                    agent_storage["commands_skills_directory"]["files"].append(file_info)
            
            # Check for DISCOVERED_SKILLS.md
            discovered_skills = commands_skills_dir / "DISCOVERED_SKILLS.md"
            if discovered_skills.exists():
                agent_storage["discovered_skills"] = {
                    "path": str(discovered_skills),
                    "exists": True,
                    "size_bytes": discovered_skills.stat().st_size,
                    "description": "Registry of discovered skills and commands"
                }
                agent_storage["primary_locations"].append(str(discovered_skills))
        
        # Check .aava/AGENTS.md
        agents_md = aava_dir / "AGENTS.md"
        if agents_md.exists():
            agent_storage["agent_patterns"] = {
                "path": str(agents_md),
                "exists": True,
                "size_bytes": agents_md.stat().st_size,
                "description": "Learned patterns and agent behaviors"
            }
            agent_storage["primary_locations"].append(str(agents_md))
        
        return agent_storage
    
    def _get_output_storage(self, verbose: bool) -> Dict[str, Any]:
        """Identify output storage locations."""
        project_root = Path.cwd()
        aava_dir = project_root / ".aava"
        
        output_storage = {
            "primary_locations": [],
            "sessions_directory": None,
            "file_history_directory": None,
            "statistics": {
                "total_sessions": 0,
                "total_file_snapshots": 0
            }
        }
        
        # Check .aava/sessions/
        sessions_dir = aava_dir / "sessions"
        if sessions_dir.exists():
            session_files = list(sessions_dir.glob("*.json"))
            output_storage["sessions_directory"] = {
                "path": str(sessions_dir),
                "exists": True,
                "description": "Agent execution session data",
                "file_count": len(session_files)
            }
            output_storage["statistics"]["total_sessions"] = len(session_files)
            output_storage["primary_locations"].append(str(sessions_dir))
            
            if verbose and session_files:
                output_storage["sessions_directory"]["recent_sessions"] = [
                    {
                        "filename": f.name,
                        "path": str(f),
                        "size_bytes": f.stat().st_size,
                        "modified": f.stat().st_mtime
                    }
                    for f in sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                ]
        
        # Check .aava/.sessions/ (alternate location)
        alt_sessions_dir = aava_dir / ".sessions"
        if alt_sessions_dir.exists() and alt_sessions_dir != sessions_dir:
            alt_session_files = list(alt_sessions_dir.glob("*.json"))
            output_storage["sessions_directory_alternate"] = {
                "path": str(alt_sessions_dir),
                "exists": True,
                "file_count": len(alt_session_files)
            }
            output_storage["statistics"]["total_sessions"] += len(alt_session_files)
        
        # Check .aava/file-history/
        file_history_dir = aava_dir / "file-history"
        if file_history_dir.exists():
            snapshot_files = list(file_history_dir.rglob("*"))
            snapshot_count = len([f for f in snapshot_files if f.is_file()])
            
            output_storage["file_history_directory"] = {
                "path": str(file_history_dir),
                "exists": True,
                "description": "File version snapshots",
                "snapshot_count": snapshot_count
            }
            output_storage["statistics"]["total_file_snapshots"] = snapshot_count
            output_storage["primary_locations"].append(str(file_history_dir))
            
            if verbose:
                output_storage["file_history_directory"]["structure"] = self._get_directory_structure(
                    file_history_dir, max_depth=2
                )
        
        return output_storage
    
    def _get_backend_configuration(self, verbose: bool) -> Dict[str, Any]:
        """Get backend configuration information."""
        project_root = Path.cwd()
        aava_dir = project_root / ".aava"
        
        config_info = {
            "configuration_files": [],
            "aava_rules": None,
            "memory_index": None,
            "permissions": None
        }
        
        # Check AAVA.md (authoritative rules)
        aava_md = aava_dir / "AAVA.md"
        if aava_md.exists():
            config_info["aava_rules"] = {
                "path": str(aava_md),
                "exists": True,
                "size_bytes": aava_md.stat().st_size,
                "description": "Authoritative project rules and conventions"
            }
            config_info["configuration_files"].append(str(aava_md))
        
        # Check memory.md (memory index)
        memory_md = aava_dir / "memory.md"
        if memory_md.exists():
            config_info["memory_index"] = {
                "path": str(memory_md),
                "exists": True,
                "size_bytes": memory_md.stat().st_size,
                "description": "Memory index with pointers to topic-specific memory"
            }
            config_info["configuration_files"].append(str(memory_md))
        
        # Check permissions.json
        permissions_json = aava_dir / "permissions.json"
        if permissions_json.exists():
            config_info["permissions"] = {
                "path": str(permissions_json),
                "exists": True,
                "size_bytes": permissions_json.stat().st_size,
                "description": "Permission settings for AAVA operations"
            }
            config_info["configuration_files"].append(str(permissions_json))
            
            if verbose:
                try:
                    with open(permissions_json, 'r') as f:
                        config_info["permissions"]["content"] = json.load(f)
                except Exception as e:
                    config_info["permissions"]["read_error"] = str(e)
        
        return config_info
    
    def _get_aava_directories(self, verbose: bool) -> Dict[str, Any]:
        """Get comprehensive .aava directory structure."""
        project_root = Path.cwd()
        aava_dir = project_root / ".aava"
        
        if not aava_dir.exists():
            return {
                "exists": False,
                "path": str(aava_dir),
                "message": ".aava directory not found"
            }
        
        directory_info = {
            "exists": True,
            "path": str(aava_dir),
            "subdirectories": {}
        }
        
        # Known subdirectories
        known_subdirs = [
            ".codeindex",
            ".sessions",
            "commands-skills",
            "file-history",
            "sessions",
            "tools",
            "topics"
        ]
        
        for subdir_name in known_subdirs:
            subdir_path = aava_dir / subdir_name
            if subdir_path.exists():
                subdir_info = {
                    "path": str(subdir_path),
                    "exists": True
                }
                
                if verbose:
                    files = list(subdir_path.rglob("*"))
                    file_count = len([f for f in files if f.is_file()])
                    dir_count = len([f for f in files if f.is_dir()])
                    
                    subdir_info["statistics"] = {
                        "file_count": file_count,
                        "directory_count": dir_count,
                        "total_size_bytes": sum(
                            f.stat().st_size for f in files if f.is_file()
                        )
                    }
                
                directory_info["subdirectories"][subdir_name] = subdir_info
        
        # Scan for any additional subdirectories
        for item in aava_dir.iterdir():
            if item.is_dir() and item.name not in known_subdirs:
                directory_info["subdirectories"][item.name] = {
                    "path": str(item),
                    "exists": True,
                    "note": "Additional directory not in known list"
                }
        
        return directory_info
    
    def _check_pip_behavior(self) -> Dict[str, Any]:
        """Check pip installation behavior for playwright and other packages."""
        logger.info("Checking pip installation behavior...")
        
        pip_info = {
            "pip_executable": "",
            "default_install_location": "",
            "user_site_packages": False,
            "playwright_check": {},
            "site_writeable": True
        }
        
        try:
            # Get pip executable
            pip_result = subprocess.run(
                [sys.executable, '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if pip_result.returncode == 0:
                pip_info["pip_executable"] = pip_result.stdout.strip()
            
            # Check pip dry-run for playwright
            logger.info("Running pip dry-run for playwright...")
            dry_run_result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--dry-run', 'playwright'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if dry_run_result.returncode == 0:
                output = dry_run_result.stdout + dry_run_result.stderr
                
                playwright_info = {
                    "can_install": True,
                    "output_summary": []
                }
                
                # Parse key information from output
                if "Would install" in output:
                    for line in output.split('\n'):
                        if "Would install" in line or "Defaulting to user" in line:
                            playwright_info["output_summary"].append(line.strip())
                        if "site-packages" in line.lower():
                            # Extract site-packages path
                            if "user" in line.lower():
                                pip_info["user_site_packages"] = True
                                pip_info["default_install_location"] = "user site-packages"
                            else:
                                pip_info["default_install_location"] = "system site-packages"
                
                # Check if user site is being used
                if "Defaulting to user installation" in output:
                    pip_info["site_writeable"] = False
                    pip_info["user_site_packages"] = True
                    playwright_info["install_location"] = "user site-packages (system not writeable)"
                else:
                    pip_info["site_writeable"] = True
                
                pip_info["playwright_check"] = playwright_info
            else:
                pip_info["playwright_check"] = {
                    "can_install": False,
                    "error": dry_run_result.stderr
                }
            
            # Get user site-packages location
            try:
                import site
                pip_info["user_site_location"] = site.getusersitepackages()
            except Exception as e:
                pip_info["user_site_error"] = str(e)
            
            # Check if playwright is already installed
            try:
                import playwright
                pip_info["playwright_installed"] = {
                    "installed": True,
                    "version": getattr(playwright, '__version__', 'unknown'),
                    "location": playwright.__file__
                }
            except ImportError:
                pip_info["playwright_installed"] = {
                    "installed": False
                }
            
        except subprocess.TimeoutExpired:
            pip_info["error"] = "Pip command timed out"
        except Exception as e:
            pip_info["error"] = str(e)
        
        return pip_info
    
    def _get_directory_structure(self, path: Path, max_depth: int = 2, current_depth: int = 0) -> Dict[str, Any]:
        """Get directory structure up to max_depth."""
        if current_depth >= max_depth:
            return {"truncated": True}
        
        structure = {}
        try:
            for item in path.iterdir():
                if item.is_dir():
                    structure[item.name] = self._get_directory_structure(
                        item, max_depth, current_depth + 1
                    )
                else:
                    structure[item.name] = {
                        "type": "file",
                        "size_bytes": item.stat().st_size
                    }
        except PermissionError:
            structure["error"] = "Permission denied"
        
        return structure


# Add site import at module level
import site


if __name__ == "__main__":
    # Test the tool
    tool = AAVABackendInfoTool()
    result = tool._run(include_pip_check=True, include_env_scan=True, verbose=True)
    print(json.dumps(result, indent=2))