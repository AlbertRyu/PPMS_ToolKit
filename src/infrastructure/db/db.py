# src/yourapp_infra_local/db.py
from __future__ import annotations
from curses import meta
from importlib import metadata
import sqlite3
from pathlib import Path
from dataclasses import dataclass
import json
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


@dataclass(frozen=True)
class MeasurementDTO:
    id: int | None
    sample_id: int | None
    measurement_type: str
    mode: str | None 
    const_temperature: float | None
    const_field: float | None      
    original_filepath: str
    data_filepath: str     
    extra_parameters: dict | None 
    comment: str           
    created_at: str        
    updated_at: str

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

        CREATE TABLE IF NOT EXISTS measurements (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_id         INTEGER NOT NULL,        -- 关联 samples.id
        measurement_type  TEXT NOT NULL,          -- 'VSM','HeatCapacity',...
        mode              TEXT,                   -- 只有 VSM 有，NULL表示不适用
        const_temperature REAL,                   -- HC 常用
        const_field       REAL,                   -- VSM 常用
        original_filepath TEXT NOT NULL,          -- 原始导入文件（可为空或放路径）
        data_filepath     TEXT NOT NULL,          -- Parquet 存储路径
        extra_parameters  TEXT,                   -- JSON 字符串，存放任意测量专有字段（例如 {"mode":"MH"}）
        comment           TEXT,
        created_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
        );

        -- 创建索引加速查询
        CREATE INDEX IF NOT EXISTS idx_measurement_sample ON measurements(sample_id);
        CREATE INDEX IF NOT EXISTS idx_measurement_type ON measurements(measurement_type);
        CREATE INDEX IF NOT EXISTS idx_measurement_mode ON measurements(mode);
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
    
    def delete_sample(self, sample:SampleDTO) -> int:
        if sample is None:
            return 0
        cur = self.con.cursor()
        cur.execute("DELETE FROM samples WHERE id = ?", (sample.id,))
        self.con.commit()
        rc = cur.rowcount
        cur.close()
        return rc # expect 1


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

    ### Measurement related function.
    def select_vsm_measurement(self):
        pass

    def add_measurement(self, dto: MeasurementDTO):

        cur = self.con.cursor()
        cur.execute(
            '''INSERT INTO measurements(
            id
            sample_id
            measurement_type
            mode
            const_temperature
            const_field
            original_filepath
            data_filepath
            extra_parameters
            comment
            created_at 
            updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?));
            ''',
            (dto.id, 
             dto.sample_id, 
             dto.measurement_type,
             dto.mode,
             dto.const_temperature,
             dto.const_field,
             dto.original_filepath,
             dto.data_filepath,
             dto.extra_parameters,
             dto.comment,
             dto.created_at,
             dto.updated_at)
            )
        

        pass

    def del_measurement(self):
        pass

    def close(self):
        self.con.close()


# Util Funcitons
def _serilize_data(meta_data: dict | None):
    if meta_data is None:
        return None
    return json.dumps(meta_data, ensure_ascii=False)
