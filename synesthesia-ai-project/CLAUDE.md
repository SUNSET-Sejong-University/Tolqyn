# Synesthesia Media Art - Brain Engine

## 프로젝트 개요

실시간 오디오 입력을 AI 에이전트가 분석하여 공감각적 시각화 명령을 생성하는 미디어 아트 프로젝트입니다.
SpoonOS 프레임워크를 활용한 AI 에이전트가 소리를 "듣고" 해석하여, 시각적 표현으로 변환하는 실시간 공감각 시스템을 구현합니다.

## 핵심 아이디어

**공감각(Synesthesia)**: 소리 → 색상/형태/움직임 매핑
- AI 에이전트가 오디오의 주파수, 진폭, 리듬 패턴을 분석
- 학습된 공감각 모델을 통해 시각적 파라미터로 변환
- OSC 프로토콜로 Java 시각화 엔진에 실시간 전송

## 현재 구현 범위 (Phase 1)

```
brain_engine/ (Python - SpoonOS & AI)
│   ├── main_agent.py          # SpoonOS 에이전트: 오디오 해석 및 시각화 명령 생성
│   ├── audio_processor.py      # 실시간 마이크 입력 및 FFT/MFCC 특징 추출
│   ├── bridge_osc.py           # Java 비주얼라이저로 OSC 메시지 전송 로직
│   ├── models/                 # 공감각 학습 모델 (소리-색상 매핑 가중치)
│   └── config/
│       └── mapping_rules.json  # AI가 실시간으로 갱신하는 공감각 물리 법칙
```

## 기술 스택

### Python (Brain Engine)
- **SpoonOS**: AI 에이전트 프레임워크
- **sounddevice**: 실시간 마이크 입력
- **numpy/scipy**: FFT, MFCC 오디오 특징 추출
- **python-osc**: OSC 프로토콜로 시각화 엔진과 통신
- **OpenAI/Anthropic API**: 공감각 매핑 해석 및 학습

### 오디오 처리
- FFT (Fast Fourier Transform): 주파수 스펙트럼 분석
- MFCC (Mel-Frequency Cepstral Coefficients): 음색 특징 추출
- Onset Detection: 리듬/비트 감지
- RMS Energy: 소리 강도 측정

### OSC (Open Sound Control)
- Python → Java 실시간 메시지 전송
- 낮은 레이턴시로 시각화 파라미터 전달

## 컴포넌트 설명

### 1. main_agent.py
**SpoonOS AI 에이전트 메인 로직**
- 오디오 프로세서에서 특징 데이터 수신
- AI 모델을 통한 공감각 해석
  - 저주파 → 따뜻한 색상 (빨강, 주황)
  - 고주파 → 차가운 색상 (파랑, 보라)
  - 리듬 → 움직임 속도/강도
  - 음량 → 입자 밀도/크기
- OSC 브릿지를 통해 시각화 명령 전송
- 실시간으로 mapping_rules.json 갱신 (학습)

### 2. audio_processor.py
**실시간 오디오 분석 엔진**
- 마이크 입력 캡처 (sounddevice)
- 실시간 FFT 계산 (주파수 스펙트럼)
- MFCC 특징 추출 (음색 분석)
- Onset detection (비트/리듬 감지)
- 추출된 특징을 main_agent로 전달

**출력 데이터:**
```json
{
  "timestamp": 1234567890,
  "spectrum": [0.1, 0.3, 0.5, ...],  // FFT 결과
  "mfcc": [12.3, -4.5, ...],         // MFCC 계수
  "rms": 0.65,                        // 음량
  "onset": true,                      // 비트 감지
  "dominant_freq": 440.0              // 주요 주파수
}
```

### 3. bridge_osc.py
**OSC 통신 브릿지**
- python-osc 라이브러리 사용
- Java Processing/OpenFrameworks 시각화 엔진으로 전송
- 메시지 포맷 정의

**OSC 메시지 예시:**
```
/visual/color r g b          # 색상 변경
/visual/particles count size # 입자 파라미터
/visual/motion speed angle   # 움직임 제어
/visual/energy level         # 에너지 레벨
```

