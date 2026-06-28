from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from data.repositories import BorrowerRepository, InstallmentRepository, LoanRepository
from domain.calculations import gross_profit, loan_irr
from domain.dashboard import portfolio_irr, realized_profit

ZERO = Decimal("0")


class AnalysisTab(QWidget):
    def __init__(
        self,
        loan_repository: LoanRepository,
        installment_repository: InstallmentRepository,
        borrower_repository: BorrowerRepository,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._loan_repository = loan_repository
        self._installment_repository = installment_repository
        self._borrower_repository = borrower_repository

        # ---- Summary cards ----
        self._total_principal_card = _SummaryCard("💰 Capital total prestado")
        self._total_profit_card = _SummaryCard(
            "📈 Ganancia proyectada total", value_class="card-value-success"
        )
        self._realized_card = _SummaryCard(
            "💵 Ganancia realizada", value_class="card-value-accent"
        )
        self._portfolio_irr_card = _SummaryCard(
            "📊 TIR de la cartera", value_class="card-value-accent"
        )

        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.addWidget(self._total_principal_card, 0, 0)
        cards_layout.addWidget(self._total_profit_card, 0, 1)
        cards_layout.addWidget(self._realized_card, 0, 2)
        cards_layout.addWidget(self._portfolio_irr_card, 0, 3)

        cards_container = QWidget()
        cards_container_layout = QVBoxLayout(cards_container)
        cards_container_layout.setContentsMargins(0, 0, 0, 0)
        cards_container_layout.addLayout(cards_layout)

        # ---- TIR table ----
        self._tir_table = QTableWidget(0, 4)
        self._tir_table.setHorizontalHeaderLabels(
            ["Cliente", "Capital", "Ganancia proyectada", "TIR del préstamo"]
        )
        self._tir_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._tir_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )
        self._tir_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self._tir_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )
        self._tir_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tir_table.setAlternatingRowColors(True)
        self._tir_table.verticalHeader().setVisible(False)

        tir_box = QGroupBox("📊 TIR por préstamo")
        tir_layout = QVBoxLayout()
        tir_layout.addWidget(self._tir_table)
        tir_box.setLayout(tir_layout)

        # ---- Ranking table ----
        self._ranking_table = QTableWidget(0, 5)
        self._ranking_table.setHorizontalHeaderLabels(
            ["#", "Cliente", "Capital", "Ganancia realizada", "Rentabilidad"]
        )
        self._ranking_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        for col in (0, 2, 3, 4):
            self._ranking_table.horizontalHeader().setSectionResizeMode(
                col, QHeaderView.ResizeToContents
            )
        self._ranking_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._ranking_table.setAlternatingRowColors(True)
        self._ranking_table.verticalHeader().setVisible(False)

        ranking_box = QGroupBox("🏆 Ranking de rentabilidad por cliente")
        ranking_layout = QVBoxLayout()
        ranking_layout.addWidget(self._ranking_table)
        ranking_box.setLayout(ranking_layout)

        # ---- Sort selector ----
        self._sort_combo = QComboBox()
        self._sort_combo.addItem("TIR (mayor a menor)", "tir_desc")
        self._sort_combo.addItem("TIR (menor a mayor)", "tir_asc")
        self._sort_combo.addItem("Capital (mayor a menor)", "capital_desc")
        self._sort_combo.addItem("Ganancia (mayor a menor)", "profit_desc")
        self._sort_combo.setToolTip("Ordenar la tabla de TIR")
        self._sort_combo.currentIndexChanged.connect(self._refresh_tir_table)

        refresh_button = QPushButton("🔄 Actualizar")
        refresh_button.setToolTip("Recalcular análisis")
        refresh_button.clicked.connect(self.refresh)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("🔎 Ordenar por:"))
        filter_row.addWidget(self._sort_combo)
        filter_row.addStretch()
        filter_row.addWidget(refresh_button)

        # ---- Scroll area ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addLayout(filter_row)
        content_layout.addWidget(cards_container)
        content_layout.addWidget(tir_box)
        content_layout.addWidget(ranking_box)
        content_layout.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self._loans: list = []
        self._borrower_name_by_id: dict[int, str] = {}
        self._all_installments: list = []

        self.refresh()

    def refresh(self) -> None:
        self._loans = self._loan_repository.list_all()
        self._all_installments = self._installment_repository.list_all()
        self._borrower_name_by_id = {
            b.id: b.name for b in self._borrower_repository.list_all()
        }

        total_principal = sum((loan.principal for loan in self._loans), ZERO)
        total_profit = sum((gross_profit(loan) for loan in self._loans), ZERO)
        realized = realized_profit(self._loans, self._all_installments)

        irr = portfolio_irr(self._loans)

        self._total_principal_card.set_value(f"${total_principal:,.2f}")
        self._total_profit_card.set_value(f"${total_profit:,.2f}")
        self._realized_card.set_value(f"${realized:,.2f}")
        self._portfolio_irr_card.set_value(f"{irr * 100:.2f}%")

        self._refresh_tir_table()
        self._refresh_ranking()

    def _refresh_tir_table(self) -> None:
        sort_key = self._sort_combo.currentData() or "tir_desc"

        rows = []
        for loan in self._loans:
            borrower_name = self._borrower_name_by_id.get(loan.borrower_id, "—")
            tir = loan_irr(loan)
            profit = gross_profit(loan)
            rows.append((borrower_name, loan.principal, profit, tir))

        if sort_key == "tir_desc":
            rows.sort(key=lambda r: r[3], reverse=True)
        elif sort_key == "tir_asc":
            rows.sort(key=lambda r: r[3])
        elif sort_key == "capital_desc":
            rows.sort(key=lambda r: r[1], reverse=True)
        elif sort_key == "profit_desc":
            rows.sort(key=lambda r: r[2], reverse=True)

        self._tir_table.setSortingEnabled(False)
        self._tir_table.setRowCount(len(rows))
        for row_idx, (name, principal, profit, tir) in enumerate(rows):
            self._tir_table.setItem(row_idx, 0, QTableWidgetItem(name))
            self._tir_table.setItem(row_idx, 1, QTableWidgetItem(f"${principal:,.2f}"))
            self._tir_table.setItem(row_idx, 2, QTableWidgetItem(f"${profit:,.2f}"))

            tir_item = QTableWidgetItem(f"{tir * 100:.2f}%")
            if tir > 0.5:
                tir_item.setForeground(Qt.GlobalColor.darkGreen)
            elif tir < 0:
                tir_item.setForeground(Qt.GlobalColor.red)
            self._tir_table.setItem(row_idx, 3, tir_item)

    def _refresh_ranking(self) -> None:
        stats_by_borrower: dict[str, list] = {}
        for loan in self._loans:
            name = self._borrower_name_by_id.get(loan.borrower_id, "—")
            loan_installments = [
                i for i in self._all_installments if i.loan_id == loan.id
            ]
            collected = sum(
                (p.amount_paid for i in loan_installments for p in i.payments), ZERO
            )
            stats_by_borrower.setdefault(name, []).append(
                (loan.principal, collected, gross_profit(loan))
            )

        ranking = []
        for name, entries in stats_by_borrower.items():
            total_principal = sum((e[0] for e in entries), ZERO)
            total_collected = sum((e[1] for e in entries), ZERO)
            roi = (
                float(total_collected) / float(total_principal) * 100
                if total_principal > ZERO
                else 0.0
            )
            ranking.append((name, total_principal, total_collected, roi))

        ranking.sort(key=lambda r: r[3], reverse=True)

        self._ranking_table.setRowCount(len(ranking))
        for row_idx, (name, principal, collected, roi) in enumerate(ranking):
            self._ranking_table.setItem(
                row_idx, 0, QTableWidgetItem(str(row_idx + 1))
            )
            self._ranking_table.setItem(row_idx, 1, QTableWidgetItem(name))
            self._ranking_table.setItem(
                row_idx, 2, QTableWidgetItem(f"${principal:,.2f}")
            )
            self._ranking_table.setItem(
                row_idx, 3, QTableWidgetItem(f"${collected:,.2f}")
            )

            roi_item = QTableWidgetItem(f"{roi:.1f}%")
            if roi >= 80:
                roi_item.setForeground(Qt.GlobalColor.darkGreen)
            elif roi >= 50:
                roi_item.setForeground(Qt.GlobalColor.darkYellow)
            else:
                roi_item.setForeground(Qt.GlobalColor.red)
            self._ranking_table.setItem(row_idx, 4, roi_item)


class _SummaryCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str = "—",
        value_class: str = "card-value",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setProperty("cssClass", "card")
        self.setFixedHeight(110)

        self._title_label = QLabel(title)
        self._title_label.setProperty("cssClass", "card-title")
        self._title_label.setAlignment(Qt.AlignLeft)

        self._value_label = QLabel(value)
        self._value_label.setProperty("cssClass", value_class)
        self._value_label.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        layout.addWidget(self._title_label)
        layout.addWidget(self._value_label)
        layout.addStretch()

    def set_value(self, value: str) -> None:
        self._value_label.setText(value)
