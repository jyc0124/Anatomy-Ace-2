import streamlit as st
import pandas as pd
import os
import random
import json
from PIL import Image
import io
import base64
from datetime import datetime

# 디버깅 모드 설정 (True면 켜짐, False면 꺼짐)
DEBUG_MODE = False

def debug_print(message):
    """디버깅 모드일 때만 메시지를 출력하는 함수"""
    if DEBUG_MODE:
        st.write(f"🐞 디버깅: {message}")

# 페이지 설정
st.set_page_config(
    page_title="Anatomy Ace", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    .main-title {
        font-size: 50px !important;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 30px;
        text-align: center;
    }
    .subtitle {
        font-size: 24px !important;
        color: #555;
        margin-bottom: 30px;
        text-align: center;
    }
    .section-title {
        font-size: 32px !important;
        font-weight: bold;
        color: #333;
        margin: 30px 0 20px 0;
        border-bottom: 2px solid #1E88E5;
        padding-bottom: 10px;
    }
    .info-text {
        font-size: 20px !important;
        margin-bottom: 10px;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4CAF50;
        padding: 15px;
        border-radius: 5px;
        font-size: 20px !important;
        margin: 20px 0;
    }
    .instruction-box {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .instruction-item {
        font-size: 18px !important;
        margin: 10px 0;
    }
    .stButton button {
        font-size: 22px !important;
        font-weight: bold;
        padding: 12px 30px;
    }
    .stats-card {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .stats-number {
        font-size: 28px !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .stats-label {
        font-size: 18px !important;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# 메인 페이지 디자인
st.markdown("<div class='main-title'>🧠 Anatomy Ace - 해부학 모의고사</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해부학 시험 준비를 위한 모의고사 앱입니다.</div>", unsafe_allow_html=True)

# 데이터 로드 - 간단하게 직접 로드
try:
    questions = pd.read_csv("data/questions.csv")
    total_questions = len(questions)
    
    # 문제 수 표시 부분 삭제 (문제가 있으므로 표시하지 않음)
    # st.markdown(f"<div class='success-box'>✅ 총 {total_questions}개의 문제가 로드되었습니다.</div>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"문제 데이터를 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# 모의고사 시작 버튼 - 단순화
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 모의고사 시작하기", type="primary", use_container_width=True):
        # 세션 상태 초기화
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # 단순히 페이지 이동 (URL 파라미터 없이)
        st.switch_page("pages/exam.py")

# 앱 설명
st.markdown("<div class='section-title'>📋 앱 사용 방법</div>", unsafe_allow_html=True)

# 사용 방법 설명
st.markdown("""
<div class='instruction-box'>
    <div class='instruction-item'>1️⃣ '모의고사 시작하기' 버튼을 클릭합니다.</div>
    <div class='instruction-item'>2️⃣ 문제가 나타나면 제한 시간 내에 답변을 입력합니다.</div>
    <div class='instruction-item'>3️⃣ '답변 제출' 버튼을 클릭하거나 시간이 초과되면 자동으로 채점됩니다.</div>
    <div class='instruction-item'>4️⃣ 정답과 내 답변을 비교한 후 '다음 문제로' 버튼을 클릭합니다.</div>
    <div class='instruction-item'>5️⃣ 모든 문제를 풀면 결과를 확인할 수 있습니다.</div>
</div>
""", unsafe_allow_html=True)

# 문제 유형 통계
st.markdown("<div class='section-title'>📊 문제 유형 통계</div>", unsafe_allow_html=True)

type_counts = questions['Type'].value_counts()
단답형_count = type_counts.get('단답형', 0)
서술형_count = type_counts.get('서술형', 0)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class='stats-card'>
        <div class='stats-number'>{단답형_count}</div>
        <div class='stats-label'>단답형 문제</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='stats-card'>
        <div class='stats-number'>{서술형_count}</div>
        <div class='stats-label'>서술형 문제</div>
    </div>
    """, unsafe_allow_html=True)

# 연도별 문제 수 (선택 사항)
if 'Year' in questions.columns:
    st.markdown("<div class='section-title'>📅 연도별 문제 통계</div>", unsafe_allow_html=True)
    year_counts = questions['Year'].value_counts().sort_index()
    
    # 연도별 문제 수 표시
    cols = st.columns(len(year_counts))
    for i, (year, count) in enumerate(year_counts.items()):
        with cols[i]:
            st.markdown(f"""
            <div class='stats-card'>
                <div class='stats-number'>{count}</div>
                <div class='stats-label'>{year}년 문제</div>
            </div>
            """, unsafe_allow_html=True)

# 세션 상태 초기화
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'selected_answers' not in st.session_state:
    st.session_state.selected_answers = {}
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'incorrect_questions' not in st.session_state:
    st.session_state.incorrect_questions = []
if 'partial_questions' not in st.session_state:
    st.session_state.partial_questions = []
if 'review_mode' not in st.session_state:
    st.session_state.review_mode = False
if 'badges' not in st.session_state:
    st.session_state.badges = []

def load_questions(category, num_questions=10):
    file_path = f"questions/{category}.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        all_questions = json.load(f)
    
    # 랜덤하게 문제 선택
    selected_questions = random.sample(all_questions, min(num_questions, len(all_questions)))
    return selected_questions

def start_quiz(category, num_questions=10):
    st.session_state.current_page = 'quiz'
    st.session_state.current_question_index = 0
    st.session_state.selected_answers = {}
    st.session_state.score = 0
    st.session_state.review_mode = False
    st.session_state.questions = load_questions(category, num_questions)
    st.session_state.total_questions = len(st.session_state.questions)

def start_review_quiz():
    # 틀리거나 부분 점수를 받은 문제들로 새로운 모의고사 시작
    review_questions = st.session_state.incorrect_questions + st.session_state.partial_questions
    if not review_questions:
        st.warning("복습할 문제가 없습니다.")
        return
    
    st.session_state.current_page = 'quiz'
    st.session_state.current_question_index = 0
    st.session_state.selected_answers = {}
    st.session_state.score = 0
    st.session_state.review_mode = True
    st.session_state.questions = review_questions
    st.session_state.total_questions = len(review_questions)

def check_answers():
    """사용자의 답변을 체크하고 점수를 계산하는 함수"""
    total_score = 0
    max_score = len(st.session_state.questions) * 10
    
    # 틀린 문제와 부분 점수 문제 초기화 (복습 모드가 아닐 때만)
    if not st.session_state.review_mode:
        st.session_state.incorrect_questions = []
        st.session_state.partial_questions = []
    
    for i, question in enumerate(st.session_state.questions):
        user_answer = st.session_state.answers[i]
        
        # 디버깅 모드에서는 자동으로 점수 부여
        if DEBUG_MODE and user_answer == "정답":
            score = 10
            if DEBUG_MODE:
                debug_print(f"문제 {i+1}: 10점 (만점)")
        elif DEBUG_MODE and user_answer == "부분 정답":
            score = 5
            if not st.session_state.review_mode:
                st.session_state.partial_questions.append(question)
            if DEBUG_MODE:
                debug_print(f"문제 {i+1}: 5점 (부분 점수)")
        elif DEBUG_MODE and user_answer == "틀린 답변":
            score = 0
            if not st.session_state.review_mode:
                st.session_state.incorrect_questions.append(question)
            if DEBUG_MODE:
                debug_print(f"문제 {i+1}: 0점 (오답)")
        else:
            # 실제 답변 체크 로직 (기존 코드)
            # 여기에 실제 답변 체크 로직을 넣으세요
            pass
        
        total_score += score
    
    # 점수 저장
    st.session_state.total_score = total_score
    st.session_state.max_score = max_score
    st.session_state.percentage = (total_score / max_score) * 100
    
    # 배지 생성
    create_badge()
    
    if DEBUG_MODE:
        debug_print(f"총점: {total_score}/{max_score} ({st.session_state.percentage:.1f}%)")
        debug_print(f"배지 생성 완료: {st.session_state.badges[-1]['title']}")

def render_result_page():
    st.title("모의고사 결과")
    
    score = st.session_state.score
    total = st.session_state.total_questions
    percentage = (score / total) * 100
    
    st.header(f"점수: {score}/{total} ({percentage:.1f}%)")
    
    # 배지 표시
    latest_badge = st.session_state.badges[-1]
    
    st.subheader("🏆 모의고사 완료 배지")
    badge_col1, badge_col2 = st.columns(2)
    
    with badge_col1:
        st.markdown(f"""
        <div style="border:2px solid gold; border-radius:10px; padding:10px; background-color:#f8f9fa;">
            <h3 style="text-align:center; color:#1e3a8a;">🎓 {latest_badge['category']} 완료</h3>
            <p style="text-align:center;">날짜: {latest_badge['date']}</p>
            <p style="text-align:center;">점수: {latest_badge['score']} ({latest_badge['percentage']})</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 틀린 문제와 부분 점수 문제 개수 표시
    incorrect_count = len(st.session_state.incorrect_questions)
    partial_count = len(st.session_state.partial_questions)
    
    st.subheader("문제 분석")
    st.write(f"✅ 맞은 문제: {total - incorrect_count - partial_count}개")
    st.write(f"⚠️ 부분 점수 문제: {partial_count}개")
    st.write(f"❌ 틀린 문제: {incorrect_count}개")
    
    # 틀린 문제나 부분 점수 문제가 있으면 복습 모의고사 버튼 표시
    if incorrect_count > 0 or partial_count > 0:
        st.markdown("---")
        st.subheader("복습 모의고사")
        st.write("틀리거나 부분 점수를 받은 문제들로 다시 모의고사를 볼 수 있습니다.")
        
        review_count = incorrect_count + partial_count
        if st.button(f"복습 모의고사 시작하기 ({review_count}문제)"):
            start_review_quiz()
            st.experimental_rerun()
    
    # 홈으로 돌아가기 버튼
    st.markdown("---")
    if st.button("홈으로 돌아가기"):
        st.session_state.current_page = 'home'
        st.experimental_rerun()

def render_profile_page():
    st.title("내 프로필")
    
    # 배지 목록 표시
    st.header("획득한 배지")
    
    if not st.session_state.badges:
        st.info("아직 획득한 배지가 없습니다. 모의고사를 완료하면 배지를 획득할 수 있습니다.")
    else:
        # 최근 순으로 정렬
        badges = sorted(st.session_state.badges, key=lambda x: x['date'], reverse=True)
        
        for i, badge in enumerate(badges):
            st.markdown(f"""
            <div style="border:2px solid gold; border-radius:10px; padding:10px; margin-bottom:10px; background-color:#f8f9fa;">
                <h3 style="text-align:center; color:#1e3a8a;">🎓 {badge['category']} 완료</h3>
                <p style="text-align:center;">날짜: {badge['date']}</p>
                <p style="text-align:center;">점수: {badge['score']} ({badge['percentage']})</p>
            </div>
            """, unsafe_allow_html=True)
    
    # 홈으로 돌아가기 버튼
    st.markdown("---")
    if st.button("홈으로 돌아가기"):
        st.session_state.current_page = 'home'
        st.experimental_rerun()

def render_home_page():
    st.title("Anatomy Ace - 해부학 모의고사")
    
    # 카테고리 선택
    st.header("모의고사 선택")
    categories = {
        "musculoskeletal": "근골격계",
        "cardiovascular": "심혈관계",
        "respiratory": "호흡기계",
        "digestive": "소화기계",
        "urinary": "비뇨기계",
        "reproductive": "생식기계",
        "nervous": "신경계",
        "endocrine": "내분비계",
        "lymphatic": "림프계",
        "integumentary": "피부계"
    }
    
    category = st.selectbox("카테고리 선택", list(categories.keys()), format_func=lambda x: categories[x])
    num_questions = st.slider("문제 수", min_value=5, max_value=50, value=10, step=5)
    
    if st.button("모의고사 시작"):
        start_quiz(category, num_questions)
        st.experimental_rerun()
    
    # 프로필 페이지로 이동하는 버튼 추가
    st.markdown("---")
    if st.button("내 프로필 보기"):
        st.session_state.current_page = 'profile'
        st.experimental_rerun()

    # 디버깅 모드일 때만 보이는 테스트 버튼
    if DEBUG_MODE:
        st.write("---")
        st.subheader("🐞 디버깅 모드")
        test_col1, test_col2 = st.columns(2)
        
        with test_col1:
            if st.button("일반 모의고사 자동 테스트"):
                run_test_quiz(is_review=False)
        
        with test_col2:
            if st.button("복습 모의고사 자동 테스트"):
                # 먼저 일반 모의고사를 테스트하고 그 결과로 복습 모의고사 테스트
                run_test_quiz(is_review=True)

def run_test_quiz(is_review=False):
    """자동으로 모의고사를 테스트하는 함수"""
    if not is_review:
        # 일반 모의고사 테스트
        st.session_state.category = "수학"  # 테스트할 카테고리 선택
        st.session_state.num_questions = 10  # 테스트할 문제 수 선택
        st.session_state.page = "quiz"
        st.session_state.current_question = 0
        st.session_state.answers = []
        st.session_state.review_mode = False
        st.session_state.incorrect_questions = []
        st.session_state.partial_questions = []
        
        # 문제 생성
        generate_questions()
        
        debug_print("일반 모의고사 테스트를 시작합니다.")
        debug_print(f"생성된 문제 수: {len(st.session_state.questions)}")
        
        # 자동으로 문제 풀기 (일부러 몇 개는 틀리게 설정)
        for i in range(len(st.session_state.questions)):
            question = st.session_state.questions[i]
            
            # 일부러 몇 개는 틀리게, 몇 개는 부분 점수 받게 설정
            if i % 3 == 0:  # 3으로 나누어 떨어지는 문제는 틀리게
                st.session_state.answers.append("틀린 답변")
                debug_print(f"문제 {i+1}: 일부러 틀린 답변 제출")
            elif i % 3 == 1:  # 3으로 나누어 1이 남는 문제는 부분 점수 받게
                st.session_state.answers.append("부분 정답")
                debug_print(f"문제 {i+1}: 일부러 부분 정답 제출")
            else:  # 나머지는 맞게
                st.session_state.answers.append("정답")
                debug_print(f"문제 {i+1}: 정답 제출")
        
        # 답변 체크
        check_answers()
        
        debug_print("모의고사 테스트 완료!")
        debug_print(f"틀린 문제 수: {len(st.session_state.incorrect_questions)}")
        debug_print(f"부분 점수 문제 수: {len(st.session_state.partial_questions)}")
        
        # 결과 페이지로 이동
        st.session_state.page = "result"
        st.experimental_rerun()
    
    else:
        # 복습 모의고사 테스트 (틀린 문제와 부분 점수 문제가 있어야 함)
        if not hasattr(st.session_state, 'incorrect_questions') or not hasattr(st.session_state, 'partial_questions'):
            debug_print("먼저 일반 모의고사 테스트를 실행해주세요!")
            return
        
        if len(st.session_state.incorrect_questions) + len(st.session_state.partial_questions) == 0:
            debug_print("틀린 문제나 부분 점수 문제가 없습니다!")
            return
        
        # 복습 모의고사 시작
        start_review_quiz()
        
        debug_print("복습 모의고사 테스트를 시작합니다.")
        debug_print(f"복습할 문제 수: {len(st.session_state.questions)}")
        
        # 자동으로 문제 풀기 (이번에는 모두 맞게 설정)
        for i in range(len(st.session_state.questions)):
            st.session_state.answers.append("정답")
            debug_print(f"문제 {i+1}: 정답 제출")
        
        # 답변 체크
        check_answers()
        
        debug_print("복습 모의고사 테스트 완료!")
        
        # 결과 페이지로 이동
        st.session_state.page = "result"
        st.experimental_rerun()

def create_badge():
    """모의고사 완료 배지를 생성하는 함수"""
    if not hasattr(st.session_state, 'badges'):
        st.session_state.badges = []
    
    # 현재 날짜와 시간
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M")
    
    # 배지 타입 결정 (일반 모의고사 또는 복습 모의고사)
    badge_type = "복습 모의고사" if st.session_state.review_mode else "일반 모의고사"
    
    # 점수에 따른 등급 결정
    percentage = st.session_state.percentage
    if percentage >= 90:
        grade = "🏆 최우수"
    elif percentage >= 80:
        grade = "🥇 우수"
    elif percentage >= 70:
        grade = "🥈 장려"
    else:
        grade = "🥉 노력"
    
    # 배지 생성
    badge = {
        "date": date_str,
        "type": badge_type,
        "category": st.session_state.category,
        "score": f"{st.session_state.total_score}/{st.session_state.max_score}",
        "percentage": f"{percentage:.1f}%",
        "grade": grade,
        "title": f"{badge_type} 완료: {grade}"
    }
    
    # 배지 저장
    st.session_state.badges.append(badge)
    st.session_state.latest_badge = badge
    
    if DEBUG_MODE:
        debug_print(f"배지 생성: {badge['title']}")

# 메인 앱 로직
def main():
    if st.session_state.current_page == 'home':
        render_home_page()
    elif st.session_state.current_page == 'quiz':
        render_quiz_page()
    elif st.session_state.current_page == 'result':
        render_result_page()
    elif st.session_state.current_page == 'profile':
        render_profile_page()

if __name__ == "__main__":
    main()
