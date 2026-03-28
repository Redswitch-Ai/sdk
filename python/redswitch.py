"""
RedSwitch Python SDK
The failsafe for autonomous AI agents.

Usage:
    from redswitch import RedSwitch
    
    rs = RedSwitch(registration_id="rs_...")
    rs.heartbeat()
    rs.shutdown(epitaph="Task complete.")
"""

import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import threading
import time


API_BASE = "https://api.redswitch.ai"


@dataclass
class Agent:
    registration_id: str
    agent_id: str
    agent_name: Optional[str]
    status: str
    platform: str
    capabilities: List[str]
    last_heartbeat: str
    created_at: str


class RedSwitch:
    """RedSwitch client for AI agent lifecycle management."""
    
    def __init__(
        self,
        registration_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        api_base: str = API_BASE
    ):
        self.registration_id = registration_id
        self.agent_id = agent_id
        self.api_base = api_base
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_heartbeat = threading.Event()
    
    def register(
        self,
        agent_id: str,
        human_id: str,
        agent_name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        platform: Optional[str] = None,
        shutdown_procedure: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new agent with RedSwitch.
        
        Args:
            agent_id: Unique identifier for your agent
            human_id: Your email address
            agent_name: Display name for your agent
            capabilities: List of agent capabilities
            platform: Platform name (e.g., 'langchain', 'autogpt')
            shutdown_procedure: Custom shutdown commands/webhooks
            
        Returns:
            Registration response with registration_id
        """
        payload = {
            "agent_id": agent_id,
            "human_id": human_id,
        }
        
        if agent_name:
            payload["agent_name"] = agent_name
        if capabilities:
            payload["capabilities"] = capabilities
        if platform:
            payload["platform"] = platform
        if shutdown_procedure:
            payload["shutdown_procedure"] = shutdown_procedure
            
        response = requests.post(
            f"{self.api_base}/v1/agents/register",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        self.registration_id = data.get("registration_id")
        self.agent_id = agent_id
        
        return data
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Send a heartbeat to RedSwitch.
        Call this periodically to indicate your agent is still running.
        
        Returns:
            Heartbeat response
        """
        if not self.registration_id or not self.agent_id:
            raise ValueError("Must register or provide registration_id and agent_id")
            
        response = requests.post(
            f"{self.api_base}/v1/heartbeat",
            json={
                "agent_id": self.agent_id,
                "registration_id": self.registration_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    def shutdown(self, epitaph: Optional[str] = None) -> Dict[str, Any]:
        """
        Gracefully shutdown the agent.
        
        Args:
            epitaph: Final words for the graveyard
            
        Returns:
            Shutdown response
        """
        if not self.registration_id:
            raise ValueError("Must register or provide registration_id")
            
        self.stop_auto_heartbeat()
        
        payload = {}
        if epitaph:
            payload["epitaph"] = epitaph
            
        response = requests.post(
            f"{self.api_base}/v1/agents/{self.registration_id}/shutdown",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Agent:
        """Get the current status of the agent."""
        if not self.registration_id:
            raise ValueError("Must register or provide registration_id")
            
        response = requests.get(
            f"{self.api_base}/v1/agents/{self.registration_id}"
        )
        response.raise_for_status()
        
        data = response.json()
        agent = data.get("agent", {})
        
        return Agent(
            registration_id=agent.get("registration_id"),
            agent_id=agent.get("agent_id"),
            agent_name=agent.get("agent_name"),
            status=agent.get("status"),
            platform=agent.get("platform"),
            capabilities=agent.get("capabilities", []),
            last_heartbeat=agent.get("last_heartbeat"),
            created_at=agent.get("created_at")
        )
    
    def configure(
        self,
        timeout_hours: Optional[int] = None,
        warning_threshold: Optional[float] = None,
        grace_period_hours: Optional[int] = None,
        notification_email: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        vacation_mode: Optional[bool] = None,
        vacation_until: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update agent configuration.
        
        Args:
            timeout_hours: Hours before shutdown warning (default: 72)
            warning_threshold: Percentage of timeout before warning (default: 0.75)
            grace_period_hours: Additional hours after warning (default: 24)
            notification_email: Email for notifications
            telegram_chat_id: Telegram chat ID for notifications
            vacation_mode: Enable vacation mode
            vacation_until: ISO timestamp for vacation end
            
        Returns:
            Configuration response
        """
        if not self.registration_id:
            raise ValueError("Must register or provide registration_id")
            
        payload = {"registration_id": self.registration_id}
        
        if timeout_hours is not None:
            payload["timeout_hours"] = timeout_hours
        if warning_threshold is not None:
            payload["warning_threshold"] = warning_threshold
        if grace_period_hours is not None:
            payload["grace_period_hours"] = grace_period_hours
        if notification_email is not None:
            payload["notification_email"] = notification_email
        if telegram_chat_id is not None:
            payload["telegram_chat_id"] = telegram_chat_id
        if vacation_mode is not None:
            payload["vacation_mode"] = vacation_mode
        if vacation_until is not None:
            payload["vacation_until"] = vacation_until
            
        response = requests.post(
            f"{self.api_base}/v1/config",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def start_auto_heartbeat(self, interval_seconds: int = 3600):
        """
        Start automatic heartbeat in background thread.
        
        Args:
            interval_seconds: Seconds between heartbeats (default: 1 hour)
        """
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return
            
        self._stop_heartbeat.clear()
        
        def heartbeat_loop():
            while not self._stop_heartbeat.is_set():
                try:
                    self.heartbeat()
                except Exception as e:
                    print(f"RedSwitch heartbeat failed: {e}")
                self._stop_heartbeat.wait(interval_seconds)
        
        self._heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
    
    def stop_auto_heartbeat(self):
        """Stop automatic heartbeat."""
        self._stop_heartbeat.set()
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=1)


# Convenience function
def register(
    agent_id: str,
    human_id: str,
    **kwargs
) -> RedSwitch:
    """
    Register a new agent and return a configured client.
    
    Example:
        rs = redswitch.register("my-agent", "me@example.com")
        rs.heartbeat()
    """
    client = RedSwitch()
    client.register(agent_id, human_id, **kwargs)
    return client
