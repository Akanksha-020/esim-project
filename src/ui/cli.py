"""
Command-Line Interface for eSim Tool Manager
Provides user-friendly commands for tool management
"""

import sys
import click
from tabulate import tabulate
from typing import Optional
from src.utils.logger import get_logger
from src.core.config_manager import ConfigManager
from src.core.installer import InstallationManager
from src.core.updater import UpdateChecker
from src.utils.dependency_checker import DependencyChecker

# Initialize managers
logger = get_logger()
config_manager = ConfigManager()
installer = InstallationManager()
updater = UpdateChecker()
dep_checker = DependencyChecker()

@click.group()
@click.version_option(version="1.0.0", prog_name="eSim Tool Manager")
def cli():
    """
    eSim Tool Manager - Automated tool installation and management
    
    Manage external tools and dependencies for eSim
    """
    pass

@cli.command()
@click.argument('tool_name')
@click.option('--version', '-v', default=None, help='Specific version to install')
def install(tool_name: str, version: Optional[str] = None):
    """
    Install a tool
    
    Example: tool-manager install ngspice --version 39
    """
    try:
        with click.progressbar(length=1, label=f'Installing {tool_name}') as bar:
            result = installer.install_tool(tool_name, version)
            bar.update(1)
        
        if result:
            click.echo(f"✓ {tool_name} installed successfully")
        else:
            click.echo(f"✗ Failed to install {tool_name}", err=True)
            sys.exit(1)
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)
    
    finally:
        installer.cleanup_temp_files()

@cli.command()
@click.argument('tool_name', required=False)
@click.option('--all', is_flag=True, help='Update all tools')
def update(tool_name: Optional[str], all: bool):
    """
    Update tool(s)
    
    Examples:
        tool-manager update ngspice              # Update specific tool
        tool-manager update --all                 # Update all tools
    """
    try:
        if all or not tool_name:
            click.echo("Updating all tools with available updates...")
            results = updater.perform_update_all()
            
            success_count = sum(1 for v in results.values() if v)
            click.echo(f"\n✓ Updated {success_count}/{len(results)} tools successfully")
        else:
            click.echo(f"Updating {tool_name}...")
            if updater.perform_update(tool_name):
                click.echo(f"✓ {tool_name} updated successfully")
            else:
                click.echo(f"✗ Failed to update {tool_name}", err=True)
                sys.exit(1)
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
def checks_updates():
    """Check for available updates for all tools"""
    try:
        updater.print_update_report()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
