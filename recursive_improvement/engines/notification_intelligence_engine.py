"""
Notification Intelligence Engine - Advanced autonomous notification monitoring and classification

This engine monitors all system outputs, logs, errors, and notifications to:
1. Automatically detect and classify notifications by type and severity
2. Learn patterns from historical notification data
3. Trigger appropriate recursive improvement responses
4. Track resolution effectiveness for continuous learning

Part of the Complex Autonomy Innovation framework for recursive notification resolution.
"""

import re
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from pathlib import Path

from ..base import RecursiveEngine, CompoundingAction


class NotificationIntelligenceEngine(RecursiveEngine):
    """Advanced notification intelligence for autonomous resolution."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("notification_intelligence_engine", config or {})
        
        # Notification classification patterns
        self.notification_patterns = {
            'error': [
                r'error.*?:',
                r'exception.*?:',
                r'failed.*?:',
                r'traceback',
                r'critical.*?:',
                r'fatal.*?:'
            ],
            'warning': [
                r'warning.*?:',
                r'deprecated.*?:',
                r'caution.*?:',
                r'alert.*?:'
            ],
            'performance': [
                r'slow.*?query',
                r'timeout.*?:',
                r'high.*?cpu',
                r'memory.*?usage',
                r'performance.*?degradation'
            ],
            'security': [
                r'security.*?violation',
                r'unauthorized.*?access',
                r'authentication.*?failed',
                r'permission.*?denied',
                r'vulnerability.*?detected'
            ],
            'system': [
                r'system.*?down',
                r'service.*?unavailable',
                r'connection.*?failed',
                r'disk.*?full',
                r'network.*?error'
            ]
        }
        
        # Notification storage and learning
        self.notifications_db = []
        self.pattern_learning = defaultdict(int)
        self.resolution_history = defaultdict(list)
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Learning capabilities
        self.learning_threshold = 3  # Learn patterns after 3 occurrences
        self.auto_resolve_confidence = 0.8  # Confidence threshold for auto-resolution
        
        # Setup monitoring paths
        self.monitor_paths = [
            "logs/",
            "/var/log/",
            "/tmp/",
            "."
        ]
        
    def initialize(self) -> bool:
        """Initialize the notification intelligence engine."""
        try:
            # Initialize compounding actions
            self.initialize_actions()
            
            self.logger.info(f"{self.name}: Notification Intelligence Engine initialized")
            return True
        except Exception as e:
            self.logger.error(f"{self.name}: Initialization failed - {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute the main notification intelligence action."""
        return self._comprehensive_notification_analysis()
    
    def initialize_actions(self):
        """Initialize compounding actions for notification monitoring."""
        # Main action: Comprehensive notification scan and analysis
        def comprehensive_notification_scan():
            return self._comprehensive_notification_analysis()
        
        # Pre-action: Quick notification detection during main scan
        def quick_notification_detection():
            return self._quick_notification_scan()
        
        scan_action = CompoundingAction(
            name="comprehensive_notification_scan",
            action=comprehensive_notification_scan,
            interval=1.0,  # Weekly comprehensive scan
            pre_action=quick_notification_detection,
            pre_interval=0.25,  # Quick scans every ~2 days
            metadata={
                "type": "monitoring",
                "priority": "high",
                "learning_enabled": True
            }
        )
        
        self.add_compounding_action(scan_action)
    
    def start(self) -> bool:
        """Start the notification intelligence engine with continuous monitoring."""
        if not super().start():
            return False
        
        # Start continuous monitoring thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._continuous_monitor, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info(f"{self.name}: Continuous notification monitoring started")
        return True
    
    def stop(self):
        """Stop the notification intelligence engine."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        super().stop()
    
    def _continuous_monitor(self):
        """Continuously monitor for new notifications."""
        while self.monitoring_active:
            try:
                # Quick scan for new notifications
                new_notifications = self._scan_for_notifications()
                
                if new_notifications:
                    # Process new notifications immediately
                    for notification in new_notifications:
                        self._process_notification(notification)
                        
                        # Trigger autonomous resolution if confidence is high
                        if self._should_auto_resolve(notification):
                            self._trigger_autonomous_resolution(notification)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Continuous monitoring error: {e}")
                time.sleep(60)  # Longer wait on error
    
    def _comprehensive_notification_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive notification analysis and learning."""
        self.logger.info("Starting comprehensive notification analysis")
        
        analysis_results = {
            "notifications_analyzed": 0,
            "patterns_learned": 0,
            "auto_resolutions_triggered": 0,
            "learning_updates": []
        }
        
        try:
            # Scan all monitoring paths
            all_notifications = []
            for path in self.monitor_paths:
                path_notifications = self._scan_path_for_notifications(path)
                all_notifications.extend(path_notifications)
            
            analysis_results["notifications_analyzed"] = len(all_notifications)
            
            # Process each notification
            for notification in all_notifications:
                # Learn from the notification
                learning_result = self._learn_from_notification(notification)
                if learning_result:
                    analysis_results["learning_updates"].append(learning_result)
                    analysis_results["patterns_learned"] += 1
                
                # Check if we should auto-resolve
                if self._should_auto_resolve(notification):
                    self._trigger_autonomous_resolution(notification)
                    analysis_results["auto_resolutions_triggered"] += 1
            
            # Update pattern learning database
            self._update_pattern_database()
            
            self.logger.info(f"Comprehensive analysis complete: {analysis_results}")
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis error: {e}")
            analysis_results["error"] = str(e)
        
        return analysis_results
    
    def _quick_notification_scan(self) -> Dict[str, Any]:
        """Quick scan for immediate notifications during main analysis."""
        self.logger.debug("Quick notification detection running")
        
        scan_results = {
            "quick_scan": True,
            "notifications_found": 0,
            "immediate_actions": 0
        }
        
        try:
            # Focus on most recent logs and critical areas
            recent_notifications = self._scan_recent_notifications()
            scan_results["notifications_found"] = len(recent_notifications)
            
            # Immediate response for critical notifications
            for notification in recent_notifications:
                if notification.get("severity") == "critical":
                    self._trigger_immediate_response(notification)
                    scan_results["immediate_actions"] += 1
        
        except Exception as e:
            self.logger.debug(f"Quick scan error: {e}")
        
        return scan_results
    
    def _scan_for_notifications(self) -> List[Dict[str, Any]]:
        """Scan for new notifications across all monitored sources."""
        notifications = []
        
        try:
            # Check log files
            for path in self.monitor_paths:
                if Path(path).exists():
                    path_notifications = self._scan_path_for_notifications(path)
                    notifications.extend(path_notifications)
            
            # Filter to only new notifications (not seen in last scan)
            new_notifications = self._filter_new_notifications(notifications)
            
        except Exception as e:
            self.logger.error(f"Notification scan error: {e}")
        
        return new_notifications
    
    def _scan_path_for_notifications(self, path: str) -> List[Dict[str, Any]]:
        """Scan a specific path for notifications."""
        notifications = []
        path_obj = Path(path)
        
        try:
            if path_obj.is_file():
                notifications.extend(self._scan_file_for_notifications(str(path_obj)))
            elif path_obj.is_dir():
                # Scan recent log files
                for file_path in path_obj.glob("*.log"):
                    if file_path.stat().st_mtime > (time.time() - 86400):  # Last 24 hours
                        notifications.extend(self._scan_file_for_notifications(str(file_path)))
                        
        except Exception as e:
            self.logger.debug(f"Path scan error for {path}: {e}")
        
        return notifications
    
    def _scan_file_for_notifications(self, file_path: str) -> List[Dict[str, Any]]:
        """Scan a file for notification patterns."""
        notifications = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines[-1000:], 1):  # Last 1000 lines
                for category, patterns in self.notification_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            notification = {
                                "id": f"{file_path}_{line_num}_{hash(line)}",
                                "source": file_path,
                                "line_number": line_num,
                                "content": line.strip(),
                                "category": category,
                                "severity": self._determine_severity(line, category),
                                "timestamp": datetime.now().isoformat(),
                                "pattern_matched": pattern
                            }
                            notifications.append(notification)
                            break  # Only match first pattern per line
                    
        except Exception as e:
            self.logger.debug(f"File scan error for {file_path}: {e}")
        
        return notifications
    
    def _determine_severity(self, line: str, category: str) -> str:
        """Determine notification severity based on content and category."""
        line_lower = line.lower()
        
        # Critical keywords
        if any(keyword in line_lower for keyword in ['critical', 'fatal', 'emergency', 'panic']):
            return 'critical'
        
        # High severity keywords
        if any(keyword in line_lower for keyword in ['error', 'exception', 'failed', 'security']):
            return 'high'
        
        # Medium severity
        if any(keyword in line_lower for keyword in ['warning', 'deprecated', 'timeout']):
            return 'medium'
        
        # Category-based severity
        severity_map = {
            'error': 'high',
            'security': 'critical',
            'performance': 'medium',
            'system': 'high',
            'warning': 'medium'
        }
        
        return severity_map.get(category, 'low')
    
    def _process_notification(self, notification: Dict[str, Any]):
        """Process a notification for learning and potential resolution."""
        # Store in notifications database
        self.notifications_db.append(notification)
        
        # Update pattern learning
        pattern = notification.get("pattern_matched", "unknown")
        self.pattern_learning[pattern] += 1
        
        # Log the notification
        self.logger.info(f"Processed notification: {notification['category']} - {notification['severity']}")
    
    def _learn_from_notification(self, notification: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Learn patterns from notification for future autonomous resolution."""
        pattern_key = f"{notification['category']}:{notification['severity']}"
        
        # Check if we've seen this pattern enough to learn
        if self.pattern_learning[pattern_key] >= self.learning_threshold:
            learning_result = {
                "pattern": pattern_key,
                "occurrences": self.pattern_learning[pattern_key],
                "confidence": min(self.pattern_learning[pattern_key] / 10.0, 1.0),
                "learned_at": datetime.now().isoformat()
            }
            
            # Add to resolution history if we have successful resolutions
            if pattern_key in self.resolution_history:
                success_rate = sum(1 for r in self.resolution_history[pattern_key] if r.get("success")) / len(self.resolution_history[pattern_key])
                learning_result["success_rate"] = success_rate
            
            return learning_result
        
        return None
    
    def _should_auto_resolve(self, notification: Dict[str, Any]) -> bool:
        """Determine if notification should be automatically resolved."""
        pattern_key = f"{notification['category']}:{notification['severity']}"
        
        # Check if we have enough confidence to auto-resolve
        confidence = min(self.pattern_learning[pattern_key] / 10.0, 1.0)
        
        # Check success rate if we have history
        if pattern_key in self.resolution_history:
            success_rate = sum(1 for r in self.resolution_history[pattern_key] if r.get("success")) / len(self.resolution_history[pattern_key])
            return confidence >= self.auto_resolve_confidence and success_rate >= 0.7
        
        # For new patterns, only auto-resolve if we have high confidence
        return confidence >= self.auto_resolve_confidence
    
    def _trigger_autonomous_resolution(self, notification: Dict[str, Any]):
        """Trigger autonomous resolution for a notification."""
        self.logger.info(f"Triggering autonomous resolution for: {notification['id']}")
        
        # This will be enhanced when we integrate with NotificationResolver
        # For now, log the autonomous trigger
        resolution_attempt = {
            "notification_id": notification["id"],
            "triggered_at": datetime.now().isoformat(),
            "pattern": f"{notification['category']}:{notification['severity']}",
            "method": "autonomous"
        }
        
        pattern_key = f"{notification['category']}:{notification['severity']}"
        self.resolution_history[pattern_key].append(resolution_attempt)
    
    def _trigger_immediate_response(self, notification: Dict[str, Any]):
        """Trigger immediate response for critical notifications."""
        self.logger.warning(f"Immediate response triggered for critical notification: {notification['id']}")
        # Implement immediate response logic here
        pass
    
    def _scan_recent_notifications(self) -> List[Dict[str, Any]]:
        """Scan for notifications from the last few minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=5)
        return [n for n in self.notifications_db if datetime.fromisoformat(n["timestamp"]) > cutoff_time]
    
    def _filter_new_notifications(self, notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter to only new notifications not seen before."""
        existing_ids = {n["id"] for n in self.notifications_db}
        return [n for n in notifications if n["id"] not in existing_ids]
    
    def _update_pattern_database(self):
        """Update the pattern learning database."""
        # Save learning data to file for persistence
        try:
            learning_data = {
                "pattern_counts": dict(self.pattern_learning),
                "resolution_history": dict(self.resolution_history),
                "updated_at": datetime.now().isoformat()
            }
            
            Path("logs").mkdir(exist_ok=True)
            with open("logs/notification_learning.json", "w") as f:
                json.dump(learning_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save pattern database: {e}")
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get a summary of the notification intelligence."""
        return {
            "total_notifications": len(self.notifications_db),
            "patterns_learned": len(self.pattern_learning),
            "auto_resolution_confidence": self.auto_resolve_confidence,
            "monitoring_active": self.monitoring_active,
            "recent_notifications": len(self._scan_recent_notifications()),
            "top_patterns": dict(sorted(self.pattern_learning.items(), key=lambda x: x[1], reverse=True)[:5])
        }