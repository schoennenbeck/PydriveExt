from pydrive.files import GoogleDriveFile
from pydrive.drive import GoogleDrive

from pydriveext.files import _normalize_path

def make_dir(drive: GoogleDrive, path: str) -> GoogleDriveFile:
    """Makes a new directory in google drive. Including all 
    necessary intermediate directories. Returns the directory

    Args:
      drive: The google drive in question.
      path: The absolute path of the directory.
    """
    path = _normalize_path(path)
    exists, result = drive.path_exists(path, return_file=True)
    if exists:
        return result
    else:
        split_path = path.split('/')
        name = split_path[-1]
        parent_path = '/'.join(split_path[:-1])
        parent = make_dir(drive, parent_path)
        metadata = {
            'title': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent['id']}]
        }
        file = drive.CreateFile(metadata)
        file.Upload()
        return file

GoogleDrive.make_dir = make_dir
