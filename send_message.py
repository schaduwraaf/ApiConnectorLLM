#!/usr/bin/env python3
"""
User-friendly message sender for BusDaemon

Usage:
    python3 send_message.py "claude_main" "claude_code" "execute" "Please implement the new feature"
    python3 send_message.py "human_coordinator" "autistic_verifier" "pattern_analysis" "Check this pattern"
    
This handles all the JSON formatting, timestamps, nonces, and crypto signing automatically.
"""

import os
import sys
import json
import time
import uuid
from pathlib import Path

# Add zero_trust_research to path for crypto imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'zero_trust_research'))

def create_message(sender_id: str, receiver_id: str, message_type: str, content: str) -> dict:
    """Create a properly formatted ComponentMessage"""
    
    # Generate unique message ID and nonce
    message_id = f"{sender_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    nonce = f"{sender_id}_nonce_{uuid.uuid4().hex[:16]}"
    
    # Create the message structure
    message = {
        "message_id": message_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message_type": message_type,
        "payload": {
            "content_reference": "user_provided_content",
            "description": content,
            "priority": "normal"
        },
        "timestamp": time.time(),
        "nonce": nonce,
        "signature": None  # Will be signed if keys available
    }
    
    return message

def try_sign_message(message: dict, sender_id: str) -> dict:
    """Attempt to sign the message if crypto keys are available"""
    try:
        from crypto.signing import sign_message
        from crypto.keys import load_private_key
        
        # Look for sender's private key
        key_paths = [
            f"bus/keys/{sender_id}.pem",
            f"bus/keys/{sender_id}_private.pem", 
            f"keys/{sender_id}.pem",
            "bus/keys/bus_daemon.pem"  # Fallback to daemon key
        ]
        
        private_key = None
        used_key_path = None
        
        for key_path in key_paths:
            if os.path.exists(key_path):
                try:
                    private_key = load_private_key(key_path)
                    used_key_path = key_path
                    break
                except Exception as e:
                    print(f"Warning: Could not load key {key_path}: {e}")
                    continue
        
        if private_key:
            # Create message payload for signing (exclude signature field)
            message_for_signing = {
                'sender_id': message['sender_id'],
                'receiver_id': message['receiver_id'], 
                'message_type': message['message_type'],
                'payload': message['payload'],
                'timestamp': message['timestamp'],
                'nonce': message['nonce']
            }
            
            signature_obj = sign_message(message_for_signing, private_key)
            message['signature'] = signature_obj.to_dict()
            print(f"✅ Message signed with key: {used_key_path}")
        else:
            print("⚠️  No private key found - message will be unsigned")
            
    except ImportError:
        print("⚠️  Crypto signing not available - message will be unsigned")
    except Exception as e:
        print(f"⚠️  Signing failed: {e} - message will be unsigned")
    
    return message

def save_message(message: dict, inbox_dir: str = "bus/inbox") -> str:
    """Save message to inbox directory"""
    
    # Ensure inbox directory exists
    Path(inbox_dir).mkdir(parents=True, exist_ok=True)
    
    # Create filename
    filename = f"{message['message_id']}.json"
    filepath = os.path.join(inbox_dir, filename)
    
    # Save message
    with open(filepath, 'w') as f:
        json.dump(message, f, indent=2)
    
    return filepath

def main():
    if len(sys.argv) != 5:
        print("Usage: python3 send_message.py <sender_id> <receiver_id> <message_type> <content>")
        print()
        print("Examples:")
        print("  python3 send_message.py 'claude_main' 'claude_code' 'execute' 'Implement dark mode toggle'")
        print("  python3 send_message.py 'human_coordinator' 'autistic_verifier' 'pattern_analysis' 'Check this pattern'")
        print("  python3 send_message.py 'openai' 'claude_code' 'plan' 'Design the authentication system'")
        print()
        print("Message types: execute, plan, verification_request, consensus_update, health_report, alert")
        sys.exit(1)
    
    sender_id = sys.argv[1]
    receiver_id = sys.argv[2]
    message_type = sys.argv[3] 
    content = sys.argv[4]
    
    print(f"Creating message: {sender_id} → {receiver_id}")
    print(f"Type: {message_type}")
    print(f"Content: {content}")
    print()
    
    # Create the message
    message = create_message(sender_id, receiver_id, message_type, content)
    
    # Try to sign it
    message = try_sign_message(message, sender_id)
    
    # Save to inbox
    filepath = save_message(message)
    
    print(f"✅ Message saved to: {filepath}")
    print(f"📨 Message ID: {message['message_id']}")
    print()
    print("The BusDaemon will process this message automatically if running.")
    print("To start BusDaemon: make bus")

if __name__ == "__main__":
    main()