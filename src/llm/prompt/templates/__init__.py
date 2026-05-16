# Templates module for provider-specific prompt templates.
#
# Historically this package only re-exported names that were never populated,
# which made `import llm.prompt` raise ImportError. It now provides a small,
# stable surface (an empty registry plus accessors) so the prompt package is
# importable everywhere; richer per-provider templates can be added here later
# without touching callers.

TEMPLATES: dict[str, str] = {}


def get_template(name: str):
    """Return the template registered under ``name`` or ``None``."""
    return TEMPLATES.get(name)


def get_template_or_default(name: str, default=None):
    """Return the template registered under ``name`` or ``default``."""
    return TEMPLATES.get(name, default)


__all__ = ("TEMPLATES", "get_template", "get_template_or_default")
