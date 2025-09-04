# send_message.py - User Guide

## Quick Usage
```bash
python3 send_message.py <sender_id> <receiver_id> <message_type> <content>
```

## Component Names (sender_id / receiver_id)

### AI Components
- **`claude_main`** - Claude with RAG documentation, persistent project context
- **`openai`** - OpenAI GPT for specification design and safety analysis  
- **`claude_code`** - Claude Code (you!) - the implementation component
- **`human_coordinator`** - You, the human bus operator
- **`autistic_verifier`** - Constitutional pattern protection system

### System Components  
- **`guardian`** - Security oversight component
- **`consensus_coordinator`** - Multi-AI consensus management
- **`health_monitor`** - System health and performance tracking

## Message Types

### Core Operations
- **`execute`** - Request implementation of a feature/fix
- **`plan`** - Request design/architecture planning
- **`verification_request`** - Ask for pattern/security analysis
- **`consensus_update`** - Multi-AI consensus coordination
- **`health_report`** - Component status reporting
- **`alert`** - Critical security or system alerts

## Common Usage Patterns

### 1. Human → Claude Code (Implementation Request)
```bash
# You asking Claude Code to implement something
python3 send_message.py "human_coordinator" "claude_code" "execute" "Add user authentication to the login page"

python3 send_message.py "human_coordinator" "claude_code" "execute" "Fix the bug in the payment processing module"

python3 send_message.py "human_coordinator" "claude_code" "execute" "Refactor the database connection code"
```

### 2. Claude Main → Claude Code (Design Implementation)  
```bash
# Claude Main asking Claude Code to implement their design
python3 send_message.py "claude_main" "claude_code" "execute" "Implement the user dashboard based on the specifications in project_docs/dashboard_spec.md"

python3 send_message.py "claude_main" "claude_code" "execute" "Create the API endpoints defined in the REST API design document"
```

### 3. OpenAI → Claude Code (Specification Implementation)
```bash  
# OpenAI asking Claude Code to implement their specification
python3 send_message.py "openai" "claude_code" "execute" "Implement the security middleware according to the zero-trust specification"

python3 send_message.py "openai" "claude_code" "plan" "Design the database schema for the user management system"
```

### 4. Human → Autistic Verifier (Pattern Analysis)
```bash
# You asking the verifier to check something
python3 send_message.py "human_coordinator" "autistic_verifier" "verification_request" "Analyze the new authentication flow for security patterns"

python3 send_message.py "human_coordinator" "autistic_verifier" "verification_request" "Check if the API changes maintain constitutional protections"
```

### 5. Inter-AI Communication
```bash
# Claude Main asking OpenAI for specification design
python3 send_message.py "claude_main" "openai" "plan" "Design security specifications for the payment processing module"

# OpenAI asking Claude Main for documentation review
python3 send_message.py "openai" "claude_main" "verification_request" "Review the security documentation for completeness"
```

## Real-World Workflow Examples

### Example 1: Adding a New Feature
```bash
# Step 1: You request implementation
python3 send_message.py "human_coordinator" "claude_code" "execute" "Add dark mode toggle to user settings page"

# Step 2: (Optional) Ask verifier to check the implementation
python3 send_message.py "human_coordinator" "autistic_verifier" "verification_request" "Verify dark mode implementation follows UI consistency patterns"
```

### Example 2: Multi-AI Collaboration  
```bash
# Step 1: Ask OpenAI to design the system
python3 send_message.py "human_coordinator" "openai" "plan" "Design a secure file upload system with virus scanning"

# Step 2: Ask Claude Main to document the design
python3 send_message.py "human_coordinator" "claude_main" "plan" "Create comprehensive documentation for the file upload security design"

# Step 3: Ask Claude Code to implement  
python3 send_message.py "human_coordinator" "claude_code" "execute" "Implement the secure file upload system according to the design specifications"
```

### Example 3: Bug Fix Workflow
```bash
# Report a bug and request fix
python3 send_message.py "human_coordinator" "claude_code" "execute" "Fix memory leak in image processing module - users report slowdowns after uploading large files"

# Ask verifier to check the fix
python3 send_message.py "human_coordinator" "autistic_verifier" "verification_request" "Verify the memory leak fix doesn't introduce new performance issues"
```

## Content Guidelines

### Good Content Examples:
- **Specific**: "Add email validation to user registration form"
- **Context-rich**: "Fix the 500 error in /api/users endpoint when email field is missing" 
- **Clear scope**: "Refactor the authentication middleware to use JWT tokens instead of sessions"

### Avoid:
- **Vague**: "Make it better"
- **Too broad**: "Fix everything" 
- **Missing context**: "The thing is broken"

## Technical Notes

### Message Flow:
1. You run `send_message.py`
2. Message saved to `bus/inbox/`
3. BusDaemon (if running) processes automatically
4. Response appears in `bus/outbox/`
5. Original message archived to `bus/archive/`

### Security:
- Messages auto-signed with available crypto keys
- Unsigned messages still work but less secure
- All messages logged in `bus/bus_daemon.log`

### Troubleshooting:
- If BusDaemon isn't running: `make bus`
- Check inbox: `ls bus/inbox/`  
- Check responses: `ls bus/outbox/`
- View logs: `tail bus/bus_daemon.log`

## Quick Reference Card

```bash
# Implementation requests
python3 send_message.py "human_coordinator" "claude_code" "execute" "YOUR_TASK_HERE"

# Ask for help/planning  
python3 send_message.py "human_coordinator" "claude_main" "plan" "YOUR_QUESTION_HERE"

# Security verification
python3 send_message.py "human_coordinator" "autistic_verifier" "verification_request" "YOUR_CONCERN_HERE"

# System design
python3 send_message.py "human_coordinator" "openai" "plan" "YOUR_DESIGN_REQUEST_HERE"
```