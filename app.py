import streamlit as st
import random
import time

# --- 1. CSS 樣式注入 (維持商朝風格) ---
def inject_custom_css():
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-family: "KaiTi", "楷体", serif;
            color: #4a3b2a;
            background-color: #f4f0e6;
        }
        .stButton > button {
            background-color: transparent;
            color: #800000;
            border: 2px solid #800000;
            border-radius: 0px; /* 方正風格 */
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #800000;
            color: #fff;
        }
        /* 側邊欄樣式 */
        [data-testid="stSidebar"] {
            background-color: #e8e4d9;
            border-right: 1px solid #c0b0a0;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 數據結構定義 (Map & Entities) ---

# 世界地圖數據：定義各地點的敵人和 NPC
WORLD_MAP = {
    "朝歌 (王都)": {
        "desc": "大商國都，繁華靡麗，摘星樓高聳入雲。",
        "enemies": [
            {"name": "禁衛軍", "hp": 80, "atk": 15, "exp": 30},
            {"name": "比干怨魂", "hp": 60, "atk": 20, "exp": 25}
        ],
        "npcs": [
            {"name": "多寶道人", "type": "merchant", "items": {"回氣丹": 20, "強身酒": 30}},
            {"name": "殷商遺老", "type": "civilian", "dialogs": ["大王沈迷妲己，國將不國啊...", "聽說西邊有鳳鳴之聲。"]}
        ]
    },
    "西岐 (周原)": {
        "desc": "周文王治下之地，民風淳樸，靈氣充沛。",
        "enemies": [
            {"name": "巡山靈獸", "hp": 50, "atk": 10, "exp": 20},
            {"name": "崑崙探子", "hp": 70, "atk": 12, "exp": 25}
        ],
        "npcs": [
            {"name": "姜子牙", "type": "merchant", "items": {"打神鞭碎片": 100, "杏黃旗殘卷": 80}},
            {"name": "樵夫", "type": "civilian", "dialogs": ["渭水河邊有個怪老頭直鉤釣魚。", "姬昌大人真是仁義之君。"]}
        ]
    },
    "陳塘關 (東海)": {
        "desc": "濱海雄關，浪濤洶湧，常有龍族出沒。",
        "enemies": [
            {"name": "巡海夜叉", "hp": 90, "atk": 18, "exp": 40},
            {"name": "蝦兵蟹將", "hp": 40, "atk": 8, "exp": 15},
            {"name": "龍宮三太子", "hp": 150, "atk": 25, "exp": 100}
        ],
        "npcs": [
            {"name": "李靖", "type": "civilian", "dialogs": ["我家那逆子又闖禍了！", "此塔專鎮妖邪。"]},
            {"name": "東海漁商", "type": "merchant", "items": {"深海珍珠": 50, "龍涎香": 60}}
        ]
    }
}

class QiRefiner:
    def __init__(self, name, hp, max_hp, mp, max_mp, attack):
        self.name = name
        self.hp = hp; self.max_hp = max_hp
        self.mp = mp; self.max_mp = max_mp
        self.attack = attack; self.exp = 0; self.level = 1

    def is_alive(self): return self.hp > 0
    
    def heal(self, amount):
        self.hp = min(self.hp + amount, self.max_hp)

    def restore_mp(self, amount):
        self.mp = min(self.mp + amount, self.max_mp)
        
    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)

    def consume_mp(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.level * 100:
            self.exp -= self.level * 100
            self.level += 1
            self.max_hp += 20; self.max_mp += 10; self.attack += 5
            self.hp = self.max_hp; self.mp = self.max_mp
            return True
        return False

# --- 3. 系統初始化 ---
st.set_page_config(page_title="殷商‧九州行", page_icon="🗺️", layout="wide")
inject_custom_css()

if 'player' not in st.session_state:
    st.session_state.player = QiRefiner("煉氣士", 120, 120, 80, 80, 15)
    st.session_state.shells = 50
    st.session_state.location = "朝歌 (王都)"
    st.session_state.log = ["【系統】你出生於大商王都朝歌。"]
    st.session_state.game_state = "IDLE" # IDLE, COMBAT, INTERACT
    st.session_state.target = None # 儲存當前的敵人或 NPC 物件

def add_log(msg):
    st.session_state.log.insert(0, msg)
    if len(st.session_state.log) > 10: st.session_state.log.pop()

# --- 4. 邏輯函數 ---

def travel(new_location):
    if st.session_state.game_state == "COMBAT":
        add_log("🚫 戰鬥中無法移動！")
        return
    st.session_state.location = new_location
    st.session_state.game_state = "IDLE"
    st.session_state.target = None
    add_log(f"🐎 跋涉千里，抵達了【{new_location}】。")

def explore_location():
    loc_data = WORLD_MAP[st.session_state.location]
    dice = random.randint(1, 100)
    
    if dice <= 40: # 遭遇敵人 (40%)
        enemy_data = random.choice(loc_data["enemies"])
        # 根據玩家等級動態調整敵人
        scaling = st.session_state.player.level * 5
        st.session_state.target = QiRefiner(enemy_data["name"], enemy_data["hp"]+scaling, enemy_data["hp"]+scaling, 0, 0, enemy_data["atk"] + int(scaling/2))
        st.session_state.game_state = "COMBAT"
        add_log(f"⚔️ 殺氣逼人！遭遇【{st.session_state.target.name}】！")
        
    elif dice <= 70: # 遭遇 NPC (30%)
        npc_data = random.choice(loc_data["npcs"])
        st.session_state.target = npc_data
        st.session_state.game_state = "INTERACT"
        add_log(f"🗣️ 前方遇到一位【{npc_data['name']}】。")
        
    else: # 撿錢/無事 (30%)
        found = random.randint(5, 20)
        st.session_state.shells += found
        add_log(f"🐚 撿到遺落的貝幣 {found} 朋。")

# 戰鬥邏輯
def combat_logic(action):
    player = st.session_state.player
    enemy = st.session_state.target
    
    dmg = 0
    if action == "attack":
        dmg = random.randint(player.attack, player.attack + 5)
        add_log(f"🗡️ 你攻擊造成 {dmg} 傷害。")
    elif action == "skill":
        if player.consume_mp(20):
            dmg = random.randint(player.attack * 2, player.attack * 3)
            add_log(f"⚡ 施展雷法造成 {dmg} 傷害！")
        else:
            add_log("🚫 巫力不足！")
            
    if dmg > 0: enemy.take_damage(dmg)
    
    if not enemy.is_alive():
        base_exp = 30 * player.level
        bonus = random.randint(10, 50)
        player.gain_exp(base_exp)
        st.session_state.shells += bonus
        add_log(f"🏆 獲勝！得貝幣 {bonus}，修為 {base_exp}。")
        st.session_state.game_state = "IDLE"
        st.session_state.target = None
    else:
        # 敵人反擊
        enemy_dmg = random.randint(enemy.attack-2, enemy.attack+5)
        player.take_damage(enemy_dmg)
        add_log(f"👹 敵人反擊造成 {enemy_dmg} 傷害。")
        if not player.is_alive():
            add_log("💀 勝敗乃兵家常事...")
            st.session_state.game_state = "DEAD"

# 交易/對話邏輯
def interact_logic(action, item_name=None, price=0):
    npc = st.session_state.target
    
    if action == "chat":
        dialog = random.choice(npc["dialogs"]) if "dialogs" in npc else "......"
        add_log(f"🗨️ {npc['name']}：「{dialog}」")
        
    elif action == "buy":
        if st.session_state.shells >= price:
            st.session_state.shells -= price
            # 簡單實作：購買直接使用
            if "丹" in item_name or "珠" in item_name:
                st.session_state.player.heal(50)
                add_log(f"💊 購買並服用 {item_name}，氣血恢復。")
            elif "酒" in item_name or "香" in item_name:
                st.session_state.player.restore_mp(50)
                add_log(f"🍶 購買並飲用 {item_name}，巫力恢復。")
            else:
                st.session_state.player.attack += 2
                add_log(f"🗡️ 購買 {item_name}，攻擊力永久提升！")
        else:
            add_log("❌ 貝幣不足！")
            
    elif action == "leave":
        st.session_state.game_state = "IDLE"
        st.session_state.target = None
        add_log("👋 告別了對方。")

# --- 5. 介面渲染 (UI Rendering) ---

# 側邊欄：地圖導航
with st.sidebar:
    st.header("🗺️ 九州輿圖")
    current_loc = st.session_state.location
    st.info(f"當前位置：{current_loc}")
    st.write(WORLD_MAP[current_loc]["desc"])
    st.markdown("---")
    st.write("前往其他地區：")
    for loc in WORLD_MAP:
        if loc != current_loc:
            if st.button(f"前往 {loc}"):
                travel(loc)
                st.rerun()

# 主介面：狀態欄
p = st.session_state.player
c1, c2, c3, c4 = st.columns(4)
c1.metric("境界", f"Lv.{p.level}")
c2.metric("氣血", f"{p.hp}/{p.max_hp}")
c3.metric("巫力", f"{p.mp}/{p.max_mp}")
c4.metric("貝幣", st.session_state.shells)

st.progress(p.hp / p.max_hp)
st.markdown("---")

# 主介面：動態內容區
if st.session_state.game_state == "DEAD":
    st.error("你已氣絕身亡。")
    if st.button("🔥 轉世重修"):
        st.session_state.clear()
        st.rerun()

elif st.session_state.game_state == "COMBAT":
    enemy = st.session_state.target
    st.subheader(f"⚔️ 對決：{enemy.name}")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"敵方氣血：{enemy.hp}")
        st.progress(min(enemy.hp/100, 1.0)) # 簡化顯示
    with col2:
        if st.button("普通攻擊", use_container_width=True):
            combat_logic("attack")
            st.rerun()
        if st.button("五雷正法 (20MP)", use_container_width=True):
            combat_logic("skill")
            st.rerun()

