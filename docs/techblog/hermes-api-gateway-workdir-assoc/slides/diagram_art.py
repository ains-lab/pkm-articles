"""Original inline SVG teaching diagrams; stdlib only, no external rendering."""
from html import escape as E

class Graph:
    def __init__(self, key, desc):
        self.key=key; self.desc=desc; self.boxes=[]; self.edges=[]; self.regions=[]; self.labels=[]
    def node(self,x,y,w,title,sub='',h=90,tone='normal'):
        color='#FFADA5' if tone=='danger' else '#76C9E6'
        self.boxes.append(f'<g class="node"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#183453" stroke="{color}" stroke-width="2"/><text x="{x+w/2}" y="{y+35}" text-anchor="middle" class="node-title">{E(title)}</text><text x="{x+w/2}" y="{y+66}" text-anchor="middle" class="node-sub">{E(sub)}</text></g>')
        return self
    def edge(self,x1,y1,x2,y2,label='',danger=False,via=None):
        col='#FFADA5' if danger else '#76C9E6'; marker=f'{self.key}-red' if danger else f'{self.key}-arrow'
        path=f'M{x1},{y1} '+(' '.join(f'L{x},{y}' for x,y in via)+' ' if via else '')+f'L{x2},{y2}'
        dash=' stroke-dasharray="8 6"' if danger else ''
        self.edges.append(f'<path d="{path}" fill="none" stroke="{col}" stroke-width="2.5" marker-end="url(#{marker})"{dash}/>')
        if label:
            self.label((x1+x2)/2,(y1+y2)/2-15,label)
        return self
    def label(self,x,y,text,anchor='middle'):
        self.labels.append(f'<text class="edge-label" x="{x}" y="{y}" text-anchor="{anchor}" paint-order="stroke" stroke="#10233F" stroke-width="8" stroke-linejoin="round">{E(text)}</text>'); return self
    def region(self,x,y,w,h,title):
        self.regions.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#D3DAE4" stroke-dasharray="8 6"/><text x="{x+16}" y="{y+29}" class="region-label">{E(title)}</text>'); return self
    def html(self):
        return f'<figure class="diagram"><div class="diagram-scroll" tabindex="0" role="region" aria-label="도식: {E(self.desc)}. 좁은 화면에서는 가로로 스크롤하세요."><svg viewBox="0 0 1400 500" role="img" aria-labelledby="{self.key}-title {self.key}-desc"><title id="{self.key}-title">{E(self.desc)}</title><desc id="{self.key}-desc">{E(self.desc)}</desc><defs><marker id="{self.key}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" fill="#76C9E6"/></marker><marker id="{self.key}-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" fill="#FFADA5"/></marker></defs>{"".join(self.regions+self.edges+self.boxes+self.labels)}<text x="28" y="480" class="legend">실선: 데이터·상태   /   붉은 점선: 별도 조건·통제 경로   /   회색 점선: 영역·생명선</text></svg></div><figcaption class="sr-only">{E(self.desc)}</figcaption></figure>'

def chain(key, desc, nodes, labels=None):
    g=Graph(key,desc)
    w=260 if len(nodes)<=4 else 220
    step=340 if len(nodes)<=4 else 276
    start=(1400-((len(nodes)-1)*step+w))/2
    for i,(a,b) in enumerate(nodes):
        x=start+i*step; g.node(x,190,w,a,b)
        if i: g.edge(x-step+w,235,x,235, (labels or ['']*len(nodes))[i-1])
    return g

def sequence(key,desc,participants,steps):
    g=Graph(key,desc); xs=[150,510,870,1230][:len(participants)]
    for x,p in zip(xs,participants):
        g.node(x-120,20,240,p,'역할',80)
        g.edges.append(f'<path d="M{x},100 V440" stroke="#4E5F78" stroke-dasharray="5 6"/>')
    for idx,(a,b,label) in enumerate(steps):
        y=160+idx*82; g.edge(xs[a],y,xs[b],y,label)
    return g

