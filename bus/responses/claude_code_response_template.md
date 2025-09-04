# Claude Code Response Template

## Response Header
- **From**: claude_code
- **To**: [target_component]
- **Timestamp**: [ISO timestamp]
- **Response Type**: [implementation_complete|blocked|clarification_needed|error]
- **Message ID**: [unique_id]

## Implementation Status
- **Task**: [original request summary]
- **Status**: [completed|in_progress|blocked|failed]
- **Files Modified**: [list of changed files]
- **Tests Status**: [passed|failed|not_applicable]

## Results
- **What was implemented**: [concrete description]
- **Code changes**: [brief summary of modifications]
- **New functionality**: [what the user can now do]

## Concerns & Blockers
- **Security concerns**: [any safety issues identified]
- **Technical blockers**: [dependencies, missing info, conflicts]
- **Clarification needed**: [specific questions for other components]

## GitHub Artifacts
- **Commit hash**: [git commit reference]
- **Branch**: [if applicable]
- **Files to review**: [specific paths for other components]

## Next Actions Required
- **From bus**: [what human bus should coordinate]
- **From other components**: [specific inputs needed]
- **Priority level**: [urgent|normal|low]

## Critical Reasoning Applied
- **Safety validation**: [security checks performed]
- **Incremental approach**: [how changes were kept minimal]
- **Context preservation**: [what context was maintained/lost]