from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
import uuid
from datetime import datetime, timedelta
import jwt
from django.conf import settings


# ---------------- LOGIN ----------------
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])  # 🔥 VERY IMPORTANT
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    print("LOGIN HIT:", email)  # debug

    with connection.cursor() as cursor:
        # 1. Get user
        cursor.execute(
            """
            SELECT id, password_hash FROM users
            WHERE email=%s
            """,
            [email]
        )

        user = cursor.fetchone()

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        user_id, password_hash = user

        # 2. Verify password
        cursor.execute(
            """
            SELECT crypt(%s, %s)
            """,
            [password, password_hash]
        )

        test_hash = cursor.fetchone()[0]

        if test_hash != password_hash:
            return Response({"error": "Invalid credentials"}, status=401)

    # 3. Generate JWT manually
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=2),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    return Response({
        "access": token
    })


# ---------------- REQUEST RESET ----------------
reset_tokens = {}

@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def request_reset(request):
    email = request.data.get("email")

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE email=%s", [email])
        user = cursor.fetchone()

        if not user:
            return Response({"error": "User not found"}, status=404)

    token = str(uuid.uuid4())

    reset_tokens[token] = {
        "email": email,
        "expires": datetime.now() + timedelta(minutes=5)
    }

    return Response({
        "message": "Reset token generated",
        "token": token  # simulate email
    })


# ---------------- RESET PASSWORD ----------------
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def reset_password(request):
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    data = reset_tokens.get(token)

    if not data:
        return Response({"error": "Invalid token"}, status=400)

    if datetime.now() > data["expires"]:
        return Response({"error": "Token expired"}, status=400)

    email = data["email"]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE users
            SET password_hash = crypt(%s, gen_salt('bf'))
            WHERE email=%s
            """,
            [new_password, email]
        )

    return Response({"message": "Password reset successful"})