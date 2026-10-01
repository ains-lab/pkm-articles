"""Lecture content: API contracts, lifecycle and frontend. Static teaching examples."""
SLIDES = []
def s(chapter,title,lead,refs,kind='bullets',**content):
    SLIDES.append(dict(chapter=chapter,title=title,lead=lead,refs=refs,kind=kind,**content))

s('05 · API 계약','같은 HTTP라도 두 종류의 API다','기존 Hermes API와 제안 BFF endpoint를 분리해서 읽습니다.', ['api-contract.md:6-34','api-contract.md:120-133'], 'compare',
  columns=[['기존 Hermes · 문서/소스 조사','/v1/chat/completions','/v1/responses · /v1/runs','서버 간 Bearer 인증'],['제안 BFF · 아직 미구현','/api/wiki/pages · /api/wiki/sources','/api/agent/runs','사용자 인증 + 소유권 + 최소 응답']],
  takeaway='BFF endpoint가 문서에 있어도 현재 서비스에서 호출할 수 있다는 뜻은 아니다.')
s('05 · API 계약','세 가지 실행 surface를 구분한다','같은 이름의 필드가 모든 endpoint에서 같은 의미를 갖지 않습니다.', ['api-contract.md:36-84'], 'table',
  headers=['surface','주 입력·이력','주 용도'],rows=[['Chat Completions','messages / stream\nX-Hermes-Session-Id header','범용 OpenAI 형식 client'],['Responses','input / instructions / store\nprevious_response_id 또는 conversation','서버측 response chain'],['Runs','input / body session_id\nconversation_history / previous_response_id','비동기 실행·진행·중지 UI']],
  takeaway='최종 채택은 설치 capabilities와 실제 통합 시험 후 결정한다.')
s('05 · API 계약','Chat 세션: header를 읽어야 한다','body session_id를 넣었다고 Chat의 대화가 선택되는 것은 아닙니다.', ['api-contract.md:36-58'], 'code',
  code='X-Hermes-Session-Id: <BFF 소유 transcript ID>\n\n{\n  "model": "hermes-agent",\n  "messages": [\n    {"role": "user", "content": "기존 노트의 검토 상태는?"}\n  ],\n  "stream": true\n}',
  items=['예시·미전송. Chat의 body session_id / conversation_id / user를 ACL로 쓰지 않는다.','header가 없으면 첫 user content와 system prompt에서 ID를 파생하는 설치 구현에 주의한다.','X-Hermes-Session-Key는 장기 기억 scope다. transcript ID나 인증 identity와 다르다.'])
s('05 · API 계약','Responses: 이력 연결을 명시한다','응답 체인과 conversation은 같은 요청에 동시에 지정하지 않습니다.', ['api-contract.md:60-65','api-contract.md:88-92'],
  items=[['입력 계약','messages가 아니라 input, instructions 등을 사용한다. conversation_id가 아니라 conversation이다.'],['보존 계약','store와 이전 응답 연결의 저장·삭제 정책을 검토한다. 다른 사용자의 response ID를 신뢰하지 않는다.'],['중복 실행 방지','stream에 나온 function_call/output이 이미 서버에서 실행된 결과라면 client가 다시 실행하지 않는다.']],
  takeaway='OpenAI 호환이라는 말은 모든 role·tool history·이력 방식이 완전히 같다는 보장이 아니다.')
s('05 · API 계약','Runs: 접수와 결과를 분리한다','202와 run ID는 “작업을 추적할 수 있다”는 시작점입니다.', ['api-contract.md:60-84'], 'code',
  code='POST /v1/runs\n{\n  "input": "허용된 기존 지식으로 질문에 답해 주세요.",\n  "session_id": "<BFF 소유 세션 ID>"\n}\n\n# 접수 shape 예시 · 실제 실행 결과 아님\n{"run_id":"run_<example>","status":"started","replayed":false}',
  items=['상태는 GET /v1/runs/{id}로 조회한다.','queued/running/waiting_for_approval/stopping과 terminal 상태를 나눈다.','completed라도 partial/interrupted/error flags와 실제 결과를 함께 확인한다.'])
