import sys
from PySide6 import QtCore, QtWidgets
import subprocess


class Installer(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        if True:
            notin = QtWidgets.QMessageBox()
            notin.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            notin.setText("Error")
            notin.setInformativeText(
                "Please install FFmpeg to continue."
            )
            notin.setWindowTitle("FFmpeg Not Found")

            install_button = notin.addButton(
                "Install FFmpeg",
                QtWidgets.QMessageBox.ButtonRole.AcceptRole
            )
            close_button = notin.addButton(
                QtWidgets.QMessageBox.StandardButton.Close
            )

            notin.exec()

            if notin.clickedButton() == install_button:
                self.installffmpeg()
            elif notin.clickedButton() == close_button:
                sys.exit()

    def installffmpeg(self) -> None:
        platform_identifier = sys.platform

        if platform_identifier.startswith("win"):
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Installing")
            msg.setText("You're using Windows. Please install FFmpeg manually.")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.exec()

        elif platform_identifier == "linux":
            msg = QtWidgets.QProgressDialog("Installing FFmpeg...", None, 0, 0)
            msg.setWindowTitle("Installing")
            msg.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            msg.show()
            QtWidgets.QApplication.processEvents()

            subprocess.run(["sudo", "apt", "install", "ffmpeg", "-y"])
            msg.close()

        elif platform_identifier == "darwin":
            msg = QtWidgets.QProgressDialog("Installing FFmpeg...", None, 0, 0)
            msg.setWindowTitle("Installing")
            msg.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            msg.show()
            QtWidgets.QApplication.processEvents()

            subprocess.run(["brew", "install", "ffmpeg"])
            msg.close()