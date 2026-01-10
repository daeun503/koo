# AGENTS.md

이 문서는 이 저장소에서 작업하는 에이전틱 코딩 에이전트를 위한 가이드입니다. 빌드, 린트, 테스트 방법과 코드 스타일 및 기여 규칙을 정의합니다.

## 프로젝트 개요

- 언어: Python 3.12+
- 패키징: Poetry
- CLI 프레임워크: Typer
- ORM / DB: SQLAlchemy, Alembic
- 설정: pydantic-settings
- 의존성 주입: dependency-injector
- 외부 API: OpenAI, httpx, requests
- 린터: Ruff

---

## 개발 환경 설정

```bash
poetry install && poetry shell
```

---

## 빌드 / 린트 / 테스트 명령어

### 빌드

- 패키지 빌드: `poetry build`
- 로컬 editable 설치: `poetry install`

### CLI 실행

- 엔트리 포인트: `koo = app.cli:app`
- 예시: `poetry run koo --help`

### 린트 (Ruff)

- 전체 프로젝트: `poetry run ruff check .`
- 자동 수정: `poetry run ruff check . --fix`
- 특정 파일: `poetry run ruff check app/models/base.py`

### 포매팅

- Ruff는 린트 전용으로 사용됨
- 최대 줄 길이: 120자
- 별도의 포매터는 명시적 요청 없이 추가하지 말 것

### 테스트

- 전체 테스트: `poetry run pytest`
- 특정 파일: `poetry run pytest tests/test_example.py`
- 특정 테스트: `poetry run pytest -k "test_name"`
- 자세한 출력: `poetry run pytest -vv`

---

## 코드 스타일 가이드

### 일반 원칙

- 똑똑해 보이는 코드보다 **명확한 코드**를 우선할 것
- 변경 사항은 최소화하고, 목적에 집중할 것
- 관련 없는 코드 수정은 피할 것
- 기존 코드베이스의 패턴을 반드시 따를 것

### Import 규칙

- 가능하면 프로젝트 내부에서는 절대 경로 import 사용
- Import 순서: 표준 라이브러리 → 서드파티 → 로컬 모듈
- 각 그룹 사이에는 빈 줄 추가
- `*` 와일드카드 import 금지

### 포매팅 규칙

- 들여쓰기: 공백 4칸
- 한 줄 최대 길이: 120자
- 여러 줄 컬렉션에는 trailing comma 사용
- 역슬래시(`\\`) 대신 괄호를 사용해 줄 나누기

### 타입 힌트

- 모든 함수와 공개 속성에 타입 힌트 사용
- 최신 Python 3.10+ 타입 문법: `str | None`, `list[int]`, `dict[str, int]`
- `dataclass(slots=True)` for immutable data structures

### 네이밍 규칙

- 변수 / 함수: `snake_case`
- 클래스 / 예외: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`
- Enum 클래스: `PascalCase`, Enum 멤버: `UPPER_SNAKE_CASE`
- 파일 / 모듈명: `snake_case.py`

### 에러 처리

- `except:` 같은 포괄적 예외 처리 금지
- 실제로 처리 가능한 경우에만 예외를 catch할 것
- 의미 있는 메시지와 함께 예외를 재발생(re-raise)할 것
- 에러를 조용히 무시하지 말 것

예시: `raise RuntimeError("메시지") from exc`

### 비동기 코드

- 동기 API와 비동기 API를 명확히 분리할 것
- `async` 함수 내부에서 블로킹 I/O 사용 금지
- 비동기 라이브러리를 동기 코드에서 호출할 때는 `asyncio.run()` 사용

### Protocol / 인터페이스

- `typing.Protocol` 사용하여 인터페이스 정의
- 리포지토리 인터페이스는 `Protocol`로 구현

### 의존성 주입

- `dependency-injector` 사용
- `container/container.py`에서 Singleton/Factory 패턴 사용

### 설정 및 시크릿

- 설정 값은 `pydantic-settings` 사용
- 시크릿을 코드에 하드코딩하지 말 것
- 필요한 환경 변수는 `.env.sample` 참고

---

## 데이터베이스 & 마이그레이션

- SQLAlchemy 모델 위치: `app/models`
- 마이그레이션 도구: Alembic
- 새 마이그레이션 생성: `poetry run alembic revision --autogenerate -m "메시지"`
- 마이그레이션 적용: `poetry run alembic upgrade head`

---

## Ruff 규칙

- Ruff 설정은 `pyproject.toml`에 정의됨
- 제외 경로 예시: `alembic/`, 가상 환경 디렉터리
- 정당한 이유 없이 Ruff 규칙을 비활성화하지 말 것

---

## Cursor / Copilot 가이드라인

- `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md` 파일 없음
- AI가 생성한 코드는 반드시 사람이 검토할 것
- 이 문서의 규칙을 항상 우선 적용할 것

---

이 문서는 사람과 에이전틱 코딩 시스템 모두가 일관되고 유지보수 가능한 코드를 작성하기 위한 기준입니다.
