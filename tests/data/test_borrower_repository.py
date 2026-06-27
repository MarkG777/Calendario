from datetime import date

from data.repositories import BorrowerRepository
from domain.entities import Borrower


def test_add_and_get_borrower(session):
    repo = BorrowerRepository(session)
    borrower = Borrower(name="Juan Perez", phone="555-1234", created_at=date(2026, 1, 1))

    saved = repo.add(borrower)

    assert saved.id is not None
    fetched = repo.get(saved.id)
    assert fetched.name == "Juan Perez"
    assert fetched.phone == "555-1234"


def test_list_all_borrowers(session):
    repo = BorrowerRepository(session)
    repo.add(Borrower(name="Juan Perez"))
    repo.add(Borrower(name="Maria Lopez"))

    borrowers = repo.list_all()

    assert {b.name for b in borrowers} == {"Juan Perez", "Maria Lopez"}


def test_update_borrower(session):
    repo = BorrowerRepository(session)
    saved = repo.add(Borrower(name="Juan Perez", phone="555-1234", created_at=date(2026, 1, 1)))

    saved.name = "Juan Perez Gomez"
    saved.phone = "555-9999"
    repo.update(saved)

    fetched = repo.get(saved.id)
    assert fetched.name == "Juan Perez Gomez"
    assert fetched.phone == "555-9999"
    assert fetched.created_at == date(2026, 1, 1)
