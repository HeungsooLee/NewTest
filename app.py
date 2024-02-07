from flask import Flask, render_template, request, redirect, url_for, jsonify, session, current_app
import os
import base64
from fpdf import FPDF
import random
import openai
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler

# 기존 로깅 설정 수정
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False if os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'False' else True
    app.config['DEBUG'] = True
    # 환경 변수 검증 로그 추가
    app.logger.debug(f"OpenAI API Key: {os.getenv('OPENAI_API_KEY')}")


    db = SQLAlchemy(app)

    # 로거 설정을 여기에 추가
    if not app.debug:
        file_handler = RotatingFileHandler('flask_app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask application startup')    

    class UserResponse(db.Model):
        __tablename__ = 'user_responses'
        id = db.Column(db.Integer, primary_key=True)
        nickname = db.Column(db.String(255), nullable=False)
        work_preference = db.Column(db.String(255), nullable=True)
        creative_thinking = db.Column(db.String(255), nullable=True)
        detail_oriented = db.Column(db.String(255), nullable=True)
        enjoy_social_interaction = db.Column(db.String(255), nullable=True)
        prefer_routine = db.Column(db.String(255), nullable=True)
        hobby = db.Column(db.String(255), nullable=True)
        mbti = db.Column(db.String(255), nullable=True)
        selected_industries = db.Column(db.String(255), nullable=True)
        other_industry = db.Column(db.String(255), nullable=True)
        selected_jobs = db.Column(db.String(255), nullable=True)
        other_job = db.Column(db.String(255), nullable=True)
        social_issue = db.Column(db.String(255), nullable=True)
        dream = db.Column(db.String(255), nullable=True)
        job_success_definition = db.Column(db.String(255), nullable=True)
        career_plan = db.Column(db.String(255), nullable=True)
        self_evaluation = db.Column(db.String(255), nullable=True)
        job_experience = db.Column(db.String(255), nullable=True)
        ai_response = db.Column(db.Text, nullable=True)


    # # 데이터베이스 초기화 및 테이블 생성
    # @app.before_first_request
    # def create_tables():
    #     db.create_all()

    def save_response(**kwargs):
        try:
            # 리스트로 된 필드를 적절히 처리
            kwargs['selected_industries'] = ",".join(kwargs.get('selected_industries', []))
            kwargs['selected_jobs'] = ",".join(kwargs.get('selected_jobs', []))
            
            new_response = UserResponse(**kwargs)
            db.session.add(new_response)
            db.session.commit()
            current_app.logger.info("Data saved successfully.")
        except Exception as e:
            current_app.logger.error(f"Error saving data: {e}")


    # def save_response(**kwargs):
    #     new_response = UserResponse(**kwargs)
    #     db.session.add(new_response)
    #     db.session.commit()

    # 데이터베이스 초기화 및 테이블 생성
    with app.app_context():
        db.create_all()


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
            self.set_font('NanumGothic', 'B', 12)
            self.cell(0, 10, title, 0, 1, 'L')
            self.ln(5)

        def chapter_body(self, body):
            self.set_font('NanumGothic', '', 12)
            self.multi_cell(0, 10, body)
            self.ln(10)    

    # PDF 생성 함수
    def create_downloadable_pdf(text_content):
        pdf = PDF()
        pdf.add_page()
        lines = text_content.split('\n')
        for line in lines:
            if line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5.") or line.startswith("6.") or line.startswith("7."):
                pdf.chapter_title(line)
            else:
                pdf.chapter_body(line)

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
            # Azure OpenAI 설정
            openai.api_type = "azure"
            openai.api_base = "https://pro.openai.azure.com/"
            openai.api_version = "2023-07-01-preview"
            openai.api_key = os.getenv("OPENAI_API_KEY")

            # input_data 로깅 추가
            app.logger.debug(f"Prepared input_data for OpenAI API: {input_data}")  # 이 줄을 추가

            # 요청 전 로그 추가
            app.logger.debug(f"Sending request to OpenAI API with input_data: {input_data}")            
     

            # Azure OpenAI를 사용하여 GPT-4에 요청
            response = openai.ChatCompletion.create(
                engine="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": """너는 개인 맞춤 진로 추천 전문가야.
            응답은 심층적이고 구체적이어야 하며, 유저에게 새로운 관점을 제공해야만 해. 유저의 데이터를 기반으로 한 추천 사항은 실제로 유용하고 실행 가능해야만 해.
            유저가 제공한 정보를 분석하여, 그들의 성향과 잠재력에 가장 적합한 산업군 및 직무를 식별하고, 이에 대한 근거를 명확히 제시해.

            모든 응답은 한국어로, 아래의 포맷과 목차를 엄격하게 지켜서 작성해야만해. 
            반드시 각 산업군별로 최소 2가지 이상의 직무를 추천하고, 총 추천 직무는 반드시 10개가 되도록 해줘.

            너무 일반적인 응답은 피하도록 해. 창의적으로 대답해.
            최대한 AI같지 않은 자연스러운 사람 말투로 응답해.

            ---
            1. 적합한 산업군 및 직무 조합 추천
            1)산업군:
            1-1)직무:
            1-2)직무:
            1-3)근거:

            2)산업군:
            2-1)직무:
            2-2)직무:
            2-3)근거:

            3)산업군:
            3-1)직무:
            3-2)직무:
            3-3)근거:

            2. 가급적 피해야 할 직업 유형
            1)
            2)
            3)

            3. 개인화된 경력 개발 조언
            1)
            2)
            3)
            4)

            4. 자기 이해 및 자아 성찰
            [지침: 이 섹션에서는 유저가 자신의 강점, 약점, 가치관, 열정 등을 탐색하고 이해하는 방법에 대한 조언을 제공합니다. 자기 인식을 통해 더 만족스러운 직업 경로를 찾는 데 도움을 줍니다. 이 지침을 바탕으로 유저에게 구체적인 조언을 제공해야 합니다.]
            1)
            2)
            3)

            5. 기술 및 능력 개발 가이드
            1) 추천된 직무에 필요한 핵심 기술 및 능력:

            2) 개발해야 할 추가 기술 및 능력:

            6. 업계 동향 및 미래 전망
            1)선택된 산업군의 현재 상황 및 미래 전망:

            2)변화하는 시장 요구사항 및 기술 트렌드:

            7. 결론 및 행동 계획
            1)개인의 목표와 비전에 맞는 행동 계획:

            2)다음 단계 및 추적 방법:"""
                    },
                    {"role": "user", "content": input_data}
                ],
                temperature=0.8,
                max_tokens=4096,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,                   
                stop=None
                # stop=["\n", "1.", "2.", "3."]
            )                       

            # API 응답 전체 로깅 - 세부 정보 포함
            app.logger.debug(f"Full OpenAI API Response: {response}")  # 이 줄을 추가            
            
            # 디버깅: API 호출 응답 전체 로깅
            app.logger.debug(f"OpenAI API Response: {response}")

            # # 수정된 응답 처리 부분
            # if response.choices and response.choices[0].text.strip():
            #     ai_text = response.choices[0].text.strip()
            # else:
            #     ai_text = "AI 응답이 비어있습니다."

            # 수정된 응답 처리 부분
            if response.choices and response.choices[0].message['content'].strip():
                ai_text = response.choices[0].message['content'].strip()
            else:
                ai_text = "AI 응답이 비어있습니다."
            
            return ai_text
        except Exception as e:
            app.logger.error(f"Exception occurred during AI response generation: {e}", exc_info=True)
            return "응답 생성 중 오류 발생"            

        #     # 응답 처리 수정
        #     if 'choices' in response and len(response['choices']) > 0 and 'text' in response['choices'][0]:
        #         ai_text = response['choices'][0]['text'].strip()
        #     else:
        #         ai_text = "AI 응답이 비어있습니다."
            
        #     return ai_text
        # except Exception as e:
        #     app.logger.error(f"Exception occurred during AI response generation: {e}", exc_info=True)
        #     return "응답 생성 중 오류 발생"            


        #     # OpenAI 응답에서 실제 텍스트 데이터 추출
        #     if 'choices' in response and len(response['choices']) > 0:
        #         ai_text = response['choices'][0]['message']['content'].strip() if 'message' in response['choices'][0] and 'content' in response['choices'][0]['message'] else "AI 응답 생성 오류"
        #         # 추출된 AI 응답 로깅
        #         app.logger.debug(f"Extracted AI Text: {ai_text}")
        #     else:
        #         ai_text = "AI 응답이 비어있습니다."
        #         # 비어있는 응답에 대한 로그 추가
        #         app.logger.debug("AI response is empty.")                

        #     # 디버깅: 추출된 AI 응답 로깅
        #     app.logger.debug(f"Extracted AI Text: {ai_text}")
            
        #     return ai_text
        # except Exception as e:
        #     # 예외 발생 시 로그 추가
        #     app.logger.error(f"Exception occurred during AI response generation: {e}", exc_info=True)
        #     return "응답 생성 중 오류 발생"
            
        #     return response.choices[0].message['content']
        # except Exception as e:
        #     return str(e)            




    # 메인 페이지
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html')

    @app.route('/terms')
    def terms():
        return render_template('terms.html')        

    # 추천 요청 페이지
    @app.route('/recommendation', methods=['GET', 'POST'])
    def recommendation():
        if request.method == 'POST':
            app.logger.info("Processing recommendation form submission")
            # 폼 데이터 수집
            form_data = {
                'nickname': request.form.get('nickname', ''),
                'work_preference': request.form.get('work_preference', ''),
                'creative_thinking': request.form.get('creative_thinking', ''),
                'detail_oriented': request.form.get('detail_oriented', ''),
                'enjoy_social_interaction': request.form.get('enjoy_social_interaction', ''),
                'prefer_routine': request.form.get('prefer_routine', ''),
                'hobby': request.form.get('hobby', ''),
                'mbti': request.form.get('mbti', ''),
                'selected_industries': request.form.getlist('selected_industries'),
                'other_industry': request.form.get('other_industry', ''),
                'selected_jobs': request.form.getlist('selected_jobs'),
                'other_job': request.form.get('other_job', ''),
                'social_issue': request.form.get('social_issue', ''),
                'dream': request.form.get('dream', ''),
                'job_success_definition': request.form.get('job_success_definition', ''),
                'career_plan': request.form.get('career_plan', ''),
                'self_evaluation': request.form.get('self_evaluation', ''),
                'job_experience': request.form.get('job_experience', ''),
                'ai_response': ''  # AI 응답은 이후에 설정
            }                

            # form_data = {
            #     'nickname': request.form.get('nickname'),
            #     'work_preference': request.form.get('work_preference'),
            #     'creative_thinking': request.form.get('creative_thinking'),
            #     'detail_oriented': request.form.get('detail_oriented'),
            #     'enjoy_social_interaction': request.form.get('enjoy_social_interaction'),
            #     'prefer_routine': request.form.get('prefer_routine'),
            #     'hobby': request.form.get('hobby'),
            #     'mbti': request.form.get('mbti'),
            #     'selected_industries': ",".join(request.form.getlist('industry_interests')),
            #     'other_industry': request.form.get('other_industry'),
            #     'selected_jobs': ",".join(request.form.getlist('job_interests')),
            #     'other_job': request.form.get('other_job'),
            #     'social_issue': request.form.get('social_issue'),
            #     'dream': request.form.get('dream'),
            #     'job_success_definition': request.form.get('job_success_definition'),
            #     'career_plan': request.form.get('career_plan'),
            #     'self_evaluation': request.form.get('self_evaluation'),
            #     'job_experience': request.form.get('job_experience')            
            # }        
            session['nickname'] = form_data['nickname']  # 사용자 식별 정보를 세션에 저장


            # 입력 데이터를 구조화된 형식으로 변환
            request_data = f"""
            이름 또는 별명: {form_data['nickname']},
            선호하는(좋아하는) 업무 환경: {form_data['work_preference']},
            창의적 사고를 자주 하시나요: {form_data['creative_thinking']},
            세부 사항에 주의를 기울이시나요: {form_data['detail_oriented']},
            사회적 상호작용을 즐기시나요: {form_data['enjoy_social_interaction']},
            일상적이고 반복적인 작업을 선호하시나요: {form_data['prefer_routine']},
            취미: {form_data['hobby']},
            MBTI 성격 유형: {form_data['mbti']},
            관심 있는 산업분야: {form_data['selected_industries']},
            위의 카테고리에 없는 산업분야를 자유롭게 입력해주세요: {form_data['other_industry']},
            관심 있는 직업분야: {form_data['selected_jobs']},
            위의 카테고리에 없는 직업분야를 자유롭게 입력해주세요: {form_data['other_job']},
            해결하고 싶은 사회문제(예시 : 저출산, 고령화, 기아, 노동력 부족, 지역 경제 활성화): {form_data['social_issue']},
            나에게도 의미가 있고 세상에도 기여할 수 있는 이루고 싶은 꿈: {form_data['dream']},
            귀하에게 직업적 성공이란 무엇인가요: {form_data['job_success_definition']},
            앞으로 5년 또는 10년 내에 달성하고 싶은 경력 목표가 있나요: {form_data['career_plan']},
            자신의 강점, 약점에 대해 서술해주세요: {form_data['self_evaluation']},
            이전에 가졌던 직업 체험, 인턴십, 자원봉사 등에 대해 자유롭게 서술해주세요: {form_data['job_experience']}
            """    
   
            # 입력 데이터를 구조화된 형식으로 변환하여 AI 응답 생성
            ai_response = generate_ai_response(request_data)
            form_data['ai_response'] = ai_response

            # DB에 저장하고 성공적으로 저장되었다면 결과 페이지로 리디렉션
            try:
                save_response(**form_data)
                session['ai_response'] = ai_response
                return redirect(url_for('result'))
            except Exception as e:
                app.logger.error(f"Error saving data: {e}")
                # 오류 처리 로직 추가 (예: 오류 메시지를 사용자에게 표시)
                return "데이터 저장 중 오류가 발생했습니다."


        return render_template('recommendation.html')



    # # 결과 페이지
    # @app.route('/result')
    # def result():
    #     ai_response = session.get('ai_response', None)
    #     if ai_response:
    #         b64_pdf = create_downloadable_pdf(ai_response)
    #         # 세션에서 AI 응답 제거
    #         session.pop('ai_response', None)
    #         return render_template('result.html', ai_response=ai_response, b64_pdf=b64_pdf)
    #     else:
    #         return "결과를 찾을 수 없습니다."

    # 결과 페이지
    # @app.route('/result')
    # def result():
    #     # 사용자 식별 정보를 세션에서 가져오기
    #     nickname = session.get('nickname')
    #     if not nickname:
    #         return "사용자 식별 정보가 없습니다."

    #     # nickname을 사용하여 데이터베이스에서 사용자의 마지막 응답 검색
    #     user_response = UserResponse.query.filter_by(nickname=nickname).order_by(UserResponse.id.desc()).first()

    #     if user_response:
    #         ai_response = user_response.ai_response
    #         b64_pdf = create_downloadable_pdf(ai_response)  # PDF 생성 로직은 동일하게 유지
    #         return render_template('result.html', ai_response=ai_response, b64_pdf=b64_pdf)
    #     else:
    #         return "결과를 찾을 수 없습니다."    

    # 결과 페이지
    @app.route('/result')
    def result():
        nickname = session.get('nickname')
        if not nickname:
            app.logger.debug("No nickname found in session.")
            return "사용자 식별 정보가 없습니다."

        try:
            user_response = UserResponse.query.filter_by(nickname=nickname).order_by(UserResponse.id.desc()).first()
            if user_response:
                app.logger.info(f"User response found for nickname: {nickname}")  # 사용자 응답 발견 로깅
                logging.info(f"User response found for nickname: {nickname}")
                ai_response = user_response.ai_response
                app.logger.debug(f"AI response for nickname {nickname}: {ai_response}")  # 디버깅 로그 추가
                b64_pdf = create_downloadable_pdf(ai_response)
                return render_template('result.html', ai_response=ai_response, b64_pdf=b64_pdf)
            else:
                app.logger.error("No user response found.")  # 사용자 응답 미발견 로깅
                logging.error("No user response found.")
                return "결과를 찾을 수 없습니다."
        except Exception as e:
            app.logger.debug(f"No user response found for nickname: {nickname}")  # 디버깅 로그 추가
            app.logger.error(f"Error fetching user response: {e}")  # 데이터 조회 오류 로깅
            logging.error(f"Error fetching user response: {e}")
            return "데이터 조회 중 오류가 발생했습니다."

    # if __name__ == '__main__':
    #     app.logger.setLevel(logging.DEBUG)
    #     app.run(debug=True)

    return app  # 애플리케이션 객체를 반환합니다.


# 애플리케이션 인스턴스 생성
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)