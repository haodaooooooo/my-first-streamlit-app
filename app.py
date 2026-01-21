import streamlit as st
import random
import uuid

# --- 引入外部數據模組 ---
# 科學說明：這行指令會讓 Python 去讀取 game_data.py 裡面的變數
from game_data import ITEMS_DB, GENERALS_DB

# ... (其餘邏輯代碼保持不變) ...

# 測試點：原本用到 ITEMS_DB 的地方都不需要改，
# 因為 import 進來後，它就存在於這個命名空間 (Namespace) 了。

# --- 1. CSS 樣式：漢末烽火風格 ---
def inject_custom_css():
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-family: "KaiTi", "楷体", serif;
            color: #2b2b2b;
            background-color: #e0d8c8; /* 古紙色 */
        }
        .stButton > button {
            background-color: #8b0000; /* 血紅 */
            color: #fff;
            border: 2px solid #5c0000;
            border-radius: 4px;
        }
        .stButton > button:hover {
            background-color: #a52a2a;
        }
        /* 特殊裝備欄高亮 */
        .artifact-slot {
            border: 2px solid #ffd700;
            background-color: #fff8dc;
            padding: 10px;
            color: #8b4500;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 2. 數據庫結構 (The Database) ---

# 裝備定義
ITEMS_DB = {
    # 武器
    "環首刀": {"slot": "weapon", "type": "atk", "val": 10, "price": 50},
    "點鋼槍": {"slot": "weapon", "type": "atk", "val": 25, "price": 200},
    # 防具
    "皮甲": {"slot": "body", "type": "hp", "val": 50, "price": 100},
    "明光鎧": {"slot": "body", "type": "hp", "val": 120, "price": 500},
    # 特殊寶物 (Artifacts) - 只有名將掉落或高價購買
    "青釭劍": {"slot": "artifact", "type": "atk", "val": 80, "price": 9999, "desc": "曹操佩劍，削鐵如泥"},
    "丈八蛇矛": {"slot": "artifact", "type": "atk", "val": 75, "price": 9999, "desc": "張飛兵器，如巨蟒吞信"},
    "青龍偃月刀": {"slot": "artifact", "type": "atk", "val": 85, "price": 9999, "desc": "關羽神兵，重八十二斤"},
    "羽扇": {"slot": "artifact", "type": "int", "val": 50, "price": 9999, "desc": "孔明之物，運籌帷幄"},
    "赤兔馬": {"slot": "artifact", "type": "hp", "val": 200, "price": 9999, "desc": "人中呂布，馬中赤兔"},
}

# 武將資料庫 (你可以依照此格式複製擴充至 50 人)
# type: 'war' (武力), 'int' (智力), 'balance' (平衡)
GENERALS_DB = [
    # 蜀漢
    {"name": "關羽", "loc": "荊州", "type": "war", "stats": {"hp": 300, "atk": 98, "int": 75}, "drop": "青龍偃月刀", 
     "dialogs": ["吾觀顏良文醜，如插標賣首耳！", "關某的大刀已經飢渴難耐了。", "酒且斟下，某去便來。"]},
    {"name": "張飛", "loc": "荊州", "type": "war", "stats": {"hp": 320, "atk": 99, "int": 30}, "drop": "丈八蛇矛",
     "dialogs": ["燕人張翼德在此！誰敢決一死戰！", "三姓家奴休走！", "大哥，俺想死你了！"]},
    {"name": "諸葛亮", "loc": "荊州", "type": "int", "stats": {"hp": 150, "atk": 40, "int": 100}, "drop": "羽扇",
     "dialogs": ["主公之志，亮願效犬馬之勞。", "我從未見過如此厚顏無恥之人！", "今夜星象有變。"]},
    # 曹魏
    {"name": "曹操", "loc": "許昌", "type": "balance", "stats": {"hp": 250, "atk": 85, "int": 95}, "drop": "青釭劍",
     "dialogs": ["寧教我負天下人，休教天下人負我。", "周公吐哺，天下歸心。", "此人不可留！"]},
    {"name": "夏侯惇", "loc": "許昌", "type": "war", "stats": {"hp": 280, "atk": 90, "int": 60}, "drop": "明光鎧",
     "dialogs": ["父精母血，不可棄也！", "魏軍威武！", "孟德兄，交給我吧。"]},
    {"name": "郭嘉", "loc": "許昌", "type": "int", "stats": {"hp": 120, "atk": 30, "int": 98}, "drop": "點鋼槍",
     "dialogs": ["主公，兵貴神速。", "嘉，願為主公決斷。", "咳咳...天命如此。"]},
    # 東吳
    {"name": "周瑜", "loc": "建業", "type": "int", "stats": {"hp": 200, "atk": 70, "int": 96}, "drop": "點鋼槍",
     "dialogs": ["既生瑜，何生亮！", "談笑間，檣櫓灰飛煙滅。", "這場東風，我借定了。"]},
    {"name": "孫尚香", "loc": "建業", "type": "war", "stats": {"hp": 220, "atk": 88, "int": 70}, "drop": "環首刀",
     "dialogs": ["誰說女子不如男？", "看箭！", "父親大人的基業由我守護。"]},
    # 群雄
    {"name": "呂布", "loc": "下邳", "type": "war", "stats": {"hp": 400, "atk": 100, "int": 20}, "drop": "赤兔馬",
     "dialogs": ["神擋殺神，佛擋殺佛！", "誰能擋我！", "貂蟬..."]},
    {"name": "貂蟬", "loc": "下邳", "type": "int", "stats": {"hp": 150, "atk": 40, "int": 90}, "drop": "皮甲",
     "dialogs": ["妾身...身不由己。", "大人，請喝了這杯酒吧。", "月光...好美。"]}
]

# --- 3. 類別定義 (Classes) ---

class Item:
    def __init__(self, name):
        data = ITEMS_DB.get(name, {"slot": "misc", "type": "none", "val": 0, "price": 0})
        self.id = str(uuid.uuid4())
        self.name = name
        self.slot = data["slot"]
        self.type = data["type"]
        self.val = data["val"]
        self.price = data["price"]
        self.desc = data.get("desc", "")

class Player:
    def __init__(self, name, gender):
        self.name = name
        self.gender = gender
        self.level = 1
        self.exp = 0
        self.money = 200 # 五銖錢
        
        # 基礎屬性 (隨性別微調)
        if gender == "男":
            self.base_hp = 120; self.base_atk = 20; self.base_int = 15
        else:
            self.base_hp = 100; self.base_atk = 18; self.base_int = 25
            
        self.hp = self.base_hp
        self.inventory = []
        self.equipment = {"weapon": None, "body": None, "artifact": None}

    # 計算總屬性 (含裝備)
    def get_stat(self, stat_name):
        base = 0
        if stat_name == "hp": base = self.base_hp
        elif stat_name == "atk": base = self.base_atk
        elif stat_name == "int": base = self.base_int
        
        bonus = 0
        for slot, item in self.equipment.items():
            if item and item.type == stat_name:
                bonus += item.val
        return base + bonus

    def max_hp(self): return self.get_stat("hp")
    def atk(self): return self.get_stat("atk")
    def intelligence(self): return self.get_stat("int")

    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.level * 100:
            self.exp -= self.level * 100
            self.level += 1
            self.base_hp += 30; self.base_atk += 5; self.base_int += 5
            self.hp = self.max_hp() # 升級補滿
            return True
        return False

# --- 4. 系統邏輯 ---

st.set_page_config(page_title="三國‧赤壁前夕", page_icon="🔥", layout="wide")
inject_custom_css()

if 'started' not in st.session_state:
    st.session_state.started = False

# --- 遊戲開始畫面 ---
if not st.session_state.started:
    st.title("🔥 三國‧赤壁前夕")
    st.markdown("### 建安十三年，天下三分之勢未定...")
    
    col1, col2 = st.columns(2)
    name = col1.text_input("請輸入俠士姓名", value="無名氏")
    gender = col2.selectbox("選擇性別", ["男", "女"])
    
    if st.button("投身亂世"):
        st.session_state.player = Player(name, gender)
        st.session_state.location = "荊州"
        st.session_state.log = [f"【史官】{name} 於亂世中覺醒，身處荊州之地。"]
        st.session_state.state = "IDLE" # IDLE, COMBAT, DEBATE, SHOP
        st.session_state.target = None
        st.session_state.started = True
        st.rerun()

else:
    # --- 主遊戲迴圈 ---
    p = st.session_state.player
    
    def add_log(msg):
        st.session_state.log.insert(0, msg)
        if len(st.session_state.log) > 10: st.session_state.log.pop()

    # 側邊欄：角色狀態
    with st.sidebar:
        st.header(f"🚩 {p.name} ({p.gender})")
        st.write(f"官階: Lv.{p.level}")
        st.write(f"五銖錢: {p.money}")
        
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("武力", p.atk())
        col_s2.metric("智力", p.intelligence())
        
        st.write(f"兵力 (HP): {p.hp}/{p.max_hp()}")
        st.progress(max(0, p.hp/p.max_hp()))
        
        st.markdown("---")
        st.subheader("🛡️ 裝備")
        
        # 裝備顯示
        for slot in ["weapon", "body"]:
            item = p.equipment[slot]
            label = "⚔️ 武器" if slot == "weapon" else "👕 防具"
            st.write(f"**{label}**")
            if item:
                st.caption(f"{item.name} ({item.type.upper()}+{item.val})")
                if st.button("卸下", key=f"unequip_{slot}"):
                    p.inventory.append(item)
                    p.equipment[slot] = None
                    st.rerun()
            else:
                st.caption("無")
        
        # 特殊裝備欄
        st.markdown('<div class="artifact-slot">✨ 寶物欄</div>', unsafe_allow_html=True)
        art = p.equipment["artifact"]
        if art:
            st.info(f"{art.name}：{art.desc}")
            if st.button("收藏", key="unequip_art"):
                p.inventory.append(art)
                p.equipment["artifact"] = None
                st.rerun()
        else:
            st.caption("空缺")

        st.markdown("---")
        st.subheader("🎒 行囊")
        for i, item in enumerate(p.inventory):
            c1, c2 = st.columns([3, 1])
            c1.write(f"{item.name}")
            if c2.button("裝", key=f"eq_{item.id}"):
                # 換裝邏輯
                current = p.equipment[item.slot]
                if current: p.inventory.append(current)
                p.equipment[item.slot] = item
                p.inventory.pop(i)
                st.rerun()

    # 主視窗內容
    st.title(f"📍 {st.session_state.location}")
    
    # 邏輯區塊
    
    # 1. 探索邏輯 (移動與遭遇)
    if st.session_state.state == "IDLE":
        locations = ["荊州", "許昌", "建業", "下邳"]
        
        st.markdown("### 🗺️ 九州大地")
        cols = st.columns(len(locations))
        for idx, loc in enumerate(locations):
            if loc != st.session_state.location:
                if cols[idx].button(f"前往{loc}"):
                    st.session_state.location = loc
                    add_log(f"🐎 車馬勞頓，抵達了{loc}。")
                    st.rerun()
                    
        st.markdown("---")
        col_act1, col_act2, col_act3 = st.columns(3)
        
        if col_act1.button("🌲 探索周遭", use_container_width=True):
            dice = random.randint(1, 100)
            # 篩選當前地區的武將
            local_generals = [g for g in GENERALS_DB if g["loc"] == st.session_state.location]
            
            if dice <= 60 and local_generals: # 遭遇武將
                target_data = random.choice(local_generals)
                st.session_state.target = target_data
                st.session_state.temp_hp = target_data["stats"]["hp"] # 敵人臨時血量
                add_log(f"⚠️ 前方殺氣騰騰，那是... {target_data['name']}！")
                st.session_state.state = "ENCOUNTER" # 進入遭遇狀態
                
            elif dice <= 80: # 商人
                st.session_state.state = "SHOP"
                add_log("💰 偶遇西域行商。")
                
            else:
                found = random.randint(10, 50)
                p.money += found
                add_log(f"⚪ 撿到了散落的五銖錢 {found} 文。")
            st.rerun()

        if col_act2.button("💤 紮營休息 (50錢)", use_container_width=True):
            if p.money >= 50:
                p.money -= 50
                p.hp = p.max_hp()
                add_log("💤 體力全滿。")
            else:
                add_log("❌ 盤纏不足。")
            st.rerun()

    # 2. 遭遇狀態 (對話/選擇戰鬥)
    elif st.session_state.state == "ENCOUNTER":
        target = st.session_state.target
        st.subheader(f"對峙：{target['name']}")
        
        # 顯示隨機台詞
        if "said" not in st.session_state:
            dialog = random.choice(target["dialogs"])
            st.info(f"🗨️ {target['name']}：「{dialog}」")
            st.session_state.said = True
            
        c1, c2, c3 = st.columns(3)
        if c1.button("⚔️ 比武 (單挑)"):
            st.session_state.mode = "DUEL"
            st.session_state.state = "COMBAT"
            del st.session_state.said
            st.rerun()
            
        if c2.button("📜 舌戰 (辯論)"):
            st.session_state.mode = "DEBATE"
            st.session_state.state = "COMBAT"
            del st.session_state.said
            st.rerun()
            
        if c3.button("👋 撤退"):
            st.session_state.state = "IDLE"
            del st.session_state.said
            add_log("💨 你選擇了戰略性撤退。")
            st.rerun()

    # 3. 戰鬥狀態 (單挑/舌戰)
    elif st.session_state.state == "COMBAT":
        target = st.session_state.target
        mode = st.session_state.mode # DUEL or DEBATE
        enemy_hp = st.session_state.temp_hp
        enemy_max = target["stats"]["hp"]
        
        st.subheader(f"⚔️ {mode}：VS {target['name']}")
        
        # 顯示血量條
        col_p, col_e = st.columns(2)
        with col_p:
            st.write("我方狀態")
            st.progress(p.hp / p.max_hp())
        with col_e:
            st.write(f"敵方狀態 (Lv.{p.level+2})")
            st.progress(max(0, enemy_hp / enemy_max))

        if st.button("🔴 進攻 / 辯駁", use_container_width=True):
            # --- 戰鬥計算核心 ---
            
            # 1. 玩家攻擊
            player_dmg = 0
            dmg_msg = ""
            if mode == "DUEL":
                base_dmg = random.randint(int(p.atk()*0.8), int(p.atk()*1.2))
                crit = 2 if random.random() < 0.2 else 1
                player_dmg = base_dmg * crit
                dmg_msg = f"🗡️ 揮砍造成 {player_dmg} 傷害！" + ("(暴擊!)" if crit>1 else "")
            else: # DEBATE
                base_dmg = random.randint(int(p.intelligence()*0.8), int(p.intelligence()*1.2))
                player_dmg = base_dmg
                dmg_msg = f"📜 引經據典，造成 {player_dmg} 精神傷害！"

            st.session_state.temp_hp -= player_dmg
            add_log(dmg_msg)

            # 2. 勝利判定
            if st.session_state.temp_hp <= 0:
                exp_gain = 50 * p.level
                money_gain = random.randint(50, 200)
                add_log(f"🏆 勝利！獲得 {money_gain} 錢，{exp_gain} 經驗。")
                p.money += money_gain
                
                if p.gain_exp(exp_gain):
                    add_log(f"🌟 等級提升至 Lv.{p.level}！")
                    st.balloons()
                
                # 掉寶系統 (25% 機率)
                if random.random() < 0.25:
                    drop_item = target["drop"]
                    add_log(f"🎁 {target['name']} 贈予/掉落了：【{drop_item}】！")
                    p.inventory.append(Item(drop_item))
                
                st.session_state.state = "IDLE"
                st.rerun()

            # 3. 敵人反擊
            enemy_dmg = 0
            enemy_act_msg = ""
            
            if mode == "DUEL":
                enemy_atk = target["stats"]["atk"] + (p.level * 2)
                enemy_dmg = max(5, enemy_atk - random.randint(0, 5))
                enemy_act_msg = f"👹 對方武力反擊，你受到 {enemy_dmg} 傷害。"
            else:
                enemy_int = target["stats"]["int"] + (p.level * 2)
                enemy_dmg = max(5, enemy_int - random.randint(0, int(p.intelligence()/2)))
                enemy_act_msg = f"💢 對方口若懸河，你受到 {enemy_dmg} 精神傷害。"

            p.hp -= enemy_dmg
            add_log(enemy_act_msg)

            # 4. 失敗判定
            if p.hp <= 0:
                p.hp = 1
                st.session_state.state = "IDLE"
                add_log("💀 你被擊敗了，狼狽逃回。")
                st.rerun()
            
            st.rerun()

    # 4. 商店狀態
    elif st.session_state.state == "SHOP":
        st.subheader("💰 西域行商")
        st.write("商人：「客官，這些都是戰亂中撿來的寶貝。」")
        
        items_on_sale = ["環首刀", "點鋼槍", "皮甲", "明光鎧"]
        
        for i_name in items_on_sale:
            data = ITEMS_DB[i_name]
            c1, c2, c3 = st.columns([2, 1, 1])
            c1.write(f"**{i_name}** ({data['type']}+{data['val']})")
            c2.write(f"{data['price']} 錢")
            if c3.button("購買", key=f"buy_{i_name}"):
                if p.money >= data['price']:
                    p.money -= data['price']
                    p.inventory.append(Item(i_name))
                    add_log(f"🛒 購買了 {i_name}。")
                    st.rerun()
                else:
                    add_log("❌ 錢不夠！")
        
        if st.button("👋 離開"):
            st.session_state.state = "IDLE"
            st.rerun()

    # 日誌區
    st.markdown("---")
    st.caption("📜 建安紀事")
    for msg in st.session_state.log:
        st.text(msg)

