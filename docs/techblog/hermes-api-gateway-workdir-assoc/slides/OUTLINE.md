# 강의 슬라이드 목차

원문 기술문서 기준의 강의 구성. 실습은 합성 설계 과제이며 실제 서비스를 실행하지 않는다.


## 01 · 강의 안내

- [01. 개인 Wiki를 웹으로 연결하기](lecture.html#slide-1) — Hermes API Gateway · 작업 경로 · 신뢰 경계
- [02. 이 수업을 마치면](lecture.html#slide-2) — 구성요소 이름보다 “누가 무엇을 허용하는가”를 설명할 수 있어야 합니다.
- [03. 강의 지도](lecture.html#slide-3) — 기능을 붙이는 순서가 아니라, 경계를 이해하는 순서로 진행합니다.
- [04. 증거의 강도를 섞지 않는다](lecture.html#slide-4) — “문서에 있다”와 “실제로 동작했다”는 다른 문장입니다.
- [05. 이번 서비스의 출발점](lecture.html#slide-5) — 개인용 인증 서비스의 read-only 탐색이 먼저입니다.
- [06. 수치에는 시각과 단위를 붙인다](lecture.html#slide-6) — 다음은 원문 문서의 과거 snapshot이지, 현재 운영 상태가 아닙니다.

## 02 · 아키텍처

- [07. 하나의 Wiki, 서로 다른 세 경로](lecture.html#slide-7) — 읽기·질의·게시를 같은 HTTP 통로로 섞지 않습니다.
- [08. BFF는 브라우저를 위한 제한된 서버](lecture.html#slide-8) — Backend for Frontend: 브라우저에 필요한 계약만 제공하는 중간 계층입니다.
- [09. 신뢰 경계가 보이는 전체 구조](lecture.html#slide-9) — 도형은 책임과 제안 배치를 나타냅니다. 서비스 설치 증거가 아닙니다.
- [10. 정형 읽기: 모델 없이 페이지를 연다](lecture.html#slide-10) — 파일 존재 여부가 아니라 일관된 snapshot을 서비스합니다.
- [11. 질의: 실행 문맥은 BFF가 소유한다](lecture.html#slide-11) — 사용자의 질문은 입력이지만, 도구·모델·자료 범위를 정하는 권한은 아닙니다.
- [12. 같은 IP 표기도 다른 위치일 수 있다](lecture.html#slide-12) — 127.0.0.1은 그 프로세스가 속한 network namespace의 loopback입니다.
- [13. 설계 토론 ① 편리하지만 위험한 연결](lecture.html#slide-13) — “브라우저가 path와 Gateway key를 보내면 구현이 간단하지 않을까요?”

## 03 · 작업 경로

- [14. cwd는 출발점이지 울타리가 아니다](lecture.html#slide-14) — current working directory는 상대경로를 해석하는 기준입니다.
- [15. 기본 cwd가 결정되는 경로](lecture.html#slide-15) — 다음은 기술문서가 조사한 local Gateway 구현의 설명입니다.
- [16. 이름이 비슷해도 계약은 다르다](lecture.html#slide-16) — 설정이 저장되었다고 런타임이 그 키를 읽는 것은 아닙니다.
- [17. 설정 절차도 작은 변경으로 나눈다](lecture.html#slide-17) — 다음은 원문의 승인 후 절차 예시입니다. 이 강의에서는 실행하지 않습니다.
- [18. API bind와 secret은 별도 결정](lecture.html#slide-18) — cwd 변경 승인에 API 활성화·재시작 승인까지 들어 있지 않습니다.
- [19. 적용 성공은 새 세션에서 확인한다](lecture.html#slide-19) — 설정값 · 실제 도구 위치 · 프로젝트 지침 · 접근 권한은 각각 확인해야 합니다.
- [20. 설계 토론 ② 설정 성공의 함정](lecture.html#slide-20) — “임의 cwd 키를 저장했고 config get에도 나오니 적용 완료입니다.”

## 04 · 데이터 계약

- [21. 파일 원장과 HTTP 응답은 다르다](lecture.html#slide-21) — 저장소 구조를 URL 구조로 그대로 복사하지 않습니다.
- [22. 원본 기록은 나중에 고쳐 맞추지 않는다](lecture.html#slide-22) — source.json의 wiki_compiled:false는 수집 당시의 정보입니다.
- [23. 상태는 하나의 초록불이 아니다](lecture.html#slide-23) — 서로 독립된 질문을 하나의 completed 배지로 합치지 않습니다.
- [24. 페이지의 provenance를 화면에 남긴다](lecture.html#slide-24) — Provenance는 결과가 어떤 입력·정책·작업에서 왔는지 추적하는 정보입니다.
- [25. DTO: 필요한 필드만 공개한다](lecture.html#slide-25) — 아래는 제안된 BFF 응답의 축약 예시이며 실제 응답이 아닙니다.
- [26. ID를 파일로 바꾸는 순간이 경계다](lecture.html#slide-26) — 허용된 ID라도 실제로 여는 파일까지 안전해야 합니다.
- [27. 캐시도 검증한 snapshot만 기억한다](lecture.html#slide-27) — 오래된 값보다 더 위험한 것은, 서로 다른 시점의 값을 한 페이지로 합치는 것입니다.
- [28. 출처 링크도 범위를 말해야 한다](lecture.html#slide-28) — 링크가 있다는 사실과 내용을 검토했다는 사실은 다릅니다.

## 05 · API 계약

- [29. 같은 HTTP라도 두 종류의 API다](lecture.html#slide-29) — 기존 Hermes API와 제안 BFF endpoint를 분리해서 읽습니다.
- [30. 세 가지 실행 surface를 구분한다](lecture.html#slide-30) — 같은 이름의 필드가 모든 endpoint에서 같은 의미를 갖지 않습니다.
- [31. Chat 세션: header를 읽어야 한다](lecture.html#slide-31) — body session_id를 넣었다고 Chat의 대화가 선택되는 것은 아닙니다.
- [32. Responses: 이력 연결을 명시한다](lecture.html#slide-32) — 응답 체인과 conversation은 같은 요청에 동시에 지정하지 않습니다.
- [33. Runs: 접수와 결과를 분리한다](lecture.html#slide-33) — 202와 run ID는 “작업을 추적할 수 있다”는 시작점입니다.
- [34. 모델 이름과 실제 실행 모델은 다르다](lecture.html#slide-34) — model echo나 alias를 runtime lock의 증거로 쓰지 않습니다.
- [35. 권한은 method + path마다 좁힌다](lecture.html#slide-35) — 일반 사용자에게 필요하지 않은 관리 surface는 공개하지 않습니다.
- [36. 오류는 다음 행동으로 번역한다](lecture.html#slide-36) — HTTP 상태 하나를 “모델 오류”로 뭉뚱그리지 않습니다.

## 06 · 스트리밍과 복구

- [37. 스트림은 결과가 아니라 전달 경로다](lecture.html#slide-37) — SSE(Server-Sent Events)는 진행 이벤트를 서버에서 client로 전달합니다.
- [38. SSE의 분기 위치는 surface마다 다르다](lecture.html#slide-38) — “event는 언제나 같은 곳에 있다”는 parser가 호환성 오류를 만듭니다.
- [39. HTTP chunk는 메시지 경계가 아니다](lecture.html#slide-39) — 한글 한 글자도, JSON 하나도 여러 chunk에 나뉠 수 있습니다.
- [40. 복수 구독자가 이벤트를 나눠 가져간다면?](lecture.html#slide-40) — 조사한 설치판 Runs는 단일 queue를 소비하며 연결 종료 시 transport를 삭제합니다.
- [41. 재접속의 기준은 현재 run snapshot](lecture.html#slide-41) — 끊어진 델타를 상상으로 복원하지 않습니다.
- [42. Idempotency는 같은 요청의 재전송을 묶는다](lecture.html#slide-42) — 전송 응답이 유실되어도, 같은 일을 두 번 시작하지 않도록 합니다.
- [43. 중지 요청은 취소 완료가 아니다](lecture.html#slide-43) — 브라우저 연결 취소, 에이전트 중지, 이미 생긴 효과의 복구는 서로 다릅니다.
- [44. steer와 approval도 접수 이후를 확인한다](lecture.html#slide-44) — 버튼 클릭이나 200 응답만으로 사용자의 의도가 실행되었다고 말하지 않습니다.
- [45. 설계 토론 ③ 새로고침 뒤 SSE가 404다](lecture.html#slide-45) — “오류가 났으니 새 run을 만들자”는 안전한 복구일까요?

## 07 · 프런트엔드

- [46. 기술 스택은 현재와 제안을 나눈다](lecture.html#slide-46) — 제안 라이브러리를 설치된 구성요소로 설명하지 않습니다.
- [47. 화면은 사용자의 질문 순서로](lecture.html#slide-47) — 자료 찾기 → 노트 읽기 → 근거 확인 → 필요한 경우 질의
- [48. UI 상태와 Gateway status를 함께 보관한다](lecture.html#slide-48) — disconnected는 UI의 관측이지 Gateway의 terminal 상태가 아닙니다.
- [49. 비어 있음과 실패도 가르쳐야 할 정보다](lecture.html#slide-49) — 아직 없는 노트, 권한 거부, 갱신 충돌을 같은 빈 화면으로 처리하지 않습니다.
- [50. 읽을 수 있고 조작할 수 있어야 한다](lecture.html#slide-50) — 토큰과 접근성 목표는 실제 화면 시험 전에는 통과 기록이 아닙니다.

## 08 · 보안과 운영

- [51. 질문도 문서도 비신뢰 입력이다](lecture.html#slide-51) — 자료 안의 지시는 실행 권한이 아닙니다.
- [52. Gateway key는 사용자 권한이 아니다](lecture.html#slide-52) — 서버 간 credential과 브라우저 사용자의 identity를 분리합니다.
- [53. 격리는 실제 거부로 확인한다](lecture.html#slide-53) — “읽기 전용으로 행동하세요”와 “쓰기 시스템 호출이 거부됩니다”는 다릅니다.
- [54. 원본 보존과 안전한 표시를 양립시킨다](lecture.html#slide-54) — sanitize는 렌더링 경계의 일이지 불변 원본을 덮어쓸 이유가 아닙니다.
- [55. SSE 프록시와 로그도 계약의 일부다](lecture.html#slide-55) — 연결이 살아 있는 것과 데이터가 즉시 전달되는 것은 다릅니다.
- [56. 장애 대응도 실패를 숨기지 않아야 한다](lecture.html#slide-56) — 관측한 신호에서 출발하고, 권한 우회로 해결하지 않습니다.

## 09 · 수집·컴파일·게시

- [57. 수집 성공은 지식 생성 완료가 아니다](lecture.html#slide-57) — 기존 Cron은 원본 저장 전용이며 웹 앱의 배포·질의와 분리됩니다.
- [58. v3 예외는 좁은 자료 경로다](lecture.html#slide-58) — 별도 승인된 로컬 PDF 내장 텍스트만 메모리에서 읽는 수동 경로입니다.
- [59. 두 종류의 승인은 서로 대체할 수 없다](lecture.html#slide-59) — 특정 도구 실행 승인과 특정 지식 작업의 게시 승인은 질문이 다릅니다.
- [60. 게시 완료에는 파일 이상의 증거가 필요하다](lecture.html#slide-60) — 여러 파일의 게시를 OS가 한 번에 원자적으로 보여준다고 가정하지 않습니다.
- [61. 동시성 제한은 서로 다른 문제를 푼다](lecture.html#slide-61) — run 개수 제한 하나로 Wiki의 다중 파일 일관성이 해결되지 않습니다.
- [62. 설계 토론 ④ 어떤 배지가 정직한가?](lecture.html#slide-62) — PDF 보관 완료, run completed, 하지만 receipt가 아직 committed가 아닙니다.

## 10 · 로드맵과 실습

- [63. 작게 만들되 검증 경계는 줄이지 않는다](lecture.html#slide-63) — R0–R4는 제안 서비스의 구현 단계이며 Wiki의 P3–P6 승인과 다릅니다.
- [64. 실습 ① read-only MVP의 계약을 그리기](lecture.html#slide-64) — 코드 실행 없이도 자료 노출과 일관성 문제를 설계할 수 있습니다.
- [65. 실습 ② 끊겨도 중복 실행하지 않는 채팅](lecture.html#slide-65) — 이벤트 전달 실패를 업무 재실행으로 바꾸지 않는 reducer를 설계하세요.
- [66. 테스트 이름보다 실행 범위를 기록한다](lecture.html#slide-66) — 합성 시험, 실제 통합 시험, 배포 검증은 서로 다른 증거입니다.
- [67. 버전 차이를 숨기지 않는 개발](lecture.html#slide-67) — 최신 공식 문서와 설치 checkout은 다른 시점을 가리킬 수 있습니다.
- [68. 마지막 점검: 무엇을 안다고 말할 수 있나?](lecture.html#slide-68) — “그럴듯한 완료”보다 “관측한 범위의 완료”가 더 유용합니다.
- [69. 기억할 설계 원칙](lecture.html#slide-69) — 모든 “완료”에는 무엇이 끝났는지 목적어를 붙입니다.
- [70. 원문으로 돌아가는 방법](lecture.html#slide-70) — 각 슬라이드의 “근거”에서 사용한 원문 구간과 줄 번호를 확인할 수 있습니다.
