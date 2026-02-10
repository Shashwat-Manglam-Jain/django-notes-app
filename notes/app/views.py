from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializer import NotesSerializer
from .models import NotesModel
from accounts.models import CustomUser

from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404


class NoteView(APIView):
    permission_classes = (IsAuthenticated,)


    def send_email(self, receiver_email: str):
        if not receiver_email:
            return
        email = EmailMessage(
            subject="A manager viewed your work note",
            body="Your work note was accessed by a manager.",
            to=[receiver_email],
        )
        email.send(fail_silently=True)


    def post(self, request):
        serializer = NotesSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def get(self, request):
        role = str(request.user.Role).strip().lower()

        if role == "user":
            notes = NotesModel.objects.filter(user=request.user)

        elif role == "manager":
            user_id = request.query_params.get("userId")

            if not user_id:
                return Response(
                    {"detail": "userId is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            notes = NotesModel.objects.filter(
                note_type="work",
                user_id=user_id
            )

            receiver_email = (
                CustomUser.objects.filter(id=user_id)
                .values_list("email", flat=True)
                .first()
            )
            self.send_email(receiver_email)

        elif role in {"superadmin", "super_admin", "super-admin"}:
            notes = NotesModel.objects.all()

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = NotesSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, id=None):
        if id is None:
            return Response(
                {"detail": "Note ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role = str(getattr(request.user, "Role", "")).strip().lower()
        note = get_object_or_404(NotesModel, id=id)

      
        if role == "user":
            if note.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            if note.note_type == "personal":
                 note.delete()
                 return Response(status=status.HTTP_204_NO_CONTENT)

            if note.validateDeleteManager and note.validateDeleteSuperAdmin:
                note.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            note.isActiveReq = True
            note.save(update_fields=["isActiveReq"])
            return Response(
                {"detail": "Delete request submitted"},
                status=status.HTTP_202_ACCEPTED,
            )

      
        if role == "manager":
            if not note.isActiveReq:
                return Response(
                    {"detail": "No active delete request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            note.validateDeleteManager = True
            note.save(update_fields=["validateDeleteManager"])
            return Response(
                {"detail": "Delete approved by manager"},
                status=status.HTTP_200_OK,
            )

        if role in {"superadmin", "super_admin", "super-admin"}:
            if not note.isActiveReq:
                return Response(
                    {"detail": "No active delete request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            note.validateDeleteSuperAdmin = True
            note.save(update_fields=["validateDeleteSuperAdmin"])
            return Response(
                {"detail": "Delete approved by super admin"},
                status=status.HTTP_200_OK,
            )

        return Response(status=status.HTTP_403_FORBIDDEN)
    

