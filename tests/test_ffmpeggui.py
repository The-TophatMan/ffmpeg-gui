"""Tests for the central FfmpegGui class."""

import os
import sys
from unittest.mock import MagicMock, patch

from hypothesis import given
from hypothesis import strategies as st
from PySide6 import QtWidgets

from ffmpeggui import FfmpegGui


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def get_qapp() -> QtWidgets.QApplication:
    """Create or return the existing QApplication."""
    app = QtWidgets.QApplication.instance()

    if isinstance(app, QtWidgets.QApplication):
        return app

    return QtWidgets.QApplication(sys.argv)


def fake_process(returncode: int = 0, stdout: str = "",
                 stderr: str = "") -> MagicMock:
    """Create a fake subprocess result."""
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


def reset_singleton() -> None:
    """Reset the singleton before creating a new GUI."""
    FfmpegGui._instance = None


@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4", "mov"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3", "wav"])
@patch("ffmpeggui.subprocess.run")
def test_one(
    mock_run: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
) -> None:
    """Test that the GUI initializes its main widgets."""
    get_qapp()
    reset_singleton()

    mock_run.return_value = fake_process(returncode=0)

    gui = FfmpegGui()

    assert gui._input_label.text() == "Input"
    assert gui._output_label.text() == "Output"
    assert gui._convert_button.text() == "Convert"
    assert gui._log_button.text() == "View Logs"
    assert gui._output_extension.count() == 2
    assert gui._output_extension.itemText(0) == ".mp3"
    assert gui._output_extension.itemText(1) == ".wav"


def test_ffmpeggui_two() -> None:
    """Test that __new__ returns the same instance."""
    reset_singleton()

    gui_one = FfmpegGui.__new__(FfmpegGui)
    gui_two = FfmpegGui.__new__(FfmpegGui)

    assert gui_one is gui_two


@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3"])
@patch("ffmpeggui.Installer")
@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_three(
    mock_run: MagicMock,
    mock_installer: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
) -> None:
    """Test that Installer is called when ffmpeg is not found."""
    get_qapp()
    reset_singleton()

    mock_run.return_value = fake_process(returncode=1)

    FfmpegGui()

    mock_installer.assert_called_once()


@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3"])
@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_four(
    mock_run: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
) -> None:
    """Test that a successful conversion is logged."""
    get_qapp()
    reset_singleton()

    mock_run.side_effect = [
        fake_process(returncode=0),
        fake_process(returncode=0),
    ]

    gui = FfmpegGui()
    gui._logger = MagicMock()

    gui._input_text.setText("input.mp4")
    gui._output_text.setText("output")
    gui._output_extension.setCurrentText(".mp3")

    gui.beginconversion()

    mock_run.assert_called_with(
        ["ffmpeg", "-i", "input.mp4", "output.mp3"],
        capture_output=True,
        text=True,
    )

    gui._logger.add_entry.assert_called_once_with(
        "input.mp4",
        "output.mp3",
        True,
    )


@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3"])
@patch("ffmpeggui.ErrorOut")
@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_five(
    mock_run: MagicMock,
    mock_errorout: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
) -> None:
    """Test that a failed conversion logs an error and shows ErrorOut."""
    get_qapp()
    reset_singleton()

    fake_stderr = "\n".join([f"line {number}" for number in range(20)])

    mock_run.side_effect = [
        fake_process(returncode=0),
        fake_process(returncode=1, stderr=fake_stderr),
    ]

    gui = FfmpegGui()
    gui._logger = MagicMock()

    gui._input_text.setText("bad_input.mp4")
    gui._output_text.setText("bad_output")
    gui._output_extension.setCurrentText(".mp3")

    gui.beginconversion()

    expected_error = "line 18\nline 19"

    gui._logger.add_entry.assert_called_once_with(
        "bad_input.mp4",
        "bad_output.mp3",
        False,
        expected_error,
    )

    mock_errorout.assert_called_once_with(expected_error)


@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3"])
@patch("ffmpeggui.QtWidgets.QFileDialog")
@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_six(
    mock_run: MagicMock,
    mock_file_dialog_class: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
) -> None:
    """Test that promptinputfile updates the input and output text fields."""
    get_qapp()
    reset_singleton()

    mock_run.return_value = fake_process(returncode=0)

    mock_dialog = MagicMock()
    mock_dialog.selectedFiles.return_value = ["videos/example.mp4"]
    mock_file_dialog_class.return_value = mock_dialog

    gui = FfmpegGui()
    gui.promptinputfile()

    mock_dialog.setNameFilter.assert_called_once_with(
        "Supported Files (*.mp4)")
    mock_dialog.exec.assert_called_once()

    assert gui._input_text.text() == "videos/example.mp4"
    assert gui._output_text.text() == "videos/example"


@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3"])
@patch("ffmpeggui.QtWidgets.QFileDialog")
@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_seven(
    mock_run: MagicMock,
    mock_file_dialog_class: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
) -> None:
    """Test that promptinputfile does nothing when no file is selected."""
    get_qapp()
    reset_singleton()

    mock_run.return_value = fake_process(returncode=0)

    mock_dialog = MagicMock()
    mock_dialog.selectedFiles.return_value = []
    mock_file_dialog_class.return_value = mock_dialog

    gui = FfmpegGui()
    gui._input_text.setText("")
    gui._output_text.setText("")

    gui.promptinputfile()

    assert gui._input_text.text() == ""
    assert gui._output_text.text() == ""


