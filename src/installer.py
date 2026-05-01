import subprocess
import sys
from typing import List

from PySide6 import QtCore, QtWidgets


class Installer(QtWidgets.QWidget):
    """Prompt the user to install FFmpeg if it is missing."""

    def __init__(self) -> None:
        """Initialize and show the install prompt."""
        super().__init__()
        self._prompt_install()

    def _prompt_install(self) -> None:
        """Display a message box asking the user to install FFmpeg."""
        message_box = QtWidgets.QMessageBox(self)
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        message_box.setText("FFmpeg Not Found")
        message_box.setInformativeText(
            "FFmpeg is required to use this application."
        )
        message_box.setWindowTitle("Error")

        install_button = message_box.addButton(
            "Install FFmpeg",
            QtWidgets.QMessageBox.ButtonRole.AcceptRole,
        )
        message_box.addButton(QtWidgets.QMessageBox.StandardButton.Close)

        message_box.exec()

        if message_box.clickedButton() == install_button:
            self.install_ffmpeg()
        else:
            QtWidgets.QApplication.quit()

    def install_ffmpeg(self) -> None:
        """Install FFmpeg depending on the user's operating system."""
        platform_identifier = sys.platform

        if platform_identifier.startswith("win"):
            self._show_info(
                "Manual Installation Required",
                "You're using Windows.\n"
                "Please install FFmpeg manually from:\n"
                "https://ffmpeg.org/download.html",
            )
        elif platform_identifier == "linux":
            self._run_install(["sudo", "apt", "install", "ffmpeg", "-y"])
        elif platform_identifier == "darwin":
            self._run_install(["brew", "install", "ffmpeg"])
        else:
            self._show_info(
                "Unsupported Platform",
                "Automatic installation is not supported on this system.",
            )

    def _run_install(self, command: List[str]) -> None:
        """Run an install command with a progress dialog."""
        progress = QtWidgets.QProgressDialog(
            "Installing FFmpeg...",
            "",
            0,
            0,
            self,
        )
        progress.setWindowTitle("Installing")
        progress.setWindowModality(
            QtCore.Qt.WindowModality.ApplicationModal
        )
        progress.setCancelButton(None)
        progress.show()

        QtWidgets.QApplication.processEvents()

        subprocess.run(command, check=False)

        progress.close()

        self._show_info(
            "Installation Complete",
            "FFmpeg installation finished.\n"
            "Please restart the application.",
        )

    def _show_info(self, title: str, text: str) -> None:
        """Show an informational message box."""
        message_box = QtWidgets.QMessageBox(self)
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Information)
        message_box.exec()