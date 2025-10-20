# Pull Request Guide

- Format: The PR description MUST start with the list of Conventional Commit types included in the branch, ideally grouped by feature, fix, or chore.
- Title: The PR title should follow the Conventional Commit style, representing the most significant change (e.g., feat(ui): Implement weighted card selection dashboard).
- Required Sections: The description must contain the following sections to facilitate review:
    1. Summary: A brief, non-technical explanation of what the PR does and why (the business value).
    2. Technical Changes: Detail the key files/components modified, focusing on architectural changes (e.g., "Updated card_model.py to use selectinload to fix the N+1 problem," or "Refactored Controller to handle View signal types explicitly").
    3. Testing: List the unit tests created or modified (Section 9) and provide clear steps for the reviewer to manually test the feature in the PySide6 UI.
    4. Breaking Changes: If applicable, explicitly state any changes that are not backward-compatible. This section is mandatory if a commit type included ! or BREAKING CHANGE.
- Linking: SHOULD include links to any related issues or tickets.
- Reviewer Focus: Specifically highlight areas where the reviewer should focus their attention (e.g., security checks, performance of a new SQL query, adherence to Mypy typing in a complex function).
