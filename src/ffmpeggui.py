"""A GUI for FFMPEG
"""
from PySide6 import QtCore, QtWidgets
from conversionlog import ConversionLog
from errout import ErrorOut
from installer import Installer
import subprocess
import sys
from alive_progress import alive_bar
print("RUNNING THIS EXACT FILE", flush=True)
__authors__ = "Benjamin Arent", "Christian Tuttle"
__created__ = "3/10/2026"
__updated__ = "5/01/2026"


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
        # Check if FFmpeg is installed
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        if result.returncode != 0:
            Installer()
        self._logger = ConversionLog()
        self._main_layout = QtWidgets.QVBoxLayout(self)
        self._top_bar = QtWidgets.QHBoxLayout()
        self._top_bar.addStretch()
        self._log_button = QtWidgets.QPushButton("View Logs")
        self._log_button.clicked.connect(
            lambda: self._logger.show_window(self)
        )
        self._top_bar.addWidget(self._log_button)
        self._main_layout.addLayout(self._top_bar)
        # Input Section
        self._input_label = QtWidgets.QLabel('Input')
        self._input_text = QtWidgets.QLineEdit()
        self._input_dialog = QtWidgets.QPushButton(self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_DialogOpenButton), '')
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
        print('Getting supported inputs...')
        all_formats = subprocess.run(
            ['ffmpeg', '-formats'], capture_output=True, text=True)
        unclean_formats: list[str] = []
        for line in all_formats.stdout.splitlines()[5::]:
            stripped_line = line.strip()

            if stripped_line[0] != 'D':
                continue

            format_section = stripped_line[4::]
            format_parts = format_section.split(' ')[0].split(',')

            for o in format_parts:
                unclean_formats.append(o)
        unclean_formats = list(dict.fromkeys(unclean_formats))
        input_formats: list[str] = []
        with alive_bar(len(unclean_formats)) as bar:
            for i in unclean_formats:
                support = subprocess.run(
                    ["ffmpeg", "-h", f"demuxer={i}"],
                    capture_output=True,
                    text=True,
                )

                try:
                    ext_line = support.stdout.splitlines()[1]
                except IndexError:
                    bar()
                    continue

                ext_parts = ext_line.strip().split()

                if not ext_parts:
                    bar()
                    continue

                if ext_parts[0] == "Common":
                    ext_list = ext_parts[2].split(",")

                    for o in ext_list:
                        input_formats.append(o.strip("."))

                elif len(ext_parts) > 1 and ext_parts[1] == "demuxer":
                    input_formats.append(i.rsplit("_")[0])

                input_formats = list(dict.fromkeys(input_formats))
                bar()
        return input_formats

    def supported_outputs(self) -> list[str]:
        """Makes a list of all supported output extensions

        Returns:
            list[str]: All supported output extensions
        """
        print('Getting supported outputs...')
        all_formats = subprocess.run(
            ['ffmpeg', '-formats'], capture_output=True, text=True)
        unclean_formats: list[str] = []
        for line in all_formats.stdout.splitlines()[5::]:
            stripped_line = line.strip()
            if stripped_line[1] != 'E':
                continue
            format_parts = stripped_line[4::].rsplit()
            for o in format_parts:
                unclean_formats.append(o)
        unclean_formats = list(dict.fromkeys(unclean_formats))
        output_formats: list[str] = []
        with alive_bar(len(unclean_formats)) as bar:
            for i in unclean_formats:
                support = subprocess.run(
                    ["ffmpeg", "-h", f"muxer={i}"],
                    capture_output=True,
                    text=True,
                )

                try:
                    ext_line = support.stdout.splitlines()[1]
                except IndexError:
                    bar()
                    continue

                ext_parts = ext_line.strip().split()

                if not ext_parts:
                    bar()
                    continue

                if ext_parts[0] != "Common":
                    bar()
                    continue

                ext_list = ext_parts[2].split(",")[:-1]

                if ext_list:
                    for o in ext_list:
                        output_formats.append(o.strip("."))
                else:
                    output_formats.append(ext_parts[2].strip("."))

                bar()
        return sorted(list(dict.fromkeys(output_formats)))

    def enable(self) -> None:
        """Shows the GUI
        """
        self.show()

    @QtCore.Slot()
    def beginconversion(self) -> None:
        """Attempts the conversion
        """
        input_file = self._input_text.text()
        output_file = (
            self._output_text.text() +
            self._output_extension.itemText(
                self._output_extension.currentIndex()
            )
        )

        output = subprocess.run(
            ['ffmpeg', '-i', input_file, output_file],
            capture_output=True,
            text=True
        )

        if output.returncode != 0:
            error_message = '\n'.join(output.stderr.splitlines()[18:])
            self._logger.add_entry(
                input_file,
                output_file,
                False,
                error_message
            )
            ErrorOut(error_message)
        else:
            self._logger.add_entry(input_file, output_file, True)

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
        app = QtWidgets.QApplication([])
        gui = FfmpegGui()
        gui.enable()
        sys.exit(app.exec())


if __name__ == "__main__":
    print("ENTERING __main__", flush=True)
    FfmpegGui.main()
