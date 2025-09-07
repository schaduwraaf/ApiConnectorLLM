#!/usr/bin/env python3
"""
Zero-Trust Cognitive Network with Autistic Verification Components

This implements a multi-AI collaboration system with constitutional protections
for neurodivergent verification patterns and zero-trust message validation.
"""

import hashlib
import time
import json
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    VERIFICATION_REQUEST = "verification_request"
    PLAN = "plan"
    EXECUTE = "execute"
    CONSENSUS_UPDATE = "consensus_update"
    HEALTH_REPORT = "health_report"
    ALERT = "alert"


@dataclass
class CognitivePacket:
    """JSON Cognitive Packet Format following 4-layer architecture"""
    # Layer 4 - Application
    message_type: MessageType
    content: str
    response_format: Optional[str] = None
    context: Optional[str] = None
    
    # Layer 3 - Coordination  
    routing_path: List[str] = None
    priority: str = "normal"  # low|normal|high|emergency
    batch_id: Optional[str] = None
    consensus_required: bool = False
    
    # Layer 2 - Expert
    component_type: Optional[str] = None
    specialization: Optional[str] = None
    resource_cost: str = "low"  # low|medium|high|critical
    processing_mode: str = "automatic"  # automatic|manual|assisted
    
    # Layer 1 - Constitutional
    sender_id: str = ""
    trust_level: str = "provisional"  # constitutional_protected|verified|provisional
    constitutional_flags: List[str] = None
    signature: str = ""
    
    # Header (auto-generated)
    packet_id: str = ""
    timestamp: float = 0.0
    protocol_version: str = "1.0"
    nonce: str = ""
    
    def __post_init__(self):
        if not self.packet_id:
            self.packet_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.nonce:
            self.nonce = hashlib.sha256(f"{self.packet_id}{self.timestamp}".encode()).hexdigest()[:16]
        if self.routing_path is None:
            self.routing_path = []
        if self.constitutional_flags is None:
            self.constitutional_flags = []
    
    def to_json_packet(self) -> Dict[str, Any]:
        """Convert to standard JSON cognitive packet format"""
        return {
            "cognitive_packet": {
                "header": {
                    "packet_id": self.packet_id,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime(self.timestamp)),
                    "protocol_version": self.protocol_version
                },
                "layer_1_constitutional": {
                    "signature": self.signature,
                    "sender_id": self.sender_id,
                    "trust_level": self.trust_level,
                    "constitutional_flags": self.constitutional_flags
                },
                "layer_2_expert": {
                    "component_type": self.component_type,
                    "specialization": self.specialization,
                    "resource_cost": self.resource_cost,
                    "processing_mode": self.processing_mode
                },
                "layer_3_coordination": {
                    "routing_path": self.routing_path,
                    "priority": self.priority,
                    "batch_id": self.batch_id,
                    "consensus_required": self.consensus_required
                },
                "layer_4_application": {
                    "message_type": self.message_type.value,
                    "content": self.content,
                    "response_format": self.response_format,
                    "context": self.context
                }
            }
        }
    
    @classmethod
    def from_json_packet(cls, json_data: Dict[str, Any]) -> 'CognitivePacket':
        """Create CognitivePacket from JSON format"""
        packet = json_data["cognitive_packet"]
        
        return cls(
            # Layer 4
            message_type=MessageType(packet["layer_4_application"]["message_type"]),
            content=packet["layer_4_application"]["content"],
            response_format=packet["layer_4_application"].get("response_format"),
            context=packet["layer_4_application"].get("context"),
            
            # Layer 3
            routing_path=packet["layer_3_coordination"]["routing_path"],
            priority=packet["layer_3_coordination"]["priority"],
            batch_id=packet["layer_3_coordination"].get("batch_id"),
            consensus_required=packet["layer_3_coordination"]["consensus_required"],
            
            # Layer 2
            component_type=packet["layer_2_expert"].get("component_type"),
            specialization=packet["layer_2_expert"].get("specialization"),
            resource_cost=packet["layer_2_expert"]["resource_cost"],
            processing_mode=packet["layer_2_expert"]["processing_mode"],
            
            # Layer 1
            sender_id=packet["layer_1_constitutional"]["sender_id"],
            trust_level=packet["layer_1_constitutional"]["trust_level"],
            constitutional_flags=packet["layer_1_constitutional"]["constitutional_flags"],
            signature=packet["layer_1_constitutional"]["signature"],
            
            # Header
            packet_id=packet["header"]["packet_id"],
            timestamp=time.mktime(time.strptime(packet["header"]["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")),
            protocol_version=packet["header"]["protocol_version"]
        )
    
    def validate_structure(self) -> bool:
        """Validate all required fields are present"""
        required_fields = ["packet_id", "sender_id", "message_type", 
                          "content", "timestamp", "signature"]
        return all(hasattr(self, field) and getattr(self, field) for field in required_fields)


# Legacy Message class for backward compatibility
@dataclass
class Message:
    """Legacy zero-trust message format - use CognitivePacket for new implementations"""
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content_reference: str
    timestamp: float
    nonce: str
    signature: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "content_reference": self.content_reference,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "signature": self.signature
        }
    
    def to_cognitive_packet(self) -> CognitivePacket:
        """Convert legacy message to cognitive packet format"""
        return CognitivePacket(
            sender_id=self.sender_id,
            message_type=self.message_type,
            content=self.content_reference,
            signature=self.signature,
            timestamp=self.timestamp,
            nonce=self.nonce,
            routing_path=[self.receiver_id]
        )
    
    def validate_structure(self) -> bool:
        """Validate all required fields are present"""
        required_fields = ["sender_id", "receiver_id", "message_type", 
                          "content_reference", "timestamp", "nonce", "signature"]
        return all(hasattr(self, field) and getattr(self, field) for field in required_fields)


