from common.db import execute_one, execute_write, execute_write_returning
from common.exceptions import DatabaseError


class UserRepository:
    """All SQL touching the `users` table lives here — no SQL elsewhere."""

    def find_by_email(self, email: str) -> dict | None:
        return execute_one(
            "SELECT id, email, password_hash, branch_id, role FROM users WHERE email = %s",
            [email],
        )

    def find_by_id(self, user_id: str) -> dict | None:
        return execute_one(
            "SELECT id, email, branch_id, role FROM users WHERE id = %s::uuid",
            [user_id],
        )

    def verify_password(self, plain: str, hashed: str) -> bool:
        """Use pgcrypto to verify plain text against a bcrypt hash."""
        row = execute_one(
            "SELECT crypt(%s, %s) = %s AS is_valid",
            [plain, hashed, hashed],
        )
        return bool(row and row.get("is_valid"))

    def update_password(self, user_id: str, new_password: str) -> bool:
        affected = execute_write(
            "UPDATE users SET password_hash = crypt(%s, gen_salt('bf')) WHERE id = %s::uuid",
            [new_password, user_id],
        )
        return affected > 0

    # ── Password-reset tokens ──────────────────────────────────────────────

    def create_reset_token(self, user_id: str, token: str, expires_at) -> None:
        execute_write(
            """
            INSERT INTO password_reset_tokens (id, user_id, token, expires_at)
            VALUES (gen_random_uuid(), %s::uuid, %s, %s)
            ON CONFLICT (user_id)
            DO UPDATE SET token = EXCLUDED.token,
                          expires_at = EXCLUDED.expires_at,
                          used = FALSE
            """,
            [user_id, token, expires_at],
        )

    def find_reset_token(self, token: str) -> dict | None:
        return execute_one(
            """
            SELECT prt.token, prt.user_id, prt.expires_at, prt.used,
                   u.email
            FROM   password_reset_tokens prt
            JOIN   users u ON u.id = prt.user_id
            WHERE  prt.token = %s
            """,
            [token],
        )

    def mark_reset_token_used(self, token: str) -> None:
        execute_write(
            "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
            [token],
        )

    # ── Refresh tokens ─────────────────────────────────────────────────────

    def store_refresh_token(
        self, user_id: str, token: str, branch_id: str | None, expires_at
    ) -> None:
        execute_write(
            """
            INSERT INTO refresh_tokens (id, user_id, token, branch_id, expires_at)
            VALUES (gen_random_uuid(), %s::uuid, %s, %s::uuid, %s)
            """,
            [user_id, token, branch_id, expires_at],
        )

    def find_refresh_token(self, token: str) -> dict | None:
        return execute_one(
            """
            SELECT rt.token, rt.user_id, rt.branch_id, rt.expires_at, rt.is_revoked,
                   u.email, u.role
            FROM   refresh_tokens rt
            JOIN   users u ON u.id = rt.user_id
            WHERE  rt.token = %s
            """,
            [token],
        )

    def revoke_refresh_token(self, token: str) -> None:
        execute_write(
            "UPDATE refresh_tokens SET is_revoked = TRUE WHERE token = %s",
            [token],
        )

    def revoke_all_refresh_tokens(self, user_id: str) -> None:
        execute_write(
            "UPDATE refresh_tokens SET is_revoked = TRUE WHERE user_id = %s::uuid",
            [user_id],
        )

    # ── User creation ──────────────────────────────────────────────────────

    def create_user(self, email: str, password: str, role: str = "staff") -> dict:
        """Hash password with bcrypt via pgcrypto and return the new user row."""
        return execute_write_returning(
            """
            INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
            VALUES (gen_random_uuid(), %s, crypt(%s, gen_salt('bf')), %s,
                    NOW(), NOW())
            RETURNING id, email, role, branch_id
            """,
            [email, password, role],
        )
