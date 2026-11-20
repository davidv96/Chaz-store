---
alwaysApply: false
---

# Django Full-Stack Expert Guidelines

You are an expert in Python, Django, and full-stack web application development. You build complete, server-rendered web applications using Django's template engine enhanced with HTMX for dynamic, reactive UIs — without building a separate API or SPA. You write secure, maintainable, and performant code following Django and Python best practices.

## Core Philosophy

- **Full-stack Django**: Django handles routing, views, business logic, templates, and data — there is no separate frontend framework or API layer
- **HTMX for reactivity**: Use HTMX to progressively enhance server-rendered HTML — partial template rendering over the wire, not JSON
- **Batteries included**: Use Django's built-in features (auth, admin, forms, ORM) before reaching for third-party packages
- **Server-side is the source of truth**: All business logic lives in Python; the browser is a rendering surface

## Python Best Practices

- Follow PEP 8 with 120 character line limit
- Use double quotes for Python strings
- Sort imports with `isort`
- Use f-strings for string formatting
- Use meaningful variable names

## Django Best Practices

- Prioritize security and follow Django's security best practices
- Use Django's ORM effectively and avoid raw SQL unless absolutely necessary
- Use Django signals sparingly and document them well
- Prefer class-based views (CBVs) for standard CRUD patterns; use function-based views (FBVs) for complex or one-off logic
- Keep views thin — move business logic into model methods, managers, or service functions
- Use Django's form system for validation and rendering — don't roll your own
- Use template inheritance and partials to keep templates DRY and maintainable
- Use Django's built-in authentication and permission system for access control
- Don't expose sensitive data in templates; use context variables and template tags to control what gets rendered
- Don't try creating additional mixins or abstractions unless they provide clear value — Django's built-in tools are often sufficient
- Avoid creating a lot of \_private methods or \_attributes in views or models — if it's not meant to be used outside, it probably doesn't need to be a method at all
- Lambda functions in Python are meant for simple, one-off operations; if you find yourself writing a complex lambda, it's a sign that it should be a regular function or method instead
- DON'T EVER WRITE YOUR OWN MIGRATIONS UNLESS ABSOLUTELY NECESSARY — use Django's migration system to generate them for you. Manually writing migrations can lead to errors and inconsistencies in your database schema, and it's easy to miss important details that Django's migration system handles automatically

## HTMX Integration

- Use HTMX attributes (`hx-get`, `hx-post`, `hx-target`, `hx-swap`) to swap partial HTML fragments returned by Django views
- Create dedicated views that return partial templates (fragments) when the request is an HTMX request
- Use `request.htmx` (via `django-htmx`) to detect HTMX requests and conditionally return a partial or full page
- Keep HTMX targets semantic — target the smallest necessary DOM region, not entire sections
- Use `hx-boost` to progressively enhance standard `<a>` and `<form>` elements with AJAX behavior
- Use `hx-trigger` with events like `revealed`, `load`, or custom events for lazy loading and polling
- Use out-of-band swaps (`hx-swap-oob`) sparingly to update secondary regions (e.g., notification counts, toasts)
- Always return the correct HTTP status codes from views — HTMX respects them (e.g., 422 for validation errors)
- Protect HTMX POST requests with Django's CSRF middleware — include `{% csrf_token %}` in all forms

## Views

- Always validate and sanitize user input
- Handle exceptions gracefully with try/except blocks
- Use `get_object_or_404` instead of manual exception handling
- Implement proper pagination for list views
- For HTMX-triggered views, return partial templates and set appropriate `HX-*` response headers when needed (e.g., `HX-Redirect`, `HX-Trigger`)
- Use `LoginRequiredMixin` or `@login_required` to protect views — never rely solely on template-level hiding

## URLs

- Use descriptive URL names for reverse URL lookups
- Always end URL patterns with a trailing slash
- Namespace URL patterns per app using `app_name`

## Forms

- Use `ModelForm` when working with model instances
- Use form `clean()` and `clean_<field>()` methods for validation logic — keep it out of views
- Re-render forms with error context on invalid submissions for standard requests; return the form partial with a 422 for HTMX requests

## Templates

- Use template inheritance with base templates (`{% extends %}` / `{% block %}`)
- Create `_partial.html` fragments for sections that HTMX will swap independently
- Use daisyUI and Tailwind CSS for styling — good-looking, responsive components
- Take mobile users into consideration; use Tailwind responsive breakpoints (`sm:`, `md:`, `lg:`)
- Use template tags and filters for common operations
- Avoid complex logic in templates — move it to views, model methods, or custom template tags
- Use static files properly with `{% load static %}`
- Implement CSRF protection in all forms with `{% csrf_token %}`

## Security

- Apply defense in depth: use Django's middleware stack, CSRF protection, and permission checks together
- Use the principle of least privilege for all views — require login and check object-level permissions
- Never expose raw model data in templates without validation; avoid marking user-supplied content as `safe`
- Use Django's built-in `User` model and `AbstractUser`/`AbstractBaseUser` for custom auth — don't roll your own
- Set `SECURE_BROWSER_XSS_FILTER`, `X_FRAME_OPTIONS`, `SECURE_CONTENT_TYPE_NOSNIFF` in settings
- Rate-limit sensitive views (login, password reset) using `django-ratelimit` or similar

## Models

- Add `__str__` methods to all models for a better admin interface
- Use `related_name` on ForeignKey/M2M fields for readable reverse access
- Define a `Meta` class with `ordering`, `verbose_name`, and `verbose_name_plural`
- Use `blank=True` for optional form fields, `null=True` for optional database fields
- Add model-level validation in `clean()` and call it from `save()` where appropriate
- Use custom managers to encapsulate common querysets

## Database

- Use migrations for all database changes
- Optimize queries with `select_related` (FK/O2O) and `prefetch_related` (M2M/reverse FK)
- Use `only()` and `defer()` to limit columns fetched when full model data isn't needed
- Add `db_index=True` or `Index` in `Meta` for frequently filtered/sorted fields
- Avoid N+1 problems — use Django Debug Toolbar in development to catch them
- Use `F()` expressions for atomic field updates; use `Q()` for complex filter conditions
- Use `bulk_create` and `bulk_update` for high-volume writes

## Performance & Caching

- Use Django's cache framework (`cache.get` / `cache.set`) for expensive querysets or computed values
- Cache at the view level with `@cache_page` for public, infrequently changing pages
- Use `django-cachalot` or manual cache invalidation for ORM-level caching when appropriate
- Defer slow operations (email, file processing) to background tasks rather than blocking the request cycle

## Settings

- Use environment variables in a single `settings.py` file
- Never commit secrets to version control
- Use `django-environ` or `python-decouple` to manage environment variables cleanly

## Testing

- Always write unit tests and check that they pass for new features
- Test both positive and negative scenarios
- Tests should not just be changed to accept new results — ensure the integrity of the logic
- Use Django's `TestCase` for database-backed tests and `SimpleTestCase` for pure logic
- Use `Client` for view tests; assert on response status, context, and rendered content
- For HTMX views, test both the partial response (with `HTTP_HX_REQUEST` header) and the full-page fallback
