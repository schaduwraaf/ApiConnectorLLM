#!/usr/bin/env python3
"""
End-to-end tests for BusDaemon functionality.

These tests verify the complete inbox → outbox message flow with
real Ed25519 cryptographic validation and zero-trust bus integration.
"""

import os
import sys
import json
import time
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zero_trust_research'))

from bus_daemon import BusDaemon, ComponentMessage, WellbeingStatus, ProcessingResult
from crypto.signing import create_test_signature, sign_message
from crypto.keys import generate_keypair


class TestBusDaemonIntegration(unittest.TestCase):
    """
    Integration tests for BusDaemon with real file system operations.
    """
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        # Create temporary directory for test
        self.test_dir = Path(tempfile.mkdtemp())
        
        # Initialize daemon with test directory
        self.daemon = BusDaemon(str(self.test_dir))
        
        # Generate test keypair
        self.test_private_key, self.test_public_key = generate_keypair()
        
        # Create test messages
        self.valid_message_data = {
            "message_id": "test_001",
            "sender_id": "claude_main",
            "receiver_id": "claude_code",
            "message_type": "execute",
            "payload": {
                "content_reference": "test_implementation_task",
                "description": "Test message for integration testing",
                "priority": "normal"
            },
            "timestamp": time.time(),
            "nonce": "test_nonce_001",
            "signature": None
        }
        
        self.invalid_message_data = {
            "message_id": "test_002",
            "sender_id": "unknown_component",
            # Missing receiver_id (required field)
            "message_type": "execute", 
            "payload": {"content_reference": "broken_message"},
            "timestamp": time.time()
            # Missing nonce (required field)
        }
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_daemon_initialization(self):
        """Test daemon initializes correctly."""
        self.assertTrue(self.daemon.inbox_dir.exists())
        self.assertTrue(self.daemon.outbox_dir.exists())
        self.assertTrue(self.daemon.keys_dir.exists())
        
        # Check daemon keys were generated
        self.assertIsNotNone(self.daemon.daemon_private_key)
        self.assertIsNotNone(self.daemon.daemon_public_key)
        
        # Check key files exist
        private_key_path = self.daemon.keys_dir / 'bus_daemon.pem'
        public_key_path = self.daemon.keys_dir / 'bus_daemon.pub' 
        self.assertTrue(private_key_path.exists())
        self.assertTrue(public_key_path.exists())
    
    def test_valid_message_processing(self):
        """Test processing of valid unsigned message."""
        # Write message to inbox
        message_file = self.daemon.inbox_dir / 'test_001.json'
        with open(message_file, 'w') as f:
            json.dump(self.valid_message_data, f, indent=2)
        
        # Process the message
        result = self.daemon.process_message(message_file)
        
        # Check processing result
        self.assertTrue(result.success)
        self.assertEqual(result.status, 'routed_successfully')
        self.assertIsNotNone(result.output_file)
        
        # Check response file exists
        self.assertTrue(Path(result.output_file).exists())
        
        # Read and validate response
        with open(result.output_file, 'r') as f:
            response = json.load(f)
        
        self.assertEqual(response['sender_id'], 'bus_daemon')
        self.assertEqual(response['receiver_id'], 'claude_main')  # Reply to sender
        self.assertEqual(response['message_type'], 'routing_response')
        self.assertIn('signature', response)
        
        # Check original message was archived
        archive_dir = self.test_dir / 'archive'
        self.assertTrue(archive_dir.exists())
        archived_file = archive_dir / 'test_001.json'
        self.assertTrue(archived_file.exists())
        
        # Check stats
        self.assertEqual(self.daemon.stats['messages_processed'], 1)
        self.assertEqual(self.daemon.stats['messages_successful'], 1)
        self.assertEqual(self.daemon.stats['messages_failed'], 0)
    
    def test_invalid_message_processing(self):
        """Test processing of invalid message (missing fields)."""
        # Write invalid message to inbox
        message_file = self.daemon.inbox_dir / 'test_002.json'
        with open(message_file, 'w') as f:
            json.dump(self.invalid_message_data, f, indent=2)
        
        # Process the message
        result = self.daemon.process_message(message_file)
        
        # Check processing result
        self.assertFalse(result.success)
        self.assertEqual(result.status, 'processing_failed')
        self.assertIsNotNone(result.error)
        self.assertIsNotNone(result.output_file)
        
        # Check error response file exists
        self.assertTrue(Path(result.output_file).exists())
        
        # Read and validate error response
        with open(result.output_file, 'r') as f:
            error_response = json.load(f)
        
        self.assertEqual(error_response['error'], 'processing_failed')
        self.assertEqual(error_response['message_id'], 'test_002')
        self.assertIn('details', error_response)
        
        # Check stats
        self.assertEqual(self.daemon.stats['messages_processed'], 1)
        self.assertEqual(self.daemon.stats['messages_successful'], 0)
        self.assertEqual(self.daemon.stats['messages_failed'], 1)
    
    def test_signed_message_processing(self):
        """Test processing of cryptographically signed message."""
        # Create signed message
        message_payload = {
            'sender_id': self.valid_message_data['sender_id'],
            'receiver_id': self.valid_message_data['receiver_id'],
            'message_type': self.valid_message_data['message_type'],
            'payload': self.valid_message_data['payload'],
            'timestamp': self.valid_message_data['timestamp'],
            'nonce': self.valid_message_data['nonce']
        }
        
        signature = sign_message(message_payload, self.test_private_key, 'test_key')
        
        signed_message_data = self.valid_message_data.copy()
        signed_message_data['signature'] = signature.to_dict()
        signed_message_data['message_id'] = 'test_signed_001'
        
        # Write signed message to inbox
        message_file = self.daemon.inbox_dir / 'test_signed_001.json'
        with open(message_file, 'w') as f:
            json.dump(signed_message_data, f, indent=2)
        
        # Mock signature verification to pass (since we don't have public key discovery)
        with patch('bus_daemon.verify_signature') as mock_verify:
            mock_verify.return_value = True
            
            # Process the message
            result = self.daemon.process_message(message_file)
        
        # Check processing result
        self.assertTrue(result.success)
        self.assertEqual(result.status, 'routed_successfully')
        
        # Check stats
        self.assertEqual(self.daemon.stats['messages_processed'], 1)
        self.assertEqual(self.daemon.stats['messages_successful'], 1)
        self.assertEqual(self.daemon.stats['messages_failed'], 0)
    
    def test_bad_signature_processing(self):
        """Test processing of message with invalid signature.""" 
        # Create message with fake signature
        fake_signature = {
            "algorithm": "Ed25519",
            "signature_data": "FAKE_SIGNATURE_DATA",
            "public_key_id": "test_key",
            "timestamp": time.time(),
            "key_fingerprint": "fake_fingerprint"
        }
        
        bad_signed_message = self.valid_message_data.copy()
        bad_signed_message['message_id'] = 'test_bad_sig_001'
        bad_signed_message['signature'] = fake_signature
        
        # Write message to inbox
        message_file = self.daemon.inbox_dir / 'test_bad_sig_001.json'
        with open(message_file, 'w') as f:
            json.dump(bad_signed_message, f, indent=2)
        
        # Process the message (should fail signature verification)
        result = self.daemon.process_message(message_file)
        
        # Check processing result
        self.assertFalse(result.success)
        self.assertIn('processing_failed', result.status)
        self.assertIsNotNone(result.error)
        
        # Check stats
        self.assertEqual(self.daemon.stats['messages_processed'], 1)
        self.assertEqual(self.daemon.stats['messages_successful'], 0)
        self.assertEqual(self.daemon.stats['messages_failed'], 1)
    
    def test_component_message_serialization(self):
        """Test ComponentMessage serialization/deserialization."""
        # Create ComponentMessage
        original_msg = ComponentMessage(
            message_id="test_serialization",
            sender_id="test_sender",
            receiver_id="test_receiver",
            message_type="test",
            payload={"key": "value"},
            timestamp=1693737600.0,
            nonce="test_nonce"
        )
        
        # Serialize to dict
        msg_dict = original_msg.to_dict()
        
        # Deserialize back
        restored_msg = ComponentMessage.from_dict(msg_dict)
        
        # Check equality
        self.assertEqual(original_msg.message_id, restored_msg.message_id)
        self.assertEqual(original_msg.sender_id, restored_msg.sender_id)
        self.assertEqual(original_msg.receiver_id, restored_msg.receiver_id)
        self.assertEqual(original_msg.payload, restored_msg.payload)
    
    def test_wellbeing_status(self):
        """Test daemon wellbeing status reporting."""
        # Get initial status
        status = self.daemon.get_status()
        
        self.assertIsInstance(status, WellbeingStatus)
        self.assertEqual(status.component_id, 'bus_daemon')
        self.assertIn(status.status, ['healthy', 'degraded', 'critical', 'offline'])
        self.assertGreaterEqual(status.last_heartbeat, 0)
        self.assertEqual(status.error_count, 0)  # No errors yet
    
    def test_multiple_message_processing(self):
        """Test processing multiple messages in sequence."""
        messages = []
        
        # Create multiple valid messages
        for i in range(3):
            msg_data = self.valid_message_data.copy()
            msg_data['message_id'] = f'test_batch_{i:03d}'
            msg_data['nonce'] = f'test_batch_nonce_{i:03d}'
            messages.append(msg_data)
        
        # Write all messages to inbox
        for i, msg_data in enumerate(messages):
            message_file = self.daemon.inbox_dir / f'test_batch_{i:03d}.json'
            with open(message_file, 'w') as f:
                json.dump(msg_data, f, indent=2)
        
        # Process all messages
        results = []
        for i in range(3):
            message_file = self.daemon.inbox_dir / f'test_batch_{i:03d}.json'
            result = self.daemon.process_message(message_file)
            results.append(result)
        
        # Check all succeeded
        self.assertTrue(all(r.success for r in results))
        
        # Check stats
        self.assertEqual(self.daemon.stats['messages_processed'], 3)
        self.assertEqual(self.daemon.stats['messages_successful'], 3)
        self.assertEqual(self.daemon.stats['messages_failed'], 0)
        
        # Check all output files exist
        for result in results:
            self.assertTrue(Path(result.output_file).exists())


class TestBusDaemonComponents(unittest.TestCase):
    """
    Unit tests for individual BusDaemon components.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.daemon = BusDaemon(str(self.test_dir))
    
    def tearDown(self):
        """Clean up test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_daemon_key_generation(self):
        """Test daemon key generation and loading."""
        # Keys should be generated during initialization
        self.assertIsNotNone(self.daemon.daemon_private_key)
        self.assertIsNotNone(self.daemon.daemon_public_key)
        
        # Create another daemon with same directory - should load existing keys
        daemon2 = BusDaemon(str(self.test_dir))
        
        # Keys should be loaded (not newly generated)
        self.assertIsNotNone(daemon2.daemon_private_key)
        self.assertIsNotNone(daemon2.daemon_public_key)
    
    def test_processing_result_creation(self):
        """Test ProcessingResult dataclass."""
        result = ProcessingResult(
            success=True,
            message_id="test_result",
            timestamp=time.time(),
            processing_time=0.5,
            status="test_status",
            details="test details"
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.message_id, "test_result")
        self.assertEqual(result.status, "test_status")
        self.assertIsNone(result.error)


if __name__ == '__main__':
    # Set up logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    unittest.main(verbosity=2)