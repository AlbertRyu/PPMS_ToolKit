# src/yourapp_infra_local/db.py
from __future__ import annotations
from multiprocessing import Value
import sqlite3
from pathlib import Path
from dataclasses import dataclass

from ppms_toolkit.sample import Sample

@dataclass(frozen=True)
class SampleDTO:
    id: int | None
    name: str
    mass : float
    chemical: str
    orientation: str
    created_at: str
    notes: str | None

class LocalDB:
    """最小可用 SQLite 封装，用于保存/读取 Sample 列表。"""
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.db_path = self.project_root / "db.sqlite3"
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(str(self.db_path))
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

    def add_sample(self, sample : SampleDTO):
        cur = self.con.cursor()

        cur.execute("""
        SELECT id, name FROM samples
        WHERE chemical = ? AND ABS(mass - ?) < 1e-6
        """, (sample.chemical, sample.mass))
        dup = cur.fetchall()
        if dup:
            dup_names = [d[1] for d in dup]
            print(f"⚠️ Possible duplicate samples: {dup_names}")
            return False

        cur = self.con.execute(
            "INSERT INTO samples(name, mass, chemical, orientation, created_at, notes) VALUES(?,?,?,?,?,?);",
            (sample.name, sample.mass, sample.chemical, sample.orientation, sample.created_at, sample.notes),
        )
        self.con.commit()
        return cur.lastrowid
    
    def update_sampe(self, sample: SampleDTO):
        if sample.id is None:
            raise ValueError("update samples needs sample ID")
        sql = """
            UPDATE samples
            SET
                name        = ?,
                mass        = ?,
                chemical    = ?,
                orientation = ?,
                created_at  = ?,   -- 若不希望改动，传旧值即可
                notes       = ?
            WHERE id = ?
            """
        params = (
            sample.name,
            sample.mass,
            sample.chemical,
            sample.orientation,
            sample.created_at,
            sample.notes,
            sample.id,
        )
        cur = self.con.cursor()
        cur.execute(sql, params)
        self.con.commit()
        rc = cur.rowcount # How many lines been affect by this cur.
        cur.close()
        return rc  # should return 1


    def fetch_all_distinct_chemical(self):
        cur = self.con.cursor()
        cur.execute(
            '''
            SELECT DISTINCT TRIM(chemical)
            FROM samples
            WHERE chemical IS NOT NULL
            AND TRIM(chemical) <> ''
            ORDER BY LOWER(chemical);
            '''
        )
        rows = cur.fetchall()
        return [rows[r][0] for r in range(len(rows))]

    def list_samples(self) -> list[SampleDTO]:
        rows = self.con.execute(
            "SELECT id, name, mass, chemical, orientation, created_at, notes FROM samples ORDER BY created_at DESC"
        ).fetchall()
        return [SampleDTO(*r) for r in rows]
    
    def close(self):
        self.con.close()