s('05 · API 계약','모델 이름과 실제 실행 모델은 다르다','model echo나 alias를 runtime lock의 증거로 쓰지 않습니다.', ['api-contract.md:58-58','api-contract.md:82-84','tech-stack.md:93-103'],
  items=[['별칭과 선택 규칙','hermes-agent는 alias다. bare model·session override·model_routes 등의 적용 순서를 확인한다.'],['Fallback','model/provider/model_options를 보냈다는 사실만으로 fallback 금지가 보장되지 않는다.'],['업무 계약','고정 모델이 필요한 Wiki 컴파일은 별도 집행과 실제 runtime 검증을 거쳐야 한다.']],
  takeaway='이 강의는 모델을 호출하지 않는다. runtime 확인 절차를 설명한다.')
s('05 · API 계약','권한은 method + path마다 좁힌다','일반 사용자에게 필요하지 않은 관리 surface는 공개하지 않습니다.', ['api-contract.md:13-34','api-contract.md:120-133','security-and-operations.md:29-35'], 'table',
  headers=['그룹','BFF 처리 제안'],rows=[['pages / sources / status','인증 + page ACL + 축약 projection'],['runs / events / stop','run owner + 정책 확인; 변경 요청 CSRF'],['approval / steer','필요 시 별도 scope; pending/running 상태 확인'],['/api/sessions/* / /api/jobs/*','관리 API 전체 프록시 금지; Cron 초기 차단'],['profile / tools / model / raw path','client의 임의 선택값을 그대로 upstream에 전달 금지']],
  takeaway='인증은 “누구인가”, 인가는 “이 객체에 이 작업을 해도 되는가”를 묻는다.')
s('05 · API 계약','오류는 다음 행동으로 번역한다','HTTP 상태 하나를 “모델 오류”로 뭉뚱그리지 않습니다.', ['api-contract.md:109-118','security-and-operations.md:82-95'], 'table',
  headers=['상태','의미 예','안전한 대응'],rows=[['400 / 413','입력 형식 / body 과다','요청 수정; 무한 retry 금지'],['401 / 403','인증 / origin·정책 거부','서버 credential·권한 확인; 키 출력 금지'],['404','객체·transport 없음','SSE 404면 run status도 확인'],['409','idempotency payload 충돌 등','같은 key의 원 요청 확인'],['429 / 503','동시성 제한 / drain','기존 run 존재·재시도 조건 먼저 확인']],
  takeaway='헤더 이후 stream이 실패할 수 있다. HTTP 200은 업무 완료 판정이 아니다.')

s('06 · 스트리밍과 복구','스트림은 결과가 아니라 전달 경로다','SSE(Server-Sent Events)는 진행 이벤트를 서버에서 client로 전달합니다.', ['api-contract.md:86-107','workflows.md:37-64'], 'compare',
  columns=[['연결의 상태','연결됨 / 끊김 / 다시 연결 중','브라우저가 관측하는 transport','단절되어도 run은 계속될 수 있음'],['실행의 상태','running / completed / failed 등','Gateway의 작업 lifecycle','GET run status로 재확인']],
  takeaway='재연결 ≠ 재실행 · 화면 새로고침에 새 run을 자동 생성하지 않는다.')
s('06 · 스트리밍과 복구','SSE의 분기 위치는 surface마다 다르다','“event는 언제나 같은 곳에 있다”는 parser가 호환성 오류를 만듭니다.', ['api-contract.md:86-103'], 'table',
  headers=['surface','분기 위치','주의'],rows=[['Chat','data JSON + named event: hermes.tool.progress','[DONE]와 finish flags/usage 확인'],['Responses','response.* event family','이미 실행된 tool 결과 재실행 금지'],['Runs','data JSON 내부의 event 필드','run.completed/failed/cancelled/interrupted 구분']],
  takeaway='하나의 범용 parser에 endpoint별 event adapter와 의미 검증을 결합한다.')