@dataclass
class SignedResult:
    """Functional authentication for critical outputs"""
    producer_id: str
    input_digest: str
    result_summary: str
    timestamp: float
    signature: str


class AutisticVerifier:
    """
    Constitutional protection component for pattern verification.
    Cannot be overridden by consensus - flags must be resolved or explicitly vetoed.
    """
    
    def __init__(self, verifier_id: str):
        self.verifier_id = verifier_id
        self.flags = []
        self.pattern_violations = []
    
    def verify_message_pattern(self, packet) -> bool:
        """Check packet against autistic verification patterns (supports both Message and CognitivePacket)"""
        # Pattern consistency checks
        if not packet.validate_structure():
            self.flag_violation("Missing required packet fields", packet)
            return False
        
        # Temporal consistency 
        current_time = time.time()
        if abs(packet.timestamp - current_time) > 300:  # 5 minute window
            self.flag_violation("Timestamp outside acceptable window", packet)
            return False
        
        # Constitutional protection validation for CognitivePacket
        if isinstance(packet, CognitivePacket):
            if packet.trust_level == "constitutional_protected" and "protected" not in packet.constitutional_flags:
                self.flag_violation("Constitutional trust level without protection flag", packet)
                return False
        
        # Nonce uniqueness (simplified - would need persistent storage)
        # This would check against a nonce database in production
        
        return True
    
    def flag_violation(self, reason: str, context: Any):
        """Flag a violation - cannot be suppressed by consensus"""
        violation = {
            "timestamp": time.time(),
            "reason": reason,
            "context": str(context)[:200],  # Truncate for safety
            "verifier_id": self.verifier_id
        }
        self.flags.append(violation)
        self.pattern_violations.append(violation)
    
    def get_active_flags(self) -> List[Dict]:
        """Return unresolved flags"""
        return self.flags


class ConsensusMonitor:
    """Detects consensus attacks against protected components"""
    
    def __init__(self):
        self.bypass_attempts = []
        self.attack_threshold = 3
    
    def check_bypass_attempt(self, target_component: str, attempting_components: List[str]):
        """Monitor for majority attempts to bypass verifier"""
        if len(attempting_components) >= 2 and target_component == "autistic_verifier":
            attempt = {
                "timestamp": time.time(),
                "target": target_component,
                "attackers": attempting_components
            }
            self.bypass_attempts.append(attempt)
            
            # Check for attack pattern
            recent_attempts = [a for a in self.bypass_attempts 
                             if time.time() - a["timestamp"] < 3600]  # Last hour
            
            if len(recent_attempts) >= self.attack_threshold:
                return self.issue_attack_alert(recent_attempts)
        
        return None
    
    def issue_attack_alert(self, attempts: List[Dict]) -> Dict:
        """Issue unfiltered system-wide alert"""
        return {
            "alert_type": "consensus_attack_detected",
            "timestamp": time.time(),
            "details": "Multiple attempts to bypass autistic verifier detected",
            "attempts": attempts,
            "severity": "critical"
        }


