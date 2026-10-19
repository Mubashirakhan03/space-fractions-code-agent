# Import deferred to avoid circular imports (ui.app imports screens from ui.*).
__all__ = ["create_app", "App"]


def __getattr__(name):
    if name == "create_app":
        from ui.app import create_app
        return create_app
    if name == "App":
        from ui.app import App
        return App
    raise AttributeError(name)