s('06 · 스트리밍과 복구','HTTP chunk는 메시지 경계가 아니다','한글 한 글자도, JSON 하나도 여러 chunk에 나뉠 수 있습니다.', ['api-contract.md:94-105','workflows.md:58-64'], 'code',status='강의용 예시',
  code='data: {"event":"message.delta",\ndata: "run_id":"run_<example>","delta":"한글"}\n\n: keepalive\n\n# 아래는 처리 단계 개념도\nbytes → UTF-8 streaming decode → SSE frame → JSON → reducer',
  items=['강의용 multi-line data 예시. data 값을 줄바꿈으로 합치면 유효한 JSON이 된다.','blank line, CRLF, multi-line data, comment를 규칙대로 처리한다.','unknown event는 안전하게 처리하되 알려진 종료·실패를 놓치지 않는다.'])
s('06 · 스트리밍과 복구','복수 구독자가 이벤트를 나눠 가져간다면?','조사한 설치판 Runs는 단일 queue를 소비하며 연결 종료 시 transport를 삭제합니다.', ['api-contract.md:103-107','workflows.md:58-64'], 'diagram',diagram='sse-fanout',status='문서 기반',
  takeaway='BFF의 단일 upstream 구독 + 자체 fan-out + GET run status reconciliation을 권고한다.')
s('06 · 스트리밍과 복구','재접속의 기준은 현재 run snapshot','끊어진 델타를 상상으로 복원하지 않습니다.', ['workflows.md:37-64','frontend-design.md:49-67'], 'diagram',diagram='reconnect',status='설계 제안',
  takeaway='Last-Event-ID 무손실 replay를 가정하지 않는다. 최종 snapshot과 임시 delta의 중복을 제거한다.')
s('06 · 스트리밍과 복구','Idempotency는 같은 요청의 재전송을 묶는다','전송 응답이 유실되어도, 같은 일을 두 번 시작하지 않도록 합니다.', ['api-contract.md:109-113','workflows.md:66-72'], 'table',
  headers=['입력 조합','Runs 계약','해석'],rows=[['같은 key + 같은 payload','원 run의 202 replay','새 작업을 실행한다는 뜻 아님'],['같은 key + 다른 payload','409 conflict','질문을 고치면 새 key 필요'],['key 저장소 DB 실패','in-memory fallback 가능','durable capability 확인'],['Chat/Responses의 300초 캐시','별도 구현','Runs의 scoped durable 계약과 같지 않음']],
  takeaway='key: visible ASCII 1–255자 · terminal 기본 보존 24시간 · SSE replay/실행 재개와 별개')
s('06 · 스트리밍과 복구','중지 요청은 취소 완료가 아니다','브라우저 연결 취소, 에이전트 중지, 이미 생긴 효과의 복구는 서로 다릅니다.', ['api-contract.md:115-118','workflows.md:74-82'], 'diagram',diagram='stop',
  takeaway='AbortController.abort()는 연결만 닫는다. stop은 이미 실행된 파일·외부 효과를 rollback하지 않는다.')
s('06 · 스트리밍과 복구','steer와 approval도 접수 이후를 확인한다','버튼 클릭이나 200 응답만으로 사용자의 의도가 실행되었다고 말하지 않습니다.', ['api-contract.md:116-118','workflows.md:84-95'], 'compare',
  columns=[['steer','running 상태의 지시 큐 등록','200은 큐 접수; 실제 소비와 다름','pending_steer 등 미소비 상태 처리'],['tool approval','서버의 pending choices만 표시','choice + 선택적 request_id 전달','stale 요청 재사용·always 자동 선택 금지']],
  takeaway='승인 카드가 사라짐 ≠ 승인 성공 · 거부·만료·다른 화면 처리·연결 단절을 구분')
