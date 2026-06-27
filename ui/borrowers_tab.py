from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.repositories import BorrowerRepository
from domain.entities import Borrower


class BorrowerDialog(QDialog):
    def __init__(self, borrower: Borrower | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._editing_borrower = borrower
        self.setWindowTitle("Editar deudor" if borrower else "Nuevo deudor")

        self.name_input = QLineEdit(borrower.name if borrower else "")
        self.phone_input = QLineEdit(borrower.phone if borrower else "")
        self.address_input = QLineEdit(borrower.address if borrower else "")
        self.notes_input = QLineEdit(borrower.notes if borrower else "")

        form = QFormLayout()
        form.addRow("Nombre*:", self.name_input)
        form.addRow("Teléfono:", self.phone_input)
        form.addRow("Dirección:", self.address_input)
        form.addRow("Notas:", self.notes_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Falta el nombre", "El nombre del deudor es obligatorio.")
            self.name_input.setFocus()
            return
        self.accept()

    def borrower(self) -> Borrower:
        if self._editing_borrower is not None:
            return Borrower(
                id=self._editing_borrower.id,
                name=self.name_input.text().strip(),
                phone=self.phone_input.text().strip(),
                address=self.address_input.text().strip(),
                notes=self.notes_input.text().strip(),
                created_at=self._editing_borrower.created_at,
            )
        return Borrower(
            name=self.name_input.text().strip(),
            phone=self.phone_input.text().strip(),
            address=self.address_input.text().strip(),
            notes=self.notes_input.text().strip(),
            created_at=date.today(),
        )


class BorrowersTab(QWidget):
    def __init__(
        self, borrower_repository: BorrowerRepository, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._repository = borrower_repository
        self._borrowers: list[Borrower] = []

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nombre", "Teléfono", "Dirección", ""])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        new_button = QPushButton("Nuevo deudor")
        new_button.clicked.connect(self._open_new_borrower_dialog)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(new_button)
        buttons_row.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(buttons_row)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        self._borrowers = self._repository.list_all()
        self.table.setRowCount(len(self._borrowers))
        for row, borrower in enumerate(self._borrowers):
            self.table.setItem(row, 0, QTableWidgetItem(borrower.name))
            self.table.setItem(row, 1, QTableWidgetItem(borrower.phone))
            self.table.setItem(row, 2, QTableWidgetItem(borrower.address))

            edit_button = QPushButton("Editar")
            edit_button.clicked.connect(lambda _checked, r=row: self._open_edit_borrower_dialog(r))
            self.table.setCellWidget(row, 3, edit_button)

    def _open_new_borrower_dialog(self) -> None:
        dialog = BorrowerDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self._repository.add(dialog.borrower())
            except Exception as error:
                QMessageBox.critical(self, "No se pudo guardar el deudor", str(error))
                return
            self.refresh()

    def _open_edit_borrower_dialog(self, row: int) -> None:
        borrower = self._borrowers[row]
        dialog = BorrowerDialog(borrower=borrower, parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self._repository.update(dialog.borrower())
            except Exception as error:
                QMessageBox.critical(self, "No se pudo actualizar el deudor", str(error))
                return
            self.refresh()
