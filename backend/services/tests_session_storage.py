import pytest
import os
from backend.services.session_storage import EncryptedFileStorage

def test_encrypted_file_storage():
    storage = EncryptedFileStorage(storage_dir="backend/data/test_sessions")
    provider = "test_provider"
    data = {"cookies": [{"name": "test", "value": "secret"}]}

    # Save
    assert storage.save(provider, data) == True
    assert storage.exists(provider) == True

    # Verify it is encrypted (not plain JSON)
    filepath = storage._get_filepath(provider)
    with open(filepath, 'r') as f:
        content = f.read()
        assert "secret" not in content

    # Load
    loaded = storage.load(provider)
    assert loaded == data

    # Delete
    assert storage.delete(provider) == True
    assert storage.exists(provider) == False

    # Cleanup
    if os.path.exists("backend/data/test_sessions"):
        import shutil
        shutil.rmtree("backend/data/test_sessions")
