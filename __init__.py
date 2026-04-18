from .auto_grid_saver import AutoGridSaver
from .metadata_extractor import MetadataExtractor # 새로 만든 파일 임포트

NODE_CLASS_MAPPINGS = {
    "AutoGridSaver": AutoGridSaver,
    "MetadataExtractor": MetadataExtractor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoGridSaver": "Auto Grid Saver zk",
    "MetadataExtractor": "Metadata Extractor zk"
}

WEB_DIRECTORY = "./web"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']