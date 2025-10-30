# src/yourapp_infra_local/db.py
from __future__ import annotations
import uuid
import hashlib
from datetime import datetime
import sqlite3
from pathlib import Path
from dataclasses import dataclass
import json


# Util Funcitons
def _serialize_data(meta_data: dict | None):
    if meta_data is None:
        return None
    return json.dumps(meta_data, ensure_ascii=False)


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def _to_relative_path(absolute_path: Path, base_path: Path) -> str:
    """将绝对路径转为相对于 base_path 的相对路径"""
    try:
        return str(absolute_path.relative_to(base_path))
    except ValueError:
        # 如果路径不在 base_path 下，返回绝对路径（兼容性）
        return str(absolute_path)

def _to_absolute_path(relative_path: str, base_path: Path) -> Path:
    """将相对路径转为绝对路径"""
    p = Path(relative_path)
    if p.is_absolute():
        return p  # 已经是绝对路径，直接返回
    return base_path / p  # 拼接成绝对路径

@dataclass(frozen=True)
class SampleDTO:
    id: int | None
    name: str
    mass : float
    chemical: str
    orientation: str | None
    created_at: str
    notes: str | None


@dataclass(frozen=True)
class MeasurementDTO:
    sample_id: int | None
    measurement_type: str
    original_filepath: str
    id: int | None = None
    mode: str | None = None
    const_temperature: float | None = None
    const_field: float | None = None      
    data_filepath: str | None = None
    processed_data_filepath: str | None = None
    extra_parameters: dict | None  = None
    comment: str | None  = None
    created_at: str | None = None
    updated_at: str | None = None

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
        processed_data_filepath     TEXT NOT NULL,          -- Parquet 存储路径
        extra_parameters  TEXT,                   -- JSON 字符串，存放任意测量专有字段（例如 {"mode":"MH"}）
        comment           TEXT,
        created_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        content_hash      TEXT NOT NULL,

        FOREIGN KEY (sample_id) REFERENCES samples(id) ON DELETE CASCADE
        );

        -- 创建索引加速查询
        CREATE INDEX IF NOT EXISTS idx_measurement_sample ON measurements(sample_id);
        CREATE INDEX IF NOT EXISTS idx_measurement_type ON measurements(measurement_type);
        CREATE INDEX IF NOT EXISTS idx_measurement_mode ON measurements(mode);
        """)

        self.con.commit()
    
    def get_sample(self, sample_id: int | None) -> SampleDTO | None:
        # get SampleDTO from sample ID, return None if not exist
        if sample_id is None:
            raise ValueError("sample_id must be provided")

        row = self.con.execute(
            "SELECT id, name, mass, chemical, orientation, created_at, notes FROM samples WHERE id = ?",
            (sample_id,)
        ).fetchone()

        return SampleDTO(*row) if row else None
    
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
    
    def update_sampel(self, sample: SampleDTO):
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
         # 1. Query measurements
        rows = cur.execute(
            "SELECT id, data_filepath, processed_data_filepath FROM measurements WHERE sample_id = ?",
            (sample.id,)
        ).fetchall()
        
        # 2. Delete parquet files
        file_errors = []
        for row in rows:
            mid, data_fp, proc_fp = row[0], row[1], row[2]
            for fp in (data_fp, proc_fp):
                if fp:
                    try:
                        p = _to_absolute_path(fp, self.project_root)
                        if p.exists():
                            p.unlink()
                    except Exception as e:
                        file_errors.append((fp, str(e)))
        
        # 3. if errors, report back 
        if file_errors:
            import warnings
            msgs = "; ".join([f"{p}: {m}" for p, m in file_errors])
            warnings.warn(f"Some files couldn't be deleted: {msgs}")
            
        # 4. del record from sample table
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
    def list_measurements(self) -> list[MeasurementDTO]:
        rows = self.con.execute(
            """
            SELECT sample_id, measurement_type, original_filepath, id, mode, 
            const_temperature, const_field, data_filepath, processed_data_filepath, 
            extra_parameters, comment, created_at, updated_at 
            FROM measurements ORDER BY created_at DESC"""
        ).fetchall()
        result = []
        for row in rows:
            # row[9] 是 extra_parameters
            extra = json.loads(row[9]) if row[9] else None
            
            dto = MeasurementDTO(
                sample_id=row[0],
                measurement_type=row[1],
                original_filepath=row[2],
                id=row[3],
                mode=row[4],
                const_temperature=row[5],
                const_field=row[6],
                data_filepath=str(_to_absolute_path(row[7],self.project_root)) if row[7] else None,
                processed_data_filepath=str(_to_absolute_path(row[8],self.project_root)) if row[8] else None,
                extra_parameters=extra,  # ✅ 反序列化后的 dict
                comment=row[10],
                created_at=row[11],
                updated_at=row[12]
            )
            result.append(dto)
        return result
    
    
    def select_vsm_measurements_from_sample_id(self, sample_id: int):
        cur = self.con.cursor()
        sql = (
            "SELECT id, sample_id, measurement_type, original_filepath, mode, const_temperature, "
            "const_field, data_filepath, processed_data_filepath, extra_parameters, comment, created_at, updated_at "
            "FROM measurements "
            "WHERE sample_id = ? AND measurement_type = ?"
        )
        rows = cur.execute(sql, (sample_id,"VSM",)).fetchall()
        result = []
        for row in rows:
            extra = json.loads(row[9]) if row[9] else None
            dto = MeasurementDTO(
                sample_id=row[1],
                measurement_type=row[2],
                original_filepath=row[3],
                id=row[0],
                mode=row[4],
                const_temperature=row[5],
                const_field=row[6],
                data_filepath=row[7],
                processed_data_filepath=row[8],
                extra_parameters=extra,
                comment=row[10],
                created_at=row[11],
                updated_at=row[12],
            )
            result.append(dto)
        return result

    def add_measurement(self, dto: MeasurementDTO, raw_df, processed_df):
        
        sample = self.get_sample(dto.sample_id)
        if sample is None:
            raise ValueError(f"Sample with {dto.sample_id} does't exist.")
        
        content_hash = _sha256_of_file(Path(dto.original_filepath))
        existing = self.con.execute("SELECT original_filepath FROM measurements WHERE content_hash = ?", (content_hash,)).fetchone()
        if existing:
            raise ValueError(f"duplicate, Same content as: {existing[0]}")
        
        measurement_uuid = uuid.uuid4().hex
        data_dir = self.project_root / "data" / "measurements" / "raw"
        proc_dir = self.project_root / "data" / "measurements" / "processed"
        data_dir.mkdir(parents=True, exist_ok=True)
        proc_dir.mkdir(parents=True, exist_ok=True)

        raw_parquet_path = Path(dto.data_filepath) if dto.data_filepath else data_dir / f"{dto.sample_id}_{measurement_uuid}.parquet"
        processed_parquet_path = Path(dto.processed_data_filepath) if dto.processed_data_filepath else (proc_dir / f"{dto.sample_id}_{measurement_uuid}_proc.parquet")
        # 写文件（如果有 DataFrame）
        try:
            if raw_df is not None:
                raw_df.to_parquet(raw_parquet_path, compression='snappy')
            if processed_df is not None:
                processed_df.to_parquet(processed_parquet_path, compression='snappy')
        except Exception as e:
            # 清理失败文件
            if raw_parquet_path.exists():
                raw_parquet_path.unlink(missing_ok=True) # unlink means remove
            if processed_parquet_path and processed_parquet_path.exists(): # missing_ok raise no error when files not there
                processed_parquet_path.unlink(missing_ok=True)
            raise # Raise error to the upper level

        now = datetime.now().isoformat()
        cur = self.con.cursor()
        cur.execute(
            '''INSERT INTO measurements(
            sample_id,
            measurement_type,
            mode,
            const_temperature,
            const_field,
            original_filepath,
            data_filepath,
            processed_data_filepath,
            extra_parameters,
            comment,
            created_at, 
            updated_at,
            content_hash)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);
            ''',
            (dto.sample_id, 
             dto.measurement_type,
             dto.mode,
             dto.const_temperature,
             dto.const_field,
             dto.original_filepath,
             _to_relative_path(raw_parquet_path, self.project_root),
             _to_relative_path(processed_parquet_path, self.project_root),
             _serialize_data(dto.extra_parameters),
             dto.comment,
             now,
             now,
             content_hash)
        )
        self.con.commit()
        return cur.lastrowid
        
    def del_measurement(self, mid: int):
        if mid is None:
            raise ValueError('Mid must not be none')
        cur = self.con.cursor()
        # 1) Query the row to get file paths
        row = cur.execute(
            "SELECT data_filepath, processed_data_filepath FROM measurements WHERE id = ?",
            (mid,)
        ).fetchone()
        if not row:
            cur.close()
            return 0  # nothing to delete

        data_fp, proc_fp = row[0], row[1]

        # 2) Try to delete files (if present). Collect errors to raise if necessary.
        errors = []
        for p in (data_fp, proc_fp):
            if p:
                try:
                    ppath = _to_absolute_path(p, self.project_root)
                    if ppath.exists():
                        ppath.unlink()
                except Exception as e:
                    errors.append((p, str(e)))

        if errors:
            cur.close()
            # raise a combined exception so caller knows which files failed
            msgs = "; ".join([f"{p}: {m}" for p, m in errors])
            raise IOError(f"Failed to delete files for measurement {mid}: {msgs}")
        
        # 3) Delete DB row inside transaction
        try:
            cur.execute("DELETE FROM measurements WHERE id = ?", (mid,))
            deleted = cur.rowcount
            self.con.commit()
            cur.close()
            return deleted
        except Exception:
            self.con.rollback()
            cur.close()
            raise
        

    def close(self):
        self.con.close()

    def migrate_paths_to_relative(self):
        cursor = self.con.cursor()
        
        # 1. 获取所有 measurements
        rows = cursor.execute(
            "SELECT id, data_filepath, processed_data_filepath FROM measurements"
        ).fetchall()
        
        if not rows:
            print("No measurements to migrate.")
            return
        
        # 2. 统计和转换
        total = len(rows)
        updated = 0
        errors = []
        
        print(f"Found {total} measurements to check...")
        
        for row in rows:
            mid, data_fp, proc_fp = row
            
            # 检查是否已经是相对路径
            data_path = Path(data_fp) if data_fp else None
            proc_path = Path(proc_fp) if proc_fp else None
            
            # 如果已经是相对路径，跳过
            if data_path and not data_path.is_absolute() and proc_path and not proc_path.is_absolute():
                continue
            
            # 转换为相对路径
            try:
                new_data_fp = _to_relative_path(data_path, self.project_root) if data_path else None
                new_proc_fp = _to_relative_path(proc_path, self.project_root) if proc_path else None
                
                # 更新数据库
                cursor.execute(
                    "UPDATE measurements SET data_filepath = ?, processed_data_filepath = ? WHERE id = ?",
                    (new_data_fp, new_proc_fp, mid)
                )
                updated += 1
                print(f"✅ Migrated measurement {mid}:")
                print(f"   {data_fp} → {new_data_fp}")
                print(f"   {proc_fp} → {new_proc_fp}")
                
            except Exception as e:
                errors.append((mid, str(e)))
                print(f"❌ Failed to migrate measurement {mid}: {e}")
        
        # 3. 提交更改
        if updated > 0:
            try:
                self.con.commit()
                print(f"\n🎉 Successfully migrated {updated}/{total} measurements.")
            except Exception as e:
                self.con.rollback()
                print(f"\n❌ Migration failed, rolled back: {e}")
                raise
        else:
            print("\n✨ All paths are already relative, no migration needed.")
        
        if errors:
            print(f"\n⚠️ Errors occurred for {len(errors)} measurements:")
            for mid, err in errors:
                print(f"   - Measurement {mid}: {err}")
