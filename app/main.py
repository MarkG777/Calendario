from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from data.database import create_engine_for, init_db, session_factory
from data.repositories import (
    BorrowerRepository,
    InstallmentRepository,
    LoanRepository,
    PaymentRepository,
)
from ui.main_window import MainWindow
from ui.theme import apply_theme


def _resolve_db_path() -> Path:
    if getattr(sys, "frozen", False):
        # PyInstaller --onefile extracts code to a fresh temp dir on every
        # launch, so the db must live next to the .exe instead of __file__.
        return Path(sys.executable).resolve().parent / "cobros.db"
    return Path(__file__).resolve().parent.parent / "cobros.db"


DB_PATH = _resolve_db_path()


def main() -> int:
    engine = create_engine_for(str(DB_PATH))
    init_db(engine)
    session = session_factory(engine)()

    borrower_repository = BorrowerRepository(session)
    loan_repository = LoanRepository(session)
    installment_repository = InstallmentRepository(session)
    payment_repository = PaymentRepository(session)

    app = QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow(
        borrower_repository, loan_repository, installment_repository, payment_repository
    )
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
