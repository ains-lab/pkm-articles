# 질의 환류·수정·철회 계약

Policy `pkm-html-knowledge/v2` / contract `pkm-contracts/v2`. 상태는 [feedback.json](state/feedback.json). 현재 비활성, 사건 0개이며 P4 실행은 별도 승인 대상이다.

1. 질문에는 기존 Wiki와 실제 원문 근거로 답한다. 단순 조회를 저장할 문서로 억지 확대하지 않는다. 장기 가치가 있는 수정·비교·열린 질문·사용자 가설/판단만 후보로 한다.
2. **사용자가 해당 연구 내용을 저장하라고 명시한 경우만** 사건을 만든다. 사용자 원문 전체 대화, 비밀/민감 개인정보를 저장하지 않는다. 원문 입력 허용은 상시 채팅 수집 권한이 아니다.
3. event_id와 feedback_id, 작성 주체, 대상 page/hash, claim_ref, 내용, evidence_refs, 이유, 영향 페이지, 사용자 저장 요청 근거를 기록한다. 동일 요청/대상/내용의 반복은 기존 feedback_id로 조회하고 중복 적용하지 않는다. target hash가 달라지면 자동 재기반하지 않고 충돌 검토한다.
4. 상태는 proposed→accepted/rejected, accepted→withdrawn이다. 각각 새 event_id의 사건으로 남긴다. 철회된 동일 revision은 재사용하지 않으며 새 승인 요청은 새 revision/사건으로 기록한다. accepted는 사용자 판단을 채택했다는 뜻이지 논문 사실 검증 성공이 아니다.
5. 저자 보고, AI 해석, 사용자 의견, 미검증 가설, 실제 실험 관측을 분리한다. 사용자 의견이 원문과 다르면 이견/가설로 보존하고 원문 보고를 바꾸지 않는다. 다수 AI의 동의도 독립 출처가 아니다.
6. 지식 변경은 AUTOMATION의 공통 잠금·journal·receipt를 거친다. reviewed 또는 사용자 수정 문서에는 덮어쓰기 대신 승인 대기 변경안을 만든다. 10개 이상 기존 페이지 변경은 별도 범위 승인 대상이다.
7. 철회/반박은 과거 사건을 삭제하지 않고 영향 페이지·비교·연구 아이디어에 needs_review 변경안을 만든다. 확정 근거로 계속 소비하지 않는다. 회수 전 사용자 편집을 덮어쓰지 않는다. 문서 frontmatter의 status는 draft/reviewed/superseded를 유지하고 추가 검토 필요는 review_state=needs_review로 표시한다.
8. committed_at은 실제 지식 거래 완료 시각이며 요청/생성 시각과 다르다. 격주 reviewer는 committed 사건과 미해결 철회의 영향 목록을 확인한다. 질문 답변을 했다는 이유로 지식 반영 receipt를 만들어 넣지 않는다.

피드백 독립 처리의 모델 비용과 P4 실행 범위는 아직 미승인이다. P1은 스키마와 처리 규칙을 준비한 것이며 실제 대화 저장·지식 환류는 하지 않았다.
