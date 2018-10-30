import os
import sys
import solvebio


def download_vault_folder(remote_path, local_path, dry_run=False, force=False):
    """Recursively downloads a folder in a vault to a local directory.
    Only downloads files, not datasets."""

    local_path = os.path.normpath(os.path.expanduser(local_path))
    if not os.access(local_path, os.W_OK):
        raise Exception(
            'Write access to local path ({}) is required'
            .format(local_path))

    full_path, path_dict = solvebio.Object.validate_full_path(remote_path)
    vault = solvebio.Vault.get_by_full_path(path_dict['vault'])
    print('Downloading all files from {} to {}'.format(full_path, local_path))

    if path_dict['path'] == '/':
        parent_object_id = None
    else:
        parent_object = solvebio.Object.get_by_full_path(
            remote_path, assert_type='folder')
        parent_object_id = parent_object.id

    # Scan the folder for all sub-folders and create them locally
    print('Creating local directory structure at: {}'.format(local_path))
    if not os.path.exists(local_path):
        if not dry_run:
            os.makedirs(local_path)

    folders = vault.folders(parent_object_id=parent_object_id)
    for f in folders:
        path = os.path.normpath(local_path + f.path)
        if not os.path.exists(path):
            print('Creating folder: {}'.format(path))
            if not dry_run:
                os.makedirs(path)

    files = vault.files(parent_object_id=parent_object_id)
    for f in files:
        path = os.path.normpath(local_path + f.path)
        if os.path.exists(path):
            if force:
                # Delete the local copy
                print('Deleting local file (force download): {}'.format(path))
                if not dry_run:
                    os.remove(path)
            else:
                print('Skipping file (already exists): {}'.format(path))
                continue

        print('Downloading file: {}'.format(path))
        if not dry_run:
            f.download(path)


def main():
    if len(sys.argv) < 3:
        print('Usage: {} <vault path> <local path>'.format(sys.argv[0]))
        sys.exit(1)

    solvebio.login()
    download_vault_folder(sys.argv[1], sys.argv[2], dry_run=True)


if __name__ == '__main__':
    main()
