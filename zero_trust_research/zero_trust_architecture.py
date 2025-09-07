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

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not available. Ed25519 verification disabled.")
    print("Install with: pip3 install cryptography")


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
    
    def __init__(self, verifier_id: str, bus_registry=None):
        self.verifier_id = verifier_id
        self.flags = []
        self.pattern_violations = []
        self.bus_registry = bus_registry
    
    def get_sender_info(self, sender_id: str) -> Dict:
        """Get sender information from bus registry"""
        if self.bus_registry:
            return self.bus_registry.get(sender_id, {})
        return {}
    
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
            if packet.trust_level == "constitutional_protected":
                if "protected" not in packet.constitutional_flags:
                    self.flag_violation("Constitutional trust level without protection flag", packet)
                    return False
                
                # Verify sender has constitutional authority
                sender_info = self.get_sender_info(packet.sender_id)
                if sender_info and sender_info.get('trust_level') != 'constitutional_protected':
                    self.flag_violation("Non-constitutional component claiming constitutional trust", packet)
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


class CryptographicValidator:
    """Ed25519 signature validation for zero-trust authentication"""
    
    @staticmethod
    def generate_keypair() -> tuple:
        """Generate Ed25519 keypair (private_key, public_key_bytes)"""
        if not CRYPTO_AVAILABLE:
            return ("mock_private_key", b"mock_public_key_bytes")
        
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return (private_key, public_key_bytes)
    
    @staticmethod
    def sign_packet_content(private_key, packet_content: str) -> str:
        """Sign packet content with Ed25519 private key"""
        if not CRYPTO_AVAILABLE or private_key == "mock_private_key":
            return f"mock_signature_{hashlib.sha256(packet_content.encode()).hexdigest()[:16]}"
        
        signature = private_key.sign(packet_content.encode())
        return signature.hex()
    
    @staticmethod
    def verify_signature(public_key_bytes: bytes, signature_hex: str, content: str) -> bool:
        """Verify Ed25519 signature"""
        if not CRYPTO_AVAILABLE:
            # Mock verification for testing
            expected_mock = f"mock_signature_{hashlib.sha256(content.encode()).hexdigest()[:16]}"
            return signature_hex == expected_mock
        
        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature_bytes = bytes.fromhex(signature_hex)
            public_key.verify(signature_bytes, content.encode())
            return True
        except Exception:
            return False


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
        self.autistic_verifier = AutisticVerifier("primary_verifier", self.component_registry)
        self.consensus_monitor = ConsensusMonitor()
        self.crypto_validator = CryptographicValidator()
    
    def register_component(self, component_id: str, public_key_bytes: bytes, trust_level: str = "provisional", 
                          constitutional_flags: List[str] = None):
        """Register component with Ed25519 public key and constitutional protections"""
        if constitutional_flags is None:
            constitutional_flags = []
            
        self.component_registry[component_id] = {
            "public_key_bytes": public_key_bytes,
            "public_key_hex": public_key_bytes.hex() if isinstance(public_key_bytes, bytes) else "mock_key",
            "registered_at": time.time(),
            "status": "active",
            "trust_level": trust_level,
            "constitutional_flags": constitutional_flags
        }
    
    def validate_packet(self, packet) -> bool:
        """Full zero-trust packet validation with Ed25519 signature verification"""
        # Structure validation
        if not packet.validate_structure():
            return False
        
        # Cryptographic signature validation
        if not self._verify_packet_signature(packet):
            self.autistic_verifier.flag_violation("Invalid cryptographic signature", packet)
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
    
    def _verify_packet_signature(self, packet) -> bool:
        """Verify Ed25519 signature for packet"""
        # Get sender's public key
        sender_info = self.component_registry.get(packet.sender_id)
        if not sender_info:
            return False
        
        public_key_bytes = sender_info["public_key_bytes"]
        
        # Create signable content
        if isinstance(packet, CognitivePacket):
            signable_content = f"{packet.sender_id}{packet.content}{packet.timestamp}{packet.nonce}"
        else:  # Legacy Message
            signable_content = f"{packet.sender_id}{packet.content_reference}{packet.timestamp}{packet.nonce}"
        
        # Verify signature
        return self.crypto_validator.verify_signature(
            public_key_bytes, packet.signature, signable_content
        )
    
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
    
    # Generate keypairs for components
    claude_code_private, claude_code_public = CryptographicValidator.generate_keypair()
    claude_main_private, claude_main_public = CryptographicValidator.generate_keypair()
    openai_private, openai_public = CryptographicValidator.generate_keypair()
    autistic_verifier_private, autistic_verifier_public = CryptographicValidator.generate_keypair()
    
    # Register components with Ed25519 public keys and constitutional protections
    bus.register_component("claude_code", claude_code_public, "verified", ["safe_implementation"])
    bus.register_component("claude_main", claude_main_public, "verified", ["pattern_detection"])
    bus.register_component("openai", openai_public, "verified", ["specification_design"])
    bus.register_component("autistic_verifier", autistic_verifier_public, "constitutional_protected", 
                         ["protected", "cannot_consensus_override", "system_integrity"])
    
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
        constitutional_flags=["safe_implementation"]
    )
    
    # Sign the packet after creation
    signable_content = f"{test_cognitive_packet.sender_id}{test_cognitive_packet.content}{test_cognitive_packet.timestamp}{test_cognitive_packet.nonce}"
    test_cognitive_packet.signature = CryptographicValidator.sign_packet_content(
        claude_main_private, signable_content
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
    
    legacy_timestamp = time.time()
    test_legacy_message = Message(
        sender_id="openai",
        receiver_id="claude_code",
        message_type=MessageType.VERIFICATION_REQUEST,
        content_reference="verify_constitutional_protection",
        timestamp=legacy_timestamp,
        nonce="legacy_nonce_67890",
        signature=CryptographicValidator.sign_packet_content(
            openai_private, "openaiverify_constitutional_protection" + 
            str(legacy_timestamp) + "legacy_nonce_67890"
        )
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
        priority="emergency"
    )
    
    # Sign constitutional packet
    constitutional_signable = f"{protected_packet.sender_id}{protected_packet.content}{protected_packet.timestamp}{protected_packet.nonce}"
    protected_packet.signature = CryptographicValidator.sign_packet_content(
        autistic_verifier_private, constitutional_signable
    )
    
    protected_success = bus.route_cognitive_packet(protected_packet,
                                                 "Emergency constitutional protection alert")
    print(f"Constitutional protection packet success: {protected_success}")
    
    # Test constitutional protection enforcement
    print("\n=== Constitutional Protection Enforcement ===")
    
    # Display component registry with constitutional flags
    for component_id, info in bus.component_registry.items():
        print(f"Component: {component_id}")
        print(f"  Trust Level: {info['trust_level']}")
        print(f"  Constitutional Flags: {info['constitutional_flags']}")
        print(f"  Public Key: {info['public_key_hex'][:16]}...")
        print()