@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3"])
@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_eight(
    mock_run: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
) -> None:
    """Test that enable calls show."""
    get_qapp()
    reset_singleton()

    mock_run.return_value = fake_process(returncode=0)

    gui = FfmpegGui()

    with patch.object(gui, "show") as mock_show:
        gui.enable()

    mock_show.assert_called_once()


@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_nine(mock_run: MagicMock) -> None:
    """Test that supported_inputs parses FFmpeg input formats."""
    get_qapp()
    reset_singleton()

    formats_output = "\n".join(
        [
            "header 0",
            "header 1",
            "header 2",
            "header 3",
            "header 4",
            " D  mov,mp4 QuickTime / MOV",
        ]
    )

    demuxer_output = "\n".join(
        [
            "Demuxer mov",
            "Common extensions: mov,mp4.",
        ]
    )

    mock_run.side_effect = [
        fake_process(returncode=0, stdout=formats_output),
        fake_process(returncode=0, stdout=demuxer_output),
        fake_process(returncode=0, stdout=demuxer_output),
    ]

    gui = FfmpegGui.__new__(FfmpegGui)

    result = gui.supported_inputs()

    assert "mov" in result
    assert "mp4" in result


@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_ten(
    mock_run: MagicMock,
) -> None:
    """Test supported_inputs handles incomplete demuxer output."""
    get_qapp()
    reset_singleton()

    formats_output = "\n".join(
        [
            "header 0",
            "header 1",
            "header 2",
            "header 3",
            "header 4",
            " D  badformat Bad Format",
        ]
    )

    bad_demuxer_output = "Only one line"

    mock_run.side_effect = [
        fake_process(returncode=0, stdout=formats_output),
        fake_process(returncode=0, stdout=bad_demuxer_output),
    ]

    gui = FfmpegGui.__new__(FfmpegGui)

    result = gui.supported_inputs()

    assert result == []


@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_eleven(mock_run: MagicMock) -> None:
    """Test that supported_outputs parses FFmpeg output formats."""
    get_qapp()
    reset_singleton()

    formats_output = "\n".join(
        [
            "header 0",
            "header 1",
            "header 2",
            "header 3",
            "header 4",
            " EE mp3",
        ]
    )

    muxer_output = "\n".join(
        [
            "Muxer mp3",
            "Common extensions: mp3,",
        ]
    )

    mock_run.side_effect = [
        fake_process(returncode=0, stdout=formats_output),
        fake_process(returncode=0, stdout=muxer_output),
    ]

    gui = FfmpegGui.__new__(FfmpegGui)

    result = gui.supported_outputs()

    assert "mp3" in result


@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_twelve(
    mock_run: MagicMock,
) -> None:
    """Test supported_outputs handles incomplete muxer output."""
    get_qapp()
    reset_singleton()

    formats_output = "\n".join(
        [
            "header 0",
            "header 1",
            "header 2",
            "header 3",
            "header 4",
            " EE badformat",
        ]
    )

    bad_muxer_output = "Only one line"

    mock_run.side_effect = [
        fake_process(returncode=0, stdout=formats_output),
        fake_process(returncode=0, stdout=bad_muxer_output),
    ]

    gui = FfmpegGui.__new__(FfmpegGui)

    result = gui.supported_outputs()

    assert result == []


safe_text = st.text(
    alphabet=st.characters(
        whitelist_categories=("Ll", "Lu", "Nd"),
        whitelist_characters=("_", "-"),
    ),
    min_size=1,
    max_size=20,
)


@given(
    input_name=safe_text,
    output_name=safe_text,
)
@patch.object(FfmpegGui, "supported_inputs", return_value=["mp4"])
@patch.object(FfmpegGui, "supported_outputs", return_value=["mp3"])
@patch("ffmpeggui.subprocess.run")
def test_ffmpeggui_thirteen(
    mock_run: MagicMock,
    mock_outputs: MagicMock,
    mock_inputs: MagicMock,
    input_name: str,
    output_name: str,
) -> None:
    """Test conversion command with Hypothesis-generated file names."""
    get_qapp()
    reset_singleton()

    mock_run.side_effect = [
        fake_process(returncode=0),
        fake_process(returncode=0),
    ]

    gui = FfmpegGui()
    gui._logger = MagicMock()

    input_file = f"{input_name}.mp4"
    output_base = output_name
    output_file = f"{output_base}.mp3"

    gui._input_text.setText(input_file)
    gui._output_text.setText(output_base)
    gui._output_extension.setCurrentText(".mp3")

    gui.beginconversion()

    mock_run.assert_called_with(
        ["ffmpeg", "-i", input_file, output_file],
        capture_output=True,
        text=True,
    )

    gui._logger.add_entry.assert_called_once_with(
        input_file,
        output_file,
        True,
    )