### 4. models/
**공감각 매핑 모델**
- 소리 특징 → 시각 파라미터 변환 가중치
- AI가 사용자 반응/패턴을 학습하여 갱신
- 초기값: 기본 공감각 연구 기반 매핑

**모델 구조 (예시):**
```python
{
  "frequency_to_hue": {
    "low": (0, 60),      # 0-500Hz → Red-Orange
    "mid": (60, 180),    # 500-2000Hz → Yellow-Cyan
    "high": (180, 300)   # 2000Hz+ → Blue-Purple
  },
  "amplitude_to_brightness": "linear",
  "onset_to_pulse": {"intensity": 0.8, "duration": 200}
}
```

### 5. config/mapping_rules.json
**공감각 물리 법칙**
- AI 에이전트가 실시간 갱신
- 사용자 선호도 학습
- 컨텍스트 기반 매핑 조정

```json
{
  "version": "1.0",
  "last_updated": "2025-12-20T...",
  "rules": {
    "color_mapping": {
      "frequency_ranges": {
        "bass": {"hz": [20, 250], "hue": [0, 30], "saturation": 0.8},
        "mid": {"hz": [250, 2000], "hue": [60, 180], "saturation": 0.6},
        "treble": {"hz": [2000, 20000], "hue": [200, 280], "saturation": 0.9}
      }
    },
    "motion_mapping": {
      "onset_velocity": 0.75,
      "decay_rate": 0.95
    },
    "particle_mapping": {
      "energy_to_count": "exponential",
      "size_range": [5, 50]
    }
  },
  "learning_params": {
    "adaptation_rate": 0.1,
    "user_feedback_weight": 0.3
  }
}
```

## 데이터 플로우

```
[마이크 입력]
    ↓
[audio_processor.py]
    ↓ (오디오 특징)
[main_agent.py] ←→ [SpoonOS AI]
    ↓ (시각화 명령)
[bridge_osc.py]
    ↓ (OSC 메시지)
[Java 시각화 엔진]
    ↓
[화면 출력]
```

## 다음 단계 (Phase 2 - 현재는 구현 안 함)

- Java/Processing 시각화 엔진 개발
- WebSocket 기반 웹 인터페이스
- 사용자 피드백 수집 시스템
- 고급 학습 모델 (강화학습)
- 다중 오디오 소스 지원

## 개발 가이드라인

### Phase 1 구현 우선순위

1. **audio_processor.py** - 오디오 입력 및 특징 추출 (가장 기본)
2. **bridge_osc.py** - OSC 통신 레이어
3. **main_agent.py** - SpoonOS 에이전트 로직
4. **models/** - 기본 매핑 모델
5. **config/mapping_rules.json** - 초기 룰셋

### 코딩 원칙

- 모듈화: 각 컴포넌트는 독립적으로 테스트 가능
- 실시간성: 오디오 처리는 낮은 레이턴시 유지 (<30ms)
- 확장성: 나중에 시각화 엔진 교체 가능하도록 OSC 인터페이스 표준화
- 학습 가능: AI 에이전트가 mapping_rules를 동적으로 수정 가능
- AI에이전트 코드는 spoonos 프레임워크사용

### 테스트 방법

1. audio_processor 단독 테스트: 마이크 입력 → FFT 출력 확인
2. OSC 브릿지 테스트: OSC 리시버로 메시지 수신 확인
3. 통합 테스트: 소리 입력 → OSC 메시지 출력까지 전체 파이프라인

## 환경 설정

```bash
# 필수 라이브러리
pip install sounddevice numpy scipy python-osc librosa

# SpoonOS (향후 추가)
# pip install spoon-os
```

## 실행 방법 (구현 후)

```bash
cd brain_engine
python main_agent.py
```

## 참고 자료

- **공감각 연구**: Synesthesia and sound symbolism
- **오디오 특징 추출**: librosa documentation
- **OSC 프로토콜**: opensoundcontrol.org
- **SpoonOS**: https://xspoonai.github.io/
- **How to use spoonos** : https://xspoonai.github.io/docs/how-to-guides/build-first-agent/

---

**현재 상태**: 설계 단계 (코드 미작성)
**다음 작업**: brain_engine/ 폴더 구조 생성 및 각 모듈 구현 시작 