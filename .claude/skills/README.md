# Project Skills

Use this catalog to find task-specific guidance for the Django codebase. See the [repository guide](../../AGENTS.md) for personas and the store design system.

## Skills by Category

### Meta & Development Tools
| Skill | Description |
|-------|-------------|
| [skill-creator](./skill-creator/SKILL.md) | Guide for writing reusable skills and bundling scripts and references |
| [django-extensions](./django-extensions/SKILL.md) | Django-extensions management commands for introspection, debugging, and development |

### Testing & Debugging
| Skill | Description |
|-------|-------------|
| [pytest-django-patterns](./pytest-django-patterns/SKILL.md) | pytest-django, Factory Boy, fixtures, TDD workflow |
| [systematic-debugging](./systematic-debugging/SKILL.md) | Four-phase debugging methodology, root cause analysis |

### Django Core
| Skill | Description |
|-------|-------------|
| [django-models](./django-models/SKILL.md) | Model design, QuerySet optimization, signals, migrations |
| [django-forms](./django-forms/SKILL.md) | Form handling, validation, ModelForm patterns |
| [django-templates](./django-templates/SKILL.md) | Template inheritance, tags, filters, partials |

### Frontend & UI
| Skill | Description |
|-------|-------------|
| [frontend-design](./frontend-design/SKILL.md) | Visual direction and implementation for pages and components |
| [htmx-patterns](./htmx-patterns/SKILL.md) | HTMX attributes, partial templates, dynamic UI |

### Background Tasks
| Skill | Description |
|-------|-------------|
| [celery-patterns](./celery-patterns/SKILL.md) | Celery tasks, retry strategies, periodic tasks |

## Skill Combinations for Common Tasks

### Building a New Feature
1. **django-models** - Design models
2. **django-forms** - Create forms for user input
3. **htmx-patterns** - Dynamic UI
4. **django-templates** - Page templates
5. **pytest-django-patterns** - Write tests (TDD)

### Building a Background Task
1. **celery-patterns** - Task definition
2. **django-models** - Database operations
3. **pytest-django-patterns** - Task tests

### Debugging an Issue
1. **systematic-debugging** - Root cause analysis
2. **pytest-django-patterns** - Write failing test first
3. **django-extensions** - Use show_urls, list_model_info, shell_plus for investigation

### Creating New Skills
1. **skill-creator** - Follow the skill creation guide
2. **django-extensions** - Test your skill with project introspection commands

## How Skills Work

Open the relevant `SKILL.md` directly, or use your client's native skill loader when available. Skills can include:

- **When to Use** - Trigger conditions
- **Core Patterns** - Best practices and examples
- **Anti-Patterns** - What to avoid
- **Integration** - How skills connect

## Adding New Skills

1. Create a directory under `.claude/skills/` named for the skill.
2. Add `SKILL.md` with YAML frontmatter. Match `name` to the directory name and use the `description` to explain when the skill applies.
   ```yaml
   ---
   name: skill-name
   description: What the skill does and when to use it.
   ---
   ```
3. Document the applicable workflow and link any bundled references by relative path.
4. Add the skill to this catalog.

## Maintenance

- Update skills when patterns change
- Remove outdated information
- Add new patterns as they emerge
- Keep examples current with codebase
