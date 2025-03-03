import streamlit as st
import json
import random
from pathlib import Path
import time

# Page config
st.set_page_config(
    page_title="GRE 단어 학습",
    page_icon="📚",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .card {
        padding: 2rem;
        border-radius: 1rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        text-align: center;
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #e2e8f0;  /* 테두리 추가 */
        background-color: #ffffff;   /* 배경색 명시적 지정 */
    }
    
    .card h2 {
        margin: 0;
        font-size: 2rem;
        padding: 2rem;              /* 내부 여백 추가 */
        width: 100%;               /* 너비 100%로 설정 */
        height: 100%;              /* 높이 100%로 설정 */
        display: flex;             /* flexbox 사용 */
        align-items: center;       /* 수직 중앙 정렬 */
        justify-content: center;   /* 수평 중앙 정렬 */
    }
    
    /* dark mode 대응 */
    @media (prefers-color-scheme: dark) {
        .card {
            background-color: #1e293b;  /* 다크모드 배경색 */
            border-color: #334155;      /* 다크모드 테두리 색상 */
        }
    }
    .word-meaning {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .progress-text {
        text-align: center;
        color: #666;
    }
    .correct {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .incorrect {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .quiz-options {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .quiz-option {
        background-color: white;
        padding: 3rem;  /* 1rem에서 3rem으로 증가 */
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .quiz-option:hover {
        background-color: #f8fafc;
        transform: translateY(-2px);
    }

    .quiz-question {
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0;
        color: #1a202c;
    }

    .stButton button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 2.25rem 1.5rem !important;  /* 버튼 높이 증가 */
        font-weight: 500;
        font-size: 1.1rem;  /* 글자 크기도 약간 증가 */
        min-height: 6rem !important;  /* 최소 높이 설정 */
    }

    /* 퀴즈 선택지 버튼 스타일 */
    .quiz-options .stButton button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 2.25rem 1.5rem !important;
        font-weight: 500;
        font-size: 1.1rem;
        min-height: 6rem !important;
    }

    /* 모드 선택 버튼 스타일 */
    .mode-buttons .stButton button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem !important;
        font-weight: 500;
        font-size: 1rem;
        min-height: 2.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'is_card_flipped' not in st.session_state:
    st.session_state.is_card_flipped = False
if 'mode' not in st.session_state:
    st.session_state.mode = 'quiz'
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'random_mode' not in st.session_state:
    st.session_state.random_mode = True  # 기본값을 True로 변경
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = True
if 'random_indices' not in st.session_state:
    st.session_state.random_indices = []

def load_vocabulary():
    try:
        vocab_file = Path(__file__).parent / 'vocabulary.json'
        with open(vocab_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"단어장을 불러올 수 없습니다: {str(e)}")
        return []

def generate_quiz(vocabulary, current_word):
    options = [current_word['meaning']]
    while len(options) < 4:
        random_word = random.choice(vocabulary)['meaning']
        if random_word not in options:
            options.append(random_word)
    random.shuffle(options)
    return {
        'question': current_word['word'],
        'options': options,
        'correct_answer': current_word['meaning']
    }

def main():
    st.title("GRE 단어 학습")
    
    vocabulary = load_vocabulary()
    if not vocabulary:
        st.error("단어장을 불러올 수 없습니다.")
        return
    
    # Mode selection 부분 수정
    st.markdown("<div class='mode-buttons'>", unsafe_allow_html=True)
    cols = st.columns(2)
    with cols[0]:
        if st.button("퀴즈", type="primary" if st.session_state.mode == 'quiz' else "secondary"):
            st.session_state.mode = 'quiz'
    with cols[1]:
        if st.button("단어 학습", type="primary" if st.session_state.mode == 'vocabulary' else "secondary"):
            st.session_state.mode = 'vocabulary'
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Progress bar
    total_words = len(vocabulary)
    st.progress((st.session_state.current_index + 1) / total_words)
    st.markdown(f"<div class='progress-text'>{st.session_state.current_index + 1} / {total_words}</div>", unsafe_allow_html=True)
    
    current_word = vocabulary[st.session_state.current_index]
    
    # Vocabulary mode 부분 수정
    if st.session_state.mode == 'vocabulary':
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.markdown("""
                <div class='card'>
                    <div class='card-content'>
            """, unsafe_allow_html=True)
            
            if st.session_state.is_card_flipped:
                st.markdown(f"<h2>{current_word['meaning']}</h2>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h2>{current_word['word']}</h2>", unsafe_allow_html=True)
                
            st.markdown("""
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("카드 뒤집기"):
                st.session_state.is_card_flipped = not st.session_state.is_card_flipped
                
        col1, col2 = st.columns(2)
        with col1:
            if st.button("이전", use_container_width=True):
                st.session_state.current_index = (st.session_state.current_index - 1) % total_words
                st.session_state.is_card_flipped = False
        with col2:
            if st.button("다음", use_container_width=True):
                st.session_state.current_index = (st.session_state.current_index + 1) % total_words
                st.session_state.is_card_flipped = False
    
    else:  # Quiz mode
        # Add random mode checkbox
        st.session_state.random_mode = st.checkbox("랜덤 학습 모드", value=st.session_state.random_mode)
        st.session_state.auto_mode = st.checkbox("자동 진행 모드", value=st.session_state.auto_mode)
        
        # Initialize or update random indices if needed
        if st.session_state.random_mode and not st.session_state.random_indices:
            st.session_state.random_indices = list(range(len(vocabulary)))
            random.shuffle(st.session_state.random_indices)
            st.session_state.current_index = 0
        
        # Get current word based on mode
        if st.session_state.random_mode:
            current_word = vocabulary[st.session_state.random_indices[st.session_state.current_index]]
        else:
            current_word = vocabulary[st.session_state.current_index]
        
        quiz = generate_quiz(vocabulary, current_word)
        st.markdown(f"<div class='quiz-question'>\"{quiz['question']}\"의 의미는?</div>", unsafe_allow_html=True)
        
        # Create 2x2 grid for options
        col1, col2 = st.columns(2)
        for i, option in enumerate(quiz['options']):
            with col1 if i % 2 == 0 else col2:
                # 답을 선택하지 않았을 때만 버튼 활성화
                if not st.session_state.answered:
                    if st.button(option, key=option, use_container_width=True):
                        st.session_state.answered = True
                        if option == quiz['correct_answer']:
                            st.success("정답입니다! 👏")
                            st.session_state.score += 1
                        else:
                            st.error(f"오답입니다. 정답은 \"{quiz['correct_answer']}\" 입니다.")
                        st.session_state.total_questions += 1
                        
                        # 1초 후 다음 문제로 자동 이동
                        time.sleep(1)
                        # Modify next question logic
                        if st.session_state.random_mode:
                            next_index = (st.session_state.current_index + 1) % len(st.session_state.random_indices)
                            if next_index == 0:  # If we've gone through all words, reshuffle
                                random.shuffle(st.session_state.random_indices)
                            st.session_state.current_index = next_index
                        else:
                            st.session_state.current_index = (st.session_state.current_index + 1) % total_words
                        st.session_state.answered = False
                        st.rerun()
                else:
                    # 답을 선택한 후에는 버튼 비활성화
                    st.button(option, key=option, use_container_width=True, disabled=True)
        
        # Score display
        st.write(f"현재 점수: {st.session_state.score}/{st.session_state.total_questions}")
        
        # 수동으로 다음 문제로 이동하는 버튼
        if st.button("다음 문제", use_container_width=True):
            st.session_state.current_index = (st.session_state.current_index + 1) % total_words
            st.session_state.answered = False
            st.rerun()

if __name__ == "__main__":
    main()
