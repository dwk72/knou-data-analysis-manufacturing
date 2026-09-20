"""
합성(Synthetic) Batch 제조 데이터를 생성하는 스크립트입니다.

목적
- 실제 회사 데이터나 실제 공정조건을 재현하지 않고,
  생산기술 데이터 분석 연습에 사용할 수 있는 데이터셋을 만듭니다.
- 단순 난수표가 아니라 원료 LOT, 설비, 시간 Drift, 공정조건 조합이
  품질과 느슨하게 연결되도록 설계했습니다.
- 어떤 변수 하나만으로 OK/NG가 완벽하게 결정되지 않도록 Noise를 포함합니다.

생성 파일
1. batch_master.csv
2. material.csv
3. process_condition.csv
4. quality_result.csv

재현성
- 아래 코드는 고정된 seed와 단순한 난수 생성 규칙을 사용합니다.
- 같은 코드를 다시 실행하면 같은 데이터가 생성됩니다.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from pathlib import Path


# ---------------------------------------------------------------------
# 0. 기본 설정
# ---------------------------------------------------------------------

N_BATCHES = 800
SEED = 42

# 이 폴더 아래에 4개의 CSV 파일을 생성합니다.
OUT_DIR = Path(__file__).parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# 1. 재현 가능한 난수 생성 도구
# ---------------------------------------------------------------------
# 일반적으로는 numpy.random을 많이 사용하지만,
# 여기서는 저장소에 포함된 CSV를 정확히 다시 만들 수 있도록
# 간단한 난수 생성 규칙을 코드 안에 명시했습니다.

_state = SEED
_spare_normal: float | None = None


def uniform() -> float:
    """0 이상 1 미만의 난수를 하나 생성합니다."""
    global _state

    # Linear Congruential Generator(LCG)
    _state = (1664525 * _state + 1013904223) % (2**32)
    return _state / (2**32)


def normal(mean: float = 0.0, sd: float = 1.0) -> float:
    """평균(mean)과 표준편차(sd)를 가진 정규분포 난수를 생성합니다."""
    global _spare_normal

    # Box-Muller 방법으로 uniform 난수를 정규분포 난수로 변환합니다.
    if _spare_normal is not None:
        z = _spare_normal
        _spare_normal = None
        return mean + sd * z

    u1 = max(uniform(), 1e-12)
    u2 = uniform()

    magnitude = math.sqrt(-2.0 * math.log(u1))
    z0 = magnitude * math.cos(2.0 * math.pi * u2)
    z1 = magnitude * math.sin(2.0 * math.pi * u2)

    _spare_normal = z1
    return mean + sd * z0


def choose_weighted(items: list[str], probabilities: list[float]) -> str:
    """정해진 비율에 따라 항목 하나를 선택합니다."""
    r = uniform()
    cumulative = 0.0

    for item, probability in zip(items, probabilities):
        cumulative += probability
        if r <= cumulative:
            return item

    return items[-1]


def clamp(value: float, low: float, high: float) -> float:
    """값이 너무 작거나 커지지 않도록 범위를 제한합니다."""
    return max(low, min(high, value))


# ---------------------------------------------------------------------
# 2. 시나리오 설정
# ---------------------------------------------------------------------

# 원료 LOT마다 아주 작은 평균 차이를 부여합니다.
# 특정 LOT 하나가 모든 불량을 결정하지는 않도록 효과를 작게 설정했습니다.
LOT_EFFECT = {
    "M01": -0.6, "M02": 0.2, "M03": 0.8, "M04": -0.2,
    "M05": 1.0, "M06": -0.8, "M07": 0.4, "M08": 1.3,
    "M09": -0.4, "M10": 0.6, "M11": -0.1, "M12": 1.1,
}

LOT_RISK = {
    "M01": 0.00, "M02": 0.00, "M03": 0.10, "M04": 0.00,
    "M05": 0.20, "M06": 0.00, "M07": 0.00, "M08": 0.45,
    "M09": 0.00, "M10": 0.10, "M11": 0.00, "M12": 0.35,
}

EQUIPMENT = ["EQ_A", "EQ_B", "EQ_C"]
SHIFTS = ["DAY", "SWING", "NIGHT"]
MATERIAL_LOTS = list(LOT_EFFECT)


# 각 CSV에 들어갈 행을 별도로 보관합니다.
batch_rows: list[list[object]] = []
material_rows: list[list[object]] = []
process_rows: list[list[object]] = []
quality_rows: list[list[object]] = []


# ---------------------------------------------------------------------
# 3. Batch 데이터 생성
# ---------------------------------------------------------------------

start_date = date(2026, 1, 1)

for sequence in range(1, N_BATCHES + 1):

    # 사람이 읽기 쉬운 Batch 번호입니다.
    # 예: 1 -> B0001
    batch_id = f"B{sequence:04d}"

    # 하루에 약 3개 Batch가 생산된다고 가정합니다.
    production_date = start_date + timedelta(days=(sequence - 1) // 3)

    # 설비별 생산량이 완전히 같지는 않도록 비율을 조금 다르게 둡니다.
    equipment_id = choose_weighted(
        EQUIPMENT,
        [0.36, 0.34, 0.30],
    )

    # Shift는 생산순서에 따라 DAY -> SWING -> NIGHT로 반복합니다.
    shift = SHIFTS[(sequence - 1) % 3]

    # 원료 LOT는 일정 기간 같은 LOT를 주로 사용하되,
    # 실제 운영처럼 일부 다른 LOT가 섞이도록 구성합니다.
    base_lot = MATERIAL_LOTS[((sequence - 1) // 67) % len(MATERIAL_LOTS)]

    if uniform() < 0.88:
        material_lot = base_lot
    else:
        material_lot = MATERIAL_LOTS[int(uniform() * len(MATERIAL_LOTS))]

    lot_effect = LOT_EFFECT[material_lot]

    # 원료 대표 물성과 투입비에도 작은 자연 변동을 줍니다.
    raw_property = 100 + lot_effect + normal(0, 0.65)
    feed_ratio = 1.0 + 0.003 * lot_effect + normal(0, 0.009)

    # 설비마다 작은 Offset이 있다고 가정합니다.
    # 특정 설비를 '불량설비'로 만드는 것이 아니라
    # 측정값과 에너지 사용 특성이 조금 다른 정도입니다.
    temperature_offset = {
        "EQ_A": 0.0,
        "EQ_B": 0.7,
        "EQ_C": -0.4,
    }[equipment_id]

    pressure_offset = {
        "EQ_A": 0.000,
        "EQ_B": 0.025,
        "EQ_C": -0.015,
    }[equipment_id]

    energy_offset = {
        "EQ_A": 0.0,
        "EQ_B": 5.0,
        "EQ_C": 2.0,
    }[equipment_id]

    # Batch 500 이후 일부 변수에 서서히 Drift가 발생하도록 합니다.
    # 갑자기 값이 튀는 이상치와 달리, 공정이 천천히 이동하는 상황을 표현합니다.
    drift_progress = max(0, sequence - 500) / 300
    reaction_time_drift = 4.8 * drift_progress
    energy_drift = 16.0 * drift_progress

    # 주요 공정조건을 생성합니다.
    # 각 변수는 완전히 독립된 난수가 아니라 서로 약간 연결되어 있습니다.
    temperature = (
        180
        + temperature_offset
        + 0.12 * (raw_property - 100)
        + normal(0, 2.15)
    )

    pressure = (
        2.30
        + pressure_offset
        + 0.018 * (temperature - 180)
        + normal(0, 0.075)
    )

    feed_rate = 100 - 0.6 * lot_effect + normal(0, 3.8)

    reaction_time = (
        60
        + 0.35 * (100 - feed_rate)
        + reaction_time_drift
        + normal(0, 2.7)
    )

    vacuum = (
        0.82
        - 0.015 * (pressure - 2.30)
        + normal(0, 0.035)
    )

    # 후반부 EQ_C에서는 산포가 조금 증가하도록 설정합니다.
    if equipment_id == "EQ_C" and sequence > 560:
        temperature += normal(0, 0.7 * drift_progress)
        reaction_time += normal(0, 1.0 * drift_progress)

    energy_kwh_per_ton = (
        235
        + 1.15 * (temperature - 180)
        + 0.85 * (reaction_time - 60)
        + energy_offset
        + energy_drift
        + normal(0, 5.5)
    )

    # 중간 품질값도 공정조건과 원료특성의 영향을 일부 받도록 합니다.
    viscosity = (
        430
        + 7.5 * (raw_property - 100)
        + 2.6 * (reaction_time - 60)
        - 1.8 * (temperature - 180)
        + 360 * (feed_ratio - 1.0)
        + normal(0, 10.5)
    )

    particle_size = (
        18
        + 0.32 * (raw_property - 100)
        + 0.08 * (reaction_time - 60)
        + normal(0, 0.58)
    )

    # 최종 연속형 품질값은 기준 운전영역에서 멀어질수록 조금 낮아집니다.
    temperature_penalty = 0.16 * ((temperature - 180) / 2.2) ** 2
    time_penalty = 0.22 * (max(0, reaction_time - 62) / 2.8) ** 2
    raw_penalty = 0.12 * ((raw_property - 100) / 1.2) ** 2
    vacuum_penalty = 0.10 * ((vacuum - 0.82) / 0.04) ** 2

    quality_value = (
        100
        - temperature_penalty
        - time_penalty
        - raw_penalty
        - vacuum_penalty
        + normal(0, 0.48)
    )

    # 수율도 공정조건과 에너지 사용량의 영향을 약하게 받도록 설정합니다.
    yield_pct = (
        97.2
        - 0.30 * abs(temperature - 180)
        - 0.18 * max(0, reaction_time - 62)
        - 0.10 * abs(raw_property - 100)
        - 0.035 * max(0, energy_kwh_per_ton - 240)
        + normal(0, 0.55)
    )

    # 품질판정은 단일 변수 하나가 아니라 여러 조건의 조합으로 결정합니다.
    # 여기에 Random Noise도 더해 모델이 정답을 너무 쉽게 맞히지 않도록 합니다.
    interaction = (
        0.75
        if reaction_time > 63.5 and raw_property > 100.7
        else 0.0
    )

    risk_logit = (
        -2.35
        + 0.42 * abs(temperature - 180) / 2.2
        + 0.50 * max(0, reaction_time - 63) / 3.0
        + 0.33 * max(0, pressure - 2.38) / 0.08
        + LOT_RISK[material_lot]
        + (0.12 if equipment_id == "EQ_B" else 0.0)
        + (
            0.22 * drift_progress
            if equipment_id == "EQ_C" and sequence > 560
            else 0.0
        )
        + 0.48 * drift_progress
        + interaction
        + normal(0, 0.45)
    )

    probability_ng = 1 / (1 + math.exp(-risk_logit))
    quality_flag = "NG" if uniform() < probability_ng else "OK"

    # 각 테이블에 해당하는 값만 나누어 저장합니다.
    batch_rows.append([
        batch_id,
        production_date.isoformat(),
        equipment_id,
        shift,
        sequence,
    ])

    material_rows.append([
        batch_id,
        material_lot,
        f"{feed_ratio:.4f}",
        f"{raw_property:.2f}",
    ])

    process_rows.append([
        batch_id,
        f"{temperature:.2f}",
        f"{pressure:.3f}",
        f"{feed_rate:.2f}",
        f"{reaction_time:.2f}",
        f"{vacuum:.3f}",
        f"{energy_kwh_per_ton:.2f}",
    ])

    quality_rows.append([
        batch_id,
        f"{viscosity:.1f}",
        f"{particle_size:.2f}",
        f"{quality_value:.2f}",
        f"{clamp(yield_pct, 88, 99.5):.2f}",
        quality_flag,
    ])


# ---------------------------------------------------------------------
# 4. 데이터 품질 문제 추가
# ---------------------------------------------------------------------
# 현실적인 분석 연습을 위해 아주 적은 양의 결측치와 센서성 이상값을 넣습니다.
# 중요한 점은 이 값들이 모든 NG의 원인이 되도록 만들지 않는 것입니다.

def set_missing(rows: list[list[object]], column_index: int, count: int) -> None:
    """지정한 열에 소량의 결측치를 삽입합니다."""
    selected: set[int] = set()

    while len(selected) < count:
        index = int(uniform() * len(rows))

        if index not in selected:
            selected.add(index)
            rows[index][column_index] = ""


set_missing(process_rows, 1, 8)   # temperature 약 1%
set_missing(process_rows, 5, 8)   # vacuum 약 1%
set_missing(quality_rows, 1, 5)   # viscosity 약 0.6%
set_missing(material_rows, 3, 4)  # raw_property 약 0.5%

# 극소수의 센서성 이상값을 추가합니다.
for _ in range(3):
    index = int(uniform() * len(process_rows))
    if process_rows[index][1] != "":
        process_rows[index][1] = f"{float(process_rows[index][1]) + 12:.2f}"

for _ in range(3):
    index = int(uniform() * len(process_rows))
    if process_rows[index][2] != "":
        process_rows[index][2] = f"{float(process_rows[index][2]) + 0.65:.3f}"


# ---------------------------------------------------------------------
# 5. CSV 저장
# ---------------------------------------------------------------------

def write_csv(filename: str, header: list[str], rows: list[list[object]]) -> None:
    """표 데이터를 쉼표로 구분된 CSV 파일로 저장합니다."""
    path = OUT_DIR / filename

    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(",".join(header) + "\n")

        for row in rows:
            file.write(",".join(str(value) for value in row) + "\n")


write_csv(
    "batch_master.csv",
    ["batch_id", "production_date", "equipment_id", "shift", "sequence"],
    batch_rows,
)

write_csv(
    "material.csv",
    ["batch_id", "material_lot", "feed_ratio", "raw_property"],
    material_rows,
)

write_csv(
    "process_condition.csv",
    [
        "batch_id",
        "temperature",
        "pressure",
        "feed_rate",
        "reaction_time",
        "vacuum",
        "energy_kwh_per_ton",
    ],
    process_rows,
)

write_csv(
    "quality_result.csv",
    [
        "batch_id",
        "viscosity",
        "particle_size",
        "quality_value",
        "yield_pct",
        "quality_flag",
    ],
    quality_rows,
)

print(f"Generated {N_BATCHES} synthetic batches in: {OUT_DIR}")
print("Files:")
print("- batch_master.csv")
print("- material.csv")
print("- process_condition.csv")
print("- quality_result.csv")
