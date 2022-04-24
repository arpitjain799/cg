from datetime import datetime

from cg.constants import Priority
from cg.models.dolores.sample import Sample


def test_instantiate_dolores_sample(dolores_sample_raw: dict):
    """
    Tests Dolores sample model
    """
    # GIVEN a dictionary with the some sample data

    # WHEN instantiating a Sample object
    dolores_samples = Sample(**dolores_sample_raw)

    # THEN assert that it was successfully created
    assert isinstance(dolores_samples, Sample)


def test_instantiate_dolores_samples_with_created_at(
    datestamp_now: datetime, dolores_sample_raw: dict
):
    """
    Tests Dolores sample model with "created_at"
    """
    # GIVEN a dictionary with the some sample data including created_at
    dolores_sample_raw.update({"created_at": datestamp_now})

    # WHEN instantiating a Sample object
    dolores_samples = Sample(**dolores_sample_raw)

    # THEN assert that it should return the current time
    assert dolores_samples.created_at == datestamp_now


def test_instantiate_dolores_samples_with_priority_str(dolores_sample_raw: dict):
    """
    Tests Dolores sample model with "priority" in str format
    """
    # GIVEN a dictionary with the some sample data including "priority" in str format
    assert isinstance(dolores_sample_raw["priority"], str)

    # WHEN instantiating a Sample object
    dolores_samples = Sample(**dolores_sample_raw)

    # THEN assert that it should return the integer value of the priority
    assert dolores_samples.priority == Priority.standard


def test_instantiate_dolores_samples_with_priority_int(dolores_sample_raw: dict):
    """
    Tests Dolores sample model with "priority" in int format
    """
    # GIVEN a dictionary with the some sample data including "priority" in int format
    dolores_sample_raw.update({"priority": Priority.standard})
    assert isinstance(dolores_sample_raw["priority"], int)

    # WHEN instantiating a Sample object
    dolores_samples = Sample(**dolores_sample_raw)

    # THEN assert that it should return the integer value of the priority
    assert dolores_samples.priority == Priority.standard
