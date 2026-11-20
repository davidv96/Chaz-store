# Custom Store agent guidance

Read the relevant project files first. Use the Markdown references below for task-specific patterns and check their examples against the code, installed dependencies, and requested scope. For example, Celery, pytest-django, and django-extensions are reference topics whose packages are currently absent from `pyproject.toml`.

Open the relevant sections directly if your client has no skill or persona loader. Use persona documents as checklists and specialist perspectives. Delegation is optional when your client supports it and the task calls for it.

## Skills

Use the [skills catalog](.claude/skills/README.md) to find the relevant `SKILL.md` for Django models, forms, templates, HTMX, frontend design, testing, debugging, and other workflows. Read bundled references only as needed.

## Personas and design

| Task | Guidance |
| --- | --- |
| Server-side architecture, data integrity, or reliability | [Backend engineer](.claude/agents/backend-engineer.md) |
| End-to-end Django and HTMX implementation | [Django expert](.claude/agents/django-expert.md) |
| Storefront styling, components, or interaction design | [Store design system](.claude/design.md), [frontend design skill](.claude/skills/frontend-design/SKILL.md), and the relevant component or design section of the [frontend expert guide](.claude/agents/front-end-expert.md) |
| UX structure, CSS architecture, or developer handoff | [UX engineer](.claude/agents/ux-engineer.md) |
| Review for correctness, security, and performance | [Code reviewer](.claude/agents/code-reviewer.md) |
| Turn a specification into tasks or clarify scope | [Project manager](.claude/agents/project-manager.md) |
