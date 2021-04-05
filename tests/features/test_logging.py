import logging

import pytest

from notepad.features import logger


@pytest.mark.parametrize(
    "level,expected_logging", [(-1, logging.WARN), (1, logging.INFO), (100, logging.DEBUG)]
)
def test_configure_logger(level, expected_logging):
    assert logger.configure_logging(level) == expected_logging
