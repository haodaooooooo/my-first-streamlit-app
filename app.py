import streamlit as st
import random
import time

# --- 1. 介面風格化 (UI Styling / CSS Injection) ---
# 科學說明：透過 CSS 選擇器強制改變 DOM 元素的渲染屬性
# 配色邏輯：
# 背景：#f9f7f0 (米白/宣紙)
# 文字：#5c4033 (深褐/墨跡)
# 按鈕：#8b0000 (朱紅/印泥) -> 邊框與文字
def inject_custom_css():
    st.markdown("""
        <style>
        /* 全局字體設定：優先使用楷體 */
        html, body, [class*="css"]  {
            font-family: "KaiTi", "楷体", "STKaiti", "SimSun", serif;
            color: #5c4033;
            background-color: #f9f7f0;
        }
        
        /* 縮小全局字體 */
        p, .stMarkdown, .stText, .stMetricLabel, .stMetricValue {
            font-size: 14px !important;
        }
        
        /* 標題樣式：書法感 */
        h1, h2, h3 {
            color: #2c1608 !important;
            font-weight: bold;
            letter-spacing: 2px;
        }
        
        /* 按鈕樣式：朱紅邊框，中國風 */
        .stButton > button {
            background-color: transparent;
            color: #8b0000;
            border: 2px solid #8b0000;
            border-radius: 4px;
            font-size: 14px;
            font-family: "KaiTi", serif;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            background-color: #8b0000;
            color: #f9f7f0;
            border-color: #5c0000;
        }
        
        /* 進度條顏色：玉色 */
        .stProgress > div > div > div > div {
            background-color: #556b2f;
        }
        
        /* 分隔線 */
        hr {
            border-color: #8b0000;
            opacity: 0.3;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 定義實體類別 ---
class QiRefiner:
    def __init__(self, name, hp, max_hp, mp, max_mp, attack):
        self.name = name
        self.hp = hp            
        self.max_hp = max_hp
        self.mp = mp            # 巫力/真氣
        self.max_mp = max_mp
        self.attack = attack    
        self.exp = 0            
        self.level = 1          # 境界

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0: self.hp = 0

    def consume_mp(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def gain_exp(self, amount):
        self.exp += amount
        threshold = self.level * 100
        if self.exp >= threshold:
            self.exp -= threshold
            self.level += 1
            self.max_hp += 25
            self.max_mp += 15
            self.attack += 8
            self.hp = self.max_hp 
            self.mp = self.max_mp
            return True 
        return False

# --- 3. 系統初始化 ---
st.set_page_config(page_title="殷商煉氣錄", page_icon="🏺")
inject_custom_css() # 執行 CSS 注入

st.title("🏺 殷商‧煉氣錄")
st.caption("西元前 1600 年，天命玄鳥，降而生商。")

if 'player' not in st.session_state:
    st.session_state.player = QiRefiner("煉氣士", 100, 100, 60, 60, 12)
    st.session_state.shells = 0  # 貝幣
    st.session_state.log = ["【卜辭】今日甲子，宜出行，利涉大川。"]
    st.session_state.enemy = None
    st.session_state.in_combat = False

def add_log(message):
    st.session_state.log.insert(0, message)
    if len(st.session_state.log) > 6: # 縮減日誌行數以配合小介面
        st.session_state.log.pop()

# --- 4. 核心邏輯 (商朝版) ---

def explore():
    event = random.randint(1, 100)
    
    if event <= 35: # 獲得貝幣
        found = random.randint(3, 15)
        st.session_state.shells += found
        add_log(f"🐚 於荒野拾得【貝幣】{found} 朋。")
        # 略微回氣
        p = st.session_state.player
        p.mp = min(p.mp + 10, p.max_mp)
        
    elif event <= 55: # 無事
        add_log("🍂 洹水之濱，青銅鼎立，四野寂寥。")
        
    else: # 遭遇戰
        level = st.session_state.player.level
        scaling = level * 6
        # 商朝/封神背景怪物
        enemy_pool = [
            {"name": "鬼方蠻兵", "hp": 35 + scaling, "atk": 6 + level},
            {"name": "青銅機關獸", "hp": 70 + scaling, "atk": 12 + level},
            {"name": "饕餮幼崽", "hp": 110 + scaling, "atk": 18 + level},
            {"name": "鹿台妖狐", "hp": 90 + scaling, "atk": 22 + level}
        ]
        data = random.choice(enemy_pool)
        st.session_state.enemy = QiRefiner(data["name"], data["hp"], data["hp"], 0, 0, data["atk"])
        st.session_state.in_combat = True
        add_log(f"⚠️ 凶煞之氣！遭遇【{st.session_state.enemy.name}】！")

def combat_round(skill_name):
    player = st.session_state.player
    enemy = st.session_state.enemy
    
    # 玩家回合
    damage = 0
    
    if skill_name == "普攻":
        damage = random.randint(player.attack, player.attack + 6)
        add_log(f"🗡️ 手持青銅戈揮擊，造成 {damage} 點傷害。")
        
    elif skill_name == "五雷正法":
        cost = 15
        if player.consume_mp(cost):
            damage = random.randint(player.attack * 2, player.attack * 3)
            add_log(f"⚡ [五雷正法] 引天雷破邪！造成 {damage} 點重傷！")
        else:
            add_log("🚫 巫力枯竭，無法溝通天地！")
            
    elif skill_name == "番天印":
        cost = 40
        if player.consume_mp(cost):
            damage = random.randint(player.attack * 5, player.attack * 7)
            add_log(f"🏔️ [番天印] 祭出法寶，泰山壓頂！造成 {damage} 點毀滅傷害！")
        else:
             add_log("🚫 巫力不足，法寶祭煉失敗！")

    if damage > 0:
        enemy.take_damage(damage)

    # 勝利判定
    if not enemy.is_alive():
        base_exp = 25 * player.level
        bonus_shells = random.randint(10, 40)
        
        st.session_state.shells += bonus_shells
        is_levelup = player.gain_exp(base_exp)
        
        add_log(f"🏆 斬妖除魔！獲得 {bonus_shells} 貝幣，道行增加 {base_exp}。")
        if is_levelup:
            add_log(f"🐲 【天命覺醒】！境界提升至第 {player.level} 重！")
            st.balloons()
            
        st.session_state.enemy = None
        st.session_state.in_combat = False
        return

    # 敵人回合
    enemy_dmg = random.randint(enemy.attack - 3, enemy.attack + 4)
    player.take_damage(enemy_dmg)
    add_log(f"👹 {enemy.name} 凶猛反撲，你受到 {enemy_dmg} 點傷害。")

    if not player.is_alive():
        add_log("💀 魂歸封神台，你的傳說到此為止。")

def meditation():
    cost = 40
    if st.session_state.shells >= cost:
        st.session_state.shells -= cost
        p = st.session_state.player
        p.hp = p.max_hp
        p.mp = p.max_mp
        add_log("🧘 燃燒蓍草占卜，休養生息，狀態全滿。")
    else:
        add_log("❌ 貝幣不足 (需 40)，無法獻祭回覆。")

def restart():
    st.session_state.clear()
    st.rerun()

# --- 5. 介面渲染 (UI Rendering) ---

# 狀態儀表 (使用小字體)
p = st.session_state.player
col1, col2, col3, col4 = st.columns(4)
col1.metric("境界", f"{p.level} 重天")
col2.metric("氣血", f"{p.hp}/{p.max_hp}")
col3.metric("巫力", f"{p.mp}/{p.max_mp}")
col4.metric("貝幣", st.session_state.shells)

# 視覺化條
st.caption("氣血 (HP)")
st.progress(p.hp / p.max_hp)
st.caption("巫力 (MP)")
st.progress(p.mp / p.max_mp)

st.markdown("---")

# 互動區
if p.is_alive():
    if st.session_state.in_combat:
        st.markdown(f"### 👹 遭遇：{st.session_state.enemy.name}")
        st.text(f"敵方氣血：{st.session_state.enemy.hp}")
        
        c1, c2, c3 = st.columns(3)
        if c1.button("青銅戈 (普攻)"):
            combat_round("普攻")
            st.rerun()
        if c2.button("五雷正法 (15巫力)"):
            combat_round("五雷正法")
            st.rerun()
        if c3.button("番天印 (40巫力)"):
            combat_round("番天印")
            st.rerun()
            
    else:
        st.markdown("### 🗺️ 大商疆域")
        c1, c2 = st.columns(2)
        if c1.button("🌲 探索九州", use_container_width=True):
            explore()
            st.rerun()
        if c2.button("🧘 祭祀休整 (40貝幣)", use_container_width=True):
            meditation()
            st.rerun()
else:
    st.error("勝敗乃兵家常事。")
    if st.button("🔥 浴火重生"):
        restart()

st.markdown("---")
st.markdown("### 📜 龜甲卜辭 (日誌)")
for msg in st.session_state.log:
    st.text(msg)
