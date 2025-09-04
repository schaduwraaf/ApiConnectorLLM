#!/usr/bin/env python3
"""
Create a fresh message with current timestamp for testing BusDaemon.
"""

import json
import time

def create_fresh_message():
    """Create a message with current timestamp."""
    
    message = {
        'message_id': 'current_test_001',
        'sender_id': 'claude_main', 
        'receiver_id': 'claude_code',
        'message_type': 'execute',
        'payload': {
            'content_reference': 'test_current_timestamp',
            'description': 'Testing BusDaemon with fresh timestamp',
            'priority': 'normal'
        },
        'timestamp': time.time(),  # Current timestamp
        'nonce': 'current_test_nonce_001',
        'signature': None
    }
    
    # Write to inbox
    with open('inbox/current_test.json', 'w') as f:
        json.dump(message, f, indent=2)
    
    print(f'✅ Created fresh message: current_test.json')
    print(f'   Timestamp: {message["timestamp"]:.1f}')
    print(f'   Sender: {message["sender_id"]}')
    print(f'   Receiver: {message["receiver_id"]}')
    print(f'   Type: {message["message_type"]}')
    print('   → Should pass timestamp validation!')

if __name__ == '__main__':
    create_fresh_message()