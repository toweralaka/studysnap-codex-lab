# StudySnap development rules

## Project scope

StudySnap is a small Django application for learning. Users should eventually be able to create subjects, create learning notes under subjects, mark notes as understood, take simple quizzes, and view basic progress. These are planned capabilities, not features to implement automatically.

## Working with the user

- Explain important decisions before making them, using beginner-friendly language and describing relevant tradeoffs.
- When a requirement is uncertain, explain the uncertainty instead of silently guessing. Ask for clarification when the answer affects behavior or scope.
- Implement only the agreed task. Do not modify unrelated functionality.

## Implementation

- Keep solutions small and easy to understand. Prefer Django's built-in capabilities where they meet the requirements.
- Do not introduce unnecessary dependencies. Explain why a new dependency is needed before adding it.
- Never put secrets in source control. Keep credentials and secret values out of code, tests, documentation, and committed configuration; use environment variables or appropriate ignored local configuration.

## Validation

- Write tests for meaningful behavior, including relevant validation and failure cases.
- Run relevant tests after changes. If tests fail or cannot run, explain what happened and any remaining limitations.
- Summarize what changed and what was tested. Do not claim that checks passed unless they were actually run and passed.
