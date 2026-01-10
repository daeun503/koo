# AGENTS.md

이 문서는 이 저장소에서 작업하는 에이전틱 코딩 에이전트(예: Codex, Cursor, Copilot Agent 등)를 위한 가이드입니다. 프로젝트의 빌드, 린트, 테스트 방법과 함께 코드 스타일 및 기여 규칙을 정의합니다.

이 파일의 적용 범위는 저장소 전체입니다.

---

## 프로젝트 개요

- 언어: Python 3.12+
- 패키징: Poetry
- CLI 프레임워크: Typer
- ORM / DB: SQLAlchemy, Alembic
- 설정 / 검증: Pydantic, pydantic-settings
- 외부 API / HTTP: OpenAI, httpx, requests
- 린터: Ruff

---

## 개발 환경 설정

- Python `>=3.12,<4` 설치 필요
- Poetry를 사용하여 의존성 설치:
  - `poetry install`
- 가상 환경 활성화:
  - `poetry shell`

---

## 빌드 / 린트 / 테스트 명령어

### 빌드

- 패키지 빌드:
  - `poetry build`
- 로컬 editable 설치:
  - `poetry install`

### CLI 실행

- 엔트리 포인트:
  - `koo = app.cli:app`
- 예시:
  - `poetry run koo --help`

### 린트 (Ruff)

- 전체 프로젝트 린트 실행:
  - `poetry run ruff check .`
- 자동 수정 가능한 항목만 수정:
  - `poetry run ruff check . --fix`
- 특정 파일만 린트:
  - `poetry run ruff check app/models/base.py`

### 포매팅

- Ruff는 린트 전용으로 사용됨
- 포매팅 규칙:
  - 최대 줄 길이: 120자
- 별도의 포매터(Black 등)는 명시적 요청 없이는 추가하지 말 것

### 테스트

- pytest가 존재하거나 추가된 경우 전체 테스트 실행:
  - `poetry run pytest`

### 단일 테스트 실행 방법 (중요)

- 특정 테스트 파일 실행:
  - `poetry run pytest tests/test_example.py`
- 특정 테스트 함수 / 케이스 실행:
  - `poetry run pytest -k "test_name"`
- 자세한 출력으로 실행:
  - `poetry run pytest -vv`

---

## 코드 스타일 가이드

### 일반 원칙

- 똑똑해 보이는 코드보다 **명확한 코드**를 우선할 것
- 변경 사항은 최소화하고, 목적에 집중할 것
- 관련 없는 코드 수정은 피할 것
- 기존 코드베이스의 패턴을 반드시 따를 것

### Import 규칙

- 가능하면 프로젝트 내부에서는 절대 경로 import 사용
- Import 순서:
  1. 표준 라이브러리
  2. 서드파티 라이브러리
  3. 로컬 애플리케이션 모듈
- 각 그룹 사이에는 빈 줄 추가
- `*` 와일드카드 import 금지

예시:
```python
from typing import Optional

import httpx
from sqlalchemy import select

from app.models.base import Base
```

### 포매팅 규칙

- 들여쓰기: 공백 4칸
- 한 줄 최대 길이: 120자
- 여러 줄 컬렉션에는 trailing comma 사용
- 역슬래시(`\\`) 대신 괄호를 사용해 줄 나누기

### 타입 힌트

- 모든 함수와 공개 속성에 타입 힌트 사용
- 다음 항목은 반드시 명시적으로 타입 지정:
  - 함수 인자
  - 반환 타입
  - 클래스의 공개 속성
- `list[str]`, `dict[str, Any]` 등 최신 typing 문법 사용
- `Optional[T]`는 `None`이 실제로 가능한 경우에만 사용

### 네이밍 규칙

- 변수 / 함수: `snake_case`
- 클래스 / 예외: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`
- Enum:
  - Enum 클래스: `PascalCase`
  - Enum 멤버: `UPPER_SNAKE_CASE`
- 파일 / 모듈명: `snake_case.py`

### 에러 처리

- `except:` 같은 포괄적 예외 처리 금지
- 실제로 처리 가능한 경우에만 예외를 catch할 것
- 의미 있는 메시지와 함께 예외를 재발생(re-raise)할 것
- 에러를 조용히 무시하지 말 것

예시:
```python
try:
    result = client.call()
except httpx.HTTPError as exc:
    raise RuntimeError("외부 API 요청 실패") from exc
```

### 비동기 코드

- 동기 API와 비동기 API를 명확히 분리할 것
- `async` 함수 내부에서 블로킹 I/O 사용 금지
- `async` / `await`를 일관되게 사용할 것

### 설정 및 시크릿

- 설정 값은 `pydantic-settings` 사용
- 시크릿을 코드에 하드코딩하지 말 것
- 필요한 환경 변수는 `.env.sample` 참고

---

## 데이터베이스 & 마이그레이션

- SQLAlchemy 모델 위치: `app/models`
- 마이그레이션 도구: Alembic
- 새 마이그레이션 생성:
  - `poetry run alembic revision --autogenerate -m "메시지"`
- 마이그레이션 적용:
  - `poetry run alembic upgrade head`

---

## Ruff 규칙

- Ruff 설정은 `pyproject.toml`에 정의됨
- 제외 경로 예시:
  - `alembic/`
  - 가상 환경 디렉터리
- 정당한 이유 없이 Ruff 규칙을 비활성화하지 말 것

---

## Cursor / Copilot 가이드라인

- `.cursor/rules/` 또는 `.cursorrules` 파일 없음
- `.github/copilot-instructions.md` 파일 없음

일반 지침:
- AI가 생성한 코드는 반드시 사람이 검토할 것
- 이 문서의 규칙을 항상 우선 적용할 것
- 기존 코드 스타일과 구조를 깨지 말 것

---

이 문서는 사람과 에이전틱 코딩 시스템 모두가 일관되고 유지보수 가능한 코드를 작성하기 위한 기준입니다.