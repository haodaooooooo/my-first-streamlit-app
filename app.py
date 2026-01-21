import streamlit as st
import random
import uuid # 用於生成唯一的物品 ID

# --- 1. CSS 樣式 (維持殷商風格) ---
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
            border-radius: 0px; 
        }
        .stButton > button:hover {
            background-color: #800000;
            color: #fff;
        }
        /* 裝備欄樣式 */
        .equip-slot {
            border: 1px dashed #8b0000;
            padding: 10px;
            text-align: center;
            background-color: #e8e4d9;
            margin-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 物品與裝備定義 ---

class Equipment:
    def __init__(self, name, slot, bonus_type, bonus_val, price):
        self.id = str(uuid.uuid4()) # 科學標記：每個物品都有唯一 ID
        self.name = name
        self.slot = slot          # weapon, head, body, feet
        self.bonus_type = bonus_type # 'atk' or 'hp'
        self.bonus_val = bonus_val
        self.price = price

    def desc(self):
        sign = "攻擊" if self.bonus_type == 'atk' else "氣血"
        return f"【{self.name}】 ({sign}+{self.bonus_val})"

# 物品資料庫 (藍圖)
ITEMS_DB = {
    # 武器
    "青銅戈": {"slot": "weapon", "type": "atk", "val": 10, "price": 50},
    "龍泉劍": {"slot": "weapon", "type": "atk", "val": 25, "price": 200},
    "打神鞭(仿)": {"slot": "weapon", "type": "atk", "val": 50, "price": 800},
    # 頭部
    "布巾": {"slot": "head", "type": "hp", "val": 20, "price": 30},
    "虎頭盔": {"slot": "head", "type": "hp", "val": 50, "price": 150},
    # 身體
    "麻衣": {"slot": "body", "type": "hp", "val": 30, "price": 40},
    "兕皮甲": {"slot": "body", "type": "hp", "val": 80, "price": 300},
    # 鞋履
    "草鞋": {"slot": "feet", "type": "hp", "val": 10, "price": 10},
    "步雲履": {"slot": "feet", "type": "hp", "val": 40, "price": 120},
}

def create_item(name):
    """工廠模式：根據名稱生成物品物件"""
    if name in ITEMS_DB:
        d = ITEMS_DB[name]
        return Equipment(name, d['slot'], d['type'], d['val'], d['price'])
    return None

# --- 3. 世界地圖數據 ---
WORLD_MAP = {
    "朝歌": {
        "desc": "大商國都，繁華靡麗。",
        "enemies": ["禁衛軍", "比干怨魂"],
        "drops": ["布巾", "麻衣", "青銅戈"], # 該地區可能掉落
        "merchant": ["青銅戈", "布巾", "麻衣", "草鞋"]
    },
    "西岐": {
        "desc": "周文王治下之地。",
        "enemies": ["巡山靈獸", "崑崙探子"],
        "drops": ["虎頭盔", "龍泉劍"],
        "merchant": ["龍泉劍", "虎頭盔", "兕皮甲"]
    },
    "陳塘關": {
        "desc": "濱海雄關，浪濤洶湧。",
        "enemies": ["巡海夜叉", "龍宮三太子"],
        "drops": ["步雲履", "打神鞭(仿)"],
        "merchant": ["步雲履", "龍泉劍", "兕皮甲"]
    }
}

ENEMY_STATS = {
    "禁衛軍": {"hp": 80, "atk": 15, "exp": 30},
    "比干怨魂": {"hp": 60, "atk": 20, "exp": 25},
    "巡山靈獸": {"hp": 50, "atk": 10, "exp": 20},
    "崑崙探子": {"hp": 70, "atk": 12, "exp": 25},
    "巡海夜叉": {"hp": 90, "atk": 18, "exp": 40},
    "龍宮三太子": {"hp": 150, "atk": 25, "exp": 100}
}

# --- 4. 角色類別 (含裝備邏輯) ---
class QiRefiner:
    def __init__(self, name):
        self.name = name
        self.base_hp = 100
        self.base_atk = 10
        self.current_hp = 100
        self.mp = 100
        self.max_mp = 100
        self.exp = 0
        self.level = 1
        
        # 容器
        self.inventory = [] # 列表
        self.equipment = {  # 字典：插槽 -> 物件
            "weapon": None,
            "head": None,
            "body": None,
            "feet": None
        }
    
    # 計算屬性：基礎 + 裝備加成
    @property
    def max_hp(self):
        bonus = 0
        for slot, item in self.equipment.items():
            if item and item.bonus_type == 'hp':
                bonus += item.bonus_val
        return self.base_hp + bonus

    @property
    def attack(self):
        bonus = 0
        for slot, item in self.equipment.items():
            if item and item.bonus_type == 'atk':
                bonus += item.bonus_val
        return self.base_atk + bonus

    def equip(self, item_id):
        # 從背包尋找物品
        item_to_equip = next((i for i in self.inventory if i.id == item_id), None)
        if not item_to_equip: return

        # 卸下當前位置裝備
        slot = item_to_equip.slot
        if self.equipment[slot]:
            self.inventory.append(self.equipment[slot]) # 舊裝備回背包
        
        # 穿上新裝備
        self.equipment[slot] = item_to_equip
        self.inventory.remove(item_to_equip)
        
        # 修正當前血量 (避免溢出或錯誤)
        self.current_hp = min(self.current_hp, self.max_hp)

    def unequip(self, slot):
        if self.equipment[slot]:
            self.inventory.append(self.equipment[slot])
            self.equipment[slot] = None

# --- 5. 系統初始化 ---
st.set_page_config(page_title="殷商‧封神武裝", page_icon="🛡️", layout="wide")
inject_custom_css()

if 'player' not in st.session_state:
    st.session_state.player = QiRefiner("煉氣士")
    st.session_state.shells = 100
    st.session_state.location = "朝歌"
    st.session_state.log = ["【系統】你下山歷練，身無長物。"]
    st.session_state.game_state = "IDLE" 
    st.session_state.target = None

def add_log(msg):
    st.session_state.log.insert(0, msg)
    if len(st.session_state.log) > 8: st.session_state.log.pop()

# --- 6. 核心邏輯 ---

def explore():
    loc = WORLD_MAP[st.session_state.location]
    dice = random.randint(1, 100)
    
    if dice <= 50: # 戰鬥
        e_name = random.choice(loc["enemies"])
        stats = ENEMY_STATS[e_name]
        # 創建臨時敵人物件
        st.session_state.target = {
            "name": e_name, 
            "hp": stats["hp"] + (st.session_state.player.level * 10), 
            "max_hp": stats["hp"] + (st.session_state.player.level * 10),
            "atk": stats["atk"] + st.session_state.player.level,
            "exp": stats["exp"]
        }
        st.session_state.game_state = "COMBAT"
        add_log(f"⚔️ 遭遇敵襲：{e_name}！")
    
    elif dice <= 80: # 商人
        st.session_state.game_state = "MERCHANT"
        add_log("💰 遇見了行腳商隊。")
    
    else:
        found = random.randint(10, 30)
        st.session_state.shells += found
        add_log(f"🐚 撿到貝幣 {found}。")

def combat_round():
    p = st.session_state.player
    e = st.session_state.target
    
    # 玩家攻擊
    dmg = random.randint(int(p.attack * 0.8), int(p.attack * 1.2))
    e["hp"] -= dmg
    add_log(f"🗡️ 你造成 {dmg} 點傷害。")
    
    if e["hp"] <= 0:
        # 勝利結算
        p.exp += e["exp"]
        coin = random.randint(10, 40)
        st.session_state.shells += coin
        add_log(f"🏆 勝利！獲 {coin} 貝幣, {e['exp']} 修為。")
        
        # 掉寶機制 (20% 機率)
        if random.random() < 0.2:
            drop_name = random.choice(WORLD_MAP[st.session_state.location]["drops"])
            item = create_item(drop_name)
            p.inventory.append(item)
            add_log(f"🎁 敵人掉落了裝備：{item.name}！")

        # 升級判定
        if p.exp >= p.level * 100:
            p.exp -= p.level * 100
            p.level += 1
            p.base_hp += 20
            p.base_atk += 5
            p.current_hp = p.max_hp
            add_log(f"🌟 境界提升至 Lv.{p.level}！")
            st.balloons()
            
        st.session_state.game_state = "IDLE"
    else:
        # 敵人反擊
        e_dmg = max(1, e["atk"] - random.randint(0, 2)) # 簡易防禦運算
        p.current_hp -= e_dmg
        add_log(f"👹 敵人反擊造成 {e_dmg} 傷害。")
        if p.current_hp <= 0:
            p.current_hp = 0
            st.session_state.game_state = "DEAD"
            add_log("💀 你已氣絕。")

def buy_item(item_name):
    item_proto = ITEMS_DB[item_name]
    if st.session_state.shells >= item_proto["price"]:
        st.session_state.shells -= item_proto["price"]
        new_item = create_item(item_name)
        st.session_state.player.inventory.append(new_item)
        add_log(f"🛒 購買了 {item_name}。")
    else:
        add_log("❌ 貝幣不足。")

def sell_item(item_id):
    p = st.session_state.player
    item = next((i for i in p.inventory if i.id == item_id), None)
    if item:
        sell_price = int(item.price * 0.5) # 半價出售
        st.session_state.shells += sell_price
        p.inventory.remove(item)
        add_log(f"⚖️ 出售 {item.name}，獲得 {sell_price} 貝幣。")

# --- 7. 介面渲染 ---

# 左側：角色裝備與狀態
with st.sidebar:
    st.header("👤 煉氣士")
    p = st.session_state.player
    st.write(f"境界: Lv.{p.level}")
    st.write(f"氣血: {p.current_hp} / {p.max_hp}")
    st.write(f"攻擊: {p.attack}")
    st.write(f"貝幣: {st.session_state.shells}")
    st.progress(p.current_hp / p.max_hp)
    
    st.markdown("---")
    st.subheader("🛡️ 當前裝備")
    
    # 裝備欄顯示
    slots = {"weapon": "⚔️ 武器", "head": "🧢 頭部", "body": "👕 身體", "feet": "👢 鞋履"}
    for slot_key, slot_name in slots.items():
        item = p.equipment[slot_key]
        st.markdown(f"**{slot_name}**")
        if item:
            st.info(f"{item.name} (+{item.bonus_val})")
            if st.button("卸下", key=f"unequip_{slot_key}"):
                p.unequip(slot_key)
                st.rerun()
        else:
            st.caption("空")
            
    st.markdown("---")
    st.subheader("🎒 背包")
    if not p.inventory:
        st.caption("空空如也")
    else:
        for item in p.inventory:
            col1, col2 = st.columns([3, 2])
            col1.write(f"{item.name}")
            if st.session_state.game_state == "MERCHANT":
                if col2.button("賣出", key=f"sell_{item.id}"):
                    sell_item(item.id)
                    st.rerun()
            else:
                if col2.button("裝備", key=f"equip_{item.id}"):
                    p.equip(item.id)
                    st.rerun()

# 主視窗
st.title("殷商‧封神武裝")

# 地點導航
if st.session_state.game_state == "IDLE":
    col_nav = st.columns(len(WORLD_MAP))
    for idx, (loc_name, loc_data) in enumerate(WORLD_MAP.items()):
        if col_nav[idx].button(loc_name, disabled=(loc_name == st.session_state.location)):
            st.session_state.location = loc_name
            add_log(f"🐎 前往 {loc_name}...")
            st.rerun()
    st.info(WORLD_MAP[st.session_state.location]["desc"])

st.markdown("---")

# 遊戲狀態區
if st.session_state.game_state == "DEAD":
    st.error("勝敗乃兵家常事。")
    if st.button("🔥 重入輪迴"):
        st.session_state.clear()
        st.rerun()

elif st.session_state.game_state == "COMBAT":
    enemy = st.session_state.target
    st.subheader(f"⚔️ 正在與 {enemy['name']} 戰鬥")
    st.write(f"HP: {enemy['hp']} / {enemy['max_hp']}")
    st.progress(max(0, enemy['hp'] / enemy['max_hp']))
    
    if st.button("👊 進攻", use_container_width=True):
        combat_round()
        st.rerun()

elif st.session_state.game_state == "MERCHANT":
    st.subheader("💰 行腳商隊")
    st.write("商人：『瞧一瞧看一看，都是上好的法器！』(點擊背包物品可出售)")
    
    goods = WORLD_MAP[st.session_state.location]["merchant"]
    
    for item_name in goods:
        data = ITEMS_DB[item_name]
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"**{item_name}** ({data['type']}+{data['val']})")
        c2.write(f"{data['price']} 貝幣")
        if c3.button("購買", key=f"buy_{item_name}"):
            buy_item(item_name)
            st.rerun()
            
    if st.button("👋 離開商店"):
        st.session_state.game_state = "IDLE"
        st.rerun()

else: # IDLE
    st.subheader(f"📍 {st.session_state.location}")
    if st.button("🌲 探索四周", use_container_width=True):
        explore()
        st.rerun()
    if st.button("🧘 休息 (恢復 HP)", use_container_width=True):
        p.current_hp = p.max_hp
        add_log("🧘 狀態全滿。")
        st.rerun()

st.markdown("---")
st.caption("📜 紀錄")
for l in st.session_state.log:
    st.text(l)
