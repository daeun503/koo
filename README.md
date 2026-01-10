# KOO

KOO는 다양한 외부 서비스(API, LLM, 데이터베이스)를 연결하고 자동화하기 위한 **Python 기반 CLI 애플리케이션**입니다.  
Typer를 기반으로 한 명령줄 인터페이스를 제공하며, SQLAlchemy + Alembic을 이용한 데이터 관리, Pydantic 기반 설정 관리, OpenAI 및 외부 API 연동을 중심으로 설계되었습니다.

이 프로젝트는 **명확성, 확장성, 유지보수성**을 목표로 합니다.

---

## 주요 특징

- ✅ Python 3.12+ 기반
- ✅ Typer 기반 CLI 애플리케이션
- ✅ SQLAlchemy ORM + Alembic 마이그레이션
- ✅ Pydantic / pydantic-settings 기반 설정 관리
- ✅ OpenAI 및 외부 API 연동 구조
- ✅ Ruff 기반 정적 분석 및 코드 품질 관리
- ✅ Poetry 기반 패키징 및 의존성 관리

---

## 프로젝트 구조

```text
koo/
├── app/
│   ├── __init__.py
│   ├── cli.py            # CLI 엔트리 포인트
│   ├── enums.py          # 공통 Enum 정의
│   └── models/           # SQLAlchemy 모델
│       ├── __init__.py
│       ├── base.py
│       └── llm.py
├── alembic/              # DB 마이그레이션
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── config.py             # 전역 설정
├── pyproject.toml        # 프로젝트 설정
├── poetry.lock
├── .env.sample           # 환경 변수 예시
├── AGENTS.md             # 에이전틱 코딩 가이드
└── README.md
```

---

## 요구 사항

- Python `>=3.12,<4`
- Poetry `>=1.7`

---

## 설치 방법

### 1. 저장소 클론

```bash
git clone <repository-url>
cd koo
```

### 2. 의존성 설치

```bash
poetry install
```

### 3. 가상 환경 활성화

```bash
poetry shell
```

---

## 환경 변수 설정

필요한 환경 변수는 `.env.sample` 파일에 정의되어 있습니다.

```bash
cp .env.sample .env
```

`.env` 파일을 열어 각 API 키 및 설정 값을 입력하세요.

> ⚠️ `.env` 파일은 절대 Git에 커밋하지 마세요.

---

## CLI 사용 방법

### CLI 엔트리 포인트

```text
koo = app.cli:app
```

### 도움말 확인

```bash
poetry run koo --help
```

### 예시

```bash
poetry run koo some-command --option value
```

(구체적인 명령어는 CLI 구현에 따라 확장됩니다.)

---

## 데이터베이스 & 마이그레이션

### 마이그레이션 생성

```bash
poetry run alembic revision --autogenerate -m "메시지"
```

### 마이그레이션 적용

```bash
poetry run alembic upgrade head
```

---

## 코드 품질 관리

### 린트 (Ruff)

```bash
poetry run ruff check .
```

자동 수정 가능한 항목만 수정하려면:

```bash
poetry run ruff check . --fix
```

---

## 테스트

현재 테스트 구조는 확장 가능하도록 설계되어 있습니다.

### 전체 테스트 실행

```bash
poetry run pytest
```

### 단일 테스트 실행

```bash
poetry run pytest tests/test_example.py
```

```bash
poetry run pytest -k "test_name"
```

---

## 개발 원칙

- 명확한 코드가 똑똑한 코드보다 우선
- 최소 변경, 목적 중심 개발
- 강한 타입 힌트와 명시적 에러 처리
- 설정과 비즈니스 로직 분리

자세한 규칙은 `AGENTS.md`를 참고하세요.

---

## 기여 가이드

1. 새로운 기능은 작은 단위로 구현
2. Ruff 린트 통과 필수
3. 마이그레이션 변경 시 Alembic 사용
4. 설정 값은 반드시 환경 변수로 관리

---

## 라이선스

현재 라이선스는 명시되어 있지 않습니다.
필요 시 추후 추가될 수 있습니다.

---

## 문의

- Author: daeun503
- Email: zerozero7bang@gmail.com

---

이 README는 사람과 에이전틱 코딩 시스템 모두가 프로젝트를 빠르게 이해하고 기여할 수 있도록 작성되었습니다.