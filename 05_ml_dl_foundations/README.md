> 복원 현황 (2026-11-05): 제출한 머신러닝 과제 PDF에서 MNIST PyTorch 코드 캡처를 확인했습니다. 이를 토대로 [mnist_reconstructed.py](./mnist_reconstructed.py)를 다시 작성했습니다. 전체 원본 노트북을 확보한 것은 아니므로 정확한 원본 코드와 동일하다고 주장하지 않습니다.

- 제출 과제에서 확인한 구조: 784→512→256→10, ReLU, Adam, 학습률 0.001, CrossEntropyLoss, 10 epochs
- 새 코드는 PyTorch 2.10.0 환경에서 합성 이미지 8개를 이용한 1회 학습 업데이트 및 출력 차원 확인을 통과했습니다.
- 실제 MNIST 학습을 실행하려면 torchvision과 데이터가 필요합니다. 로컬에서 아래 명령으로 사전 검증하거나, --download 옵션으로 데이터셋 다운로드를 명시적으로 허용할 수 있습니다.

~~~bash
python 05_ml_dl_foundations/mnist_reconstructed.py --smoke-test
python 05_ml_dl_foundations/mnist_reconstructed.py --download --epochs 10
~~~

- 제출 보고서에 기재된 정확도 97.82%는 과거 스크린샷의 기록이며, 복원 코드에서 재현 검증한 성능이 아닙니다.

---

# 05. ML / DL Foundations

## 이 프로젝트에서 한 일

KNOU 머신러닝·딥러닝 과제에서 신경망 모델의 구조와 학습조건을 직접 바꾸고 결과를 비교했습니다.

목적은 모델을 단순 실행하는 것이 아니라, **구조와 학습조건을 바꾸면 결과가 어떻게 달라지는지 이해하는 것**이었습니다.

### PyTorch MNIST 실험

MNIST는 손글씨 숫자 이미지를 분류하는 대표적인 학습용 데이터셋입니다.

과제에서 수행한 변경:
- 기존 신경망에 256차원 은닉층 추가
- ReLU 활성화함수 추가
- 학습 알고리즘을 SGD에서 Adam으로 변경
- Learning rate를 0.01에서 0.001로 변경
- 분류문제에 적합한 `CrossEntropyLoss` 사용
- 변경 후 성능 비교

### TensorFlow / 신경망 학습

다음 내용을 학습했습니다.

- 입력값이 모델을 통과하는 순전파
- 예측오차를 계산하는 손실함수
- 오차를 반대로 전달하는 역전파
- 가중치를 수정하는 최적화 과정
- `tf.GradientTape`를 이용한 자동미분
- 하이퍼파라미터 변경에 따른 결과 비교

## 사용 기술

`PyTorch` · `TensorFlow` · `MNIST` · `ReLU` · `Adam` · `Learning Rate` · `CrossEntropyLoss`

## 제조업과의 연결 방향

현재 ML/DL 과제는 제조 데이터를 사용하지 않았습니다.

향후 적용 가능성이 있는 영역:
- 품질 분류
- 이상상태 분류
- 이미지 기반 결함 탐지
- 설비 이상감지

다만 이 저장소에서는 모델을 복잡하게 만드는 것보다 **문제 정의 → 데이터 정리 → EDA → 통계적 해석**을 먼저 수행하고, 필요한 경우에만 ML/DL로 확장하는 순서를 유지합니다.
