import streamlit as st
import random
import time

st.title("♟️ 矩陣博弈實驗 (Tic-Tac-Toe)")

# --- 1. 初始化狀態 (State Initialization) ---
# board: 一個長度為 9 的列表，代表 3x3 矩陣。索引 0-8 對應棋盤位置。
# None = 空, 'X' = 玩家, 'O' = 電腦
if 'board' not in st.session_state:
    st.session_state.board = [None] * 9
    st.session_state.game_over = False
    st.session_state.winner = None

# --- 2. 核心邏輯函數 (Core Logic Functions) ---

def check_winner(board):
    """檢查矩陣中是否存在勝利連線"""
    # 定義所有勝利組合的索引 (3列, 3行, 2對角)
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), # 列
        (0, 3, 6), (1, 4, 7), (2, 5, 8), # 行
        (0, 4, 8), (2, 4, 6)             # 對角
    ]
    
    for a, b, c in winning_combinations:
        if board[a] == board[b] == board[c] and board[a] is not None:
            return board[a] # 回傳贏家 ('X' 或 'O')
            
    if None not in board:
        return "Draw" # 平手
    
    return None

def computer_move():
    """模擬電腦決策：隨機選擇一個空位"""
    available_indices = [i for i, x in enumerate(st.session_state.board) if x is None]
    if available_indices:
        # 這裡可以替換成更複雜的 Minimax 演算法，目前使用隨機選取
        choice = random.choice(available_indices)
        st.session_state.board[choice] = 'O'

def reset_game():
    st.session_state.board = [None] * 9
    st.session_state.game_over = False
    st.session_state.winner = None

# --- 3. 介面渲染與互動 (UI Rendering & Interaction) ---

# 顯示遊戲狀態
if st.session_state.winner:
    if st.session_state.winner == 'X':
        st.success("實驗結果：人類獲勝 (Human Victory)")
    elif st.session_state.winner == 'O':
        st.error("實驗結果：電腦獲勝 (AI Victory)")
    else:
        st.warning("實驗結果：平局 (Draw)")
    st.button("重置矩陣", on_click=reset_game)

else:
    st.write("人類 (X)  vs.  電腦 (O)")

    # 使用 columns 建立 3x3 網格佈局
    # 這是 CSS Grid 的 Python 抽象化
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            index = row * 3 + col
            
            # 如果該位置是空的且遊戲未結束，顯示按鈕
            if st.session_state.board[index] is None and not st.session_state.game_over:
                if cols[col].button(" ", key=index): # key 必須唯一
                    # 玩家行動
                    st.session_state.board[index] = 'X'
                    
                    # 檢查玩家是否獲勝
                    result = check_winner(st.session_state.board)
                    if result:
                        st.session_state.winner = result
                        st.session_state.game_over = True
                    else:
                        # 電腦行動
                        with st.spinner("電腦運算中..."):
                            time.sleep(0.5) # 模擬運算延遲，增加真實感
                            computer_move()
                            # 檢查電腦是否獲勝
                            result = check_winner(st.session_state.board)
                            if result:
                                st.session_state.winner = result
                                st.session_state.game_over = True
                    
                    # 強制重新執行以更新畫面
                    st.rerun()
            
            # 如果該位置已有棋子，顯示棋子 (按鈕設為 disabled)
            else:
                label = st.session_state.board[index] if st.session_state.board[index] else " "
                cols[col].button(label, key=index, disabled=True)
