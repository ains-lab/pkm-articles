"""Lecture content: security, publication, roadmap and exercises."""
SLIDES=[]
def s(chapter,title,lead,refs,kind='bullets',**content):
    SLIDES.append(dict(chapter=chapter,title=title,lead=lead,refs=refs,kind=kind,**content))

s('08 · 보안과 운영','질문도 문서도 비신뢰 입력이다','자료 안의 지시는 실행 권한이 아닙니다.', ['security-and-operations.md:6-21'], 'diagram',diagram='threats',
  takeaway='보호 대상: Wiki·host 파일·자격증명·대화·승인 이력 · 프롬프트만으로 경계를 세우지 않는다.')
s('08 · 보안과 운영','Gateway key는 사용자 권한이 아니다','서버 간 credential과 브라우저 사용자의 identity를 분리합니다.', ['security-and-operations.md:23-35'], 'compare',
  columns=[['브라우저 ↔ BFF','인증된 single-owner 세션','HttpOnly / Secure / SameSite','변경 요청의 CSRF·Origin 검사'],['BFF ↔ Gateway','API_SERVER_KEY 서버측 보관','run/session owner 매 요청 확인','method/path allowlist와 프로필 경계']],
  takeaway='NEXT_PUBLIC_* · localStorage · URL query · 브라우저 번들/콘솔에 실제 key를 넣지 않는다.')
s('08 · 보안과 운영','격리는 실제 거부로 확인한다','“읽기 전용으로 행동하세요”와 “쓰기 시스템 호출이 거부됩니다”는 다릅니다.', ['security-and-operations.md:37-50'],
  items=[['파일시스템','최소 read-only mount/OS 권한을 사용한다. host home·credential·SSH key·Docker socket은 노출하지 않는다.'],['모든 도구 경로','terminal만 컨테이너에 있어도 다른 파일 도구가 host를 읽을 수 있다. 실제 실행 위치를 각각 시험한다.'],['전송과 자료 형식','container가 egress를 자동 차단하지 않는다. 도구 allowlist와 HTML/PDF 등 자료 형식의 허용 범위도 함께 검사한다.']],
  takeaway='프로필·cwd·AGENTS는 sandbox가 아니다. read_file이라는 이름도 비분석 도구를 뜻하지 않는다.')
s('08 · 보안과 운영','원본 보존과 안전한 표시를 양립시킨다','sanitize는 렌더링 경계의 일이지 불변 원본을 덮어쓸 이유가 아닙니다.', ['security-and-operations.md:52-59','frontend-design.md:27-35'], 'compare',
  columns=[['표시 계층에서 한다','Markdown raw HTML 기본 off','URL scheme 제한·sanitize·CSP 검토','MVP에서는 공식 버전 고정 원문 링크'],['자동으로 하지 않는다','source.html 원본 덮어쓰기','앱 origin에서 raw HTML 그대로 실행','PDF preview 명목의 추출·OCR·렌더링']],
  takeaway='XSS 방어와 원본 불변성은 서로 대체 관계가 아니다.')
s('08 · 보안과 운영','SSE 프록시와 로그도 계약의 일부다','연결이 살아 있는 것과 데이터가 즉시 전달되는 것은 다릅니다.', ['security-and-operations.md:61-80','api-contract.md:103-107'], 'compare',
  columns=[['전송','text/event-stream · buffering/변환/캐시 금지','실제 keepalive·idle timeout 시험','CORS는 인증·방화벽 대체가 아님'],['로그','request/run ID·시간·HTTP/run status','허용 문서 revision/hash·정책 결과','key·cookie·대화 원문·raw tool 결과 제외']],
  takeaway='당시 공식 문서 10초 / 로컬 Runs wait timeout 30초의 차이: 설치판을 실제 측정해야 한다.')
s('08 · 보안과 운영','장애 대응도 실패를 숨기지 않아야 한다','관측한 신호에서 출발하고, 권한 우회로 해결하지 않습니다.', ['security-and-operations.md:82-103'], 'table',
  headers=['관측 신호','먼저 확인','하지 않을 대응'],rows=[['health 성공, 질의 실패','readiness·auth·model·tool','전체 정상 선언'],['SSE 단절','run 상태·buffering·timeout','새 run 자동 생성'],['stopping 장기 지속','실제 executor·도구 상태','cancelled로 숨김'],['interrupted','shutdown/restart 이력','성공 승격·효과 자동 재실행'],['snapshot 충돌 / lock 존재','receipt·hash·lock owner','partial 캐시·오래된 lock 자동 삭제']],
  takeaway='앱 배포 rollback과 Wiki 원본/상태 rollback은 다른 작업이다.')

s('09 · 수집·컴파일·게시','수집 성공은 지식 생성 완료가 아니다','기존 Cron은 원본 저장 전용이며 웹 앱의 배포·질의와 분리됩니다.', ['workflows.md:97-101','architecture.md:56-60'], 'diagram',diagram='collection',
  takeaway='403/429/5xx/timeout은 HTML 미제공이 아니다. 수집 완료를 자동 컴파일 trigger로 연결하지 않는다.')
