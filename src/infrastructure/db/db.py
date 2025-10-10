# src/yourapp_infra_local/db.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class SampleDTO:
    id: int
    name: str
    code: str | None
    notes: str | None
    created_at: str

class LocalDB:
    """最小可用 SQLite 封装，用于保存/读取 Sample 列表。"""
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.db_path = self.project_root / "db.sqlite3"
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(self.db_path)
        self.con.execute("PRAGMA foreign_keys = ON;")
        self.con.execute("PRAGMA journal_mode = WAL;")
        self._ensure_schema()

    def _ensure_schema(self):
        """若无表则自动创建（幂等）。"""
        self.con.executescript("""
        CREATE TABLE IF NOT EXISTS sample (
          id          INTEGER PRIMARY KEY,
          name        TEXT NOT NULL UNIQUE,
          code        TEXT,
          notes       TEXT,
          created_at  TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_sample_created ON sample(created_at);
        """)
        self.con.commit()

    def add_sample(self, name: str, code: str = "", notes: str = ""):
        cur = self.con.execute(
            "INSERT INTO sample(name, code, notes, created_at) VALUES(?,?,?,?)",
            (name, code, notes, datetime.now().isoformat(timespec="seconds")),
        )
        self.con.commit()
        return cur.lastrowid

    def list_samples(self) -> list[SampleDTO]:
        rows = self.con.execute(
            "SELECT id, name, code, notes, created_at FROM sample ORDER BY created_at DESC"
        ).fetchall()
        return [SampleDTO(*r) for r in rows]

    def close(self):
        self.con.close()