elif st.session_state.game_state == "INTERACT":
    npc = st.session_state.target
    st.subheader(f"👥 互動：{npc['name']}")
    
    if npc["type"] == "civilian":
        if st.button("閒聊", use_container_width=True):
            interact_logic("chat")
            st.rerun()
        if st.button("離開", use_container_width=True):
            interact_logic("leave")
            st.rerun()
            
    elif npc["type"] == "merchant":
        st.write("【商舖貨架】")
        for item, price in npc["items"].items():
            col_a, col_b = st.columns([3, 1])
            col_a.write(f"📦 {item} ({price} 貝幣)")
            if col_b.button("購買", key=item):
                interact_logic("buy", item, price)
                st.rerun()
        if st.button("離開商舖"):
            interact_logic("leave")
            st.rerun()

else: # IDLE state
    st.subheader(f"📍 {st.session_state.location}")
    if st.button("🌲 在此地探索", use_container_width=True):
        explore_location()
        st.rerun()
    if st.button("🧘 原地修整 (恢復狀態)", use_container_width=True):
        if st.session_state.shells >= 10:
            st.session_state.shells -= 10
            p.heal(999); p.restore_mp(999)
            add_log("🧘 花費 10 貝幣修整完畢。")
        else:
            add_log("❌ 盤纏不足。")
        st.rerun()

# 日誌區
st.markdown("---")
st.subheader("📜 行腳記錄")
for msg in st.session_state.log:
    st.text(msg)
