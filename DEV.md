# Dev Guide for AI Agents

## PowerShell Git Commands

**Key difference:** Use `;` not `&&` for command chaining in PowerShell.

### Basic Workflow
```powershell
# Check status
git status

# Stage changes
git add -A

# Commit with message
git commit -m "Your commit message"

# Push to branch
git push origin branch-name

# Chain commands (PowerShell syntax)
git add -A; git commit -m "Message"; git push origin branch-name
```

### Branch Management
```powershell
# Check current branch
git branch -v

# Switch branch
git checkout branch-name

# Create and switch to new branch
git checkout -b new-branch-name
```

**Remember:** Always verify you're on the correct branch before pushing! 