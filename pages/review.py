import streamlit as st
import pandas as pd
import time
from utils.scoring import check_answer

# 페이지 설정
st.set_page_config(
    page_title="Anatomy Ace - 오답 복습", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    .main-title {
        font-size: 42px !important;
        font-weight: bold;
        color: #FF5722;
        margin-bottom: 20px;
    }
    .question-text {
        font-size: 28px !important;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .info-text {
        font-size: 20px !important;
        margin-bottom: 10px;
    }
    .timer-text {
        font-size: 24px !important;
        font-weight: bold;
        color: #FF5722;
    }
    .result-title {
        font-size: 26px !important;
        font-weight: bold;
        margin-top: 20px;
    }
    .answer-text {
        font-size: 22px !important;
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 10px 0;
    }
    .stTextArea textarea {
        font-size: 22px !important;
        line-height: 1.5;
        min-height: 300px !important;
    }
    .stButton button {
        font-size: 20px !important;
        font-weight: bold;
        padding: 10px 25px;
    }
    .points-badge {
        display: inline-block;
        background-color: #FF5722;
        color: white;
        font-size: 18px !important;
        font-weight: bold;
        padding: 5px 12px;
        border-radius: 15px;
        margin-left: 10px;
    }
    .review-progress {
        font-size: 18px !important;
        color: #555;
        margin-bottom: 20px;
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 리뷰 모드 확인
if "review_mode" not in st.session_state or "review_questions" not in st.session_state:
    st.error("오답 복습 모드가 설정되지 않았습니다. 메인 페이지로 돌아가세요.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("app.py")
    st.stop()

# 리뷰 상태 초기화
if "review_state" not in st.session_state:
    st.session_state.review_state = "asking"
    st.session_state.timer_start = time.time()
    st.session_state.user_answer = ""

# 현재 리뷰 문제 가져오기
current_q = st.session_state.current_review_question
total_q = len(st.session_state.review_questions)

# 진행 상황 표시
st.markdown(f"""
<div class="review-progress">
    📚 오답 복습 모드 - 진행 상황: {current_q + 1}/{total_q} 문제
</div>
""", unsafe_allow_html=True)

if current_q < total_q:
    # 데이터프레임으로 변환 (필요한 경우)
    if not isinstance(st.session_state.review_questions, pd.DataFrame):
        review_questions_df = pd.DataFrame(st.session_state.review_questions)
    else:
        review_questions_df = st.session_state.review_questions
    
    question_data = review_questions_df.iloc[current_q]
    
    # 문제 표시
    st.markdown(f"<div class='main-title'>🔄 오답 복습 문제 {current_q + 1}/{total_q} <span class='points-badge'>{question_data['Points']}점</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-text'>{question_data['Question']}</div>", unsafe_allow_html=True)
    
    # 문제 정보 표시
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='info-text'>📋 유형: {question_data['Type']} (제한시간: {question_data['Time_lmit']}초)</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='info-text'>📅 출제 연도: {question_data['Year']}년</div>", unsafe_allow_html=True)
    
    # 이전 정답 표시 (복습 모드에서는 정답을 먼저 보여줌)
    st.markdown(f"<div class='answer-text'>✅ <b>정답:</b> {question_data['Answer']}</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-text'>💡 정답을 참고하여 다시 풀어보세요. 이해하고 외우는 것이 중요합니다!</div>", unsafe_allow_html=True)
    
    # 문제 상태에 따라 다른 UI 표시
    if st.session_state.review_state == "asking":
        # 타이머 계산
        if "time_limit" not in st.session_state:
            # 복습 모드에서는 시간 제한을 2배로 늘림
            st.session_state.time_limit = int(question_data["Time_lmit"]) * 2
        
        elapsed = time.time() - st.session_state.timer_start
        remaining = max(0, st.session_state.time_limit - elapsed)
        progress = remaining / st.session_state.time_limit
        
        # 타이머 표시
        st.progress(progress)
        st.markdown(f"<div class='timer-text'>⏱️ 남은 시간: {int(remaining)}초 (복습 모드에서는 시간이 2배로 주어집니다)</div>", unsafe_allow_html=True)
        
        # 시간이 다 되었는지 확인
        time_up = remaining <= 0
        
        # 답변 입력 영역
        user_answer = st.text_area("💬 답변을 다시 입력해보세요:", value=st.session_state.user_answer, height=300)
        st.session_state.user_answer = user_answer
        
        # 제출 버튼
        submit = st.button("📤 답변 제출", type="primary") or time_up
        
        # 제출 처리
        if submit:
            if time_up and not user_answer.strip():
                # 시간 초과 + 답변 없음
                is_correct = False
                score = 0
            else:
                # 채점
                is_correct, score = check_answer(user_answer, question_data)
            
            # 결과 저장
            st.session_state.review_answers.append({
                "question": question_data["Question"],
                "user_answer": user_answer,
                "correct_answer": question_data["Answer"],
                "is_correct": is_correct,
                "score": score,
                "max_score": question_data["Points"]
            })
            
            st.session_state.review_score += score
            
            # 결과 표시 상태로 변경
            st.session_state.review_state = "showing_result"
            st.rerun()
        
        # 타이머 자동 업데이트 (1초마다)
        if remaining > 0:
            time.sleep(1)  # 1초 대기
            st.rerun()  # 페이지 리프레시
        
        # 시간 초과 처리
        if time_up:
            st.warning("⏰ 시간이 초과되었습니다!")
            st.rerun()  # 제출 처리를 위해 리프레시
    
    elif st.session_state.review_state == "showing_result":
        # 결과 표시
        last_answer = st.session_state.review_answers[-1]
        
        if last_answer["is_correct"]:
            st.markdown(f"<div class='result-title'>🎉 정답입니다! {last_answer['score']}점을 획득했습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='result-title'>❌ 오답입니다. {last_answer['score']}점을 획득했습니다.</div>", unsafe_allow_html=True)
        
        # 사용자 답변 표시
        st.markdown(f"<div class='answer-text'>📝 <b>내 답변:</b> {last_answer['user_answer'] or '(답변 없음)'}</div>", unsafe_allow_html=True)
        
        # 학습 팁 제공
        st.markdown("""
        <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin: 15px 0; border-left: 5px solid #4CAF50;">
            <div style="font-size: 20px; font-weight: bold; margin-bottom: 10px;">💡 학습 팁</div>
            <div style="font-size: 18px;">
                - 정답과 내 답변의 차이점을 분석해보세요.<br>
                - 핵심 키워드를 노트에 정리해두면 기억에 도움이 됩니다.<br>
                - 관련 개념을 함께 학습하면 이해도가 높아집니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 다음 문제로 이동 버튼
        if st.button("➡️ 다음 문제로", type="primary"):
            # 다음 문제로 이동
            st.session_state.current_review_question += 1
            
            # 상태 완전 초기화
            if "review_state" in st.session_state:
                del st.session_state.review_state
            if "timer_start" in st.session_state:
                del st.session_state.timer_start
            if "time_limit" in st.session_state:
                del st.session_state.time_limit
            if "user_answer" in st.session_state:
                del st.session_state.user_answer
            
            # 페이지 리프레시
            st.rerun()

else:
    # 모든 복습 문제 완료
    st.markdown("<div class='main-title'>🎓 오답 복습 완료!</div>", unsafe_allow_html=True)
    
    # 총점 계산
    total_possible_score = sum(question["Points"] for question in st.session_state.review_questions)
    
    # 결과 표시 - 크게 표시
    st.markdown(f"""
    <div style="background-color: #f0f8ff; padding: 30px; border-radius: 15px; margin: 30px 0; text-align: center; border: 3px solid #FF5722;">
        <div style="font-size: 60px; font-weight: bold; color: #FF5722; margin-bottom: 20px;">
            📊 복습 점수: {st.session_state.review_score}/{total_possible_score}점
        </div>
        <div style="font-size: 40px; font-weight: bold; color: #1E88E5;">
            정답률: {(st.session_state.review_score / total_possible_score) * 100:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 이전 점수와 비교
    if "score" in st.session_state:
        original_percentage = (st.session_state.score / total_possible_score) * 100
        review_percentage = (st.session_state.review_score / total_possible_score) * 100
        improvement = review_percentage - original_percentage
        
        if improvement > 0:
            st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #4CAF50;">
                    🚀 {improvement:.1f}% 향상되었습니다!
                </div>
                <div style="font-size: 18px; margin-top: 10px;">
                    처음 시도: {original_percentage:.1f}% → 복습 후: {review_percentage:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background-color: #fff8e1; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #FFA000;">
                    더 연습이 필요합니다!
                </div>
                <div style="font-size: 18px; margin-top: 10px;">
                    처음 시도: {original_percentage:.1f}% → 복습 후: {review_percentage:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 학습 조언
    st.markdown("""
    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <div style="font-size: 22px; font-weight: bold; margin-bottom: 15px;">📚 효과적인 학습 방법</div>
        <ul style="font-size: 18px; margin-left: 20px;">
            <li>오답 문제는 반복해서 여러 번 풀어보세요.</li>
            <li>관련 개념을 함께 학습하면 이해도가 높아집니다.</li>
            <li>핵심 키워드를 노트에 정리하고 주기적으로 복습하세요.</li>
            <li>비슷한 문제들을 그룹화하여 함께 학습하면 효과적입니다.</li>
            <li>시험 전날보다는 꾸준히 조금씩 학습하는 것이 더 효과적입니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 버튼 영역
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 오답 문제 다시 복습하기", type="primary", use_container_width=True):
            # 복습 상태 초기화
            st.session_state.current_review_question = 0
            st.session_state.review_score = 0
            st.session_state.review_answers = []
            
            if "review_state" in st.session_state:
                del st.session_state.review_state
            if "timer_start" in st.session_state:
                del st.session_state.timer_start
            if "time_limit" in st.session_state:
                del st.session_state.time_limit
            if "user_answer" in st.session_state:
                del st.session_state.user_answer
            
            st.rerun()
    
    with col2:
        if st.button("🏠 메인 페이지로 돌아가기", use_container_width=True):
            st.switch_page("app.py")
