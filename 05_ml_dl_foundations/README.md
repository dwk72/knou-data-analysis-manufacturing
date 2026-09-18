# 05. ML / DL Foundations

## Academic Foundation

KNOU 머신러닝 및 딥러닝 관련 과제에서 모델 구조와 학습 설정을 변경하고 결과를 비교하는 실습을 수행했습니다.

### PyTorch MNIST Experiment
과제에서 수행한 변경:
- 512차원 → 10차원 구조 사이에 256차원 hidden layer 추가
- hidden layer 뒤 ReLU 적용
- optimizer를 SGD에서 Adam으로 변경
- learning rate를 0.01에서 0.001로 변경
- 분류문제에 `CrossEntropyLoss` 유지
- 변경 후 Test 결과 비교

이 실습의 핵심은 단순히 모델을 실행하는 것이 아니라 **구조·optimizer·learning rate 변경이 학습에 미치는 영향을 비교하는 것**이었습니다.

### TensorFlow / Neural Network Study
딥러닝 과제에서는 다음 내용을 학습했습니다.
- Perceptron / MLP
- Forward propagation
- Backpropagation
- Loss function
- Gradient-based optimization
- `tf.GradientTape` 기반 자동미분 개념
- 신경망 하이퍼파라미터 비교

## Skills Demonstrated

`PyTorch` · `TensorFlow` · `MNIST` · `ReLU` · `Adam` · `Learning Rate` · `CrossEntropyLoss`

## Manufacturing Relevance — Planned

현재 ML/DL 실습은 제조 데이터를 사용하지 않았습니다. 제조 확장은 EDA·통계분석 이후 필요한 경우에만 진행할 계획입니다.

예정 적용 후보:
- 품질 분류
- 이상 상태 분류
- 이미지 기반 결함 탐지
- 예지보전 / 이상감지

이 저장소에서는 **ML/DL 자체보다 제조문제 정의와 데이터 품질, EDA, 통계적 해석을 우선**합니다.
