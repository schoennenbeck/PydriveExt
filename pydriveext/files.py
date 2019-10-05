from typing import List
import itertools
import logging

from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile, ApiRequestError

def _normalize_path(path:str) -> str:
    """Simply removes leading '/' if present."""
    while path.startswith('/'):
        path = path[1:]
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
    candidate_list = drive.ListFile({'q': f"title = '{fname}'"}).GetList()
    if not candidate_list:
        raise FileNotFoundError(f'Could not find file {path}') 
    for cand in candidate_list:
        cand_paths = drive.get_paths(cand)
        if _normalize_path(path) in cand_paths:
            return cand
    raise FileNotFoundError(f'Could not find file {path}')



GoogleDrive.get_file = get_file
GoogleDrive.get_paths = get_paths
GoogleDrive.get_file_by_path = get_file_by_path
    

