import shutil
import atexit
import os
from pathlib import Path

from uuid import uuid4 as uuid

from util.logger import Logger
from util.error import *

class FileManager:
    command_name: str
    root: Path

    def __init__(self, command_name: str, root: Path) -> None:
        self.command_name = command_name
        self.root = root
        self.__cleanup_tmp_dir()
        
        atexit.register(self.__cleanup_tmp_dir)

    def noduplicate_path(self, directory: Path, basename: str, ext: str|None) -> Path:
        """
        @param directory: ファイルが存在するディレクトリ
        @param basename: ファイル名
        @param ext: 拡張子
        @return: 重複しないファイルパス
        """
        return directory / self.noduplicate_filename(directory, basename, ext)

    def noduplicate_filename(self, directory: Path, basename: str, ext: str|None) -> str:
        """
        :param str directory: ファイルが存在するディレクトリ
        :param basename: ファイル名
        :param ext: 拡張子
        :return: 重複しないファイル名
        """
        if ext is None:
            filename = basename
        else:
            filename = f"{basename}.{ext}"
        couter = 2
        while (directory / filename).exists():
            if ext is None:
                filename = f"{basename} ({couter})"
            else:
                filename = f"{basename} ({couter}).{ext}"
            couter += 1
        return filename

    def command_directory(self) -> Path:
        """
        Optionなど永続してほしいデータを保存するディレクトリ。存在する場合はそのまま返す。
        """
        self.__create_command_dir()
        return self.__command_path

    def temporary_directory(self) -> Path:
        """
        一時的なディレクトリを作成する。存在する場合はそのまま返す。
        """
        self.__create_tmp_dir()
        return self.__tmp_path

    def unique_temporary_directory(self) -> Path:
        """
        Tempディレクトリの中に一意なディレクトリを作成する
        """
        dirname = uuid()
        dirpath = self.temporary_directory() / str(dirname.hex)
        dirpath.mkdir(parents=True, exist_ok=True)
        return dirpath

    @property
    def __command_path(self) -> Path:
        """
        Optionなど永続してほしいデータを保存するディレクトリ
        """
        return self.root / f"{self.command_name}({os.getpid()}))"

    @property
    def __tmp_path(self) -> Path:
        """
        一時的なデータを保存するディレクトリ(プログラム終了時に削除)
        """
        return self.root / f"tmp_{self.command_name}({os.getpid()})"

    def __cleanup_tmp_dir(self):
        """
        一時的なディレクトリを削除する
        """
        try:
            if self.__tmp_path.exists():
                shutil.rmtree(self.__tmp_path)
        except Exception as e:
            raise InternalError("Cleanup temporary directory failed.")

    def __create_tmp_dir(self):
        """
        一時的なディレクトリを作成する
        """
        try:
            self.__tmp_path.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            raise InternalError(f"Create temporary directory failed. {e}")

    def __create_command_dir(self):
        """
        Optionなど永続してほしいデータを保存するディレクトリを作成する
        """
        try:
            self.__command_path.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            raise InternalError("Create command directory failed.")
