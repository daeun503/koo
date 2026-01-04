# koo

**koo**는 개인용 지식 베이스를 구축하고,  
질문이 들어오면 **CS 도메인 지식과 개발(Code/Git) 지식을 자동으로 분리·연결하여 근거 기반으로 답변하는 RAG(Retrieval-Augmented Generation) CLI 도구**입니다.

이 프로젝트의 목적은 단순한 “문서 검색”이 아니라,

- CS 응대에서 **정확한 정책·가이드 기반 답변**
- 개발 질문에서 **최근 코드 변경(git log)과의 연관성 설명**
- 질문 의도에 따라 **적절한 지식 도메인으로 자동 라우팅**

을 가능하게 하는 **실사용 가능한 개인용 LLM 시스템**을 만드는 것입니다.

---

## Why koo?

CS 문서와 개발 문서는 성격이 완전히 다릅니다.

- **CS 문서**
  - 정책, FAQ, 운영 가이드, 고객 안내 문구
  - “그럴듯한 답변”보다 **정확성과 근거**가 중요
- **개발 문서**
  - 코드, 커밋 로그, PR, 에러 원인
  - **최신 변경점과 코드 레벨 근거**가 중요

하지만 일반적인 RAG 시스템은 모든 문서를 하나의 인덱스에 섞어버리기 때문에,

- CS 질문에 개발 로그가 섞이거나
- 개발 질문에 오래된 정책 문서가 끼어드는 문제

가 자주 발생합니다.

`koo`는 이를 해결하기 위해 **도메인 분리 + 자동 라우팅 기반 RAG** 구조를 채택했습니다.

---

## Core Concepts

### 1. Domain Separation (CS / Dev)

모든 지식은 적재 시점부터 도메인을 명확히 구분합니다.

- `cs`
  - 정책, FAQ, 운영 가이드, 장애 대응 문서
- `dev`
  - 코드 변경 이력, git log, PR 요약, 기술 문서

도메인 분리는 다음과 같은 효과를 가집니다.

- 검색 범위 축소 → **정확도 향상**
- 도메인별 답변 정책 적용 가능
- 민감한 개발 정보가 CS 답변에 노출되는 리스크 감소

---

### 2. Query Routing (질문 자동 분류)

질문이 들어오면 라우터가 의도를 판단합니다.

- `cs` : 고객 안내, 정책, FAQ, 운영 문의
- `dev` : 에러, 스택트레이스, 함수/파일, 커밋, 배포 변경점
- `mixed` : CS + 개발 맥락이 함께 필요한 질문
- `unknown` : 확신이 없는 경우 (기본적으로 mixed로 처리 가능)

라우팅 결과에 따라 검색 대상이 달라집니다.

- `cs` → CS 전용 벡터 인덱스
- `dev` → Dev 전용 벡터 인덱스
- `mixed` → 두 인덱스를 모두 검색 후 결과 결합

이 패턴은 보통 다음과 같은 용어로 불립니다.

- Query Routing
- Multi-Index RAG
- Federated Search
- (개념적으로) Mixture of Experts

---

### 3. Semantic Chunking (시멘틱 청킹)

큰 문서를 그대로 임베딩하면 검색 품질이 떨어집니다.  
`koo`는 문서를 **의미 단위(chunk)**로 분해해 인덱싱합니다.

기본적인 청킹 전략은 다음을 목표로 합니다.

1. **구조 기반 1차 청킹**
   - Notion: heading / block 단위
   - Slack: thread 단위
   - Git: commit 단위
2. **시멘틱 2차 청킹**
   - 너무 긴 덩어리만 의미 단위로 분해
3. **Overlap**
   - 문맥 손실 방지를 위해 일부 겹침 허용
4. **계층형 구조**
   - 검색은 작은 chunk
   - 답변은 상위 문맥(parent chunk)까지 활용

---

## Architecture Overview

### Storage Layer

#### MySQL (Source of Truth)

MySQL은 모든 원본 데이터를 책임집니다.

- 문서 원문 (`documents`)
- 청킹된 텍스트 (`chunks`)
- 메타데이터 (source, version, hash, timestamp)
- 질의 및 응답 로그 (`query_logs`)

즉, MySQL은 **진실의 원천**이며,
벡터 DB는 캐시/가속 계층으로만 사용됩니다.

#### Milvus (Vector Search)

Milvus는 임베딩 벡터 검색 전용입니다.

- 도메인별 컬렉션 분리
  - `koo_cs_chunks`
  - `koo_dev_chunks`
- 저장 데이터 최소화
  - `chunk_id`
  - `embedding`
  - 필터용 메타 정보

---

## End-to-End Flow

### A. Ingest Flow (지식 적재)

1. **Input**
   - Slack / Notion / 임의 텍스트 / Git 로그
2. **Normalize**
   - 공통 스키마로 정규화
   - source_type, source_id, domain, raw_content
3. **Chunking**
   - 의미 단위로 문서 분해
   - chunk hash로 중복/변경 감지
4. **Embedding**
   - 각 chunk를 벡터로 변환
5. **Store**
   - MySQL에 원문/청크 저장
   - Milvus에 벡터 저장

---

### B. Query Flow (질의 처리)

1. **Route**
   - 질문을 cs / dev / mixed / unknown으로 분류
2. **Retrieve**
   - 해당 도메인의 벡터 인덱스 검색
3. **Context Build**
   - 중복 제거
   - 상위 문맥 확장
   - 출처 메타 포함
4. **Generate (RAG)**
   - 질문 + 근거 컨텍스트로 LLM 답변 생성
5. **Log**
   - 질의, 라우팅, 사용 chunk, 답변 저장

---

## CLI Usage

### Text Ingest

```bash
poetry run koo ingest text \
  --domain cs \
  --source-id mynote \
  --file ./README.md