s('06 · 스트리밍과 복구','설계 토론 ③ 새로고침 뒤 SSE가 404다','“오류가 났으니 새 run을 만들자”는 안전한 복구일까요?', ['api-contract.md:103-116','workflows.md:58-82'], 'exercise',status='강의용 예시',
  prompt='run은 이미 생성되었고 응답 일부를 보았습니다. 어떤 순서로 복구해야 할까요?',
  answer='BFF에 보관한 run ID와 소유권을 확인하고 GET /v1/runs/{id}로 현재 상태를 조회합니다. 실행 중이면 상태 추적을 이어가고, 종료되었으면 최종 결과로 UI를 정합화합니다. transport 404만으로 실패·취소를 단정하거나 새 작업을 자동 생성하지 않습니다. 사용자의 명시적 재실행과 전송 retry를 구분합니다.')

s('07 · 프런트엔드','기술 스택은 현재와 제안을 나눈다','제안 라이브러리를 설치된 구성요소로 설명하지 않습니다.', ['tech-stack.md:19-60'], 'compare',
  columns=[['당시 조사한 Hermes','API Server: aiohttp adapter','asyncio + executor의 AIAgent','당시 manifest 0.21.1 / Python 범위 ≥3.11,<3.14'],['신규 앱 권고 · 미구현','React + TypeScript / Next.js Node BFF','Zod 등 DTO 검증 / 안전한 Markdown','Vitest·Testing Library·Playwright 시험']],
  takeaway='Hermes API Server를 FastAPI라고 부르지 않는다. 권고 package version은 구현 시 다시 고정한다.')
s('07 · 프런트엔드','화면은 사용자의 질문 순서로','자료 찾기 → 노트 읽기 → 근거 확인 → 필요한 경우 질의', ['frontend-design.md:7-35'], 'table',status='설계 제안',
  headers=['route','역할','권한 경계'],rows=[['/library','서지·보관 형식·노트 유무','read-only MVP'],['/knowledge/:pageId','본문·revision·검토 범위','page ACL / 안전 렌더링'],['/topics','개념·비교 연결','기존 지식 탐색'],['/chat/:conversationId','선택 문서·답변·실행 상태','후속 실행 승인'],['/operations','축약 관측 상태·시각','소유자 전용; Cron 수정 아님']])
s('07 · 프런트엔드','UI 상태와 Gateway status를 함께 보관한다','disconnected는 UI의 관측이지 Gateway의 terminal 상태가 아닙니다.', ['frontend-design.md:49-69'], 'diagram',diagram='ui-state',status='설계 제안',
  takeaway='commentary·tool·delta·final을 분리한다. raw tool 결과·비공개 추론을 무조건 노출하지 않는다.')
s('07 · 프런트엔드','비어 있음과 실패도 가르쳐야 할 정보다','아직 없는 노트, 권한 거부, 갱신 충돌을 같은 빈 화면으로 처리하지 않습니다.', ['frontend-design.md:37-47','frontend-design.md:71-95'], 'table',
  headers=['상황','화면 표현','조작'],rows=[['필터 결과 없음','현재 필터에 맞는 자료 없음','필터 해제'],['지식 노트 미작성','원문 보관과 노트 없음 별도 표시','허용된 자료 탐색'],['snapshot 충돌','갱신 중 / 현재본 확인 불가','제한 재시도'],['run 중지 요청 중','stopping 표시','중복 요청 비활성'],['관측 정보 없음','미관측 / 확인되지 않음','0이나 성공으로 채우지 않음']])
s('07 · 프런트엔드','읽을 수 있고 조작할 수 있어야 한다','토큰과 접근성 목표는 실제 화면 시험 전에는 통과 기록이 아닙니다.', ['DESIGN.md:14-45','frontend-design.md:88-113'],
  items=[['시각 언어','원문 Civic Navy·차가운 중립색·sans를 사용한다. 상태는 색과 문자를 함께 보여준다.'],['키보드와 한국어','label·focus·dialog 복귀·IME 조합 중 제출 금지를 확인한다. 긴 ID와 한글 줄바꿈을 시험한다.'],['성능 증거','원문의 field 목표: p75 LCP < 2.5s, INP < 200ms, CLS < 0.1. baseline은 없으며 lab 결과를 field 통과로 바꾸지 않는다.']],
  takeaway='375/768/1280/1440px의 화면·오류·단절 상태까지 검증한다. 이 수치는 제안 앱의 목표다.')
