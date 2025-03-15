import streamlit as st
import time

def countdown(seconds):
    """
    카운트다운 타이머 함수
    
    Parameters:
    seconds (int): 초 단위 시간
    
    Returns:
    int: 남은 시간(초)
    """
    # 타이머 시작 시간이 없으면 초기화
    if "timer_start" not in st.session_state:
        st.session_state.timer_start = time.time()
        st.session_state.time_limit = seconds
    
    # 경과 시간 계산
    elapsed = time.time() - st.session_state.timer_start
    remaining = max(0, st.session_state.time_limit - elapsed)
    
    # 시간이 다 되면 타이머 초기화
    if remaining <= 0:
        del st.session_state.timer_start
        del st.session_state.time_limit
        return 0
    
    return int(remaining)
