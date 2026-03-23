"""A GUI for FFMPEG
"""

__authors__ = "Benjamin Arent", "Christain Tuttle"
__data__ = "3/10/2026"

from PySide6 import QtCore, QtWidgets
import sys
import subprocess


class FfmpegGui(QtWidgets.QWidget):
    """The GUI for ffmpeg

    Args:
            QtWidgets (_type_): Parent class to create a GUI
    """
    _instance: "FfmpegGui | None" = None  # Singleton

    def __new__(cls) -> "FfmpegGui":
        """Create a new GUI
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialization of the GUI
        """
        super().__init__()
        self.input_text = QtWidgets.QLabel('Input', self)
        self.input = QtWidgets.QLineEdit(self)
        self.input_file = QtWidgets.QPushButton(self)
        self.input_file.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton))
        self.output_text = QtWidgets.QLabel('Output', self)
        self.output = QtWidgets.QLineEdit()
        self.output_format = QtWidgets.QComboBox()
        self.ffmpeg = subprocess.run(
            ['ffmpeg', '-formats'], capture_output=True, text=True)
        self.supported_inputs: str = 'Supported Files ('
        for i in self.ffmpeg.stdout.split('\n')[5:]:
            try:
                types = i[4::].split()[0].split(',')
                for o in types:
                    newtype = o.rsplit('_', 1)[0]
                    if i[1] == 'D':
                        self.supported_inputs += '*.' + newtype + ' '
                    if i[2] == 'E':
                        self.output_format.addItem('.' + newtype)
            except IndexError:
                pass
        self.supported_inputs = self.supported_inputs[:-1] + ')'
        self.convert = QtWidgets.QPushButton("Convert")
        self.primary = QtWidgets.QVBoxLayout(self)
        self.input_box = QtWidgets.QHBoxLayout(self)
        self.input_box.addWidget(self.input)
        self.input_box.addWidget(self.input_file)
        self.output_box = QtWidgets.QHBoxLayout(self)
        self.output_box.addWidget(self.output)
        self.output_box.addWidget(self.output_format)
        self.primary.addWidget(self.input_text)
        self.primary.addLayout(self.input_box)
        self.primary.addWidget(self.output_text)
        self.primary.addLayout(self.output_box)
        self.primary.addWidget(self.convert)
        self.input_file.clicked.connect(self.promptinputfile)
        self.convert.clicked.connect(self.beginconversion)

    def enable(self) -> None:
        """Shows the GUI
        """
        self.resize(800, 600)
        self.show()

    @QtCore.Slot()
    def beginconversion(self) -> None:
        """Attempts the conversion
        """

    @QtCore.Slot()
    def promptinputfile(self) -> None:
        """Let's the user find a file via the file explorer
        """
        fileprompt = QtWidgets.QFileDialog()
        fileprompt.setNameFilter(self.supported_inputs)
        fileprompt.exec()
        try:
            file = fileprompt.selectedFiles()[0]
            self.input.setText(file)
            self.output.setText(file.rsplit('.', 1)[0])
        except IndexError:
            pass

    @staticmethod
    def main() -> None:
        """The main function for the GUI
        """
        app = QtWidgets.QApplication([])
        gui = FfmpegGui()
        gui.enable()
        sys.exit(app.exec())


if __name__ == "__main__":
    FfmpegGui.main()