def render(key):
    if key=='three-paths':
        g=Graph(key,'정형 읽기는 모델 없이, 질의는 승인된 실행 환경으로, 지식 게시는 별도 승인 게시 경로로 Wiki에 연결한다.')
        for y,a,b,c in [(45,'정형 읽기','BFF · 공개 DTO','기존 노트 / 서지'),(185,'에이전트 질의','Gateway · 제한 Agent','허용 자료의 답변'),(325,'지식 게시','별도 승인 게시자','lock · journal · receipt')]:
            g.node(40,y,300,a,'서로 다른 권한');g.node(550,y,310,b,'책임 경계');g.node(1030,y,320,c,'결과와 증거');g.edge(340,y+45,550,y+45);g.edge(860,y+45,1030,y+45,danger=y==325)
    elif key=='architecture':
        g=Graph(key,'사용자는 TLS를 거쳐 BFF에 접근한다. BFF는 read facade로 Wiki를 읽고, 별도 승인된 질의는 Gateway와 제한 Agent로 보낸다. 수집과 게시는 독립 경로다.')
        g.region(360,20,995,390,'사설 서비스 영역 · 제안 배치')
        g.node(30,95,250,'인증 브라우저','HTTPS');g.node(390,95,260,'BFF','auth · owner · DTO');g.node(780,95,250,'read facade','허용된 읽기');g.node(1100,95,220,'Wiki','파일 원장')
        g.node(390,295,260,'Hermes API','HTTP / SSE');g.node(780,295,250,'제한 Agent','격리 별도 검증');g.node(1100,295,220,'수집 / 게시','별도 승인 경로',tone='danger')
        g.edge(280,140,390,140);g.edge(650,140,780,140);g.edge(1030,140,1100,140);g.edge(520,185,520,295);g.edge(650,340,780,340);g.edge(905,295,1140,185,via=[(905,245),(1140,245)]);g.edge(1210,295,1210,185,danger=True)
        g.label(1010,226,'정책 허용 읽기');g.label(1230,256,'별도 쓰기',anchor='start')
    elif key=='read-sequence':
        g=sequence(key,'UI의 pageId 요청을 BFF가 권한 검사한 뒤 Wiki snapshot으로 읽고, 확인된 DTO와 검토 상태를 UI에 반환한다.',['사용자 / UI','BFF','Wiki','화면'],[(0,1,'pageId 요청 · 사용자 인증'),(1,2,'committed + 본문 hash 검사'),(2,1,'일관된 snapshot / 충돌'),(1,3,'최소 DTO + 검토 상태 + ETag')])
    elif key=='query-sequence':
        g=sequence(key,'BFF는 질문과 선택 pageId를 검증하고 서버 소유 세션과 정책으로 Runs 요청을 구성한다. 결과는 대화 답변이며 Wiki 게시가 아니다.',['사용자 / UI','BFF','Hermes','결과'],[(0,1,'질문 + 선택 pageId'),(1,2,'owner · 정책 확인 후 POST run'),(2,1,'run ID · 상태 · 허용 이벤트'),(1,3,'답변 + 확인 가능한 출처')])
    elif key=='cwd':
        g=Graph(key,'local Gateway는 명시적 terminal.cwd가 있으면 bridge로 전달한다. 점, auto, cwd는 placeholder다. 명시값이 없으면 MESSAGING_CWD, 다음으로 home을 쓴다. 명령과 세션 cwd는 별도로 우선할 수 있다.')
        g.node(40,70,370,'terminal.cwd 명시값?','., auto, cwd는 placeholder');g.node(570,70,370,'명시한 작업 기준','TERMINAL_CWD로 전달');g.edge(410,115,570,115,'있음')
        g.node(40,290,370,'명시값 없음','local backend');g.node(570,290,370,'MESSAGING_CWD','legacy fallback');g.node(1070,290,290,'사용자 home','legacy도 없을 때');g.edge(225,160,225,290,'없음');g.edge(410,335,570,335);g.edge(940,335,1070,335)
        g.label(1020,215,'명령 workdir · 세션 cwd는 별도 우선')
    elif key=='data-layers':
        g=Graph(key,'원본 raw와 지식 Markdown, 내부 운영 상태와 실행 근거를 분리한다. 승인된 지식과 서지만 BFF projection을 거쳐 공개 DTO가 된다.')
        g.node(40,50,350,'raw/','원본 + source.json');g.node(40,195,350,'지식 Markdown','entities · concepts 등');g.node(40,340,350,'_meta/','상태 · 정책 · 실행 근거',tone='danger')
        g.node(590,195,340,'BFF projection','공개 allowlist');g.node(1090,195,270,'공개 DTO','필요한 필드만')
        g.edge(390,95,590,220,via=[(470,95),(470,220)]);g.edge(390,240,590,240);g.edge(930,240,1090,240);g.label(750,355,'전체 raw · _meta · log 자동 공개 금지')
    elif key=='snapshot':
        g=chain(key,'committed receipt를 확인하고 revision과 파일 hash를 검사한다. 읽기 전후 상태가 같을 때만 캐시하고 바뀌었으면 제한 재시도나 snapshot_conflict로 처리한다.',[('거래 확인','committed receipt'),('실물 확인','revision + hash'),('전후 대조','상태 식별자'),('응답 / 캐시','일관된 snapshot')])
        g.label(720,370,'중간 상태가 바뀜 → 제한 재시도 또는 snapshot_conflict')
    elif key=='sse-fanout':
        g=Graph(key,'설치판의 Runs 단일 queue는 여러 upstream 구독자에게 이벤트를 분할 전달할 수 있다. BFF 한 곳만 구독하고 UI 탭에는 자체 fan-out한다. 끊기면 GET run status로 복구한다.')
        g.node(40,190,310,'Runs event queue','설치판 제약');g.node(560,190,310,'BFF','단일 upstream 구독');g.node(1080,80,280,'UI 탭 A','허용 이벤트');g.node(1080,300,280,'UI 탭 B','허용 이벤트')
        g.edge(350,235,560,235,'한 구독');g.edge(870,235,1080,125,via=[(970,235),(970,125)]);g.edge(870,235,1080,345,via=[(970,235),(970,345)]);g.label(690,400,'복구: GET /v1/runs/{id}')
    elif key=='reconnect':
        g=chain(key,'UI는 active에서 disconnected로 바뀐 뒤 기존 run 상태를 조회해 running 또는 terminal로 정합화한다. 자동 새 run 생성은 하지 않는다.',[('연결 단절','UI: disconnected'),('소유권 확인','보관한 run ID'),('상태 조회','GET run status'),('화면 정합화','active / terminal')])
        g.label(700,370,'최종 snapshot은 임시 delta와 분리 · 자동 재실행 금지')
    elif key=='stop':
        g=Graph(key,'stop 요청 후 stopping은 접수 상태다. executor가 중지를 인정하면 cancelled가 되지만 완료와 경합하면 completed일 수 있다. 연결 abort나 이미 생긴 효과의 rollback과 다르다.')
        g.node(40,190,280,'POST /stop','owner · 정책 확인');g.node(530,190,300,'stopping','중지 요청 접수');g.node(1070,80,290,'cancelled','실제 중지 인정');g.node(1070,300,290,'completed','완료와 경합 가능')
        g.edge(320,235,530,235);g.edge(830,235,1070,125,via=[(950,235),(950,125)]);g.edge(830,235,1070,345,via=[(950,235),(950,345)])
    elif key=='ui-state':
        g=Graph(key,'UI는 submitting, accepted, active를 거친다. active에서 승인 대기와 복귀, 단절 후 정합화, 중지 또는 terminal로 전이할 수 있다. UI 로컬 상태와 Gateway 상태를 함께 저장한다.')
        for x,a,b in [(40,'submitting','요청 중'),(430,'accepted','run ID 보관'),(820,'active','queued / running')]:g.node(x,50,290,a,b)
        g.edge(330,95,430,95);g.edge(720,95,820,95)
        g.node(40,310,350,'awaiting_approval','pending choices');g.node(520,310,370,'disconnected','→ reconciling');g.node(1020,310,340,'terminal','완료 / 실패 / 취소 / 중단')
        g.edge(910,140,215,310,via=[(910,220),(215,220)]);g.edge(965,140,705,310,via=[(965,240),(705,240)]);g.edge(1030,140,1190,310,via=[(1030,220),(1190,220)])
        g.node(1140,50,220,'stopping','중지 접수');g.edge(1110,95,1140,95);g.edge(1250,140,1250,310)
        g.label(710,438,'단순화: 승인 후 active 복귀 · 단절 후 상태 정합화 경로는 설명 참조')
    elif key=='threats':
        g=Graph(key,'질문, 문서, URL과 브라우저 요청은 비신뢰 입력이다. BFF 인증과 owner 검사, Agent 도구 및 자료 제한, OS와 egress 경계를 지나 보호 자료를 사용한다.')
        g.region(445,90,925,270,'집행해야 할 경계 · 배포/검증 별도')
        g.node(30,190,320,'비신뢰 입력','질문 · 문서 · URL',tone='danger');g.node(480,190,260,'BFF','auth · ACL');g.node(810,190,260,'Agent 환경','tool · data policy');g.node(1140,190,200,'OS / egress','실제 접근 제한');g.edge(350,235,480,235,danger=True);g.edge(740,235,810,235);g.edge(1070,235,1140,235)
    elif key=='collection':
        g=Graph(key,'같은 버전의 공식 HTML을 먼저 저장한다. 공식 미제공이 확인된 경우에만 동일 버전 PDF 원본을 저장한다. 네트워크 오류는 미제공이 아니며 둘 모두 컴파일과 분리한다.')
        g.node(40,190,310,'동일 버전 HTML','공식 원본 우선');g.node(570,60,340,'HTML 원본 저장','HTTP 바이트 보존');g.node(570,320,340,'PDF 원본 저장','공식 HTML 미제공 확인');g.node(1070,190,290,'보관 상태 기록','컴파일과 분리')
        g.edge(350,235,570,105,via=[(450,235),(450,105)]);g.edge(350,235,570,365,via=[(450,235),(450,365)],danger=True);g.edge(910,105,1070,215,via=[(990,105),(990,215)]);g.edge(910,365,1070,255,via=[(990,365),(990,255)]);g.label(690,242,'403 / 429 / 5xx / timeout ≠ 미제공')
    elif key=='publication':
        g=Graph(key,'입력과 정책 승인 및 snapshot, 읽기와 근거 검토, 게시 승인, collection lock과 최종 hash 확인, write-ahead journal과 조건부 게시를 거쳐 committed receipt와 실물을 대조한 뒤 캐시를 무효화한다.')
        positions=[(40,60,'승인 / snapshot','입력 · 정책 · 모델'),(530,60,'읽기 / 검토','인용 · 미독 범위'),(1020,60,'게시 승인','편집 중지 포함'),(1020,310,'lock / 최종 hash','수집 우선 시간'),(530,310,'journal / 게시','조건부 변경'),(40,310,'committed / 실물','receipt → 캐시 갱신')]
        for x,y,a,b in positions:g.node(x,y,340,a,b)
        g.edge(380,105,530,105);g.edge(870,105,1020,105);g.edge(1190,150,1190,310,danger=True);g.edge(1020,355,870,355);g.edge(530,355,380,355)
    elif key=='roadmap':
        g=chain(key,'R0 배포 계약 확정, R1 모델 없는 read-only MVP, R2 통제된 질의, R3 읽기 전용 운영 상태, R4 선택적인 승인 지식 작업 연결 순서다.',[('R0','배포 계약'),('R1','read-only MVP'),('R2','통제된 질의'),('R3','운영 상태'),('R4 · 선택','승인 지식 작업')])
        g.label(700,370,'각 단계의 수용 기준을 검증 · R4와 Wiki P3–P6 실행 승인은 별개')
    else:
        raise ValueError(key)
    return g.html()
