import pandas as pd
import re

# CSV 파일 읽기
df = pd.read_csv('data/Integrated data.csv')

# 키워드 추출 함수
def extract_keywords(row):
    # 답변 텍스트 가져오기
    answer = str(row['Answer']).lower()
    
    # 키워드 저장할 리스트
    keywords = []
    
    # 단답형인 경우
    if row['Type'] == '단답형':
        # 기본 키워드는 정답 자체
        main_answer = answer.strip()
        keywords.append(main_answer)
        
        # 쉼표로 구분된 항목들 추가
        parts = [p.strip() for p in answer.split(',')]
        keywords.extend(parts)
        
        # 괄호 안의 내용 추가
        brackets = re.findall(r'\((.*?)\)', answer)
        keywords.extend([b.strip() for b in brackets])
        
    # 서술형인 경우
    else:
        # 중요 단어 추출
        # 괄호 안의 내용 추출
        brackets = re.findall(r'\((.*?)\)', answer)
        keywords.extend([b.strip() for b in brackets])
        
        # 영어 단어나 구문 추출
        english_terms = re.findall(r'[a-zA-Z][a-zA-Z\s]{2,}', answer)
        keywords.extend([term.strip() for term in english_terms])
        
        # 숫자가 포함된 표현 추출
        numbers = re.findall(r'\d+[\s\w]+', answer)
        keywords.extend([n.strip() for n in numbers])
        
        # 중요 한글 용어 추출 (세미콜론이나 쉼표로 구분된 항목)
        for part in re.split(r'[,;()]', answer):
            part = part.strip()
            if len(part) > 3 and not part.isdigit():  # 길이가 3자 이상인 의미있는 단어만
                keywords.append(part)
    
    # 중복 제거 및 빈 문자열 제거
    unique_keywords = []
    for k in keywords:
        k = k.strip()
        if k and k not in unique_keywords and len(k) > 1:
            unique_keywords.append(k)
    
    # 키워드가 너무 많으면 중요한 것만 선택
    if len(unique_keywords) > 10:
        unique_keywords = unique_keywords[:10]
    
    # 세미콜론으로 구분된 문자열로 변환
    return ';'.join(unique_keywords)

# 키워드 추출 적용
df['Keywords'] = df.apply(extract_keywords, axis=1)

# 결과 저장
df.to_csv('data/questions.csv', index=False)
print("키워드 추출 완료! 'data/questions.csv' 파일이 생성되었습니다.")
