"""A GUI for FFMPEG
"""

__authors__ = "Benjamin Arent", "Christain Tuttle"
__created__ = "3/10/2026"
__updated__ = "4/16/2026"

from PySide6 import QtCore, QtWidgets
import sys
import subprocess
from installer import Installer
from errout import ErrorOut


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
        super().__init__()
        self._main_layout = QtWidgets.QVBoxLayout(self)
        # Input Section
        self._input_label = QtWidgets.QLabel('Input')
        self._input_text = QtWidgets.QLineEdit()
        self._input_dialog = QtWidgets.QPushButton(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton), '')
        self._input_dialog.clicked.connect(self.promptinputfile)
        self._input_horizontal = QtWidgets.QHBoxLayout()
        self._input_horizontal.addWidget(self._input_text)
        self._input_horizontal.addWidget(self._input_dialog)
        self._input_vertical = QtWidgets.QVBoxLayout()
        self._input_vertical.addWidget(self._input_label)
        self._input_vertical.addLayout(self._input_horizontal)
        # Output Section
        self._output_label = QtWidgets.QLabel('Output')
        self._output_text = QtWidgets.QLineEdit()
        self._output_extension = QtWidgets.QComboBox()
        self._output_horizontal = QtWidgets.QHBoxLayout()
        self._output_horizontal.addWidget(self._output_text)
        self._output_horizontal.addWidget(self._output_extension)
        self._output_vertical = QtWidgets.QVBoxLayout()
        self._output_vertical.addWidget(self._output_label)
        self._output_vertical.addLayout(self._output_horizontal)
        # Main Setup
        self._convert_button = QtWidgets.QPushButton('Convert')
        self._convert_button.clicked.connect(self.beginconversion)
        self._main_layout.addLayout(self._input_vertical)
        self._main_layout.addLayout(self._output_vertical)
        self._main_layout.addWidget(self._convert_button)
        self._supported_inputs: str = 'Supported Files ('
        for i in self.supported_inputs():
            self._supported_inputs += '*.' + i + ' '
        self._supported_inputs = self._supported_inputs[:-1] + ')'
        for i in self.supported_outputs():
            self._output_extension.addItem("." + i)

    def supported_inputs(self) -> list[str]:
        """Gets all supported input extensions

        Returns:
            list[str]: The full list of extensions
        """
        all_formats = subprocess.run(
            ['ffmpeg', '-formats'], capture_output=True, text=True)
        unclean_formats: list[str] = []
        for i in all_formats.stdout.splitlines()[5::]:
            i = i.strip()
            if i[0] != 'D':
                continue
            i = i[4::]
            i = i.split(' ')[0].split(',')
            for o in i:
                unclean_formats.append(o)
        unclean_formats = list(dict.fromkeys(unclean_formats))
        input_formats: list[str] = []
        for i in unclean_formats:
            support = subprocess.run(
                ['ffmpeg', '-h', f'demuxer={i}'], capture_output=True, text=True)
            try:
                ext = support.stdout.splitlines()[1]
            except IndexError:
                continue
            ext = ext.strip().split()
            if not ext:
                continue
            if ext[0] == 'Common':
                ext_list = ext[2].split(',')
                if len(ext_list) > 0:
                    for o in ext_list:
                        input_formats.append(o.strip('.'))
                else:
                    input_formats.append(ext[2].strip('.'))
            elif ext[1] == 'demuxer':
                input_formats.append(i.rsplit('_')[0])
            input_formats = list(dict.fromkeys(input_formats))
        return input_formats

    def supported_outputs(self) -> list[str]:
        """Makes a list of all supported output extensions

        Returns:
            list[str]: All supported output extensions
        """
        all_formats = subprocess.run(
            ['ffmpeg', '-formats'], capture_output=True, text=True)
        unclean_formats: list[str] = []
        for i in all_formats.stdout.splitlines()[5::]:
            i = i.strip()
            if i[1] != 'E':
                continue
            i = i[4::].rsplit()
            for o in i:
                unclean_formats.append(o)
        unclean_formats = list(dict.fromkeys(unclean_formats))
        output_formats: list[str] = []
        for i in unclean_formats:
            support = subprocess.run(
                ['ffmpeg', '-h', f'muxer={i}'], capture_output=True, text=True)
            try:
                ext = support.stdout.splitlines()[1]
            except IndexError:
                continue
            ext = ext.strip().split()
            if not ext:
                continue
            if ext[0] != 'Common':
                continue
            ext_list = ext[2].split(',')[:-1]
            if len(ext_list) > 0:
                for o in ext_list:
                    output_formats.append(o.strip('.'))
            else:
                output_formats.append(ext[2].strip('.'))
        return sorted(list(dict.fromkeys(output_formats)))

    def enable(self) -> None:
        """Shows the GUI
        """
        self.show()

    @QtCore.Slot()
    def beginconversion(self) -> None:
        """Attempts the conversion
        """
        output = subprocess.run(['ffmpeg', '-i', self._input_text.text(),
                                 self._output_text.text() +
                                 self._output_extension.itemText(self._output_extension.currentIndex())],
                                capture_output=True, text=True)
        if output.returncode != 0:
            ErrorOut('\n'.join(output.stderr.splitlines()[18:]))

    @QtCore.Slot()
    def promptinputfile(self) -> None:
        """Let's the user find a file via the file explorer
        """
        fileprompt = QtWidgets.QFileDialog()
        fileprompt.setNameFilter(self._supported_inputs)
        fileprompt.exec()
        try:
            file = fileprompt.selectedFiles()[0]
            self._input_text.setText(file)
            self._output_text.setText(file.rsplit('.', 1)[0])
        except IndexError:
            pass

    @staticmethod
    def main() -> None:
        """The main function for the GUI
        """
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        if result.returncode != 0:
            installer = Installer()
        app = QtWidgets.QApplication([])
        gui = FfmpegGui()
        gui.enable()
        sys.exit(app.exec())


if __name__ == "__main__":
    FfmpegGui.main()
