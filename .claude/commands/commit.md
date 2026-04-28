---

description: Create context-aware git commits following Conventional Commits. Analyze the diff, group changes logically (feat/fix/refactor/test/docs/chore), and create one commit per group — never group unrelated changes. Do NOT commit unless explicitly asked.

allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git log:*)

---

## Context

- Current git status: !`git status`

- Current git diff (staged and unstaged): !`git diff HEAD`

- Current branch: !`git branch --show-current`

- Recent commits: !`git log --oneline -5`

## Your task

Follow the Context-Aware Commits workflow:

### Objective

Commits must be small, logical, and context-based — never group unrelated changes into a single commit.

### Steps

**1.** Analyze the diff and identify logical groups: feature, bug fix, refactor, tests, docs, config/tooling.

**2.** Stage files selectively per group — never `git add -A` for everything at once.

**3.** Commit message format (Conventional Commits):

type(scope): short imperative description

- changed X in Y
- applied Z to W

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `test`, `perf`

Example: `feat(auth): implement JWT authentication`

**4.** Create one commit per logical group.
**5.** Run `git log --oneline -5` to validate history.

### Rules
- Do NOT push
- Do NOT commit unless explicitly asked by the user
- Do NOT add `Co-Authored-By` lines
- All commit messages must be in **English**