def list_tools():
    """List installed and available tools"""
    try:
        all_tools = config_manager.get_all_tools()
        
        if not all_tools:
            click.echo("No tools configured")
            return
        
        table_data = []
        for tool_name, config in all_tools.items():
            status = "Installed" if config.get("installed") else "Not installed"
            current = config.get("current_version") or "N/A"
            latest = config.get("latest_version") or "N/A"
            
            table_data.append([
                tool_name,
                current,
                latest,
                status,
                config.get("description", "")
            ])
        
        headers = ["Tool", "Current Version", "Latest Version", "Status", "Description"]
        click.echo("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        click.echo()
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('tool_name')
def status(tool_name: str):
    """Show tool status and information"""
    try:
        tool_config = config_manager.get_tool_config(tool_name)
        
        if not tool_config:
            click.echo(f"✗ Tool '{tool_name}' not found", err=True)
            sys.exit(1)
        
        click.echo(f"\nStatus for {tool_name}:")
        click.echo("=" * 50)
        
        status_info = [
            ["Name", tool_config.get("name")],
            ["Description", tool_config.get("description")],
            ["Status", "Installed" if tool_config.get("installed") else "Not installed"],
            ["Current Version", tool_config.get("current_version") or "N/A"],
            ["Latest Version", tool_config.get("latest_version") or "N/A"],
            ["Installation Path", tool_config.get("install_path") or "N/A"],
        ]
        
        click.echo(tabulate(status_info, tablefmt="simple"))
        click.echo("=" * 50 + "\n")
        
        # Show dependencies
        dep_checker.print_dependency_report(tool_name)
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('tool_name')
def uninstall(tool_name: str):
    """Uninstall a tool"""
    try:
        tool_config = config_manager.get_tool_config(tool_name)
        
        if not tool_config or not tool_config.get("installed"):
            click.echo(f"✗ Tool '{tool_name}' is not installed", err=True)
            sys.exit(1)
        
        if click.confirm(f"Are you sure you want to uninstall {tool_name}?"):
            if installer.uninstall_tool(tool_name):
                click.echo(f"✓ {tool_name} uninstalled successfully")
            else:
                click.echo(f"✗ Failed to uninstall {tool_name}", err=True)
                sys.exit(1)
        else:
            click.echo("Uninstall cancelled")
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--last', '-l', type=int, default=20, help='Number of recent logs to show')
def logs(last: int):
    """Display recent action logs"""
    try:
        action_history = logger.get_action_history(last)
        
        if not action_history:
            click.echo("No actions logged")
            return
        
        click.echo(f"\nRecent Actions (Last {min(last, len(action_history))} entries):")
        click.echo("=" * 80)
        
        for action in reversed(action_history[-last:]):
            timestamp = action.get("timestamp")
            level = action.get("level")
            message = action.get("message")
            
            # Color code by level
            if level == "ERROR":
                level_str = click.style(level, fg="red", bold=True)
            elif level == "WARNING":
                level_str = click.style(level, fg="yellow", bold=True)
            elif level == "SUCCESS":
                level_str = click.style(level, fg="green", bold=True)
            else:
                level_str = level
            
            click.echo(f"[{timestamp}] {level_str:10} {message}")
        
        click.echo("=" * 80 + "\n")
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('tool_name')
def config(tool_name: str):
    """Show tool configuration"""
    try:
        tool_config = config_manager.get_tool_config(tool_name)
        
        if not tool_config:
            click.echo(f"✗ Tool '{tool_name}' not found", err=True)
            sys.exit(1)
        
        import json
        click.echo(f"\nConfiguration for {tool_name}:")
        click.echo("=" * 50)
        click.echo(json.dumps(tool_config, indent=2))
        click.echo("=" * 50 + "\n")
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('tool_name')
def dependencies(tool_name: str):
    """Show tool dependencies"""
    try:
        dep_tree = dep_checker.get_dependency_tree(tool_name)
        
        if not dep_tree:
            click.echo(f"✗ Tool '{tool_name}' not found", err=True)
            sys.exit(1)
        
        dep_checker.print_dependency_report(tool_name)
        
        # Show missing dependencies if any
        missing = dep_checker.get_missing_dependencies(tool_name)
        if missing:
            click.echo("\nMissing Dependencies:")
            click.echo("-" * 50)
            for dep in missing:
                click.echo(f"  • {dep['name']}: {dep.get('description')}")
                if dep.get('download_url'):
                    click.echo(f"    Download: {dep['download_url']}")
            click.echo()
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command()
def system_info():
    """Display system information"""
    try:
        from src.utils.system_utils import SystemInfo
        
        click.echo("\nSystem Information:")
        click.echo("=" * 50)
        
        info_data = [
            ["Operating System", SystemInfo.get_os()],
            ["OS Version", SystemInfo.get_os_version()],
            ["Python Version", SystemInfo.get_python_version()],
            ["Architecture", SystemInfo.get_architecture()],
            ["Installation Directory", str(config_manager.get_installation_directory())],
            ["Log Directory", str(config_manager.get_log_directory())],
        ]
        
        click.echo(tabulate(info_data, tablefmt="simple"))
        click.echo("=" * 50 + "\n")
    
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        sys.exit(1)

def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n✗ Unexpected error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
