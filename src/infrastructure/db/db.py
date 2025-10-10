# src/yourapp_infra_local/db.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class SampleDTO:
    id: int | None
    name: str
    mass : float
    chemical: str
    orientation: str
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
        CREATE TABLE IF NOT EXISTS samples (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT    NOT NULL,
        mass         REAL    NOT NULL CHECK (mass >= 0),
        chemical     TEXT    NOT NULL,
        orientation  TEXT    NOT NULL CHECK (orientation IN ('In Plane', 'Out of Plane')),
        notes        TEXT,
        created_at   TEXT    NOT NULL 
            );
        CREATE INDEX IF NOT EXISTS idx_sample_created ON samples(created_at);
        """)
        self.con.commit()

    def add_sample(self, 
                   name: str,
                   mass: float,
                   chemical: str,
                   orientation :str,
                   create_at: str,
                   notes: str = "",
                   ):
        cur = self.con.execute(
            "INSERT INTO samples(name, mass, chemical, orientation, created_at, notes) VALUES(?,?,?,?,?,?)",
            (name, mass, chemical, orientation, create_at, notes),
        )
        self.con.commit()
        return cur.lastrowid

    def list_samples(self) -> list[SampleDTO]:
        rows = self.con.execute(
            "SELECT id, name, mass, chemical, orientation, created_at, notes FROM samples ORDER BY created_at DESC"
        ).fetchall()
        return [SampleDTO(*r) for r in rows]

    def close(self):
        self.con.close()
