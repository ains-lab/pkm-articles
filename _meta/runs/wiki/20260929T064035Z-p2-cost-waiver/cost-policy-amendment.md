# 비용 제약 제거 및 P2 실행 개정 — 공유 게시 대기

사용자 요청: “비용 제약사항은 제거하고 codex-lb 사용해서 다시 진행하세요”.
승인 근거: `_meta/runs/wiki/20260929T064035Z-p2-cost-waiver/approval.json`.

이번 격리 P2에는 이 명시적 지시를 적용한다. 정책 후보 `pkm-html-knowledge/v2`, 계약 후보 `pkm-contracts/v2`는 `proposed/`에 있으며 활성 파일은 바꾸지 않았다. 편집 중지 확인창 시간초과로 공유 정책·지식·index/log/state 게시는 보류한다.

## 제거하는 조건
- 파일럿 US$5, 일일 US$5/회·US$10/KST 일, 격주 US$5/회의 금액 상한.
- 비용 계측·요청 전 최대 비용 예약·강제 차단 검증을 원문 읽기/호출의 필수조건으로 요구하는 규칙.
- unknown 비용의 blocked_budget 차단. unknown은 null/미관측이지 실제 0 또는 무료가 아니다.

## 유지하는 조건
- `codex-lb / gpt-6-astra / xhigh`, 애플리케이션 fallback 금지.
- P2 대상은 `2609.30830v1`, `2609.31358v1`의 로컬 원본 HTML 텍스트. 사전 파싱본·compile-input·chunk 없음.
- PDF·이미지·외부 자산·전체 대화 수집·신규성 검색 금지, 원본/서지/수집 state/Cron 불변.
- 시간·편수·재시도·안전 중단·근거 검토·draft·인간 검토·공유 잠금·journal·조건부 복구 계약 유지.
- P3–P6, 신규 Cron 등록/활성화, 설치·전역 모델/인증 변경·알림·Git commit/push는 미승인.

## 실제 경로
`model-route.json`: 반환 모델 gpt-6-astra, reasoning xhigh, completed. tools=[], SDK 재시도 0, 애플리케이션 fallback 없음. 공급자 내부 구현 전체를 감사했다는 뜻은 아니다. 과금 null.

## 공유 반영 대기
편집 중지 확인 후 활성 AGENTS/SCHEMA/AUTOMATION/STATE-CONTRACTS/COMPILATION/README/index 및 prompt의 비용 게이트·P2 문구와 상태 revision을 함께 갱신한다. 과거 log/run/승인 기록은 변경하지 않는다. 현재 후보 JSON은 독립 검토용이며 그대로 복사해 활성 문서와 상태를 불일치하게 만들지 않는다.
