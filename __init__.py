from .auto_grid_saver import AutoGridSaver

NODE_CLASS_MAPPINGS = {
    "AutoGridSaver": AutoGridSaver
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoGridSaver": "Auto Grid Saver zk"
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']