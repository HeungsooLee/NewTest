import streamlit as st
import openai
import os
import base64
from fpdf import FPDF
import sqlite3
import about_page

# SQLite 데이터베이스 연결 및 테이블 생성
def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_responses (
            id INTEGER PRIMARY KEY,
            nickname TEXT,
            work_preference TEXT,
            creative_thinking TEXT,
            detail_oriented TEXT,
            enjoy_social_interaction TEXT,  
            prefer_routine TEXT,
            hobby TEXT,
            mbti TEXT,
            selected_industries TEXT,
            selected_jobs TEXT,
            social_issue TEXT,
            dream TEXT,
            job_success_definition TEXT,
            career_plan TEXT,
            self_evaluation TEXT,
            job_experience TEXT,
            ai_response TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 사용자 응답과 AI 응답을 데이터베이스에 저장
def save_response(nickname, work_preference, creative_thinking, detail_oriented, enjoy_social_interaction, prefer_routine, hobby, mbti, selected_industries, selected_jobs, social_issue, dream, job_success_definition, career_plan, self_evaluation, job_experience, ai_response):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO user_responses (nickname, work_preference, creative_thinking, detail_oriented, enjoy_social_interaction, prefer_routine, hobby, mbti, selected_industries, selected_jobs, social_issue, dream, job_success_definition, career_plan, self_evaluation, job_experience, ai_response)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nickname, work_preference, creative_thinking, detail_oriented, enjoy_social_interaction, prefer_routine, hobby, mbti, ','.join(selected_industries), ','.join(selected_jobs), social_issue, dream, job_success_definition, career_plan, self_evaluation, job_experience, ai_response))
    conn.commit()
    conn.close()

# 나눔고딕 폰트 추가 및 PDF 생성 클래스
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('NanumGothic', '', 'Nanum_Gothic/NanumGothic-Regular.ttf', uni=True)
        self.add_font('NanumGothic', 'B', 'Nanum_Gothic/NanumGothic-Bold.ttf', uni=True)
        
    def header(self):
        self.set_font('NanumGothic', 'B', 12)
        self.cell(0, 10, '개인 맞춤 진로 추천 보고서', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('NanumGothic', 'B', 12)  # 모든 제목에 볼드체 적용
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)  # 제목 아래에 여백 추가

    def chapter_body(self, body):
        self.set_font('NanumGothic', '', 12)
        self.multi_cell(0, 10, body)
        self.ln(10)  # 본문 내용 아래에 여백 추가

