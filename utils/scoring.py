import pandas as pd
import re

def check_answer(user_answer, question_data):
    """
    사용자 답변을 채점하는 함수
    
    Parameters:
    user_answer (str): 사용자가 입력한 답변
    question_data (Series): 문제 데이터
    
    Returns:
    tuple: (정답 여부, 점수)
    """
    # 빈 답변 처리
    if not user_answer or user_answer.strip() == "":
        return False, 0
    
    # 소문자 변환 및 공백 제거
    user_answer = user_answer.lower().strip()
    
    # 키워드 목록 가져오기
    if "Keywords" in question_data and pd.notna(question_data["Keywords"]):
        keywords = [kw.strip().lower() for kw in question_data["Keywords"].split(";") if kw.strip()]
    else:
        # 키워드가 없는 경우 정답 자체를 키워드로 사용
        answer = str(question_data["Answer"]).lower().strip()
        
        # 번호가 있는 항목으로 나누기 (예: 1) ... 2) ... 3) ...)
        numbered_items = re.split(r'\s*\d+\)\s*|\s*\d+\.\s*', answer)
        numbered_items = [item.strip() for item in numbered_items if item.strip()]
        
        if len(numbered_items) > 1:
            keywords = numbered_items
        else:
            # 세미콜론이나 쉼표로 나누기
            if ";" in answer:
                keywords = [kw.strip() for kw in answer.split(";") if kw.strip()]
            elif "," in answer:
                keywords = [kw.strip() for kw in answer.split(",") if kw.strip()]
            else:
                keywords = [answer]
    
    # 키워드가 없으면 정확한 일치만 인정
    if not keywords:
        correct_answer = str(question_data["Answer"]).lower().strip()
        is_correct = (user_answer == correct_answer)
        return is_correct, question_data["Points"] if is_correct else 0
    
    # 단답형인 경우
    if question_data["Type"] == "단답형":
        correct_answer = str(question_data["Answer"]).lower().strip()
        
        # 정확히 일치하는 경우
        if user_answer == correct_answer:
            return True, question_data["Points"]
        
        # 키워드 매칭 검사
        matched_keywords = []
        for kw in keywords:
            if kw in user_answer:
                matched_keywords.append(kw)
        
        # 모든 키워드가 포함된 경우만 정답으로 인정
        if len(matched_keywords) == len(keywords):
            return True, question_data["Points"]
        
        # 일부 키워드만 포함된 경우 부분 점수
        if matched_keywords:
            ratio = len(matched_keywords) / len(keywords)
            partial_score = round(question_data["Points"] * ratio)
            return False, partial_score
        
        return False, 0
    
    # 서술형인 경우
    elif question_data["Type"] == "서술형":
        # 번호가 있는 항목 확인 (예: 1) ... 2) ... 3) ...)
        numbered_items_in_answer = re.findall(r'\d+\)\s*|\d+\.\s*', user_answer)
        
        # 포함된 키워드 수 계산
        matched_keywords = []
        for kw in keywords:
            if kw in user_answer:
                matched_keywords.append(kw)
        
        # 키워드 비율 계산
        keyword_ratio = len(matched_keywords) / len(keywords) if keywords else 0
        
        # 번호 항목이 있는 경우, 번호 개수도 확인
        if numbered_items_in_answer and len(numbered_items_in_answer) < len(keywords):
            # 번호 항목이 부족한 경우 더 엄격하게 채점
            max_ratio = min(1.0, len(numbered_items_in_answer) / len(keywords))
            keyword_ratio = min(keyword_ratio, max_ratio)
        
        # 모든 키워드가 포함되어야만 만점 (100%)
        if keyword_ratio >= 0.99:  # 반올림 오차 고려
            return True, question_data["Points"]
        
        # 일부 키워드만 포함되면 부분 점수
        elif matched_keywords:
            # 키워드 비율에 따라 점수 계산
            partial_score = round(question_data["Points"] * keyword_ratio)
            return False, partial_score
        
        return False, 0
    
    # 기타 유형
    else:
        # 기본적으로 정확히 일치해야 정답
        correct_answer = str(question_data["Answer"]).lower().strip()
        if user_answer == correct_answer:
            return True, question_data["Points"]
        
        # 키워드 매칭 검사
        matched_keywords = []
        for kw in keywords:
            if kw in user_answer:
                matched_keywords.append(kw)
        
        # 모든 키워드가 포함된 경우만 정답으로 인정
        if len(matched_keywords) == len(keywords):
            return True, question_data["Points"]
        
        # 일부 키워드만 포함된 경우 부분 점수
        if matched_keywords:
            ratio = len(matched_keywords) / len(keywords)
            partial_score = round(question_data["Points"] * ratio)
            return False, partial_score
        
        return False, 0
