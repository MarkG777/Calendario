from __future__ import annotations

import re
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.repositories import BorrowerRepository
from domain.entities import Borrower
from ui.map_dialog import MapDialog


class BorrowerDialog(QDialog):
    def __init__(
        self,
        borrower: Borrower | None = None,
        read_only: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._editing_borrower = borrower
        self._read_only = read_only
        if read_only:
            self.setWindowTitle("👁️ Ver cliente/deudor")
        elif borrower:
            self.setWindowTitle("✏️ Editar cliente/deudor")
        else:
            self.setWindowTitle("➕ Nuevo cliente/deudor")
        self._latitude: float | None = borrower.latitude if borrower else None
        self._longitude: float | None = borrower.longitude if borrower else None

        self.name_input = QLineEdit(borrower.name if borrower else "")
        self.name_input.setToolTip("Nombre completo del cliente (obligatorio)")
        self.name_input.setReadOnly(read_only)

        self.phone_input = QLineEdit(borrower.phone if borrower else "")
        self.phone_input.setToolTip(
            "Numero de telefono de contacto (10 digitos)"
        )
        self.phone_input.setMaxLength(10)
        self.phone_input.setReadOnly(read_only)
        if not read_only:
            self.phone_input.textChanged.connect(self._validate_phone)

        self._phone_counter = QLabel("0 / 10 digitos")
        self._phone_counter.setStyleSheet("font-size: 9pt; color: #64748b;")
        self._phone_counter.setAlignment(Qt.AlignRight)

        self.address_input = QLineEdit(borrower.address if borrower else "")
        self.address_input.setToolTip("Direccion del cliente (escrita o del mapa)")
        self.address_input.setReadOnly(read_only)
        if not read_only:
            self.address_input.textChanged.connect(self._on_address_changed)

        self.map_button = QPushButton("📍 Seleccionar ubicacion")
        self.map_button.setToolTip("Seleccionar o cambiar ubicacion en el mapa")
        self.map_button.clicked.connect(self._open_map)
        if read_only:
            self.map_button.setText("📍 Ver mapa")
            self.map_button.setToolTip("Ver ubicacion del cliente en mapa")
            self.map_button.setEnabled(
                self._latitude is not None and self._longitude is not None
            )
        elif self._latitude is not None and self._longitude is not None:
            self.map_button.setText("📍 Cambiar ubicacion")
            self.map_button.setToolTip("Abrir mapa para cambiar la ubicacion")

        self._coords_label = QLabel("Coordenadas: no seleccionadas")
        if self._latitude is not None and self._longitude is not None:
            self._coords_label.setText(
                f"Coordenadas: {self._latitude:.5f}, {self._longitude:.5f}"
            )

        self._map_hint = QLabel(
            "Puedes escribir la direccion y/o seleccionar la ubicacion en el mapa. "
            "Ambas se guardan juntas."
        )
        self._map_hint.setStyleSheet(
            "font-size: 9pt; color: #64748b; font-style: italic;"
        )
        self._map_hint.setWordWrap(True)

        address_row = QHBoxLayout()
        address_row.addWidget(self.address_input, 1)
        address_row.addWidget(self.map_button)

        self.notes_input = QLineEdit(borrower.notes if borrower else "")
        self.notes_input.setToolTip("Notas internas sobre el cliente")
        self.notes_input.setReadOnly(read_only)

        form = QFormLayout()
        form.addRow("Nombre*:", self.name_input)
        form.addRow("Telefono*:", self.phone_input)
        form.addRow("", self._phone_counter)
        form.addRow("Direccion:", address_row)
        form.addRow(self._coords_label)
        form.addRow(self._map_hint)
        form.addRow("Notas:", self.notes_input)

        if read_only:
            buttons = QDialogButtonBox(QDialogButtonBox.Close)
            buttons.rejected.connect(self.reject)
        else:
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self._on_accept)
            buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _validate_phone(self) -> None:
        text = self.phone_input.text()
        # Only allow digits
        clean = re.sub(r"[^\d]", "", text)
        if clean != text:
            self.phone_input.blockSignals(True)
            self.phone_input.setText(clean)
            self.phone_input.blockSignals(False)
        count = len(clean)
        if count == 10:
            self.phone_input.setProperty("cssClass", "")
            self._phone_counter.setText("10 / 10 digitos ✓")
            self._phone_counter.setStyleSheet("font-size: 9pt; color: #22c55e; font-weight: 600;")
        elif count == 0:
            self.phone_input.setProperty("cssClass", "invalid")
            self._phone_counter.setText("0 / 10 digitos")
            self._phone_counter.setStyleSheet("font-size: 9pt; color: #64748b;")
        else:
            self.phone_input.setProperty("cssClass", "invalid")
            self._phone_counter.setText(f"{count} / 10 digitos — faltan {10 - count}")
            self._phone_counter.setStyleSheet("font-size: 9pt; color: #ef4444; font-weight: 600;")
        self.phone_input.style().unpolish(self.phone_input)
        self.phone_input.style().polish(self.phone_input)

    def _on_address_changed(self) -> None:
        if self._read_only:
            return
        has_coords = self._latitude is not None and self._longitude is not None
        if has_coords:
            self.map_button.setText("📍 Cambiar ubicacion")
            self.map_button.setToolTip("Abrir mapa para cambiar la ubicacion")
        else:
            self.map_button.setText("📍 Seleccionar ubicacion")
            self.map_button.setToolTip("Seleccionar ubicacion en el mapa")

    def _open_map(self) -> None:
        dialog = MapDialog(
            latitude=self._latitude,
            longitude=self._longitude,
            parent=self,
        )
        if self._read_only:
            dialog.exec()
            return
        if dialog.exec() == QDialog.Accepted:
            self._latitude = dialog.latitude
            self._longitude = dialog.longitude
            if self._latitude is not None and self._longitude is not None:
                self._coords_label.setText(
                    f"Coordenadas: {self._latitude:.5f}, {self._longitude:.5f}"
                )
                if dialog.reverse_address:
                    self.address_input.setText(dialog.reverse_address)
                self.map_button.setText("📍 Cambiar ubicacion")
                self.map_button.setToolTip("Abrir mapa para cambiar la ubicacion")

    def _on_accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self, "Falta el nombre", "El nombre del cliente es obligatorio."
            )
            self.name_input.setFocus()
            return
        phone = self.phone_input.text().strip()
        if not phone:
            QMessageBox.warning(
                self, "Falta el telefono", "El telefono del cliente es obligatorio."
            )
            self.phone_input.setFocus()
            return
        if len(re.sub(r"[^\d]", "", phone)) != 10:
            QMessageBox.warning(
                self,
                "Telefono invalido",
                "El telefono debe tener exactamente 10 digitos.",
            )
            self.phone_input.setFocus()
            return
        self.accept()

    def borrower(self) -> Borrower:
        address = self.address_input.text().strip()
        if self._editing_borrower is not None:
            return Borrower(
                id=self._editing_borrower.id,
                name=self.name_input.text().strip(),
                phone=self.phone_input.text().strip(),
                address=address,
                notes=self.notes_input.text().strip(),
                latitude=self._latitude,
                longitude=self._longitude,
                active=self._editing_borrower.active,
                created_at=self._editing_borrower.created_at,
            )
        return Borrower(
            name=self.name_input.text().strip(),
            phone=self.phone_input.text().strip(),
            address=address,
            notes=self.notes_input.text().strip(),
            latitude=self._latitude,
            longitude=self._longitude,
            created_at=date.today(),
        )


