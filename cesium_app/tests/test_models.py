import os
import tempfile

from cesium_app import models as m


def test_dataset_delete(project, dataset):
    """Test that deleting a `Dataset` also removes any associated files."""
    uris = [f.uri for f in dataset.files]
    assert all(os.path.exists(f) for f in uris)
    m.DBSession().delete(dataset)
    m.DBSession().commit()
    assert not any(os.path.exists(f) for f in uris)


def test_file_delete(featureset, model):
    """Test that deleting an object also removes any associated files."""
    for obj in [model, featureset]:
        assert os.path.exists(obj.file_uri)
        m.DBSession().delete(obj)
        m.DBSession().commit()
        assert not os.path.exists(obj.file_uri)
