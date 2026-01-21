import streamlit as st
import random
import time

# --- 1. 定義實體類別 (Class Definition) ---
# 科學說明：這就像生物學分類，定義了生物的基本屬性

class Entity:
    def __init__(self, name, hp, max_hp, attack):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0: self.hp = 0

# --- 2. 系統初始化 (System Initialization) ---

st.title("🏰 文字地牢實驗 (Text RPG)")

# 初始化遊戲狀態
if 'player' not in st.session_state:
    st.session_state.player = Entity("冒險者", 100, 100, 15)
    st.session_state.gold = 0
    st.session_state.log = ["實驗開始。你站在黑暗的地牢入口。"]
    st.session_state.enemy = None # 當前遭遇的敵人
    st.session_state.in_combat = False # 狀態標記：是否在戰鬥中

# 輔助函數：新增日誌
def add_log(message):
    st.session_state.log.append(message)
    # 只保留最近 5 條記錄，避免畫面雜亂
    if len(st.session_state.log) > 5:
        st.session_state.log.pop(0)

# --- 3. 核心邏輯 (Core Logic) ---

def explore():
    """探索邏輯：隨機事件生成"""
    event = random.randint(1, 10)
    
    if event <= 3: # 30% 機率發現寶藏
        found_gold = random.randint(10, 50)
        st.session_state.gold += found_gold
        add_log(f"💰 發現寶箱！獲得 {found_gold} 金幣。")
        
    elif event <= 5: # 20% 機率什麼都沒發生
        add_log("👣 四周一片寂靜，你繼續前行...")
        
    else: # 50% 機率遇到怪物
        # 生成隨機怪物
        enemy_type = random.choice([
            {"name": "史萊姆", "hp": 30, "atk": 5},
            {"name": "哥布林", "hp": 50, "atk": 10},
            {"name": "黑騎士", "hp": 80, "atk": 20}
        ])
        st.session_state.enemy = Entity(enemy_type["name"], enemy_type["hp"], enemy_type["hp"], enemy_type["atk"])
        st.session_state.in_combat = True
        add_log(f"⚠️ 遭遇敵對生物：{st.session_state.enemy.name}！戰鬥開始！")

def attack_phase():
    """戰鬥邏輯：回合制運算"""
    player = st.session_state.player
    enemy = st.session_state.enemy
    
    # 1. 玩家攻擊
    dmg_dealt = random.randint(player.attack - 5, player.attack + 5)
    enemy.take_damage(dmg_dealt)
    add_log(f"⚔️ 你攻擊了 {enemy.name}，造成 {dmg_dealt} 點傷害。")
    
    # 2. 判定敵人是否死亡
    if not enemy.is_alive():
        loot = random.randint(20, 100)
        st.session_state.gold += loot
        add_log(f"🏆 {enemy.name} 被消滅！獲得 {loot} 金幣。")
        st.session_state.enemy = None
        st.session_state.in_combat = False
        return # 戰鬥結束，跳出函數

    # 3. 敵人反擊
    dmg_taken = random.randint(enemy.attack - 2, enemy.attack + 2)
    player.take_damage(dmg_taken)
    add_log(f"🛡️ {enemy.name} 反擊！你受到 {dmg_taken} 點傷害。")

    # 4. 判定玩家是否死亡
    if not player.is_alive():
        add_log("💀 生命跡象消失。實驗失敗。")

def heal():
    """治療邏輯：金幣換取生命"""
    if st.session_state.gold >= 50:
        st.session_state.gold -= 50
        heal_amount = 30
        st.session_state.player.hp = min(st.session_state.player.hp + heal_amount, st.session_state.player.max_hp)
        add_log("💖 支付 50 金幣進行治療。生命值恢復。")
    else:
        add_log("❌ 金幣不足 (需要 50G)。")

def reset_game():
    st.session_state.player = Entity("冒險者", 100, 100, 15)
    st.session_state.gold = 0
    st.session_state.log = ["實驗重啟。"]
    st.session_state.enemy = None
    st.session_state.in_combat = False

# --- 4. 介面渲染 (UI Rendering) ---

# 頂部儀表板
col1, col2, col3 = st.columns(3)
col1.metric("冒險者生命", f"{st.session_state.player.hp}/{st.session_state.player.max_hp}")
col2.metric("金幣", st.session_state.gold)
if st.session_state.enemy:
    col3.metric(f"敵人: {st.session_state.enemy.name}", f"{st.session_state.enemy.hp}/{st.session_state.enemy.max_hp}")
else:
    col3.metric("狀態", "安全")

# 生命條視覺化
st.progress(st.session_state.player.hp / st.session_state.player.max_hp)

# 分隔線
st.markdown("---")

# 遊戲日誌顯示區
st.subheader("📜 事件日誌")
for line in st.session_state.log:
    st.text(line)

st.markdown("---")

# 操作區：根據狀態顯示不同按鈕
if st.session_state.player.is_alive():
    if st.session_state.in_combat:
        # 戰鬥模式介面
        c1, c2 = st.columns(2)
        if c1.button("⚔️ 攻擊", use_container_width=True):
            attack_phase()
            st.rerun()
        if c2.button("🏃 逃跑 (30%機率)", use_container_width=True):
            if random.random() < 0.3:
                st.session_state.in_combat = False
                st.session_state.enemy = None
                add_log("💨 成功逃脫！")
            else:
                add_log("🚫 逃跑失敗！被敵人追上攻擊！")
                dmg = random.randint(5, 10)
                st.session_state.player.take_damage(dmg)
            st.rerun()
    else:
        # 探索模式介面
        c1, c2 = st.columns(2)
        if c1.button("🔍 繼續探索", use_container_width=True):
            explore()
            st.rerun()
        if c2.button("💖 休息治療 (50G)", use_container_width=True):
            heal()
            st.rerun()
else:
    # 死亡介面
    st.error("實驗對象已死亡。")
    if st.button("🧬 重新生成實驗對象"):
        reset_game()
        st.rerun()
