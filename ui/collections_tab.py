from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, QLocale
from PySide6.QtGui import QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from data.export import build_payment_records, export_to_csv, export_to_excel
from data.repositories import (
    BorrowerRepository,
    InstallmentRepository,
    LoanRepository,
    PaymentRepository,
)
from domain.calculations import installment_status, outstanding_balance
from domain.enums import InstallmentStatus
from ui.icons import icon
from ui.payment_dialog import PaymentDialog
from ui.status_colors import (
    status_background,
    status_foreground,
    worst_status,
)


class CollectionsTab(QWidget):
    def __init__(
        self,
        installment_repository: InstallmentRepository,
        loan_repository: LoanRepository,
        borrower_repository: BorrowerRepository,
        payment_repository: PaymentRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._installment_repository = installment_repository
        self._loan_repository = loan_repository
        self._borrower_repository = borrower_repository
        self._payment_repository = payment_repository
        self._marked_dates: set[date] = set()
        self._history_records: list = []

        self.calendar = QCalendarWidget()
        self.calendar.setLocale(QLocale(QLocale.Spanish))
        self.calendar.setGridVisible(True)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.clicked.connect(self._on_date_selected)

        self.day_label = QLabel()
        self.day_table = self._build_table()

        calendar_view = QWidget()
        calendar_layout = QVBoxLayout(calendar_view)
        calendar_layout.addWidget(self.calendar)
        calendar_layout.addWidget(self.day_label)
        calendar_layout.addWidget(self.day_table)

        self.upcoming_label = QLabel("Próximos cobros (los más cercanos primero)")
        self.upcoming_table = self._build_table()

        upcoming_view = QWidget()
        upcoming_layout = QVBoxLayout(upcoming_view)
        upcoming_layout.addWidget(self.upcoming_label)
        upcoming_layout.addWidget(self.upcoming_table)

        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(
            ["Deudor", "Fecha de pago", "Monto pagado", "Método"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.verticalHeader().setVisible(False)

        export_csv_button = QPushButton(icon("export", "#ffffff"), "Exportar a CSV")
        export_csv_button.setToolTip("Exportar el historial de cobros a un archivo CSV")
        export_csv_button.clicked.connect(self._export_history_csv)
        export_excel_button = QPushButton(icon("export", "#ffffff"), "Exportar a Excel")
        export_excel_button.setToolTip("Exportar el historial de cobros a un archivo Excel")
        export_excel_button.clicked.connect(self._export_history_excel)

        export_buttons_row = QHBoxLayout()
        export_buttons_row.addWidget(export_csv_button)
        export_buttons_row.addWidget(export_excel_button)
        export_buttons_row.addStretch()

        history_view = QWidget()
        history_layout = QVBoxLayout(history_view)
        history_layout.addWidget(QLabel("Historial de cobros (más recientes primero)"))
        history_layout.addWidget(self.history_table)
        history_layout.addLayout(export_buttons_row)

        views = QTabWidget()
        views.addTab(calendar_view, "Vista de calendario")
        views.addTab(upcoming_view, "Vista de consulta")
        views.addTab(history_view, "Historial de cobros")

        layout = QVBoxLayout(self)
        layout.addWidget(views)

        self.refresh()

    @staticmethod
    def _build_table() -> QTableWidget:
        table = QTableWidget(0, 6)
        table.setHorizontalHeaderLabels(
            ["Deudor", "Fecha", "Monto programado", "Saldo pendiente", "Estado", ""]
        )
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        return table

    def refresh(self) -> None:
        self._mark_calendar_days()
        self._show_day(self.calendar.selectedDate().toPython())
        self._show_upcoming()
        self._show_history()

    def _mark_calendar_days(self) -> None:
        today = date.today()
        all_installments = self._installment_repository.list_all()

        statuses_by_day: dict[date, list] = {}
        for installment in all_installments:
            status = installment_status(installment, today)
            statuses_by_day.setdefault(installment.due_date, []).append(status)

        blank_format = QTextCharFormat()
        for old_date in self._marked_dates:
            self.calendar.setDateTextFormat(QDate(old_date), blank_format)

        for due_date, statuses in statuses_by_day.items():
            fmt = QTextCharFormat()
            worst = worst_status(statuses)
            fmt.setBackground(status_background(worst))
            fmt.setForeground(status_foreground(worst))
            fmt.setFontWeight(700)
            self.calendar.setDateTextFormat(QDate(due_date), fmt)

        self._marked_dates = set(statuses_by_day.keys())

    def _on_date_selected(self, qdate: QDate) -> None:
        self._show_day(qdate.toPython())

    def _show_day(self, day: date) -> None:
        self.day_label.setText(f"Cobros del {day.isoformat()}")
        installments = self._installment_repository.list_due_between(day, day)
        self._populate_table(self.day_table, installments)

    def _show_upcoming(self) -> None:
        today = date.today()
        all_installments = self._installment_repository.list_all()
        upcoming = [
            i for i in all_installments if installment_status(i, today) != InstallmentStatus.PAGADO
        ]
        upcoming.sort(key=lambda i: i.due_date)
        self._populate_table(self.upcoming_table, upcoming)

    def _show_history(self) -> None:
        borrower_by_loan_id = self._borrower_name_by_loan_id()
        all_installments = self._installment_repository.list_all()
        self._history_records = build_payment_records(all_installments, borrower_by_loan_id)

        self.history_table.setRowCount(len(self._history_records))
        for row, record in enumerate(self._history_records):
            self.history_table.setItem(row, 0, QTableWidgetItem(record.borrower_name))
            self.history_table.setItem(
                row, 1, QTableWidgetItem(record.payment_date.isoformat())
            )
            self.history_table.setItem(row, 2, QTableWidgetItem(str(record.amount_paid)))
            self.history_table.setItem(row, 3, QTableWidgetItem(record.method))

    def _export_history_csv(self) -> None:
        self._export_history(export_to_csv, "CSV (*.csv)", ".csv")

    def _export_history_excel(self) -> None:
        self._export_history(export_to_excel, "Excel (*.xlsx)", ".xlsx")

    def _export_history(self, export_fn, filter_text: str, default_suffix: str) -> None:
        if not self._history_records:
            QMessageBox.information(
                self, "Sin datos", "Todavía no hay cobros registrados para exportar."
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar historial de cobros", f"historial_cobros{default_suffix}", filter_text
        )
        if not path:
            return
        if not path.endswith(default_suffix):
            path += default_suffix

        try:
            export_fn(self._history_records, path)
        except Exception as error:
            QMessageBox.critical(self, "No se pudo exportar", str(error))
            return
        QMessageBox.information(self, "Exportación exitosa", f"Historial exportado a:\n{path}")

    def _populate_table(self, table: QTableWidget, installments: list) -> None:
        borrower_by_loan_id = self._borrower_name_by_loan_id()
        today = date.today()

        table.setRowCount(len(installments))
        for row, installment in enumerate(installments):
            balance = outstanding_balance(installment)
            borrower_name = borrower_by_loan_id.get(installment.loan_id, "—")
            status = installment_status(installment, today)

            table.setItem(row, 0, QTableWidgetItem(borrower_name))
            table.setItem(row, 1, QTableWidgetItem(installment.due_date.isoformat()))
            table.setItem(row, 2, QTableWidgetItem(str(installment.scheduled_amount)))
            table.setItem(row, 3, QTableWidgetItem(str(balance)))

            status_item = QTableWidgetItem(status.value)
            status_item.setBackground(status_background(status))
            status_item.setForeground(status_foreground(status))
            table.setItem(row, 4, status_item)

            collect_button = QPushButton(icon("payment", "#ffffff"), "Registrar cobro")
            collect_button.setToolTip("Registrar un pago o abono para esta cuota")
            collect_button.clicked.connect(
                lambda _checked, inst=installment: self._open_payment_dialog(inst)
            )
            table.setCellWidget(row, 5, collect_button)

    def _borrower_name_by_loan_id(self) -> dict[int, str]:
        borrower_name_by_id = {b.id: b.name for b in self._borrower_repository.list_all()}
        return {
            loan.id: borrower_name_by_id.get(loan.borrower_id, "—")
            for loan in self._loan_repository.list_all()
        }

    def _open_payment_dialog(self, installment) -> None:
        dialog = PaymentDialog(installment, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self._payment_repository.add(dialog.payment())
            except Exception as error:
                QMessageBox.critical(self, "No se pudo registrar el cobro", str(error))
                return
            self.refresh()
