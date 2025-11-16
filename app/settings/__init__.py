from settings.config import Config


_config_instance: Config | None = None


def _get_config() -> Config:
    """Lazy initialization of config to avoid validation errors during
    import."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def __getattr__(name: str):
    """Make 'config' accessible as a module-level variable with lazy
    initialization."""
    if name == "config":
        return _get_config()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