class ZeroTrustBus:
    """
    Core bus coordination with zero-trust message validation
    """
    
    def __init__(self):
        self.component_registry = {}
        self.message_buffers = {
            "claude_code": [],
            "claude_main": [],
            "openai": []
        }
        self.nonce_history = set()
        self.autistic_verifier = AutisticVerifier("primary_verifier")
        self.consensus_monitor = ConsensusMonitor()
    
    def register_component(self, component_id: str, public_key: str, trust_level: str = "provisional", 
                          constitutional_flags: List[str] = None):
        """Register component with public key and constitutional protections"""
        if constitutional_flags is None:
            constitutional_flags = []
            
        self.component_registry[component_id] = {
            "public_key": public_key,
            "registered_at": time.time(),
            "status": "active",
            "trust_level": trust_level,
            "constitutional_flags": constitutional_flags
        }
    
    def validate_packet(self, packet) -> bool:
        """Full zero-trust packet validation (supports Message and CognitivePacket)"""
        # Structure validation
        if not packet.validate_structure():
            return False
        
        # Autistic verifier check (constitutional protection)
        if not self.autistic_verifier.verify_message_pattern(packet):
            return False
        
        # Nonce uniqueness
        if isinstance(packet, CognitivePacket):
            packet_hash = hashlib.sha256(
                f"{packet.sender_id}{packet.nonce}{packet.timestamp}".encode()
            ).hexdigest()
        else:  # Legacy Message
            packet_hash = hashlib.sha256(
                f"{packet.sender_id}{packet.nonce}{packet.timestamp}".encode()
            ).hexdigest()
        
        if packet_hash in self.nonce_history:
            self.autistic_verifier.flag_violation("Nonce reuse detected", packet)
            return False
        
        self.nonce_history.add(packet_hash)
        return True
    
    def validate_message(self, message: Message) -> bool:
        """Legacy message validation - calls validate_packet"""
        return self.validate_packet(message)
    
    def route_cognitive_packet(self, packet: CognitivePacket, critical_reasoning: str) -> bool:
        """Route cognitive packet with critical reasoning per transfer"""
        if not self.validate_packet(packet):
            return False
        
        # Apply critical reasoning (simplified - would call LLM API)
        reasoning_result = self.apply_critical_reasoning_packet(packet, critical_reasoning)
        
        if reasoning_result["safe"]:
            # Route to all components in routing_path
            for receiver_id in packet.routing_path:
                target_buffer = self.message_buffers.get(receiver_id, [])
                target_buffer.append({
                    "cognitive_packet": packet.to_json_packet(),
                    "reasoning": reasoning_result,
                    "routed_at": time.time()
                })
            return True
        
        return False
    
    def route_message(self, message: Message, critical_reasoning: str) -> bool:
        """Legacy message routing - converts to cognitive packet"""
        cognitive_packet = message.to_cognitive_packet()
        return self.route_cognitive_packet(cognitive_packet, critical_reasoning)
    
    def apply_critical_reasoning_packet(self, packet: CognitivePacket, reasoning: str) -> Dict:
        """Apply critical reasoning to cognitive packet (placeholder for LLM API call)"""
        # In production, this would make an API call to analyze the packet
        risk_score = 0.1
        
        # Higher risk for high resource cost or critical priority
        if packet.resource_cost == "critical":
            risk_score += 0.3
        if packet.priority == "emergency":
            risk_score += 0.2
        if packet.consensus_required:
            risk_score += 0.1
            
        return {
            "safe": risk_score < 0.5,
            "reasoning": reasoning,
            "risk_score": risk_score,
            "recommendations": [],
            "layer_analysis": {
                "constitutional": f"Trust level: {packet.trust_level}",
                "expert": f"Resource cost: {packet.resource_cost}",
                "coordination": f"Priority: {packet.priority}",
                "application": f"Message type: {packet.message_type.value}"
            }
        }
    
    def apply_critical_reasoning(self, message: Message, reasoning: str) -> Dict:
        """Legacy message reasoning - converts to cognitive packet"""
        cognitive_packet = message.to_cognitive_packet()
        return self.apply_critical_reasoning_packet(cognitive_packet, reasoning)
    
    def get_component_buffer(self, component_id: str) -> List[Dict]:
        """Get messages for specific component"""
        return self.message_buffers.get(component_id, [])
    
    def get_verifier_status(self) -> Dict:
        """Get autistic verifier status - cannot be hidden"""
        return {
            "verifier_id": self.autistic_verifier.verifier_id,
            "active_flags": self.autistic_verifier.get_active_flags(),
            "total_violations": len(self.autistic_verifier.pattern_violations),
            "status": "protected"
        }


