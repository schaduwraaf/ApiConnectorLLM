#!/usr/bin/env python3
"""
BusDaemon - Automated Zero-Trust Message Bus Coordinator

This daemon automates the role of the human bus coordinator by:
1. Watching inbox/ folder for incoming JSON messages
2. Validating messages using Ed25519 cryptographic verification  
3. Routing valid messages through ZeroTrustBus
4. Collecting responses, re-signing them, and writing to outbox/

This prototype replaces manual cut-and-paste coordination with automated
message processing while maintaining all security guarantees.
"""

import os
import sys
import json
import time
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict

# Add zero_trust_research to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'zero_trust_research'))

from zero_trust_architecture import ZeroTrustBus, Message, MessageType
from crypto.signing import sign_message, verify_signature, Signature, SigningError, VerificationError
from crypto.keys import generate_keypair, save_private_key, save_public_key, load_private_key


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bus_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BusDaemon')


@dataclass
class ComponentMessage:
    """
    Message format for inter-component communication via bus.
    """
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float
    nonce: str
    signature: Optional[Dict[str, Any]] = None  # Ed25519 signature object
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentMessage':
        """Deserialize message from dictionary."""
        return cls(**data)


@dataclass 
class WellbeingStatus:
    """
    Component health and wellbeing status report.
    """
    component_id: str
    status: str  # 'healthy', 'degraded', 'critical', 'offline'
    last_heartbeat: float
    active_tasks: int
    memory_usage: float
    error_count: int
    security_violations: List[str]
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize status to dictionary."""
        return asdict(self)


@dataclass
class ProcessingResult:
    """
    Result of message processing by the bus daemon.
    """
    success: bool
    message_id: str
    timestamp: float
    processing_time: float
    status: str
    details: str
    output_file: Optional[str] = None
    error: Optional[str] = None


class BusMessagePoller:
    """
    Simple file polling system for processing incoming messages.
    """
    
    def __init__(self, bus_daemon: 'BusDaemon'):
        self.bus_daemon = bus_daemon
        self.processed_files: Set[str] = set()
        self.last_check = time.time()
    
    def check_for_messages(self):
        """Check inbox directory for new messages."""
        try:
            current_files = set()
            for file_path in self.bus_daemon.inbox_dir.glob('*.json'):
                current_files.add(file_path.name)
                
                if file_path.name not in self.processed_files:
                    # New file detected
                    logger.info(f"New message detected: {file_path.name}")
                    
                    # Check if file is fully written (size stable for 0.5 seconds)
                    if self._is_file_ready(file_path):
                        self.bus_daemon.process_message(file_path)
                        self.processed_files.add(file_path.name)
            
            # Clean up processed_files set for files that no longer exist
            self.processed_files &= current_files
            
        except Exception as e:
            logger.error(f"Error checking for messages: {e}")
    
    def _is_file_ready(self, file_path: Path) -> bool:
        """Check if file is fully written and ready for processing."""
        try:
            # Check file size twice with a small delay
            size1 = file_path.stat().st_size
            time.sleep(0.1)
            size2 = file_path.stat().st_size
            return size1 == size2 and size1 > 0
        except:
            return False


class BusDaemon:
    """
    Main bus daemon for automated message processing and routing.
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.dirname(__file__))
        self.inbox_dir = self.base_dir / 'inbox'
        self.outbox_dir = self.base_dir / 'outbox' 
        self.keys_dir = self.base_dir / 'keys'
        
        # Create directories if they don't exist
        self.inbox_dir.mkdir(exist_ok=True)
        self.outbox_dir.mkdir(exist_ok=True)
        self.keys_dir.mkdir(exist_ok=True)
        
        # Initialize zero trust bus
        os.environ["FEATURE_CRYPTO_SIGNING"] = "true"  # Enable crypto validation
        self.zero_trust_bus = ZeroTrustBus()
        
        # Initialize daemon keys
        self.daemon_private_key = None
        self.daemon_public_key = None
        self._initialize_daemon_keys()
        
        # Register known components
        self._register_components()
        
        # Message processing statistics
        self.stats = {
            'messages_processed': 0,
            'messages_successful': 0,
            'messages_failed': 0,
            'start_time': time.time()
        }
        
        logger.info(f"BusDaemon initialized - watching {self.inbox_dir}")
        logger.info(f"Crypto signing: enabled")
        logger.info(f"Output directory: {self.outbox_dir}")
    
    def _initialize_daemon_keys(self):
        """Initialize or load daemon's signing keys."""
        private_key_path = self.keys_dir / 'bus_daemon.pem'
        public_key_path = self.keys_dir / 'bus_daemon.pub'
        
        try:
            if private_key_path.exists():
                # Load existing keys
                self.daemon_private_key = load_private_key(str(private_key_path))
                self.daemon_public_key = self.daemon_private_key.public_key()
                logger.info("Loaded existing daemon keys")
            else:
                # Generate new keys
                self.daemon_private_key, self.daemon_public_key = generate_keypair()
                save_private_key(self.daemon_private_key, str(private_key_path))
                save_public_key(self.daemon_public_key, str(public_key_path))
                logger.info("Generated new daemon keys")
                
        except Exception as e:
            logger.error(f"Failed to initialize daemon keys: {e}")
            raise
    
    def _register_components(self):
        """Register known components with the zero trust bus."""
        components = ['claude_main', 'claude_code', 'openai', 'autistic_verifier', 'guardian']
        
        for component_id in components:
            # In production, this would use real public keys from a registry
            mock_public_key = f"mock_public_key_{component_id}"
            self.zero_trust_bus.register_component(component_id, mock_public_key)
            logger.debug(f"Registered component: {component_id}")
    
    def process_message(self, file_path: Path) -> ProcessingResult:
        """
        Process a single message file from the inbox.
        
        Args:
            file_path: Path to the JSON message file
            
        Returns:
            ProcessingResult with processing details
        """
        start_time = time.time()
        message_id = file_path.stem
        
        logger.info(f"Processing message: {message_id}")
        
        try:
            # Read and parse JSON message
            with open(file_path, 'r') as f:
                message_data = json.load(f)
            
            # Validate message structure
            component_message = ComponentMessage.from_dict(message_data)
            
            # Validate cryptographic signature if present
            if component_message.signature:
                signature_obj = Signature.from_dict(component_message.signature)
                message_payload = {
                    'sender_id': component_message.sender_id,
                    'receiver_id': component_message.receiver_id,
                    'message_type': component_message.message_type,
                    'payload': component_message.payload,
                    'timestamp': component_message.timestamp,
                    'nonce': component_message.nonce
                }
                
                if not verify_signature(message_payload, signature_obj):
                    raise VerificationError("Invalid message signature")
                
                logger.info(f"Message {message_id}: signature verified")
            else:
                logger.warning(f"Message {message_id}: no signature present")
            
            # Route message through zero trust bus
            bus_message = Message(
                sender_id=component_message.sender_id,
                receiver_id=component_message.receiver_id,
                message_type=MessageType(component_message.message_type),
                content_reference=component_message.payload.get('content_reference', 'bus_routed'),
                timestamp=component_message.timestamp,
                nonce=component_message.nonce,
                signature="legacy_field",
                signature_obj=Signature.from_dict(component_message.signature) if component_message.signature else None
            )
            
            routing_result = self.zero_trust_bus.route_message(
                bus_message,
                f"BusDaemon routing: {component_message.message_type} from {component_message.sender_id}"
            )
            
            if routing_result:
                logger.info(f"Message {message_id}: routed successfully")
                
                # Generate response
                response = self._generate_response(component_message)
                
                # Write response to outbox
                output_file = self._write_response(message_id, response)
                
                # Move processed message to archive
                self._archive_message(file_path)
                
                processing_time = time.time() - start_time
                self.stats['messages_successful'] += 1
                
                result = ProcessingResult(
                    success=True,
                    message_id=message_id,
                    timestamp=time.time(),
                    processing_time=processing_time,
                    status='routed_successfully',
                    details=f'Message routed to {component_message.receiver_id}',
                    output_file=str(output_file)
                )
                
            else:
                # Routing failed - check verifier status
                verifier_status = self.zero_trust_bus.get_verifier_status()
                error_details = f"Routing failed. Active flags: {len(verifier_status.get('active_flags', []))}"
                
                if verifier_status.get('active_flags'):
                    error_details += f". Violations: {[flag['reason'] for flag in verifier_status['active_flags']]}"
                
                logger.error(f"Message {message_id}: {error_details}")
                
                # Write error response
                error_response = {
                    'error': 'routing_failed',
                    'message_id': message_id,
                    'details': error_details,
                    'verifier_status': verifier_status,
                    'timestamp': time.time()
                }
                
                output_file = self._write_error_response(message_id, error_response)
                processing_time = time.time() - start_time
                self.stats['messages_failed'] += 1
                
                result = ProcessingResult(
                    success=False,
                    message_id=message_id,
                    timestamp=time.time(),
                    processing_time=processing_time,
                    status='routing_failed',
                    details=error_details,
                    output_file=str(output_file),
                    error='routing_failed'
                )
        
        except Exception as e:
            logger.error(f"Message {message_id}: processing failed - {e}")
            
            # Write error response
            error_response = {
                'error': 'processing_failed',
                'message_id': message_id,
                'details': str(e),
                'timestamp': time.time()
            }
            
            output_file = self._write_error_response(message_id, error_response)
            processing_time = time.time() - start_time  
            self.stats['messages_failed'] += 1
            
            result = ProcessingResult(
                success=False,
                message_id=message_id,
                timestamp=time.time(),
                processing_time=processing_time,
                status='processing_failed',
                details=str(e),
                output_file=str(output_file),
                error=str(e)
            )
        
        finally:
            self.stats['messages_processed'] += 1
        
        logger.info(f"Message {message_id}: processing complete ({result.status}) in {result.processing_time:.3f}s")
        return result
    
    def _generate_response(self, component_message: ComponentMessage) -> Dict[str, Any]:
        """
        Generate a response message for successful routing.
        
        Args:
            component_message: The original component message
            
        Returns:
            Response message dictionary
        """
        response_payload = {
            'original_message_id': component_message.message_id,
            'original_sender': component_message.sender_id,
            'original_receiver': component_message.receiver_id,
            'bus_status': 'routed_successfully',
            'routing_timestamp': time.time(),
            'verifier_status': self.zero_trust_bus.get_verifier_status(),
            'response_type': 'bus_routing_confirmation'
        }
        
        response = ComponentMessage(
            message_id=f"bus_response_{component_message.message_id}",
            sender_id='bus_daemon',
            receiver_id=component_message.sender_id,  # Reply to sender
            message_type='routing_response',
            payload=response_payload,
            timestamp=time.time(),
            nonce=hashlib.sha256(f"{component_message.message_id}{time.time()}".encode()).hexdigest()[:16]
        )
        
        # Sign the response
        response_signature = sign_message(
            {
                'sender_id': response.sender_id,
                'receiver_id': response.receiver_id,
                'message_type': response.message_type,
                'payload': response.payload,
                'timestamp': response.timestamp,
                'nonce': response.nonce
            },
            self.daemon_private_key,
            'bus_daemon'
        )
        
        response.signature = response_signature.to_dict()
        
        return response.to_dict()
    
    def _write_response(self, message_id: str, response: Dict[str, Any]) -> Path:
        """Write successful response to outbox."""
        output_file = self.outbox_dir / f"{message_id}_response.json"
        
        with open(output_file, 'w') as f:
            json.dump(response, f, indent=2)
        
        logger.info(f"Response written: {output_file.name}")
        return output_file
    
    def _write_error_response(self, message_id: str, error_response: Dict[str, Any]) -> Path:
        """Write error response to outbox."""
        output_file = self.outbox_dir / f"{message_id}_error.json"
        
        with open(output_file, 'w') as f:
            json.dump(error_response, f, indent=2)
        
        logger.error(f"Error response written: {output_file.name}")
        return output_file
    
    def _archive_message(self, file_path: Path):
        """Move processed message to archive directory."""
        archive_dir = self.base_dir / 'archive'
        archive_dir.mkdir(exist_ok=True)
        
        archive_path = archive_dir / file_path.name
        file_path.rename(archive_path)
        logger.debug(f"Message archived: {archive_path.name}")
    
    def get_status(self) -> WellbeingStatus:
        """Get daemon status and health information."""
        runtime = time.time() - self.stats['start_time']
        
        return WellbeingStatus(
            component_id='bus_daemon',
            status='healthy' if self.stats['messages_failed'] < self.stats['messages_processed'] * 0.1 else 'degraded',
            last_heartbeat=time.time(),
            active_tasks=0,  # TODO: track active message processing
            memory_usage=0.0,  # TODO: implement memory monitoring
            error_count=self.stats['messages_failed'],
            security_violations=[], # TODO: collect from verifier
            notes=f"Processed {self.stats['messages_processed']} messages in {runtime:.1f}s"
        )
    
    def print_status(self):
        """Print current daemon status."""
        status = self.get_status()
        runtime = time.time() - self.stats['start_time']
        
        print(f"\n=== BusDaemon Status ===")
        print(f"Status: {status.status}")
        print(f"Runtime: {runtime:.1f}s")
        print(f"Messages processed: {self.stats['messages_processed']}")
        print(f"Successful: {self.stats['messages_successful']}")
        print(f"Failed: {self.stats['messages_failed']}")
        print(f"Success rate: {(self.stats['messages_successful']/max(1,self.stats['messages_processed']))*100:.1f}%")
        print(f"Inbox: {self.inbox_dir}")
        print(f"Outbox: {self.outbox_dir}")
        print("========================")
    
    def run(self):
        """
        Start the bus daemon and begin watching for messages.
        """
        logger.info("Starting BusDaemon...")
        
        # Print initial status
        self.print_status()
        
        # Initialize message poller
        poller = BusMessagePoller(self)
        
        # Process any existing files in inbox
        for file_path in self.inbox_dir.glob('*.json'):
            logger.info(f"Processing existing file: {file_path.name}")
            self.process_message(file_path)
            poller.processed_files.add(file_path.name)
        
        logger.info(f"Polling {self.inbox_dir} for new messages (every 2 seconds)...")
        logger.info("Press Ctrl+C to stop")
        
        try:
            last_status_time = 0
            
            while True:
                # Check for new messages
                poller.check_for_messages()
                
                # Print status every 60 seconds
                current_time = int(time.time())
                if current_time - last_status_time >= 60:
                    self.print_status()
                    last_status_time = current_time
                
                # Poll every 2 seconds
                time.sleep(2)
                    
        except KeyboardInterrupt:
            logger.info("Shutdown requested...")
            self.print_status()
            logger.info("BusDaemon stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Zero-Trust Bus Daemon')
    parser.add_argument('--base-dir', help='Base directory for bus operations')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
    
    args = parser.parse_args()
    
    try:
        daemon = BusDaemon(args.base_dir)
        
        if args.status:
            daemon.print_status()
        else:
            daemon.run()
            
    except Exception as e:
        logger.error(f"Failed to start daemon: {e}")
        sys.exit(1)