s('09 · 수집·컴파일·게시','v3 예외는 좁은 자료 경로다','별도 승인된 로컬 PDF 내장 텍스트만 메모리에서 읽는 수동 경로입니다.', ['README.md:43-47','implementation-roadmap.md:72-87','security-and-operations.md:52-59'], 'compare',
  columns=[['승인 범위 안의 수동 경로','표준 pypdf · embedded text only','정확한 입력·단계·모델·무결성 gate','물리적 페이지 인용·미독 범위 기록'],['계속 금지 / 자동 승계 없음','PDF 바이너리·이미지 전송','OCR·렌더링·지속 추출본','웹 자유 질의로 예외 권한 확대']],
  takeaway='codex-lb / gpt-6-astra / xhigh · no-fallback · 비용 미관측 null · no_cost_cap도 승인 면제가 아니다.')
s('09 · 수집·컴파일·게시','두 종류의 승인은 서로 대체할 수 없다','특정 도구 실행 승인과 특정 지식 작업의 게시 승인은 질문이 다릅니다.', ['workflows.md:84-95','architecture.md:56-60'], 'table',
  headers=['계층','승인의 대상','대체하지 못하는 것'],rows=[['Hermes tool approval','pending 도구 동작의 허용/거부','논문·자료·모델·게시 단계 승인'],['Wiki 정책·실행 승인','정확한 입력 snapshot과 처리 범위','원문 무결성·실제 모델 검증'],['게시·편집 중지 승인','정확한 검증 결과의 조건부 게시','lock·최종 hash·journal·receipt 확인']],
  takeaway='일반 채팅 완료를 entities/ 수정 허가로 읽지 않는다. 초기 UI에는 compile 버튼을 두지 않는다.')
s('09 · 수집·컴파일·게시','게시 완료에는 파일 이상의 증거가 필요하다','여러 파일의 게시를 OS가 한 번에 원자적으로 보여준다고 가정하지 않습니다.', ['workflows.md:103-122','architecture.md:87-93'], 'diagram',diagram='publication',
  takeaway='write-ahead journal은 변경 전 기록, receipt는 게시 결과 증거다. committed와 실물을 함께 대조한다.')
s('09 · 수집·컴파일·게시','동시성 제한은 서로 다른 문제를 푼다','run 개수 제한 하나로 Wiki의 다중 파일 일관성이 해결되지 않습니다.', ['architecture.md:87-93','workflows.md:103-122'], 'table',
  headers=['경계','막으려는 충돌','확인 대상'],rows=[['BFF 세션 단일 writer','같은 대화의 동시 turn','session ownership·직렬화'],['API concurrent-run 제한','실행 자원·남용','429·유한 재시도'],['collection.lock','수집자와 게시자의 동시 쓰기','owner·수집 우선 시간'],['최종 hash·journal·receipt','사용자 수정·부분 게시·복구 충돌','조건부 갱신·exact-repeat no-op']],
  takeaway='무한 대기·고아 lock 자동 탈취·과거 snapshot 전체 복원을 하지 않는다.')
s('09 · 수집·컴파일·게시','설계 토론 ④ 어떤 배지가 정직한가?','PDF 보관 완료, run completed, 하지만 receipt가 아직 committed가 아닙니다.', ['data-contracts.md:54-67','workflows.md:103-120'], 'exercise',status='강의용 예시',
  prompt='원문·실행·게시·검토 상태를 각각 어떻게 표시해야 할까요?',
  answer='원문은 “PDF 보관”, 실행은 관측된 run 상태와 결과 flags를 표시합니다. 게시 거래는 “미해결/완료 확인 불가”로 남기고 최신 완료본으로 캐시하지 않습니다. 인간 검토 근거가 없으면 unreviewed를 유지합니다. completed 하나로 모두 성공 처리하지 않습니다.')

s('10 · 로드맵과 실습','작게 만들되 검증 경계는 줄이지 않는다','R0–R4는 제안 서비스의 구현 단계이며 Wiki의 P3–P6 승인과 다릅니다.', ['implementation-roadmap.md:18-87'], 'diagram',diagram='roadmap',status='설계 제안',
  takeaway='R4는 선택 단계다. 로드맵 존재를 배포·컴파일·자동화 실행 허가로 해석하지 않는다.')
s('10 · 로드맵과 실습','실습 ① read-only MVP의 계약을 그리기','코드 실행 없이도 자료 노출과 일관성 문제를 설계할 수 있습니다.', ['implementation-roadmap.md:31-45','data-contracts.md:69-127'], 'exercise',status='강의용 예시',
  prompt='합성 pageId 하나로 목록/본문 DTO와 실패 응답을 설계하세요. 인증 없음, 잘못된 ID, hash 불일치, 게시 중 충돌, 악성 Markdown을 포함합니다.',
  answer='인증·page ACL → 서버 pageId 매핑 → committed receipt와 hash 대조 → 안전 렌더링 순서가 필요합니다. 목록은 최소 필드만, 충돌은 snapshot_conflict로 반환합니다. 실행 구현 시 원본/수집 state 불변과 실제 write 거부 시험을 수용 기준으로 둡니다. 합성 fixture 결과를 실제 서비스 통과라 부르지 않습니다.')
