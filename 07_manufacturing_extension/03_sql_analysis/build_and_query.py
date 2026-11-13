"""
합성 제조 CSV 4개를 SQLite 데이터베이스에 적재하고 제조 KPI SQL을 실행합니다.

이 코드는 'SQL 문법을 많이 보여주는 것'보다 다음 흐름을 보여주는 데 목적이 있습니다.

1. 서로 다른 생산·원료·공정·품질 테이블을 관계형 구조로 저장한다.
2. Primary Key / Foreign Key로 Batch 관계를 명시한다.
3. JOIN, GROUP BY, CTE, Window Function을 실제 제조 질문에 사용한다.
4. SQL 결과를 CSV로 저장해 사람이 검토할 수 있게 한다.

실제 회사 데이터가 아니라 generate_synthetic_data.py에서 생성한 학습용 합성 데이터입니다.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
SQL_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

QUERY_FILES = (
    "01_join_sample.sql",
    "02_equipment_kpi.sql",
    "03_material_lot_kpi.sql",
    "04_before_after_drift.sql",
    "05_rolling_40_ng_rate.sql",
    "06_equipment_energy_rank.sql",
)


def blank_to_none(value: str) -> str | None:
    """빈 문자열은 SQLite의 NULL로 바꿉니다."""
    return None if value == "" else value


def read_rows(file_name: str) -> list[dict[str, str]]:
    """CSV 파일을 열어 각 행을 딕셔너리 형태로 읽습니다."""
    path = DATA_DIR / file_name
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def create_schema(connection: sqlite3.Connection) -> None:
    """schema.sql에 정의한 테이블·키·인덱스를 생성합니다."""
    schema = (SQL_DIR / "schema.sql").read_text(encoding="utf-8")
    connection.executescript(schema)


def load_source_data(connection: sqlite3.Connection) -> None:
    """4개 CSV를 각각 대응하는 SQLite 테이블에 적재합니다."""

    # batch_master는 모든 다른 테이블이 참조하므로 가장 먼저 넣습니다.
    batch_rows = read_rows("batch_master.csv")
    connection.executemany(
        """
        INSERT INTO batch_master
            (batch_id, production_date, equipment_id, shift, sequence)
        VALUES
            (:batch_id, :production_date, :equipment_id, :shift, :sequence)
        """,
        [
            {
                **row,
                "sequence": int(row["sequence"]),
            }
            for row in batch_rows
        ],
    )

    # 숫자형 열의 빈 값은 0이 아니라 NULL로 보존합니다.
    # '측정되지 않음'과 실제 숫자 0은 의미가 다르기 때문입니다.
    material_rows = read_rows("material.csv")
    connection.executemany(
        """
        INSERT INTO material
            (batch_id, material_lot, feed_ratio, raw_property)
        VALUES
            (:batch_id, :material_lot, :feed_ratio, :raw_property)
        """,
        [
            {
                "batch_id": row["batch_id"],
                "material_lot": row["material_lot"],
                "feed_ratio": blank_to_none(row["feed_ratio"]),
                "raw_property": blank_to_none(row["raw_property"]),
            }
            for row in material_rows
        ],
    )

    process_rows = read_rows("process_condition.csv")
    connection.executemany(
        """
        INSERT INTO process_condition
            (
                batch_id,
                temperature,
                pressure,
                feed_rate,
                reaction_time,
                vacuum,
                energy_kwh_per_ton
            )
        VALUES
            (
                :batch_id,
                :temperature,
                :pressure,
                :feed_rate,
                :reaction_time,
                :vacuum,
                :energy_kwh_per_ton
            )
        """,
        [
            {
                key: blank_to_none(value)
                for key, value in row.items()
            }
            for row in process_rows
        ],
    )

    quality_rows = read_rows("quality_result.csv")
    connection.executemany(
        """
        INSERT INTO quality_result
            (
                batch_id,
                viscosity,
                particle_size,
                quality_value,
                yield_pct,
                quality_flag
            )
        VALUES
            (
                :batch_id,
                :viscosity,
                :particle_size,
                :quality_value,
                :yield_pct,
                :quality_flag
            )
        """,
        [
            {
                key: (
                    value
                    if key in {"batch_id", "quality_flag"}
                    else blank_to_none(value)
                )
                for key, value in row.items()
            }
            for row in quality_rows
        ],
    )

    connection.commit()


def validate_database(connection: sqlite3.Connection) -> None:
    """적재 후 행 수와 Foreign Key 무결성을 확인합니다."""
    expected_rows = {
        "batch_master": 800,
        "material": 800,
        "process_condition": 800,
        "quality_result": 800,
    }

    for table_name, expected in expected_rows.items():
        count = connection.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        if count != expected:
            raise RuntimeError(
                f"{table_name}: expected {expected} rows, got {count}"
            )

    foreign_key_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if foreign_key_errors:
        raise RuntimeError(
            f"Foreign key validation failed: {foreign_key_errors}"
        )


def write_query_result(
    connection: sqlite3.Connection,
    query_path: Path,
    output_path: Path,
) -> None:
    """SQL 한 개를 실행하고 조회 결과를 CSV로 저장합니다."""
    query = query_path.read_text(encoding="utf-8")
    cursor = connection.execute(query)

    header = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    with output_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def run(database_path: Path, output_dir: Path) -> None:
    """데이터베이스 생성부터 SQL 결과 저장까지 전체 과정을 실행합니다."""
    output_dir.mkdir(parents=True, exist_ok=True)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    # 이전 실행의 DB가 남아 있으면 새로 생성합니다.
    if database_path.exists():
        database_path.unlink()

    connection = sqlite3.connect(database_path)

    try:
        # SQLite는 연결마다 Foreign Key 검사를 활성화해야 합니다.
        connection.execute("PRAGMA foreign_keys = ON")

        create_schema(connection)
        load_source_data(connection)
        validate_database(connection)

        for file_name in QUERY_FILES:
            query_path = SQL_DIR / "queries" / file_name
            output_path = output_dir / file_name.replace(".sql", ".csv")

            write_query_result(
                connection,
                query_path,
                output_path,
            )
    finally:
        connection.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database",
        type=Path,
        default=SQL_DIR / "output" / "manufacturing.db",
        help="생성할 SQLite DB 경로",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SQL_DIR / "output",
        help="SQL 조회 결과 CSV를 저장할 폴더",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.database, args.output_dir)

    print(f"SQLite database: {args.database}")
    print(f"Query outputs   : {args.output_dir}")
