import json

from common.db import execute_write, execute_query, execute_one


class ActivityLogRepository:
    def log(
        self,
        action: str,
        user_id: str | None = None,
        branch_id: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        # Guard: empty string is not valid for inet cast
        safe_ip = ip_address or None

        execute_write(
            """
            INSERT INTO activity_logs
                (id, user_id, branch_id, action, entity_type, entity_id, details, ip_address)
            VALUES
                (gen_random_uuid(),
                 %s::uuid,
                 %s::uuid,
                 %s,
                 %s,
                 CASE WHEN %s IS NULL THEN NULL ELSE %s::uuid END,
                 %s::jsonb,
                 CASE WHEN %s IS NULL THEN NULL ELSE %s::inet END)
            """,
            [
                user_id,
                branch_id,
                action,
                entity_type,
                entity_id,
                entity_id,
                json.dumps(details) if details else None,
                safe_ip,
                safe_ip,
            ],
        )

    def count_logs(
        self,
        branch_id: str | None = None,
        user_id: str | None = None,
        action: str | None = None,
    ) -> int:
        filters = []
        params: list = []

        if branch_id:
            filters.append("branch_id = %s::uuid")
            params.append(branch_id)
        if user_id:
            filters.append("user_id = %s::uuid")
            params.append(user_id)
        if action:
            filters.append("action = %s")
            params.append(action)

        where = ("WHERE " + " AND ".join(filters)) if filters else ""
        row = execute_one(f"SELECT COUNT(*) AS total FROM activity_logs {where}", params)
        return int(row["total"]) if row else 0

    def get_logs(
        self,
        branch_id: str | None = None,
        user_id: str | None = None,
        action: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        filters = []
        params: list = []

        if branch_id:
            filters.append("branch_id = %s::uuid")
            params.append(branch_id)
        if user_id:
            filters.append("user_id = %s::uuid")
            params.append(user_id)
        if action:
            filters.append("action = %s")
            params.append(action)

        where = ("WHERE " + " AND ".join(filters)) if filters else ""
        params += [limit, offset]

        return execute_query(
            f"""
            SELECT id, user_id, branch_id, action, entity_type, entity_id,
                   details, ip_address, created_at
            FROM   activity_logs
            {where}
            ORDER  BY created_at DESC
            LIMIT  %s OFFSET %s
            """,
            params,
        )
