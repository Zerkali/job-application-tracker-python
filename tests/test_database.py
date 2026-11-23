import pytest
import database as db

@pytest.fixture(autouse=True)
def temporary_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB', tmp_path / 'test.db')
    db.init_db()

def test_authentication():
    assert db.register('student', 'password123')
    assert not db.register('student', 'password123')
    assert db.login('student', 'wrong') is None
    assert db.login('student', 'password123') is not None

def test_crud_and_ownership():
    db.register('one', 'password123')
    db.register('two', 'password123')
    one, two = db.login('one','password123'), db.login('two','password123')
    app = db.add_application(one, 'Example GmbH', 'Werkstudent IT', '2026-11-23', 'Offen')
    assert len(db.list_applications(one)) == 1
    assert db.list_applications(two) == []
    assert db.update_application(two, app, 'Other', 'IT', '2026-11-23', 'Zusage') == 0
    assert db.delete_application(two, app) == 0
    assert db.update_application(one, app, 'Example GmbH', 'IT', '2026-11-23', 'Zusage') == 1
    assert db.list_applications(one)[0]['status'] == 'Zusage'
    assert db.delete_application(one, app) == 1
    assert db.list_applications(one) == []

def test_validation():
    with pytest.raises(ValueError):
        db.register('student','short')
    with pytest.raises(ValueError):
        db.add_application(1,'','IT','2026-11-23','Offen')