class BorrowersTab(QWidget):
    def __init__(
        self, borrower_repository: BorrowerRepository, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._repository = borrower_repository
        self._borrowers: list[Borrower] = []

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Nombre", "Telefono", "Direccion", "Estado", "Acciones"]
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setTextElideMode(Qt.ElideNone)

        new_button = QPushButton("➕ Nuevo cliente/deudor")
        new_button.setToolTip("Crear un nuevo cliente/deudor (Ctrl+N)")
        new_button.clicked.connect(self._open_new_borrower_dialog)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("🔍 Buscar por nombre o telefono...")
        self._search_input.setToolTip(
            "Escribe para filtrar clientes por nombre o telefono"
        )
        self._search_input.textChanged.connect(self._filter_table)

        buttons_row = QHBoxLayout()
        buttons_row.addWidget(new_button)
        buttons_row.addStretch()
        buttons_row.addWidget(self._search_input, 1)

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

            address = borrower.address or ""
            coords = ""
            if borrower.latitude is not None and borrower.longitude is not None:
                coords = f"Lat: {borrower.latitude:.5f}, Lng: {borrower.longitude:.5f}"
            if address and coords:
                self.table.setItem(row, 2, QTableWidgetItem(f"{address}\n{coords}"))
            elif address:
                self.table.setItem(row, 2, QTableWidgetItem(address))
            elif coords:
                self.table.setItem(row, 2, QTableWidgetItem(coords))
            else:
                self.table.setItem(row, 2, QTableWidgetItem(""))

            status_item = QTableWidgetItem()
            if borrower.active:
                status_item.setText("Activo")
                status_item.setForeground(QColor("#22c55e"))
            else:
                status_item.setText("Bloqueado")
                status_item.setForeground(QColor("#ef4444"))
            font = status_item.font()
            font.setBold(True)
            status_item.setFont(font)
            self.table.setItem(row, 3, status_item)

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(6)

            view_button = QPushButton("Ver")
            view_button.setToolTip("Ver datos del cliente (solo lectura)")
            view_button.setProperty("cssClass", "secondary")
            view_button.setFixedHeight(32)
            view_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            view_button.setMinimumWidth(0)
            view_button.clicked.connect(
                lambda _checked, r=row: self._open_view_borrower_dialog(r)
            )

            edit_button = QPushButton("Editar")
            edit_button.setToolTip("Editar datos del cliente")
            edit_button.setFixedHeight(32)
            edit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            edit_button.setMinimumWidth(0)
            edit_button.clicked.connect(
                lambda _checked, r=row: self._open_edit_borrower_dialog(r)
            )

            toggle_label = "Bloquear" if borrower.active else "Activar"
            toggle_button = QPushButton(toggle_label)
            toggle_button.setToolTip(
                "Bloquear cliente" if borrower.active else "Activar cliente"
            )
            toggle_button.setFixedHeight(32)
            toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            toggle_button.setMinimumWidth(0)
            toggle_button.setCheckable(True)
            toggle_button.setChecked(not borrower.active)
            if borrower.active:
                toggle_button.setStyleSheet(
                    "QPushButton { color: #ef4444; border: 1px solid #ef4444;"
                    " border-radius: 4px; }"
                    "QPushButton:hover { background-color: #fef2f2; }"
                )
            else:
                toggle_button.setStyleSheet(
                    "QPushButton { color: #22c55e; border: 1px solid #22c55e;"
                    " border-radius: 4px; }"
                    "QPushButton:hover { background-color: #f0fdf4; }"
                )
            toggle_button.clicked.connect(
                lambda _checked, r=row: self._toggle_borrower(r)
            )

            actions_layout.addWidget(view_button, 1)
            actions_layout.addWidget(edit_button, 1)
            actions_layout.addWidget(toggle_button, 2)
            self.table.setCellWidget(row, 4, actions_widget)

    def _filter_table(self) -> None:
        query = self._search_input.text().strip().lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            phone_item = self.table.item(row, 1)
            name = name_item.text().lower() if name_item else ""
            phone = phone_item.text().lower() if phone_item else ""
            visible = query in name or query in phone
            self.table.setRowHidden(row, not visible)

    def open_new_borrower_dialog(self) -> None:
        self._open_new_borrower_dialog()

    def _open_new_borrower_dialog(self) -> None:
        dialog = BorrowerDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self._repository.add(dialog.borrower())
            except Exception as error:
                QMessageBox.critical(
                    self, "No se pudo guardar el cliente", str(error)
                )
                return
            self.refresh()

    def _open_edit_borrower_dialog(self, row: int) -> None:
        borrower = self._borrowers[row]
        dialog = BorrowerDialog(borrower=borrower, parent=self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self._repository.update(dialog.borrower())
            except Exception as error:
                QMessageBox.critical(
                    self, "No se pudo actualizar el cliente", str(error)
                )
                return
            self.refresh()

    def _open_view_borrower_dialog(self, row: int) -> None:
        borrower = self._borrowers[row]
        dialog = BorrowerDialog(borrower=borrower, read_only=True, parent=self)
        dialog.exec()

    def _toggle_borrower(self, row: int) -> None:
        borrower = self._borrowers[row]
        new_active = not borrower.active
        action = "bloquear" if not new_active else "activar"
        reply = QMessageBox.question(
            self,
            f"{action.capitalize()} cliente",
            f"¿Seguro que deseas {action} a \"{borrower.name}\"?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            self.refresh()
            return
        try:
            self._repository.set_active(borrower.id, new_active)
        except Exception as error:
            QMessageBox.critical(
                self, f"No se pudo {action} el cliente", str(error)
            )
            return
        self.refresh()
