#!/usr/bin/env python3
"""
Scheduler Expert - Local LLM Integration for Multi-AI Coordination

This bridges our existing bus system with LM Studio running on local hardware,
enabling the Scheduler Expert architecture with constitutional protections.

Requirements:
- LM Studio running with API server enabled
- At least one model loaded (8B model recommended for Scheduler)
- Existing BusDaemon and crypto infrastructure
"""

import os
import sys
import json
import time
import requests
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add zero_trust_research to path for existing infrastructure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'zero_trust_research'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SchedulerExpert - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RoutingDecision:
    """Scheduler Expert routing decision with reasoning"""
    primary_expert: str
    additional_experts: List[str]
    reasoning: str
    requires_human_approval: bool
    constitutional_checks_required: List[str]

@dataclass  
class ExpertCapability:
    """Expert capability mapping for Scheduler routing decisions"""
    expert_id: str
    capabilities: List[str]
    specialties: List[str]
    constitutional_role: str  # 'required', 'optional', 'forbidden' for certain message types

class SchedulerExpert:
    """
    Local LLM-powered Scheduler Expert for intelligent message routing
    """
    
    def __init__(self, lm_studio_url: str = "http://localhost:1234/v1", model_name: str = None):
        self.lm_studio_url = lm_studio_url
        self.model_name = model_name
        self.expert_panel = self._initialize_expert_panel()
        self.constitutional_requirements = self._load_constitutional_requirements()
        
        # Test LM Studio connection
        self._test_connection()
    
    def _test_connection(self):
        """Test connection to LM Studio API"""
        try:
            response = requests.get(f"{self.lm_studio_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                logger.info(f"✅ Connected to LM Studio. Available models: {len(models.get('data', []))}")
                if models.get('data'):
                    for model in models['data'][:3]:  # Show first 3 models
                        logger.info(f"  - {model.get('id', 'Unknown')}")
            else:
                logger.error(f"❌ LM Studio connection failed: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Cannot connect to LM Studio at {self.lm_studio_url}: {e}")
            logger.info("💡 Make sure LM Studio is running with API server enabled")
    
    def _initialize_expert_panel(self) -> Dict[str, ExpertCapability]:
        """Initialize expert panel with capabilities"""
        return {
            "motor_cortex": ExpertCapability(
                expert_id="motor_cortex",
                capabilities=["implementation", "coding", "file_operations", "git_operations", "testing"],
                specialties=["python", "javascript", "system_integration", "api_development"],
                constitutional_role="required"
            ),
            "left_brain": ExpertCapability(
                expert_id="left_brain", 
                capabilities=["analysis", "specification", "systematic_thinking", "logical_reasoning"],
                specialties=["requirements", "architecture", "formal_verification", "safety_analysis"],
                constitutional_role="optional"
            ),
            "right_brain": ExpertCapability(
                expert_id="right_brain",
                capabilities=["synthesis", "patterns", "creativity", "holistic_insight"],
                specialties=["documentation", "user_experience", "system_design", "integration"],
                constitutional_role="optional"
            ),
            "autistic_verifier": ExpertCapability(
                expert_id="autistic_verifier",
                capabilities=["verification", "truth_checking", "pattern_consistency", "lie_detection"],
                specialties=["constitutional_compliance", "security_validation", "integrity_checking"],
                constitutional_role="required"  # Cannot be bypassed
            ),
            "guardian": ExpertCapability(
                expert_id="guardian",
                capabilities=["security", "protection", "monitoring", "threat_detection"],
                specialties=["safety_oversight", "vulnerability_assessment", "access_control"],
                constitutional_role="required"  # Cannot be bypassed
            )
        }
    
    def _load_constitutional_requirements(self) -> Dict[str, Any]:
        """Load constitutional requirements that cannot be overridden"""
        return {
            "always_include_verifier": ["security", "implementation", "modification", "access"],
            "always_include_guardian": ["external_access", "file_operations", "network", "credentials"],
            "require_human_approval": ["system_modification", "security_changes", "expert_creation", "constitutional_changes"],
            "forbidden_bypasses": ["autistic_verifier", "guardian", "human_coordinator"]
        }
    
    def query_scheduler_llm(self, message: str, context: Dict[str, Any]) -> str:
        """Query the local LLM for routing decision"""
        
        # Build the Scheduler Expert prompt
        expert_list = "\n".join([
            f"- {expert.expert_id}: {', '.join(expert.capabilities)} (Constitutional: {expert.constitutional_role})"
            for expert in self.expert_panel.values()
        ])
        
        prompt = f"""You are the Scheduler Expert in a panel of AI specialists. Your job is to intelligently route messages to the most appropriate experts.

EXPERT PANEL:
{expert_list}

CONSTITUTIONAL REQUIREMENTS (CANNOT BE BYPASSED):
- Autistic Verifier MUST review: security, implementation, verification requests
- Guardian MUST review: external access, file operations, network operations
- Human approval REQUIRED for: system modifications, security changes, constitutional changes

INCOMING MESSAGE: "{message}"

CONTEXT: {json.dumps(context, indent=2)}

Please analyze this message and decide:
1. Which expert should be the PRIMARY handler?
2. Which additional experts should be included?
3. What constitutional checks are required?
4. Does this need human approval?
5. Your reasoning for these decisions?

Respond in JSON format:
{{
    "primary_expert": "expert_id",
    "additional_experts": ["expert_id1", "expert_id2"],
    "reasoning": "Your detailed reasoning here",
    "requires_human_approval": true/false,
    "constitutional_checks": ["verifier", "guardian"]
}}"""

        try:
            response = requests.post(
                f"{self.lm_studio_url}/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,  # Lower temperature for more consistent routing decisions
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"LM Studio API error: {response.status_code}")
                return self._fallback_routing(message, context)
                
        except Exception as e:
            logger.error(f"Error querying Scheduler LLM: {e}")
            return self._fallback_routing(message, context)
    
    def _fallback_routing(self, message: str, context: Dict[str, Any]) -> str:
        """Fallback routing when LLM is unavailable"""
        logger.info("Using fallback routing logic")
        
        # Simple keyword-based fallback routing
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["implement", "code", "build", "create", "fix"]):
            primary = "motor_cortex"
            additional = ["autistic_verifier"]  # Always include verifier for implementation
        elif any(word in message_lower for word in ["analyze", "specify", "define", "requirements"]):
            primary = "left_brain"
            additional = []
        elif any(word in message_lower for word in ["design", "pattern", "integrate", "synthesize"]):
            primary = "right_brain"  
            additional = []
        else:
            primary = "motor_cortex"  # Default to implementation expert
            additional = []
        
        return json.dumps({
            "primary_expert": primary,
            "additional_experts": additional,
            "reasoning": "Fallback routing based on keyword analysis (LLM unavailable)",
            "requires_human_approval": True,  # Conservative approach when LLM unavailable
            "constitutional_checks": ["autistic_verifier", "guardian"]
        })
    
    def route_message(self, message: str, sender: str, message_type: str) -> RoutingDecision:
        """Main routing function - decides which experts should handle the message"""
        
        context = {
            "sender": sender,
            "message_type": message_type,
            "timestamp": time.time(),
            "expert_panel": list(self.expert_panel.keys())
        }
        
        logger.info(f"Routing message from {sender}: {message[:50]}...")
        
        # Query the Scheduler LLM
        llm_response = self.query_scheduler_llm(message, context)
        
        try:
            # Parse LLM response
            routing_data = json.loads(llm_response)
            
            # Validate and apply constitutional requirements
            routing_decision = RoutingDecision(
                primary_expert=routing_data.get("primary_expert", "motor_cortex"),
                additional_experts=routing_data.get("additional_experts", []),
                reasoning=routing_data.get("reasoning", "No reasoning provided"),
                requires_human_approval=routing_data.get("requires_human_approval", False),
                constitutional_checks_required=routing_data.get("constitutional_checks", [])
            )
            
            # Apply constitutional safeguards
            routing_decision = self._apply_constitutional_safeguards(routing_decision, message, message_type)
            
            logger.info(f"✅ Routing decision: {routing_decision.primary_expert} + {routing_decision.additional_experts}")
            logger.info(f"📋 Reasoning: {routing_decision.reasoning}")
            
            return routing_decision
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM routing response: {e}")
            logger.info("Falling back to conservative routing")
            return self._conservative_fallback_routing(message, sender, message_type)
    
    def _apply_constitutional_safeguards(self, decision: RoutingDecision, message: str, message_type: str) -> RoutingDecision:
        """Apply constitutional requirements that cannot be bypassed"""
        
        message_lower = message.lower()
        
        # Force Autistic Verifier for security/implementation
        if any(word in message_lower for word in ["security", "implement", "modify", "change", "access"]):
            if "autistic_verifier" not in decision.additional_experts:
                decision.additional_experts.append("autistic_verifier")
        
        # Force Guardian for external operations
        if any(word in message_lower for word in ["file", "network", "external", "api", "database"]):
            if "guardian" not in decision.additional_experts:
                decision.additional_experts.append("guardian")
        
        # Force human approval for system changes
        if any(word in message_lower for word in ["system", "security", "constitutional", "expert", "architecture"]):
            decision.requires_human_approval = True
        
        return decision
    
    def _conservative_fallback_routing(self, message: str, sender: str, message_type: str) -> RoutingDecision:
        """Conservative fallback when parsing fails"""
        return RoutingDecision(
            primary_expert="motor_cortex",
            additional_experts=["autistic_verifier", "guardian"],  # Include all safeguards
            reasoning="Conservative fallback routing due to parsing failure",
            requires_human_approval=True,
            constitutional_checks_required=["autistic_verifier", "guardian"]
        )

def main():
    """Main function for testing Scheduler Expert"""
    
    print("🧠 Scheduler Expert - Local LLM Integration")
    print("=" * 50)
    
    # Initialize Scheduler Expert
    scheduler = SchedulerExpert()
    
    # Test routing
    test_messages = [
        ("Implement user authentication with JWT tokens", "human_coordinator", "execute"),
        ("Analyze the security implications of the new API", "left_brain", "analysis"), 
        ("Design a user dashboard with good UX patterns", "right_brain", "design"),
        ("Verify the cryptographic implementation is correct", "guardian", "verification")
    ]
    
    for message, sender, msg_type in test_messages:
        print(f"\n📨 Test Message: {message}")
        print(f"👤 From: {sender}")
        
        routing = scheduler.route_message(message, sender, msg_type)
        
        print(f"🎯 Primary Expert: {routing.primary_expert}")
        print(f"👥 Additional Experts: {routing.additional_experts}")
        print(f"👤 Human Approval Required: {routing.requires_human_approval}")
        print(f"🛡️ Constitutional Checks: {routing.constitutional_checks_required}")
        print(f"💭 Reasoning: {routing.reasoning}")
        print("-" * 50)

if __name__ == "__main__":
    main()