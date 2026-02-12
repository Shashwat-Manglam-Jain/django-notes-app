from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient, APITestCase, APIRequestFactory

from .models import NotesModel
from .serializer import NotesSerializer


class NotesSerializerTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user1@example.com",
            password="pass12345",
            Role="user",
        )

    def test_validate_note_type_normalizes_input(self):
        serializer = NotesSerializer(
            data={"note_type": " Work ", "description": "todo"}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["note_type"], "work")

    def test_validate_note_type_rejects_invalid_value(self):
        serializer = NotesSerializer(
            data={"note_type": "random", "description": "todo"}
        )
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["note_type"][0],
            "You have to select a proper note type (personal or work).",
        )

    def test_create_requires_authenticated_user(self):
        factory = APIRequestFactory()
        request = factory.post("/notes/", {})
        request.user = AnonymousUser()
        serializer = NotesSerializer(
            data={"note_type": "work", "description": "todo"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaisesMessage(ValidationError, "Authentication required."):
            serializer.save()

    def test_create_assigns_authenticated_request_user(self):
        factory = APIRequestFactory()
        request = factory.post("/notes/", {})
        request.user = self.user

        serializer = NotesSerializer(
            data={"note_type": "work", "description": "todo"},
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

        note = serializer.save()
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.note_type, "work")


class NoteViewTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass12345",
            Role="user",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="pass12345",
            Role="user",
        )
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="pass12345",
            Role="manager",
        )
        self.super_admin = User.objects.create_user(
            email="admin@example.com",
            password="pass12345",
            Role="superAdmin",
        )
        self.auditor = User.objects.create_user(
            email="auditor@example.com",
            password="pass12345",
            Role="auditor",
        )
        self.notes_url = reverse("notes")

    def _auth_client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def test_post_creates_note_for_authenticated_user(self):
        client = self._auth_client(self.user)
        payload = {"note_type": "WORK", "description": "Sprint plan"}

        response = client.post(self.notes_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note = NotesModel.objects.get(id=response.data["id"])
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.note_type, "work")

    def test_get_for_user_returns_only_own_notes(self):
        own_note = NotesModel.objects.create(
            user=self.user,
            note_type="personal",
            description="Mine",
        )
        NotesModel.objects.create(
            user=self.other_user,
            note_type="personal",
            description="Not mine",
        )

        response = self._auth_client(self.user).get(self.notes_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], own_note.id)

    def test_get_for_manager_requires_user_id(self):
        response = self._auth_client(self.manager).get(self.notes_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "userId is required")

    def test_get_for_manager_returns_only_work_notes_for_selected_user(self):
        work_note = NotesModel.objects.create(
            user=self.user,
            note_type="work",
            description="Visible to manager",
        )
        NotesModel.objects.create(
            user=self.user,
            note_type="personal",
            description="Should not be visible",
        )
        NotesModel.objects.create(
            user=self.other_user,
            note_type="work",
            description="Different user",
        )

        with patch("app.views.NoteView.send_email") as mock_send_email:
            response = self._auth_client(self.manager).get(
                self.notes_url, {"userId": self.user.id}
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], work_note.id)
        mock_send_email.assert_called_once_with(self.user.email)

    def test_get_for_super_admin_returns_all_notes(self):
        note_one = NotesModel.objects.create(
            user=self.user,
            note_type="personal",
            description="A",
        )
        note_two = NotesModel.objects.create(
            user=self.user,
            note_type="work",
            description="B",
        )
        note_three = NotesModel.objects.create(
            user=self.other_user,
            note_type="work",
            description="C",
        )

        response = self._auth_client(self.super_admin).get(self.notes_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {item["id"] for item in response.data}
        self.assertSetEqual(returned_ids, {note_one.id, note_two.id, note_three.id})

    def test_get_with_unsupported_role_returns_forbidden(self):
        response = self._auth_client(self.auditor).get(self.notes_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_without_id_returns_bad_request(self):
        response = self._auth_client(self.user).delete(self.notes_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Note ID is required")

    def test_user_cannot_delete_another_users_note(self):
        note = NotesModel.objects.create(
            user=self.other_user,
            note_type="personal",
            description="Other user's note",
        )

        response = self._auth_client(self.user).delete(
            reverse("note-detail", args=[note.id])
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(NotesModel.objects.filter(id=note.id).exists())
