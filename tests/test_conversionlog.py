"""Tests for the ConversionLog class."""

import sys
from unittest.mock import MagicMock, patch

from hypothesis import given
from hypothesis import strategies as st
from PySide6 import QtWidgets

from conversionlog import ConversionLog


def get_qapp() -> QtWidgets.QApplication:
    """Create or return the existing QApplication."""
    app = QtWidgets.QApplication.instance()

    if isinstance(app, QtWidgets.QApplication):
        return app

    return QtWidgets.QApplication(sys.argv)


@given(
    input_file=st.text(min_size=1, max_size=30),
    output_file=st.text(min_size=1, max_size=30),
    success=st.booleans(),
)
def test_add_entry_stores_basic_conversion(
    input_file: str,
    output_file: str,
    success: bool,
) -> None:
    """Test that add_entry stores conversion information."""
    log = ConversionLog()

    log.add_entry(input_file, output_file, success)

    formatted = log.formatted_logs()

    assert input_file in formatted
    assert output_file in formatted

    if success:
        assert "SUCCESS" in formatted
    else:
        assert "FAILURE" in formatted


@given(
    input_file=st.text(min_size=1, max_size=30),
    output_file=st.text(min_size=1, max_size=30),
    message=st.text(min_size=1, max_size=50),
)
def test_add_entry_stores_error_message(
    input_file: str,
    output_file: str,
    message: str,
) -> None:
    """Test that add_entry stores an error message when provided."""
    log = ConversionLog()

    log.add_entry(input_file, output_file, False, message)

    formatted = log.formatted_logs()

    assert input_file in formatted
    assert output_file in formatted
    assert "FAILURE" in formatted
    assert message in formatted


def test_formatted_logs_empty_message() -> None:
    """Test formatted_logs returns default message when no logs exist."""
    log = ConversionLog()

    assert log.formatted_logs() == "No conversions have happened yet."


def test_formatted_logs_multiple_entries() -> None:
    """Test formatted_logs separates multiple entries with blank lines."""
    log = ConversionLog()

    log.add_entry("input1.mp4", "output1.mp3", True)
    log.add_entry("input2.mov", "output2.wav", False, "Bad file")

    formatted = log.formatted_logs()

    assert "input1.mp4" in formatted
    assert "output1.mp3" in formatted
    assert "input2.mov" in formatted
    assert "output2.wav" in formatted
    assert "SUCCESS" in formatted
    assert "FAILURE" in formatted
    assert "Bad file" in formatted
    assert "\n\n" in formatted


@patch("conversionlog.QtWidgets.QDialog")
@patch("conversionlog.QtWidgets.QTextEdit")
@patch("conversionlog.QtWidgets.QPushButton")
@patch("conversionlog.QtWidgets.QVBoxLayout")
def test_show_window_displays_logs(
    mock_layout_class: MagicMock,
    mock_button_class: MagicMock,
    mock_text_edit_class: MagicMock,
    mock_dialog_class: MagicMock,
) -> None:
    """Test that show_window creates and displays the log window."""
    get_qapp()

    mock_dialog = MagicMock()
    mock_text_edit = MagicMock()
    mock_button = MagicMock()
    mock_layout = MagicMock()

    mock_dialog_class.return_value = mock_dialog
    mock_text_edit_class.return_value = mock_text_edit
    mock_button_class.return_value = mock_button
    mock_layout_class.return_value = mock_layout

    log = ConversionLog()
    log.add_entry("input.mp4", "output.mp3", True)

    log.show_window()

    mock_dialog.setWindowTitle.assert_called_once_with("Conversion Logs")
    mock_dialog.resize.assert_called_once_with(600, 400)
    mock_text_edit.setReadOnly.assert_called_once_with(True)

    text_argument = mock_text_edit.setPlainText.call_args.args[0]
    assert "input.mp4" in text_argument
    assert "output.mp3" in text_argument
    assert "SUCCESS" in text_argument

    mock_button_class.assert_called_once_with("Close")
    mock_button.clicked.connect.assert_called_once_with(mock_dialog.accept)
    mock_layout.addWidget.assert_any_call(mock_text_edit)
    mock_layout.addWidget.assert_any_call(mock_button)
    mock_dialog.exec.assert_called_once()
