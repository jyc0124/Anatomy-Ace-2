import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="Anatomy Ace - 결과", layout="wide")

# 결과 확인
if "answers" not in st.session_state:
    st.error("먼저 모의고사를 풀어야 합니다.")
    if st.button("메인 페이지로 돌아가기"):
        st.switch_page("app.py")
    st.stop()

# 결과 표시
st.title("모의고사 결과")

# 점수 요약
total_questions = len(st.session_state.answers)
total_score = st.session_state.score
max_score = sum(answer["max_score"] for answer in st.session_state.answers)
percentage = (total_score / max_score) * 100

st.header("점수 요약")
col1, col2, col3 = st.columns(3)
col1.metric("총 문제 수", f"{total_questions}문제")
col2.metric("획득 점수", f"{total_score}/{max_score}점")
col3.metric("정답률", f"{percentage:.1f}%")

# 문제별 결과
st.header("문제별 결과")
for i, answer in enumerate(st.session_state.answers):
    with st.expander(f"문제 {i+1}: {answer['is_correct'] and '✅ 정답' or '❌ 오답'} ({answer['score']}/{answer['max_score']}점)"):
        st.write(f"**문제:** {answer['question']}")
        st.write(f"**내 답변:** {answer['user_answer']}")
        st.write(f"**정답:** {answer['correct_answer']}")

# 오답 노트
st.header("오답 노트")
wrong_answers = [a for a in st.session_state.answers if not a['is_correct']]
if wrong_answers:
    st.write(f"총 {len(wrong_answers)}개의 오답이 있습니다.")
    for i, answer in enumerate(wrong_answers):
        with st.expander(f"오답 {i+1}: {answer['question']}"):
            st.write(f"**내 답변:** {answer['user_answer']}")
            st.write(f"**정답:** {answer['correct_answer']}")
else:
    st.write("모든 문제를 맞혔습니다! 축하합니다! 🎉")

# 다음 단계
st.header("다음 단계")
if st.button("메인 페이지로 돌아가기", type="primary"):
    # 현재 세션의 문제 관련 상태 초기화
    for key in ["current_question", "score", "answers", "wrong_questions", "exam_questions"]:
        if key in st.session_state:
            del st.session_state[key]
    st.switch_page("app.py")
