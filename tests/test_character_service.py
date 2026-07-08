import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import User
from app.schemas.character import CharacterCreate
from app.services.character_service import (
    create_character,
    get_character_by_id,
    get_user_characters,
    update_character,
)


class CharacterServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.user = User(email="test@example.com", password_hash="hash", role="player")
        self.session.add(self.user)
        self.session.commit()
        self.session.refresh(self.user)

    def tearDown(self) -> None:
        self.session.close()

    def test_character_crud_flow(self) -> None:
        created = create_character(
            self.session,
            self.user.id,
            CharacterCreate(name="Torgrim", race="Human", class_name="Barbarian", max_hp=20),
        )

        self.assertEqual(created.owner_id, self.user.id)
        self.assertEqual(created.current_hp, 20)

        fetched = get_character_by_id(self.session, created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, "Torgrim")

        characters = get_user_characters(self.session, self.user.id)
        self.assertEqual(len(characters), 1)

        updated = update_character(
            self.session,
            created.id,
            self.user.id,
            CharacterCreate(name="Torgrim", race="Human", class_name="Barbarian", max_hp=24),
        )

        self.assertEqual(updated.name, "Torgrim")
        self.assertEqual(updated.max_hp, 24)
        self.assertEqual(updated.current_hp, 24)


if __name__ == "__main__":
    unittest.main()
