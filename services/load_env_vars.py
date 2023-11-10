def load():
    import os
    import env_vars
    for key in [item for item in dir(env_vars) if not item.startswith("__") and not item == "os"]:
        if not os.environ.get(key):
            os.environ[key] = getattr(env_vars, key)