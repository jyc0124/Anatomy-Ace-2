import streamlit as st
import pandas as pd
import time
import os
import numpy as np
from utils.scoring import check_answer

# 페이지 설정
st.set_page_config(
    page_title="Anatomy Ace - 모의고사", 
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
    .section-title {
        font-size: 28px !important;
        font-weight: bold;
        color: #1E88E5;
        margin: 30px 0 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "exam_started" not in st.session_state:
    st.session_state.exam_started = True
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.session_state.answers = []
    st.session_state.wrong_questions = []
    
    # 모든 문제 로드
    try:
        # CSV 파일 로드
        questions = pd.read_csv("data/questions.csv")
        
        # NaN 값 처리 및 유효한 문제만 필터링
        questions = questions.dropna(subset=['Question', 'Answer'])  # 문제나 답이 없는 행 제거
        
        # 데이터 타입 변환 - 오류 방지
        questions['Time_lmit'] = questions['Time_lmit'].fillna(240).astype(int)  # NaN 값은 240으로 대체
        questions['Points'] = questions['Points'].fillna(3).astype(int)  # NaN 값은 3으로 대체
        questions['Year'] = questions['Year'].fillna(0).astype(int)  # NaN 값은 0으로 대체
        
        # 세션 상태에 저장
        st.session_state.exam_questions = questions
        st.session_state.total_questions = len(questions)  # 실제 총 문제 수 저장
    except Exception as e:
        st.error(f"문제 데이터를 로드하는 중 오류가 발생했습니다: {e}")
        st.stop()

# 현재 문제 가져오기
current_q = st.session_state.current_question
total_q = len(st.session_state.exam_questions)

# 문제 상태 초기화 (오류 수정)
if "question_state" not in st.session_state:
    st.session_state.question_state = "asking"
    st.session_state.timer_start = time.time()
    st.session_state.user_answer = ""

if current_q < total_q:
    question_data = st.session_state.exam_questions.iloc[current_q]
    
    # 문제 표시
    st.markdown(f"<div class='main-title'>📝 문제 {current_q + 1}/{total_q} <span class='points-badge'>{question_data['Points']}점</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='question-text'>{question_data['Question']}</div>", unsafe_allow_html=True)
    
    # 문제 정보 표시
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='info-text'>📋 유형: {question_data['Type']} (제한시간: {question_data['Time_lmit']}초)</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='info-text'>📅 출제 연도: {question_data['Year']}년</div>", unsafe_allow_html=True)
    
    # 문제 상태에 따라 다른 UI 표시
    if st.session_state.question_state == "asking":
        # 타이머 계산
        if "time_limit" not in st.session_state:
            try:
                st.session_state.time_limit = int(question_data["Time_lmit"])
            except (ValueError, TypeError):
                # NaN 값이나 변환 오류 처리
                st.session_state.time_limit = 60  # 기본값 설정
        
        elapsed = time.time() - st.session_state.timer_start
        remaining = max(0, st.session_state.time_limit - elapsed)
        progress = remaining / st.session_state.time_limit
        
        # 타이머 표시
        st.progress(progress)
        st.markdown(f"<div class='timer-text'>⏱️ 남은 시간: {int(remaining)}초</div>", unsafe_allow_html=True)
        
        # 시간이 다 되었는지 확인
        time_up = remaining <= 0
        
        # 답변 입력 영역
        if "user_answer" not in st.session_state:
            st.session_state.user_answer = ""
        
        user_answer = st.text_area("💬 답변을 입력하세요:", value=st.session_state.user_answer, height=300)
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
            st.session_state.answers.append({
                "question": question_data["Question"],
                "user_answer": user_answer,
                "correct_answer": question_data["Answer"],
                "is_correct": is_correct,
                "score": score,
                "max_score": question_data["Points"]
            })
            
            st.session_state.score += score
            
            # 오답 또는 부분 점수인 경우 오답 리스트에 추가
            if not is_correct or score < question_data["Points"]:
                st.session_state.wrong_questions.append(question_data)
            
            # 결과 표시 상태로 변경
            st.session_state.question_state = "showing_result"
            st.rerun()
        
        # 타이머 자동 업데이트 (1초마다)
        if remaining > 0:
            time.sleep(1)  # 1초 대기
            st.rerun()  # 페이지 리프레시
        
        # 시간 초과 처리
        if time_up:
            st.warning("⏰ 시간이 초과되었습니다!")
            st.rerun()  # 제출 처리를 위해 리프레시
    
    elif st.session_state.question_state == "showing_result":
        # 결과 표시
        last_answer = st.session_state.answers[-1]
        
        if last_answer["is_correct"]:
            st.markdown(f"<div class='result-title'>🎉 정답입니다! {last_answer['score']}점을 획득했습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='result-title'>❌ 오답입니다. {last_answer['score']}점을 획득했습니다.</div>", unsafe_allow_html=True)
        
        # 사용자 답변 표시
        st.markdown(f"<div class='answer-text'>📝 <b>내 답변:</b> {last_answer['user_answer'] or '(답변 없음)'}</div>", unsafe_allow_html=True)
        
        # 정답 표시
        st.markdown(f"<div class='answer-text'>✅ <b>정답:</b> {last_answer['correct_answer']}</div>", unsafe_allow_html=True)
        
        # 다음 문제로 이동 버튼
        if st.button("➡️ 다음 문제로", type="primary"):
            # 다음 문제로 이동
            st.session_state.current_question += 1
            
            # 상태 완전 초기화
            if "question_state" in st.session_state:
                del st.session_state.question_state
            if "timer_start" in st.session_state:
                del st.session_state.timer_start
            if "time_limit" in st.session_state:
                del st.session_state.time_limit
            if "user_answer" in st.session_state:
                del st.session_state.user_answer
            
            # 페이지 리프레시
            st.rerun()

else:
    # 모든 문제 완료
    st.markdown("<div class='main-title'>🎓 모의고사 완료!</div>", unsafe_allow_html=True)
    
    # 총점 계산
    total_possible_score = sum(st.session_state.exam_questions["Points"])
    
    # 결과 표시 - 크게 수정된 부분
    st.markdown(f"""
    <div style="background-color: #f0f8ff; padding: 30px; border-radius: 15px; margin: 30px 0; text-align: center; border: 3px solid #1E88E5;">
        <div style="font-size: 60px; font-weight: bold; color: #1E88E5; margin-bottom: 20px;">
            📊 총점: {st.session_state.score}/{total_possible_score}점
        </div>
        <div style="font-size: 40px; font-weight: bold; color: #FF5722;">
            정답률: {(st.session_state.score / total_possible_score) * 100:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 결과에 따른 메시지
    percentage = (st.session_state.score / total_possible_score) * 100
    if percentage >= 90:
        st.markdown("<div class='result-title'>🏆 훌륭합니다! 해부학 마스터!</div>", unsafe_allow_html=True)
    elif percentage >= 70:
        st.markdown("<div class='result-title'>🥇 잘했습니다! 조금만 더 노력하세요!</div>", unsafe_allow_html=True)
    elif percentage >= 50:
        st.markdown("<div class='result-title'>🥈 좋은 시도입니다. 더 연습해보세요!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='result-title'>💪 더 많은 연습이 필요합니다. 힘내세요!</div>", unsafe_allow_html=True)
    
    # 오답 노트 표시
    if len(st.session_state.wrong_questions) > 0:
        st.markdown("<div class='section-title'>📝 오답 노트</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background-color: #fff8e1; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #FFA000;">
            <div style="font-size: 22px; margin-bottom: 10px;">
                총 <b>{len(st.session_state.wrong_questions)}개</b>의 문제를 더 공부해야 합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 오답 문제 목록 표시
        for i, wrong_q in enumerate(st.session_state.wrong_questions):
            with st.expander(f"문제 {i+1}: {wrong_q['Question'][:50]}...", expanded=False):
                st.markdown(f"<div class='question-text'>{wrong_q['Question']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='answer-text'>✅ <b>정답:</b> {wrong_q['Answer']}</div>", unsafe_allow_html=True)
                
                # 사용자 답변 찾기
                user_answer = "답변 없음"
                for ans in st.session_state.answers:
                    if ans["question"] == wrong_q["Question"]:
                        user_answer = ans["user_answer"] or "답변 없음"
                        break
                
                st.markdown(f"<div class='answer-text'>📝 <b>내 답변:</b> {user_answer}</div>", unsafe_allow_html=True)
        
        # 다시 시작하기 버튼 추가
        if st.button("🔄 다시 시작하기", type="primary", use_container_width=True):
            # 세션 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        # 모든 문제를 맞춘 경우
        st.markdown("""
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #4CAF50;">
            <div style="font-size: 22px; font-weight: bold;">
                🎉 축하합니다! 모든 문제를 완벽하게 맞추셨습니다!
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 다시 시작하기 버튼 추가
        if st.button("🔄 다시 시작하기", type="primary", use_container_width=True):
            # 세션 상태 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