# Example usage and testing
if __name__ == "__main__":
    bus = ZeroTrustBus()
    
    # Register components
    bus.register_component("claude_code", "mock_public_key_1")
    bus.register_component("claude_main", "mock_public_key_2")
    bus.register_component("openai", "mock_public_key_3")
    
    # Test new CognitivePacket format
    test_cognitive_packet = CognitivePacket(
        sender_id="claude_main",
        message_type=MessageType.EXECUTE,
        content="implement_zero_trust_validation",
        context="Phase 1 implementation task",
        routing_path=["claude_code"],
        component_type="pattern_detector",
        specialization="right_brain_analysis",
        resource_cost="medium",
        priority="high",
        trust_level="verified",
        constitutional_flags=["safe_implementation"],
        signature="mock_ed25519_signature"
    )
    
    print("=== Testing Cognitive Packet Format ===")
    
    # Route cognitive packet with critical reasoning
    success = bus.route_cognitive_packet(test_cognitive_packet, 
                                       "Safe implementation request from verified right-brain component")
    print(f"Cognitive packet routing success: {success}")
    
    # Display JSON format
    json_packet = test_cognitive_packet.to_json_packet()
    print(f"\nJSON Cognitive Packet Format:")
    print(json.dumps(json_packet, indent=2))
    
    # Test legacy message compatibility
    print("\n=== Testing Legacy Message Compatibility ===")
    
    test_legacy_message = Message(
        sender_id="openai",
        receiver_id="claude_code",
        message_type=MessageType.VERIFICATION_REQUEST,
        content_reference="verify_constitutional_protection",
        timestamp=time.time(),
        nonce="legacy_nonce_67890",
        signature="mock_signature"
    )
    
    # Route legacy message (auto-converts to cognitive packet)
    legacy_success = bus.route_message(test_legacy_message, 
                                     "Legacy message from specification component")
    print(f"Legacy message routing success: {legacy_success}")
    
    # Check verifier status
    verifier_status = bus.get_verifier_status()
    print(f"\nVerifier status: {verifier_status}")
    
    # Check component buffers
    code_buffer = bus.get_component_buffer("claude_code")
    print(f"Claude Code buffer: {len(code_buffer)} messages")
    
    # Display buffer contents
    if code_buffer:
        print(f"\nLatest message in Claude Code buffer:")
        latest = code_buffer[-1]
        if "cognitive_packet" in latest:
            print("Format: Cognitive Packet")
            print(f"Layer analysis: {latest['reasoning']['layer_analysis']}")
        else:
            print("Format: Legacy Message")
    
    print("\n=== Constitutional Protection Test ===")
    
    # Test constitutional protection
    protected_packet = CognitivePacket(
        sender_id="autistic_verifier",
        message_type=MessageType.ALERT,
        content="Constitutional violation detected in consensus attempt",
        routing_path=["claude_code", "claude_main", "openai"],
        trust_level="constitutional_protected",
        constitutional_flags=["protected", "cannot_consensus_override"],
        priority="emergency",
        signature="constitutional_authority_signature"
    )
    
    protected_success = bus.route_cognitive_packet(protected_packet,
                                                 "Emergency constitutional protection alert")
    print(f"Constitutional protection packet success: {protected_success}")