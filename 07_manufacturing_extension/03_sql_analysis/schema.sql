PRAGMA foreign_keys = ON;

-- Batch 기본정보: 한 Batch당 한 행
CREATE TABLE batch_master (
    batch_id TEXT PRIMARY KEY,
    production_date TEXT NOT NULL,
    equipment_id TEXT NOT NULL,
    shift TEXT NOT NULL CHECK (shift IN ('DAY', 'SWING', 'NIGHT')),
    sequence INTEGER NOT NULL UNIQUE
);

-- 원료 정보: batch_master와 1:1 관계
CREATE TABLE material (
    batch_id TEXT PRIMARY KEY,
    material_lot TEXT NOT NULL,
    feed_ratio REAL,
    raw_property REAL,
    FOREIGN KEY (batch_id) REFERENCES batch_master(batch_id)
);

-- 공정조건: 센서·운전기록의 결측을 허용
CREATE TABLE process_condition (
    batch_id TEXT PRIMARY KEY,
    temperature REAL,
    pressure REAL,
    feed_rate REAL,
    reaction_time REAL,
    vacuum REAL,
    energy_kwh_per_ton REAL,
    FOREIGN KEY (batch_id) REFERENCES batch_master(batch_id)
);

-- 품질결과: 품질 측정값 일부는 결측일 수 있음
CREATE TABLE quality_result (
    batch_id TEXT PRIMARY KEY,
    viscosity REAL,
    particle_size REAL,
    quality_value REAL,
    yield_pct REAL,
    quality_flag TEXT NOT NULL CHECK (quality_flag IN ('OK', 'NG')),
    FOREIGN KEY (batch_id) REFERENCES batch_master(batch_id)
);

CREATE INDEX idx_batch_equipment ON batch_master(equipment_id);
CREATE INDEX idx_material_lot ON material(material_lot);
CREATE INDEX idx_quality_flag ON quality_result(quality_flag);
