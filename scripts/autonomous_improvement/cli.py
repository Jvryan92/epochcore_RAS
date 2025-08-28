#!/usr/bin/env python3
"""
Autonomous Continuous Improvement System CLI

This script provides a command-line interface for managing and monitoring
the autonomous continuous improvement system.
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.autonomous_improvement.orchestrator import AutonomousOrchestrator


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def run_orchestrator(args) -> int:
    """Run the autonomous orchestrator."""
    orchestrator = AutonomousOrchestrator(args.config)
    
    if args.daemon:
        print("Running autonomous orchestrator in daemon mode...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                result = await orchestrator._run_async()
                print(f"Cycle complete: {result}")
                
                if args.interval:
                    await asyncio.sleep(args.interval)
                else:
                    # Use the configuration interval
                    await asyncio.sleep(orchestrator.config.health_check_interval)
                    
        except KeyboardInterrupt:
            print("\nShutting down...")
            await orchestrator.shutdown()
            return 0
    else:
        # Run once
        result = await orchestrator._run_async()
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("status") == "success" else 1


async def show_status(args) -> int:
    """Show orchestrator status."""
    orchestrator = AutonomousOrchestrator(args.config)
    status = await orchestrator.get_status()
    print(json.dumps(status, indent=2, default=str))
    return 0


async def show_health(args) -> int:
    """Show repository health report."""
    orchestrator = AutonomousOrchestrator(args.config)
    
    # Force a health check
    await orchestrator._run_health_check()
    
    health_data = orchestrator.health_metrics
    if args.format == "json":
        print(json.dumps(health_data, indent=2, default=str))
    else:
        print_health_summary(health_data)
    
    return 0


def print_health_summary(health_data: Dict[str, Any]) -> None:
    """Print a human-readable health summary."""
    print("=== Repository Health Summary ===")
    print(f"Timestamp: {health_data.get('timestamp', 'N/A')}")
    print()
    
    repo_data = health_data.get("repository", {})
    
    # Files analysis
    files_data = repo_data.get("files", {})
    print(f"Files: {files_data.get('total_files', 0)} total, "
          f"{files_data.get('code_files', 0)} code, "
          f"{files_data.get('test_files', 0)} test")
    
    # Dependencies
    dep_data = repo_data.get("dependencies", {})
    print(f"Dependencies: {dep_data.get('total_dependencies', 0)} total, "
          f"{dep_data.get('outdated', 0)} outdated, "
          f"{dep_data.get('vulnerable', 0)} vulnerable")
    
    # Security
    sec_data = repo_data.get("security", {})
    vulns = sec_data.get("vulnerabilities", {})
    total_vulns = sum(vulns.values()) if vulns else 0
    print(f"Security: {total_vulns} vulnerabilities, "
          f"policy exists: {sec_data.get('security_policy_exists', False)}")
    
    # Quality
    quality_data = repo_data.get("quality", {})
    print(f"Quality: Linting {quality_data.get('linting_score', 0):.1f}%, "
          f"Maintainability {quality_data.get('maintainability_index', 0):.1f}%")
    
    # Tests
    test_data = repo_data.get("tests", {})
    print(f"Tests: {test_data.get('line_coverage', 0):.1f}% coverage, "
          f"{test_data.get('total_tests', 0)} total, "
          f"{test_data.get('failing_tests', 0)} failing")
    
    # Workflows
    workflow_data = health_data.get("workflows", {})
    print(f"Workflows: {workflow_data.get('total_workflows', 0)} total, "
          f"{workflow_data.get('success_rate', 0):.1%} success rate")
    
    # Performance
    perf_data = health_data.get("performance", {})
    print(f"Performance: Score {perf_data.get('score', 0):.1%}, "
          f"Build time {perf_data.get('build_time', 0)}s")


def configure_system(args) -> int:
    """Configure the autonomous system."""
    orchestrator = AutonomousOrchestrator(args.config)
    config = orchestrator.config
    
    if args.enable is not None:
        config.enabled = args.enable
    
    if args.safe_mode is not None:
        config.safe_mode = args.safe_mode
    
    if args.max_tasks is not None:
        config.max_concurrent_tasks = args.max_tasks
    
    if args.health_interval is not None:
        config.health_check_interval = args.health_interval
    
    if args.improvement_interval is not None:
        config.improvement_interval = args.improvement_interval
    
    if args.exclude_categories:
        config.excluded_categories = args.exclude_categories
    
    # Save updated configuration
    orchestrator._save_config(config)
    print("Configuration updated successfully")
    
    # Show current configuration
    print("\nCurrent Configuration:")
    print(json.dumps(config.model_dump(), indent=2))
    
    return 0


def list_reports(args) -> int:
    """List available improvement reports."""
    reports_dir = Path(".autonomous/reports")
    
    if not reports_dir.exists():
        print("No reports directory found")
        return 1
    
    reports = sorted(reports_dir.glob("report_*.json"), reverse=True)
    
    if not reports:
        print("No reports found")
        return 0
    
    print(f"Found {len(reports)} reports:")
    print()
    
    for i, report_file in enumerate(reports[:args.limit]):
        try:
            with open(report_file) as f:
                report_data = json.load(f)
            
            timestamp = report_data.get("timestamp", "Unknown")
            health_score = report_data.get("health_score", 0)
            improvements = report_data.get("recent_improvements", 0)
            
            print(f"{i+1}. {report_file.name}")
            print(f"   Time: {timestamp}")
            print(f"   Health Score: {health_score:.2%}")
            print(f"   Recent Improvements: {improvements}")
            print()
            
        except Exception as e:
            print(f"Error reading {report_file}: {e}")
    
    return 0


def show_report(args) -> int:
    """Show a specific report."""
    report_file = Path(args.report_file)
    
    if not report_file.exists():
        print(f"Report file not found: {report_file}")
        return 1
    
    try:
        with open(report_file) as f:
            report_data = json.load(f)
        
        if args.format == "json":
            print(json.dumps(report_data, indent=2))
        else:
            print_report_summary(report_data)
        
    except Exception as e:
        print(f"Error reading report: {e}")
        return 1
    
    return 0


def print_report_summary(report_data: Dict[str, Any]) -> None:
    """Print a human-readable report summary."""
    print("=== Improvement Report ===")
    print(f"Timestamp: {report_data.get('timestamp', 'N/A')}")
    print(f"Health Score: {report_data.get('health_score', 0):.2%}")
    print(f"Recent Improvements: {report_data.get('recent_improvements', 0)}")
    print(f"Active Tasks: {report_data.get('active_tasks', 0)}")
    print(f"Queued Tasks: {report_data.get('queued_tasks', 0)}")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Continuous Improvement System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                    # Run orchestrator once
  %(prog)s run --daemon           # Run continuously
  %(prog)s status                 # Show current status
  %(prog)s health                 # Show health report
  %(prog)s configure --enable     # Enable autonomous system
  %(prog)s reports                # List recent reports
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Configuration file path",
        default=".autonomous/config.yaml"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run the autonomous orchestrator")
    run_parser.add_argument(
        "--daemon", "-d",
        action="store_true",
        help="Run in daemon mode (continuously)"
    )
    run_parser.add_argument(
        "--interval", "-i",
        type=int,
        help="Interval between runs in daemon mode (seconds)"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show orchestrator status")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Show repository health")
    health_parser.add_argument(
        "--format", "-f",
        choices=["json", "summary"],
        default="summary",
        help="Output format"
    )
    
    # Configure command
    config_parser = subparsers.add_parser("configure", help="Configure the system")
    config_parser.add_argument("--enable", action="store_true", help="Enable autonomous system")
    config_parser.add_argument("--disable", dest="enable", action="store_false", help="Disable autonomous system")
    config_parser.add_argument("--safe-mode", action="store_true", help="Enable safe mode")
    config_parser.add_argument("--no-safe-mode", dest="safe_mode", action="store_false", help="Disable safe mode")
    config_parser.add_argument("--max-tasks", type=int, help="Maximum concurrent tasks")
    config_parser.add_argument("--health-interval", type=int, help="Health check interval (seconds)")
    config_parser.add_argument("--improvement-interval", type=int, help="Improvement generation interval (seconds)")
    config_parser.add_argument("--exclude-categories", nargs="+", help="Categories to exclude")
    
    # Reports command
    reports_parser = subparsers.add_parser("reports", help="List improvement reports")
    reports_parser.add_argument("--limit", type=int, default=10, help="Number of reports to show")
    
    # Show report command
    show_parser = subparsers.add_parser("show", help="Show specific report")
    show_parser.add_argument("report_file", help="Path to report file")
    show_parser.add_argument(
        "--format", "-f",
        choices=["json", "summary"],
        default="summary",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    setup_logging(args.verbose)
    
    try:
        if args.command == "run":
            return asyncio.run(run_orchestrator(args))
        elif args.command == "status":
            return asyncio.run(show_status(args))
        elif args.command == "health":
            return asyncio.run(show_health(args))
        elif args.command == "configure":
            return configure_system(args)
        elif args.command == "reports":
            return list_reports(args)
        elif args.command == "show":
            return show_report(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())