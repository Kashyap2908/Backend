from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from datetime import datetime, timedelta


# ---------------- REGISTER ----------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data

    branch_name = data.get("branch_name")
    branch_location = data.get("branch_location")
    name = data.get("name")
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    with connection.cursor() as cursor:

        # 1. Check or create branch
        cursor.execute("SELECT id FROM branches WHERE name=%s", [branch_name])
        branch = cursor.fetchone()

        if branch:
            branch_id = branch[0]
        else:
            branch_id = str(uuid.uuid4())
            cursor.execute(
                "INSERT INTO branches (id, name, location) VALUES (%s, %s, %s)",
                [branch_id, branch_name, branch_location]
            )

        # 2. Check user exists
        cursor.execute("SELECT id FROM users WHERE email=%s", [email])
        if cursor.fetchone():
            return Response({"error": "User already exists"}, status=400)

        # 3. Create user
        user_id = str(uuid.uuid4())

        cursor.execute(
            """
            INSERT INTO users (id, branch_id, name, email, password_hash, role)
            VALUES (%s, %s, %s, %s, crypt(%s, gen_salt('bf')), %s)
            """,
            [user_id, branch_id, name, email, password, role]
        )

    return Response({"message": "User registered successfully"})


# ---------------- LOGIN ----------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id FROM users
            WHERE email=%s AND password_hash = crypt(%s, password_hash)
            """,
            [email, password]
        )
        user = cursor.fetchone()

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        user_id = user[0]

    # Generate JWT
    refresh = RefreshToken()
    refresh['user_id'] = str(user_id)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    })


# ---------------- REQUEST RESET ----------------
reset_tokens = {}

@api_view(['POST'])
@permission_classes([AllowAny])
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