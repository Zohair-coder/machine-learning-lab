from __future__ import absolute_import, division, print_function

import os
from typing import Iterator, List, Optional

from contaxy.clients import FileClient
from contaxy.schema import File
from loguru import logger

from lab_client.utils import file_handler_utils, request_utils


class FileHandler:
    def __init__(self, env, file_client: FileClient):
        # Initialize variables
        self.env = env
        self.file_client = file_client
        if not self.env.is_connected():
            raise RuntimeError("Environment is not connected to Lab!")

    def get_file(
        self,
        key: str,
        version: Optional[str] = None,
        force_download: bool = False,
    ) -> str:
        """Returns local path to the file for the given `key`.
        If the file is not available locally, download it from the storage of the Lab Instance.

        Args:
            key: Key or url of the requested file.
            version: Version of the file to return. If `None` (default) the latest version will be returned.
            force_download: If `True`, the file will always be downloaded and not loaded locally (optional).
        Returns:
            Local path to the requested file or `None` if file is not available.
        """
        if request_utils.is_valid_url(key):
            # key == url -> download from url
            local_file_path = file_handler_utils.download_file(
                key, self.env.downloads_folder, force_download=force_download
            )
            return local_file_path

        if version is None:
            # Get latest version via the API
            file_info = self.file_client.get_file_metadata(
                project_id=self.env.project, file_key=key
            )
            version = file_info.version

        local_file_path = self.resolve_path_from_key(key, version)

        if force_download or not os.path.isfile(local_file_path):
            # no local file found or download forced -> try to directly download file
            return self._download_file(key, version)
        else:
            return local_file_path

    def upload_file(
        self,
        file_path: str,
        data_type: str,
        metadata: dict = None,
        file_name: str = None,
    ) -> str:
        """Uploads a file to the storage of the Lab Instance.

        Args:
            file_path: Local file path to the file you want ot upload.
            data_type: Data type of the file. Possible values are `model`, `dataset`, `experiment`.
            metadata: Adds additional metadata to remote storage (optional).
            file_name: File name to use in the remote storage. If not provided, the name will be extracted from the provided path (optional)
        Returns:
            Key of the uploaded file.
        """
        if os.path.isdir(file_path):
            logger.info("Path is a folder, uploading as folder instead.")
            return self.upload_folder(
                file_path, data_type=data_type, metadata=metadata, file_name=file_name
            )
        if not os.path.isfile(file_path):
            raise Exception("File does not exist locally:" + file_path)

        if file_name is None:
            file_name = file_path.split(os.sep)[-1]
        with open(file_path, "rb") as f:
            file = self.file_client.upload_file(
                self.env.project, f"{data_type}s/{file_name}", f
            )
        return file.key

    def upload_folder(
        self,
        folder_path: str,
        data_type: str,
        metadata: dict = None,
        file_name: str = None,
    ) -> str:
        """Packages the folder (via `zipfile`) and uploads the specified folder to the storage of the Lab instance.

        Args:
            folder_path: Local path to the folder you want ot upload.
            data_type: Data type of the resulting zip-file. Possible values are `model`, `dataset`, `experiment`.
            metadata: Adds additional metadata to remote storage (optional).
            file_name: File name to use in the remote storage. If not provided, the name will be extracted from the provided path (optional)
        Returns:
            Key of the uploaded (zipped) folder.
        """
        raise NotImplemented()

    def list_remote_files(
        self, data_type: str = None, prefix: str = None
    ) -> List[File]:
        """List remote files from Lab instance.

        Args:
            data_type (string): Data type to filter files (dataset, model...)
            prefix (string): Key prefix to filter files. If `data_type` is provided as well, the prefix will be used to filter files from the data type.
        Returns:
            List of found `Files`
        """
        path = ""
        if data_type:
            path += f"{data_type}s/"
        if prefix:
            path += prefix

        self.file_client.list_files(
            project_id=self.env.project,
            prefix=path,
        )

    def delete_remote_file(
        self, key: str, version: Optional[str] = None, keep_latest_version: bool = False
    ) -> None:
        """
        Delete a file from remote storage.
        # Arguments
            key: Key of the file.
            keep_latest_version: If `True` the latest file version will be kept.
        """
        self.file_client.delete_file(
            project_id=self.env.project,
            file_key=key,
            version=version,
            keep_latest_version=keep_latest_version,
        )

    def resolve_path_from_key(self, key: str, version: Optional[str] = None) -> str:
        """
        Return the local path for a given key.
        """
        if version:
            key = f"{key}.{version}"
        return os.path.abspath(os.path.join(self.env.project_folder, key))

    def _download_file(self, key: str, version: str) -> str or None:
        """
        Loads a local file with the given key. Will also try to find the newest version if multiple versions exists locally for the key.
        # Arguments
            key (string): Key of the file.
        # Returns
        Path to file or `None` if no local file was found.
        """
        logger.info(f"Downloading remote file: {key}")
        file_stream = self.file_client.download_file(
            project_id=self.env.project,
            file_key=key,
            version=version,
        )
        download_path = self.resolve_path_from_key(key, version)
        self._download_file_stream(file_stream, download_path)
        return download_path

    def _download_file_stream(self, stream: Iterator[bytes], file_path: str) -> bool:
        """
        Stream the requested file to file_path. This way, even large files can be downloaded.
        # Arguments
            response (#HttpResponse): the http response of the server. Should contain an output stream.
            file_path (string): the path where the file will be saved
        # Returns
        True if the download was successful, False otherwise
        """
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, "wb") as out:
            for chunk in stream:
                out.write(chunk)