def create_downloadable_pdf(text_content):
    # PDF 객체 생성 및 내용 추가
    pdf = PDF()
    pdf.add_page()
    lines = text_content.split('\n')
    for line in lines:
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5."):
            pdf.chapter_title(line)
        else:
            pdf.chapter_body(line)

    # PDF 파일 저장 및 base64 인코딩
    pdf_file_path = "report.pdf"
    pdf.output(pdf_file_path)
    with open(pdf_file_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()
        b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    return b64_pdf

# 환경 변수에서 OpenAI API 키 가져오기
openai.api_key = os.getenv("OPENAI_API_KEY")

# AI 응답 생성 함수
def generate_ai_response(input_data):
    try:
        system_message = f"""
        당신은 개인 맞춤 진로 추천 전문가입니다. 다음 정보를 바탕으로 유저에게 맞춤 진로를 추천해주세요. 
        모든 응답은 한국어로, 아래의 포맷과 목차를 엄격하게 지켜서 작성해야만 한다. 
        반드시 각 산업군별로 최소 2가지 이상의 직무를 추천하고, 총 추천 직무는 반드시 10개가 되도록 해줘.

        ---
        1. 적합한 산업군 및 직무 조합 추천
        1)산업군:
        1)직무:
        1)근거:

        2)산업군:
        2)직무:
        2)근거:

        3)산업군:
        3)직무:
        3)근거:

        2. 가급적 피해야 할 직업 유형
        1)
        2)
        3)

        3. 개인화된 경력 개발 조언
        1)
        2)
        3)
        4)

        4. 기술 및 능력 개발 가이드
        1) 추천된 직무에 필요한 핵심 기술 및 능력
        2) 개발해야 할 추가 기술 및 능력

        5. 업계 동향 및 미래 전망
        1)선택된 산업군의 현재 상황 및 미래 전망
        2)변화하는 시장 요구사항 및 기술 트렌드

        6. 결론 및 행동 계획
        1)개인의 목표와 비전에 맞는 행동 계획
        2)다음 단계 및 추적 방법
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": input_data},  # 실제 사용자 입력을 사용하는 부분
            ],
            temperature=0.7  # 적절한 창의성을 위한 온도 설정
        )
        return response.choices[0].message['content']
    except Exception as e:
        return str(e)

# AI 응답 포맷팅 함수
def format_ai_response(response):
    # 오타 수정 및 기타 필요한 변환 작업
    response = response.replace("귷거", "근거")

    # HTML 스타일 설정
    base_html = """
    <style>
        .report-container {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
        }
        .report-section-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .report-section-content {
            margin-bottom: 20px;  # 여백을 추가하여 줄바꿈 효과 부여
        }
    </style>
    <div class="report-container">
    """

    # '개인 맞춤 진로 추천 보고서' 제목을 굵게 강조하여 추가
    base_html += '<div class="report-section-title bold"><span class="bold">개인 맞춤 진로 추천 보고서</span></div>'
    base_html += '<br>'  # "개인 맞춤 진로 추천 보고서" 뒤에 공백 추가

    # AI 응답을 줄바꿈 기준으로 나누고 HTML로 변환
    lines = response.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5.") or line.startswith("6."):
            if i != 0:  # 첫 번째 제목을 제외한 나머지 제목 앞에 추가적인 줄바꿈 삽입
                base_html += '<br>'
            base_html += f'<div class="report-section-title">{line}</div>'
            base_html += '<br>'  # 제목 뒤에 공백 추가
        elif line.strip():  # 비어있지 않은 줄에 대해서만 <div> 태그 추가
            base_html += f'<div class="report-section-content">{line}</div>'
            base_html += '<br>'  # 내용 뒤에 공백 추가

    base_html += '</div>'
    return base_html



def create_multiselect_buttons(key, options, default=[]):
    selected_options = st.session_state.get(key, default)

    for option in options:
        if st.checkbox(option, key=f"{key}_{option}"):
            if option in selected_options:
                selected_options.remove(option)
            else:
                selected_options.append(option)

    st.session_state[key] = selected_options
    return selected_options

def main_page():
    # 데이터베이스 초기화
    init_db()

    st.title("[개인 맞춤 진로 추천 시스템]")

    if 'job_interests' not in st.session_state:
        st.session_state['job_interests'] = []
    if 'industry_interests' not in st.session_state:
        st.session_state['industry_interests'] = []

    with st.form("my_form"):
        st.markdown("**아래에 당신의 정보를 입력해주세요.**")

        nickname = st.text_input("이름 또는 별명:")
        work_preference = st.selectbox("선호하는 업무 환경:", 
                                    ('팀워크 중시', '독립적 업무', '혁신적 환경', '안정적 환경'))

        creative_thinking = st.radio("창의적 사고를 자주 하시나요?", ('예', '아니오'))
        detail_oriented = st.radio("세부 사항에 주의를 기울이시나요?", ('예', '아니오'))
        enjoy_social_interaction = st.radio("사회적 상호작용을 즐기시나요?", ('예', '아니오'))
        prefer_routine = st.radio("일상적이고 반복적인 작업을 선호하시나요?", ('예', '아니오'))

        hobby = st.text_input("취미:")
        mbti_types = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
                      "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
        mbti = st.selectbox("MBTI 성격 유형:", mbti_types)

        # 관심 있는 산업분야에 자유 입력 폼을 추가합니다.
        st.write("관심 있는 산업분야:")
        industry_options = ['IT/소프트웨어', '금융', '제조', '서비스', '교육', 
                            '의료/보건', '미디어/광고', '무역', '건설', '공공/정부', '기타']
        selected_industries = create_multiselect_buttons('industry_interests', industry_options)
        other_industry = st.text_input("위의 카테고리에 없는 산업분야를 자유롭게 입력해주세요:")

        # 관심 있는 직업분야
        st.write("관심 있는 직업분야:")
        job_options = ['소프트웨어 개발자', '마케터', '의사', '디자이너', '교사', 
                       '엔지니어', '회계사', '작가', '운동선수', '연구원', '기타']
        selected_jobs = create_multiselect_buttons('job_interests', job_options)
        other_job = st.text_input("위의 카테고리에 없는 직업분야를 자유롭게 입력해주세요:")

        # 구분선 및 여백 추가
        st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)

        # 강조된 텍스트
        st.markdown("**아래 정보는 필수 입력이 아닌 선택사항 입니다. 입력해주시면 더 정교한 진로 추천에 도움이 됩니다.**")
        # other_description = st.text_area("", height=100)

        # 마지막으로 추가된 자유 입력 폼
        st.text_area("그 외 자신의 관심사, 일에 대한 가치관, 선호하는 업무에 대한 설명, 꿈과 목표 등 자신을 잘 나타내는 설명을 자유롭게 입력해주세요:")
        # st.write("그 외 자신의 관심사, 일에 대한 가치관, 선호하는 업무에 대한 설명, 꿈과 목표 등 자신을 잘 나타내는 설명을 자유롭게 입력해주세요:")
        # other_description = st.text_area("", height=100)

        # 해결하고 싶은 사회문제 입력폼
        social_issue = st.text_input("해결하고 싶은 사회문제 (예: 저출산, 고령화, 기아, 노동력 부족, 지역 경제 활성화 등):")

        # 의미 있고 세상에 기여하고 싶은 꿈 입력폼
        dream = st.text_input("나에게도 의미가 있고 세상에도 기여할 수 있는 이루고 싶은 꿈:")    

        job_success_definition = st.text_input("귀하에게 직업적 성공이란 무엇인가요?")
        career_plan = st.text_input("앞으로 5년 또는 10년 내에 달성하고 싶은 경력 목표가 있나요?")
        self_evaluation = st.text_area("자신의 강점, 약점에 대해 서술해주세요:", height=100)
        job_experience = st.text_area("이전에 가졌던 직업 체험, 인턴십, 자원봉사 등에 대해 자유롭게 서술해주세요:", height=100)

        submitted = st.form_submit_button("제출")
        if submitted:
            # st.write("제출 완료:", nickname, work_preference, creative_thinking, detail_oriented, 
            #         enjoy_social_interaction, prefer_routine, hobby, mbti, selected_industries, 
            #         other_industry, other_job, selected_jobs, social_issue, dream, 
            #         job_success_definition, career_plan, self_evaluation, job_experience)

            # 입력 데이터를 더 구조화된 형식으로 변환
            request_data = f"이름: {nickname}, 업무 환경 선호도: {work_preference}, 창의적 사고: {creative_thinking}, 세부 사항 주의: {detail_oriented}, 사회적 상호작용: {enjoy_social_interaction}, 루틴 선호: {prefer_routine}, 취미: {hobby}, MBTI: {mbti}, 관심 산업: {selected_industries}, 기타 관심 산업: {other_industry}, 관심 직업: {selected_jobs}, 사회적 문제: {social_issue}, 꿈: {dream}, 직업적 성공 정의: {job_success_definition}, 경력 계획: {career_plan}, 자기 평가: {self_evaluation}, 직업 경험: {job_experience}"
            
            # GPT 모델에 요청 보내기
            ai_response = generate_ai_response(request_data)

            # AI 응답과 사용자 입력 데이터베이스에 저장
            save_response(nickname, work_preference, creative_thinking, detail_oriented, enjoy_social_interaction, prefer_routine, hobby, mbti, selected_industries, selected_jobs, social_issue, dream, job_success_definition, career_plan, self_evaluation, job_experience, ai_response)

            # AI 응답을 포맷팅하고 출력
            formatted_ai_response = format_ai_response(ai_response)
            st.markdown(formatted_ai_response, unsafe_allow_html=True)

            # 포맷팅된 AI 응답을 PDF로 변환하고 base64 인코딩된 데이터를 받아옴
            b64_pdf = create_downloadable_pdf(ai_response)

            # PDF 다운로드 버튼 생성
            st.markdown(f"""
                <a href="data:application/pdf;base64,{b64_pdf}" download="report.pdf">
                    <button>
                        Download PDF report
                    </button>
                </a>""",
                unsafe_allow_html=True
            )
# 새로운 메인 함수
def main():
    # 탭 생성
    tab1, tab2 = st.tabs(["Home", "About"])

    # '메인 페이지' 탭
    with tab1:
        main_page()

    # '소개 페이지' 탭
    with tab2:
        about_page.about_page()
     
if __name__ == "__main__":
    main()


# import streamlit as st

# def create_multiselect_buttons(key, options, default=[]):
#     selected_options = st.session_state.get(key, default)

#     for option in options:
#         if st.checkbox(option, key=f"{key}_{option}"):
#             if option in selected_options:
#                 selected_options.remove(option)
#             else:
#                 selected_options.append(option)

#     st.session_state[key] = selected_options
#     return selected_options

# def main():
#     st.title("진로 추천 시스템")

#     if 'job_interests' not in st.session_state:
#         st.session_state['job_interests'] = []
#     if 'industry_interests' not in st.session_state:
#         st.session_state['industry_interests'] = []

#     with st.form("my_form"):
#         st.write("아래에 당신의 정보를 입력해주세요.")

#         nickname = st.text_input("별명:")
#         work_preference = st.selectbox("선호하는 업무 환경:", 
#                                     ('팀워크 중시', '독립적 업무', '혁신적 환경', '안정적 환경'))

#         # 이 부분에 새로운 라디오 버튼을 추가합니다.
#         creative_thinking = st.radio("창의적 사고를 자주 하시나요?", ('예', '아니오'))
#         detail_oriented = st.radio("세부 사항에 주의를 기울이시나요?", ('예', '아니오'))
#         enjoy_social_interaction = st.radio("사회적 상호작용을 즐기시나요?", ('예', '아니오'))
#         prefer_routine = st.radio("일상적이고 반복적인 작업을 선호하시나요?", ('예', '아니오'))

#         hobby = st.text_input("취미:")
#         mbti_types = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
#                       "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
#         mbti = st.selectbox("MBTI 성격 유형:", mbti_types)

#         # 관심 있는 산업분야
#         st.write("관심 있는 산업분야:")
#         industry_options = ['IT/소프트웨어', '금융', '제조', '서비스', '교육', 
#                             '의료/보건', '미디어/광고', '무역', '건설', '공공/정부', '기타']
#         selected_industries = create_multiselect_buttons('industry_interests', industry_options)

#         # 관심 있는 직업분야
#         st.write("관심 있는 직업분야:")
#         job_options = ['소프트웨어 개발자', '마케터', '의사', '디자이너', '교사', 
#                        '엔지니어', '회계사', '작가', '운동선수', '연구원', '기타']
#         selected_jobs = create_multiselect_buttons('job_interests', job_options)
#         other_job = st.text_input("위의 카테고리에 없는 직업분야를 자유롭게 입력해주세요:")

#         submitted = st.form_submit_button("제출")
#         if submitted:
#             st.write("제출 완료:", nickname, work_preference, creative_thinking, detail_oriented, 
#                     enjoy_social_interaction, prefer_routine, hobby, mbti, selected_industries, 
#                     other_job, selected_jobs)

# if __name__ == "__main__":
#     main()


# import streamlit as st

# def create_multiselect_buttons(key, options, default=[]):
#     selected_options = st.session_state.get(key, default)

#     for option in options:
#         if st.checkbox(option, key=f"{key}_{option}"):
#             if option in selected_options:
#                 selected_options.remove(option)
#             else:
#                 selected_options.append(option)

#     st.session_state[key] = selected_options
#     return selected_options

# def main():
#     st.title("진로 추천 시스템")

#     if 'job_interests' not in st.session_state:
#         st.session_state['job_interests'] = []
#     if 'industry_interests' not in st.session_state:
#         st.session_state['industry_interests'] = []

#     with st.form("my_form"):
#         st.write("아래에 당신의 정보를 입력해주세요.")

#         nickname = st.text_input("별명:")
#         work_preference = st.selectbox("선호하는 업무 환경:", 
#                                     ('팀워크 중시', '독립적 업무', '혁신적 환경', '안정적 환경'))

#         st.write("창의적 사고를 자주 하시나요?")
#         creative_thinking = st.radio("", ('예', '아니오'))
        
#         st.write("세부 사항에 주의를 기울이시나요?")
#         detail_oriented = st.radio("", ('예', '아니오'))
        
#         st.write("사회적 상호작용을 즐기시나요?")
#         enjoy_social_interaction = st.radio("", ('예', '아니오'))
        
#         st.write("일상적이고 반복적인 작업을 선호하시나요?")
#         prefer_routine = st.radio("", ('예', '아니오'))

#         hobby = st.text_input("취미:")
#         mbti_types = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", 
#                       "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
#         mbti = st.selectbox("MBTI 성격 유형:", mbti_types)

#         # 관심 있는 산업분야
#         st.write("관심 있는 산업분야:")
#         industry_options = ['IT/소프트웨어', '금융', '제조', '서비스', '교육', 
#                             '의료/보건', '미디어/광고', '무역', '건설', '공공/정부', '기타']
#         selected_industries = create_multiselect_buttons('industry_interests', industry_options)

#         # 관심 있는 직업분야
#         st.write("관심 있는 직업분야:")
#         job_options = ['소프트웨어 개발자', '마케터', '의사', '디자이너', '교사', 
#                        '엔지니어', '회계사', '작가', '운동선수', '연구원', '기타']
#         selected_jobs = create_multiselect_buttons('job_interests', job_options)
#         other_job = st.text_input("위의 카테고리에 없는 직업분야를 자유롭게 입력해주세요:")

#         submitted = st.form_submit_button("제출")
#         if submitted:
#             st.write("제출 완료:", nickname, work_preference, creative_thinking, detail_oriented, 
#                     enjoy_social_interaction, prefer_routine, hobby, mbti, selected_industries, 
#                     other_job, selected_jobs)

# if __name__ == "__main__":
#     main()