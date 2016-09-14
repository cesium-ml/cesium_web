import os
import tempfile

from cesium_app import models as m
from cesium_app.tests.util import create_test_project, create_test_dataset


def test_file_delete():
    """Test that deleting a `File` also removes the associated file."""
    fd, path = tempfile.mkstemp()
    f = m.File.create(uri=path)
    assert os.path.exists(f.uri)
    f.delete_instance()
    assert not os.path.exists(f.uri)


def test_dataset_delete():
    """Test that deleting a `Dataset` also removes any associated files."""
    with create_test_project() as p:
        ds = create_test_dataset(p).__enter__()  # skip cleanup step
        uris = ds.uris
        assert all(os.path.exists(f) for f in uris)
        ds.delete_instance()
        assert not any(os.path.exists(f) for f in uris)
