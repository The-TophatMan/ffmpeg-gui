from datetime import datetime
from PySide6 import QtWidgets


class ConversionLog:
    """Stores conversion history and displays it in a window."""

    def __init__(self) -> None:
        self._logs: list[str] = []

    def add_entry(
            self,
            input_file: str,
            output_file: str,
            success: bool,
            message: str = "") -> None:
        """Add a conversion log entry."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILURE"
        entry = f"[{timestamp}] {status}: {input_file} -> {output_file}"
        if message:
            entry += f"\n{message}"

        self._logs.append(entry)

    def formatted_logs(self) -> str:
        """Return all logs as one formatted string."""
        if not self._logs:
            return "No conversions have happened yet."
        return "\n\n".join(self._logs)

    def show_window(self, parent: QtWidgets.QWidget | None = None) -> None:
        """Display the log window."""
        dialog = QtWidgets.QDialog(parent)
        dialog.setWindowTitle("Conversion Logs")
        dialog.resize(600, 400)

        layout = QtWidgets.QVBoxLayout(dialog)

        log_view = QtWidgets.QTextEdit()
        log_view.setReadOnly(True)
        log_view.setPlainText(self.formatted_logs())

        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(dialog.accept)

        layout.addWidget(log_view)
        layout.addWidget(close_button)

        dialog.exec()
