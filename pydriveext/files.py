from typing import List, Tuple
import itertools
import logging

from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile, ApiRequestError

def _normalize_path(path:str) -> str:
    """Simply removes leading '/' if present."""
    while path.startswith('/'):
        path = path[1:]
    while path.endswith('/'):
        path = path[:-1]
    return path 

def get_file(drive: GoogleDrive, id: str) -> GoogleDriveFile:
    """Fetch the file with the given id from the drive.

    This does not download the file.
    Args:
      drive: The google drive in which you want to search for the file.
      id: The id of the file you want.
    """
    try:
        file = drive.CreateFile({'id': id})
        file.FetchMetadata()
        return file 
    except ApiRequestError:
        raise KeyError(f"Could not find file with id {id}.")
    

def get_paths(drive: GoogleDrive, file: GoogleDriveFile) -> List[str]:
    """Returns a list of all paths under which the file can be found in the drive.

    Args:
      drive: The google drive in which to search.
      file: The file for which we need the paths.
    """
    # The root folder is the only one without parents and its path is the empty string
    if len(file.get('parents', [])) == 0:
        return ['']
    else:
        parents = [drive.get_file(p['id']) for p in file['parents']]
        parent_paths = itertools.chain(*[get_paths(drive, parent) for parent in parents])
        return [_normalize_path(f"{pp}/{file['title']}") for pp in parent_paths] 

def get_file_by_path(drive: GoogleDrive, path:str) -> GoogleDriveFile:
    """Tries to obtain a file from the drive via the given path.

    Args:
      drive: The google drive in question
      path: The path to obtain.
    """
    fname = path.split('/')[-1]
    if len(fname) == 0:
        return drive.get_file('root')
    candidate_list = drive.ListFile({'q': f"title = '{fname}' and trashed = false"}).GetList()
    
    for cand in candidate_list:
        cand_paths = drive.get_paths(cand)
        if _normalize_path(path) in cand_paths:
            return cand
    raise FileNotFoundError(f'Could not find file {path}')

def path_exists(drive: GoogleDrive, path:str, return_file=False) -> Tuple[bool, GoogleDriveFile]:
    """Checks whether the path exists in the google drive.
    Args:
      drive: The google drive in question.
      path: The path to check for.
      return_file: Whether the path should be returned if it exists.
    Returns:
      Tuple of boolean and GoogleDriveFile or None
    """
    try:
        res = drive.get_file_by_path(path)
        if return_file:
            return True, res 
        else:
            return True
    except FileNotFoundError:
        if return_file:
            return False, _
        else:
            return False

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



GoogleDrive.get_file = get_file
GoogleDrive.get_paths = get_paths
GoogleDrive.get_file_by_path = get_file_by_path
GoogleDrive.path_exists = path_exists
GoogleDrive.make_dir = make_dir

    

