"""Tests for the Installer class."""

import os
import sys
from unittest.mock import MagicMock, patch

from PySide6 import QtWidgets

from installer import Installer


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def get_qapp() -> QtWidgets.QApplication:
    """Create or return the existing QApplication."""
    app = QtWidgets.QApplication.instance()

    if isinstance(app, QtWidgets.QApplication):
        return app

    return QtWidgets.QApplication(sys.argv)


def make_installer_without_prompt() -> Installer:
    """Create Installer without opening the install prompt."""
    with patch.object(Installer, "_prompt_install"):
        installer = Installer()

    return installer


def test_installer_starts_prompt() -> None:
    """Test that Installer calls _prompt_install during initialization."""
    get_qapp()

    with patch.object(Installer, "_prompt_install") as mock_prompt:
        Installer()

    mock_prompt.assert_called_once()


def test_prompt_install_runs_install_when_install_button_clicked() -> None:
    """Test that clicking Install FFmpeg calls install_ffmpeg."""
    get_qapp()

    installer = make_installer_without_prompt()

    mock_message_box = MagicMock()
    mock_install_button = MagicMock()

    mock_message_box.addButton.side_effect = [
        mock_install_button,
        MagicMock(),
    ]
    mock_message_box.clickedButton.return_value = mock_install_button

    with patch(
        "installer.QtWidgets.QMessageBox",
        return_value=mock_message_box,
    ):
        with patch.object(installer, "install_ffmpeg") as mock_install:
            installer._prompt_install()

    mock_message_box.setIcon.assert_called_once()
    mock_message_box.setText.assert_called_once_with("FFmpeg Not Found")
    mock_message_box.setInformativeText.assert_called_once_with(
        "FFmpeg is required to use this application."
    )
    mock_message_box.setWindowTitle.assert_called_once_with("Error")
    mock_message_box.exec.assert_called_once()
    mock_install.assert_called_once()


def test_prompt_install_quits_when_close_clicked() -> None:
    """Test that closing the prompt quits the application."""
    get_qapp()

    installer = make_installer_without_prompt()

    mock_message_box = MagicMock()
    mock_install_button = MagicMock()
    mock_close_button = MagicMock()

    mock_message_box.addButton.side_effect = [
        mock_install_button,
        mock_close_button,
    ]
    mock_message_box.clickedButton.return_value = mock_close_button

    with patch(
        "installer.QtWidgets.QMessageBox",
        return_value=mock_message_box,
    ):
        with patch("installer.QtWidgets.QApplication.quit") as mock_quit:
            installer._prompt_install()

    mock_quit.assert_called_once()


def test_install_ffmpeg_windows_shows_manual_install_message() -> None:
    """Test that Windows shows a manual installation message."""
    get_qapp()

    installer = make_installer_without_prompt()

    with patch("installer.sys.platform", "win32"):
        with patch.object(installer, "_show_info") as mock_show_info:
            installer.install_ffmpeg()

    mock_show_info.assert_called_once()
    args = mock_show_info.call_args.args

    assert args[0] == "Manual Installation Required"
    assert "Windows" in args[1]
    assert "https://ffmpeg.org/download.html" in args[1]


def test_install_ffmpeg_linux_runs_apt_command() -> None:
    """Test that Linux runs the apt install command."""
    get_qapp()

    installer = make_installer_without_prompt()

    with patch("installer.sys.platform", "linux"):
        with patch.object(installer, "_run_install") as mock_run_install:
            installer.install_ffmpeg()

    mock_run_install.assert_called_once_with(
        ["sudo", "apt", "install", "ffmpeg", "-y"]
    )


def test_install_ffmpeg_macos_runs_brew_command() -> None:
    """Test that macOS runs the brew install command."""
    get_qapp()

    installer = make_installer_without_prompt()

    with patch("installer.sys.platform", "darwin"):
        with patch.object(installer, "_run_install") as mock_run_install:
            installer.install_ffmpeg()

    mock_run_install.assert_called_once_with(["brew", "install", "ffmpeg"])


def test_install_ffmpeg_unsupported_platform_shows_message() -> None:
    """Test that unsupported platforms show an unsupported message."""
    get_qapp()

    installer = make_installer_without_prompt()

    with patch("installer.sys.platform", "freebsd"):
        with patch.object(installer, "_show_info") as mock_show_info:
            installer.install_ffmpeg()

    mock_show_info.assert_called_once_with(
        "Unsupported Platform",
        "Automatic installation is not supported on this system.",
    )


def test_run_install_runs_command_and_shows_complete_message() -> None:
    """Test that _run_install runs command and shows completion message."""
    get_qapp()

    installer = make_installer_without_prompt()
    command = ["brew", "install", "ffmpeg"]

    mock_progress = MagicMock()

    with patch(
        "installer.QtWidgets.QProgressDialog",
        return_value=mock_progress,
    ):
        with patch(
            "installer.QtWidgets.QApplication.processEvents"
        ) as mock_process_events:
            with patch("installer.subprocess.run") as mock_run:
                with patch.object(installer, "_show_info") as mock_show_info:
                    installer._run_install(command)

    mock_progress.setWindowTitle.assert_called_once_with("Installing")
    mock_progress.setCancelButton.assert_called_once_with(None)
    mock_progress.show.assert_called_once()
    mock_process_events.assert_called_once()
    mock_run.assert_called_once_with(command, check=False)
    mock_progress.close.assert_called_once()
    mock_show_info.assert_called_once_with(
        "Installation Complete",
        "FFmpeg installation finished.\n"
        "Please restart the application.",
    )


def test_show_info_displays_message_box() -> None:
    """Test that _show_info creates and displays an information message."""
    get_qapp()

    installer = make_installer_without_prompt()

    mock_message_box = MagicMock()

    with patch(
        "installer.QtWidgets.QMessageBox",
        return_value=mock_message_box,
    ):
        installer._show_info("Test Title", "Test message")

    mock_message_box.setWindowTitle.assert_called_once_with("Test Title")
    mock_message_box.setText.assert_called_once_with("Test message")
    mock_message_box.setIcon.assert_called_once()
    mock_message_box.exec.assert_called_once()
