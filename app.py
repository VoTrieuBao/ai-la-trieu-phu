import streamlit as st
import pandas as pd
import random
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Ai Là Triệu Phú", layout="wide")

# ==========================================
# CẤU HÌNH ÂM THANH
# ==========================================
SOUNDS = {
    "correct": "https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3",
    "wrong": "https://assets.mixkit.co/active_storage/sfx/2874/2874-preview.mp3",
    "milestone": "https://assets.mixkit.co/active_storage/sfx/1435/1435-preview.mp3",
    "victory": "https://assets.mixkit.co/active_storage/sfx/2019/2019-preview.mp3"
}

BG_MUSIC_URL = "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3?filename=suspense-ambient-110058.mp3"

def play_sound(url):
    if url:
        sound_html = f"""
        <audio autoplay style="display:none;">
            <source src="{url}" type="audio/mp3">
        </audio>
        """
        components.html(sound_html, height=0, width=0)

# ==========================================
# CSS TÙY CHỈNH GIAO DIỆN
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #0b0c2a;
        color: #ffffff;
    }
    .question-box {
        background: linear-gradient(180deg, #102a5c, #071530);
        border: 2px solid #e0a92a;
        border-radius: 12px;
        padding: 22px;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 25px;
        color: #f7d070;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    div.stButton > button {
        width: 100%;
        background: #112244;
        color: #ffffff;
        border: 1.5px solid #2980b9;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
        font-weight: 500;
        text-align: left;
    }
    div.stButton > button:hover {
        background-color: #d35400;
        border-color: #f39c12;
        color: #ffffff;
    }
    .ladder-row {
        padding: 3px 12px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        border-radius: 4px;
        margin-bottom: 2px;
        font-size: 15px;
    }
    .current-level {
        background-color: #d35400 !important;
        color: #ffffff !important;
    }
    .milestone {
        color: #ffffff;
    }
    .normal-level {
        color: #e67e22;
    }
    .help-box {
        background-color: #162447;
        border-left: 4px solid #f39c12;
        padding: 14px;
        margin-top: 15px;
        margin-bottom: 15px;
        border-radius: 6px;
        font-size: 16px;
    }
    .help-section-title {
        font-size: 18px;
        font-weight: bold;
        color: #f39c12;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 15 mốc tiền thưởng
MONEY_LADDER = [
    (15, "250.000.000"), (14, "150.000.000"), (13, "80.000.000"),
    (12, "40.000.000"),  (11, "30.000.000"),  (10, "22.000.000"),
    (9, "14.000.000"),   (8, "10.000.000"),   (7, "6.000.000"),
    (6, "3.000.000"),    (5, "2.000.000"),    (4, "1.000.000"),
    (3, "600.000"),      (2, "400.000"),      (1, "200.000")
]

EXCEL_FILE = "bo_cau_hoi_mau_ai_la_trieu_phu.xlsx"

@st.cache_data
def load_questions_from_excel(filepath):
    if not os.path.exists(filepath):
        return [
            {
                "level": 1,
                "question": "Thủ đô của Việt Nam là gì?",
                "options": ["Hà Nội", "Đà Nẵng", "TP. Hồ Chí Minh", "Cần Thơ"],
                "answer": "Hà Nội"
            }
        ]
    df = pd.read_excel(filepath)
    if "level" in df.columns:
        df = df.sort_values(by="level")
    
    questions = []
    for _, row in df.iterrows():
        questions.append({
            "level": int(row.get("level", 1)),
            "question": str(row["question"]),
            "options": [str(row["opt_a"]), str(row["opt_b"]), str(row["opt_c"]), str(row["opt_d"])],
            "answer": str(row["answer"]).strip()
        })
    return questions

# Khởi tạo Session State
if "questions" not in st.session_state:
    st.session_state.questions = load_questions_from_excel(EXCEL_FILE)

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "game_over" not in st.session_state:
    st.session_state.game_over = False

if "won" not in st.session_state:
    st.session_state.won = False

if "sound_to_play" not in st.session_state:
    st.session_state.sound_to_play = None

if "lifelines" not in st.session_state:
    st.session_state.lifelines = {
        "5050": True,
        "audience": True,
        "call": True,
        "change": True
    }

if "hidden_options" not in st.session_state:
    st.session_state.hidden_options = []

if "lifeline_message" not in st.session_state:
    st.session_state.lifeline_message = None

def reset_game():
    st.session_state.current_index = 0
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.sound_to_play = None
    st.session_state.lifelines = {
        "5050": True,
        "audience": True,
        "call": True,
        "change": True
    }
    st.session_state.hidden_options = []
    st.session_state.lifeline_message = None
    st.rerun()

def get_guaranteed_prize(idx):
    if idx >= 10:
        return "22.000.000 VNĐ"
    elif idx >= 5:
        return "2.000.000 VNĐ"
    return "0 VNĐ"

# --- SIDEBAR: ÂM THANH & CÀI ĐẶT ---
with st.sidebar:
    st.header("🎵 Điều khiển Âm thanh")
    play_bg = st.checkbox("Bật nhạc nền hồi hộp", value=True)
    if play_bg:
        st.markdown(f"""
        <audio autoplay loop style="width: 100%; margin-top: 5px;">
            <source src="{BG_MUSIC_URL}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.write(f"📊 Bộ câu hỏi: **{len(st.session_state.questions)} câu**")
    if st.button("🔄 Chơi lại từ đầu"):
        reset_game()

# Phát âm thanh an toàn
sound_target = st.session_state.get("sound_to_play")
if sound_target:
    play_sound(sound_target)
    st.session_state["sound_to_play"] = None

# --- BỐ CỤC CHÍNH (Cột trái: Câu hỏi + Trợ giúp | Cột phải: Thang tiền thưởng) ---
col_game, col_ladder = st.columns([2.6, 1.2])

curr_q = st.session_state.questions[min(st.session_state.current_index, len(st.session_state.questions) - 1)]

# ==========================================
# CỘT PHẢI: THANG TIỀN THƯỞNG (ĐƯA LÊN TRÊN CÙNG)
# ==========================================
with col_ladder:
    st.subheader("🏆 Mốc tiền thưởng")
    for lvl, prize in MONEY_LADDER:
        is_current = (lvl == st.session_state.current_index + 1) and not st.session_state.game_over
        is_milestone = lvl in [5, 10, 15]
        
        row_class = "ladder-row "
        if is_current:
            row_class += "current-level"
        elif is_milestone:
            row_class += "milestone"
        else:
            row_class += "normal-level"

        st.markdown(
            f'<div class="{row_class}"><span>Câu {lvl:02d}</span><span>{prize}</span></div>',
            unsafe_allow_html=True
        )

# ==========================================
# CỘT TRÁI: KHUNG CHƠI & QUYỀN TRỢ GIÚP PHÍA DƯỚI
# ==========================================
with col_game:
    st.title("AI LÀ TRIỆU PHÚ")

    if st.session_state.game_over:
        if st.session_state.won:
            st.balloons()
            st.success("🎉 XUẤT SẮC! BẠN ĐÃ TRẢ LỜI ĐÚNG TẤT CẢ 15 CÂU HỎI VÀ ĐẠT 250.000.000 VNĐ!")
        else:
            st.error("❌ Rất tiếc, câu trả lời chưa chính xác!")
            st.info(f"💰 Phần thưởng an toàn mang về: **{get_guaranteed_prize(st.session_state.current_index)}**")
        
        if st.button("Chơi lại ván mới"):
            reset_game()

    else:
        q_data = curr_q
        current_question_num = st.session_state.current_index + 1
        
        # 1. Hộp câu hỏi
        st.markdown(f'<div class="question-box">Câu {current_question_num}: {q_data["question"]}</div>', unsafe_allow_html=True)

        # 2. Bốn phương án đáp án
        prefix = ["A", "B", "C", "D"]
        col_a, col_b = st.columns(2)
        columns = [col_a, col_b, col_a, col_b]

        for idx, opt in enumerate(q_data["options"]):
            with columns[idx]:
                if opt in st.session_state.hidden_options:
                    st.button(f"{prefix[idx]}: ---", key=f"empty_{idx}", disabled=True)
                else:
                    if st.button(f"{prefix[idx]}: {opt}", key=f"btn_{idx}_{st.session_state.current_index}"):
                        if opt.strip() == q_data["answer"].strip():
                            st.session_state.hidden_options = []
                            st.session_state.lifeline_message = None
                            
                            if current_question_num >= len(st.session_state.questions) or current_question_num == 15:
                                st.session_state.won = True
                                st.session_state.game_over = True
                                st.session_state.sound_to_play = SOUNDS["victory"]
                            elif current_question_num in [5, 10]:
                                st.session_state.current_index += 1
                                st.session_state.sound_to_play = SOUNDS["milestone"]
                            else:
                                st.session_state.current_index += 1
                                st.session_state.sound_to_play = SOUNDS["correct"]
                            st.rerun()
                        else:
                            st.session_state.game_over = True
                            st.session_state.sound_to_play = SOUNDS["wrong"]
                            st.rerun()

        # 3. Thông báo kết quả trợ giúp (nếu có kích hoạt)
        if st.session_state.lifeline_message:
            st.markdown(f'<div class="help-box">{st.session_state.lifeline_message}</div>', unsafe_allow_html=True)

        # 4. KHU VỰC QUYỀN TRỢ GIÚP (ĐẶT NGAY DƯỚI CÁC ĐÁP ÁN)
        st.markdown('<div class="help-section-title">✨ Quyền trợ giúp của người chơi</div>', unsafe_allow_html=True)
        h_col1, h_col2, h_col3, h_col4 = st.columns(4)

        # Trợ giúp 1: 50:50
        with h_col1:
            if st.button("⚖️ 50:50", disabled=not st.session_state.lifelines["5050"] or st.session_state.game_over):
                st.session_state.lifelines["5050"] = False
                wrongs = [opt for opt in curr_q["options"] if opt.strip() != curr_q["answer"].strip()]
                st.session_state.hidden_options = random.sample(wrongs, min(2, len(wrongs)))
                st.rerun()

        # Trợ giúp 2: Khán giả
        with h_col2:
            if st.button("👥 Khán giả", disabled=not st.session_state.lifelines["audience"] or st.session_state.game_over):
                st.session_state.lifelines["audience"] = False
                correct_pct = random.randint(65, 88)
                remaining = 100 - correct_pct
                p1 = random.randint(0, remaining)
                p2 = random.randint(0, remaining - p1)
                p3 = remaining - p1 - p2
                
                votes = {}
                wrong_idx = 0
                other_percents = [p1, p2, p3]
                for opt in curr_q["options"]:
                    if opt.strip() == curr_q["answer"].strip():
                        votes[opt] = correct_pct
                    else:
                        votes[opt] = other_percents[wrong_idx]
                        wrong_idx += 1
                
                result_str = " | ".join([f"**{opt}**: {pct}%" for opt, pct in votes.items()])
                st.session_state.lifeline_message = f"📊 **Khán giả bình chọn:** {result_str}"
                st.rerun()

        # Trợ giúp 3: Gọi điện thoại
        with h_col3:
            if st.button("📞 Gọi điện", disabled=not st.session_state.lifelines["call"] or st.session_state.game_over):
                st.session_state.lifelines["call"] = False
                is_helpful = random.random() < 0.85
                suggested = curr_q["answer"] if is_helpful else random.choice([o for o in curr_q["options"] if o.strip() != curr_q["answer"].strip()])
                st.session_state.lifeline_message = f"📞 **Người thân tư vấn:** *'Theo mình thì đáp án chắc chắn là **{suggested}**!'*"
                st.rerun()

        # Trợ giúp 4: Đổi câu hỏi
        with h_col4:
            if st.button("🔄 Đổi câu", disabled=not st.session_state.lifelines["change"] or st.session_state.game_over):
                st.session_state.lifelines["change"] = False
                st.session_state.hidden_options = []
                st.session_state.lifeline_message = "🔄 Bạn đã đổi sang câu hỏi khác!"
                if st.session_state.current_index + 1 < len(st.session_state.questions):
                    st.session_state.questions.append(st.session_state.questions.pop(st.session_state.current_index))
                st.rerun()
