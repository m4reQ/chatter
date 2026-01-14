import pathlib
import os

from app.directory import Directory

class FSService:
    def __init__(self, root_directory: os.PathLike) -> None:
        self._root_directory = pathlib.Path(root_directory)

        self._create_directory(self._root_directory)

    def get_path(self, filepath: os.PathLike, subdirectory: Directory = Directory.ROOT):
        return self._root_directory / subdirectory / filepath
    
    def remove(self, filepath: os.PathLike, subdirectory: Directory = Directory.ROOT):
        path = self.get_path(filepath, subdirectory)
        if path.exists():
            if path.is_dir():
                os.removedirs(path)
            else:
                os.remove(path)
    
    def file_exists(self, filepath: pathlib.Path, subdirectory: Directory = Directory.ROOT) -> bool:
        return os.path.exists(filepath / subdirectory)

    def save_file(self, filepath: pathlib.Path, data: bytes, replace: bool = True) -> None:
        pass

    def delete_file(self, filepath: pathlib.Path) -> None:
        pass

    def read_file(self, filepath: pathlib.Path) -> None:
        pass

    def _create_data_directory(self) -> None:
        if self._root_directory.exists():
            return
        
        os.makedirs(str(self._root_directory))