s('10 · 로드맵과 실습','실습 ② 끊겨도 중복 실행하지 않는 채팅','이벤트 전달 실패를 업무 재실행으로 바꾸지 않는 reducer를 설계하세요.', ['implementation-roadmap.md:47-64','workflows.md:37-82'], 'exercise',status='강의용 예시',
  prompt='① 요청 timeout ② 한글 byte 분할 ③ SSE 단절 ④ stopping 중 completed 도착을 넣고, 각 상황에서 UI와 BFF의 행동을 적어 보세요.',
  answer='① 생성 여부를 먼저 확인하고 같은 요청은 같은 idempotency key로 retry합니다. ② streaming UTF-8 decode 후 프레임을 조립합니다. ③ 보관한 run ID의 status로 정합화하며 자동 새 run은 금지합니다. ④ 실제 completed와 결과 flags를 반영합니다. stop 접수가 취소 완료를 보장하지는 않습니다.')
s('10 · 로드맵과 실습','테스트 이름보다 실행 범위를 기록한다','합성 시험, 실제 통합 시험, 배포 검증은 서로 다른 증거입니다.', ['implementation-roadmap.md:89-121'], 'table',
  headers=['계층','정적·합성 시험','실제 환경에서의 시험'],rows=[['Data','ID·enum·hash·경로 fixture','snapshot 충돌·read-only 권한'],['API / SSE','allowlist·ownership·프레임 reducer','capabilities·auth·proxy timeout'],['Security','악성 URL/Markdown/symlink','키 비노출·CSRF·격리'],['UX','상태 전이·IME·긴 텍스트','viewport·키보드·screen reader'],['Reliability','중복·취소·경합','restart·stop 경합·상태 복구']],
  takeaway='실행하지 않은 것은 not_run · fake provider 성공은 실제 모델 실행 성공이 아니다.')
s('10 · 로드맵과 실습','버전 차이를 숨기지 않는 개발','최신 공식 문서와 설치 checkout은 다른 시점을 가리킬 수 있습니다.', ['evidence.md:46-80'], 'table',
  headers=['차이 사례','강의의 결론'],rows=[['keepalive 간격','공식 10초 / 로컬 30초 → 설치판과 proxy 실측'],['Runs event queue','transport 삭제 → 무손실 replay 가정 금지'],['CORS 정적 위험','브라우저 재현 전 확정 장애로 표현 금지'],['runtime / terminal','실제 capabilities와 응답으로 협상'],['turn lease','모든 호출 경로의 직렬화 검증과 구분']],
  takeaway='문서 기준 Hermes HEAD: 8d79c2ff57bba4b07e5b37ed90387b16541aef53 · 현재 runtime 재검증 아님')
s('10 · 로드맵과 실습','마지막 점검: 무엇을 안다고 말할 수 있나?','“그럴듯한 완료”보다 “관측한 범위의 완료”가 더 유용합니다.', ['evidence.md:82-97','verification.json:20-26','verification.json:90-152','verification.json:884-901'], 'compare',
  columns=[['원문 기술문서가 검증한 것','로컬 문서 링크·fence·JSON 구문','Bash는 bash -n 구문 검사','당시 metadata·hash·설정 leaf 읽기'],['그 기록이 증명하지 않는 것','live API·모델·서비스 기동','BFF/frontend 배포·운영 준비','접근성·성능·논문 본문 분석']],
  takeaway='이 강의 HTML의 렌더링 검증도, 설명 대상 웹 서비스의 운영 검증은 아니다.')
s('10 · 로드맵과 실습','기억할 설계 원칙','모든 “완료”에는 무엇이 끝났는지 목적어를 붙입니다.', ['architecture.md:95-101','data-contracts.md:54-67','security-and-operations.md:97-103'], 'hero',
  items=['cwd는 위치, sandbox는 권한.','BFF는 최소 계약, API는 실행 계약.','연결과 실행, 생성과 게시, 자동 검사와 인간 검토를 분리한다.'],
  takeaway='다음 구현의 첫 단계: 배포·권한 계약 확정 → 모델 없는 read-only MVP')
s('10 · 로드맵과 실습','원문으로 돌아가는 방법','각 슬라이드의 “근거”에서 사용한 원문 구간과 줄 번호를 확인할 수 있습니다.', ['README.md:13-27','evidence.md:6-15','verification.json:3-18'],
  items=[['입력 범위','기술 Markdown 12개와 verification.json을 읽고 강의 흐름으로 재구성했다. 원문 논문 HTML/PDF는 읽지 않았다.'],['인용 방식','로컬 기술문서의 파일명·줄 범위를 붙였다. 원문이 인용한 외부 소스를 이번 강의에서 독립 재검증한 것으로 표시하지 않는다.'],['이동과 보관','HTML에는 인용 구간·폰트·SVG·코드가 내장되어 있다. 원문 전체 링크는 이 디렉터리 구조가 유지되어야 열린다.']],
  takeaway='방향키 / PageUp·Down 이동 · T 목차 · F 전체화면 · ? 도움말 · 브라우저 인쇄')
