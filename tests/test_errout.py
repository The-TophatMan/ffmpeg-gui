"""Tests for ErrorOut."""

import sys
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets

from errout import ErrorOut


def test_error_popup_is_shown() -> None:
    """Test that ErrorOut displays a popup w/ error message"""
    app = QtWidgets.QApplication.instance()

    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    mock_box = MagicMock()

    with patch("errout.QtWidgets.QMessageBox", return_value=mock_box):
        ErrorOut("FFmpeg failed")

    mock_box.setInformativeText.assert_called_once_with("FFmpeg failed")
    mock_box.exec.assert_called_once()