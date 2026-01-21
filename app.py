import streamlit as st
import random
import time

# --- 1. 定義實體類別：俠客與妖魔 ---
class Cultivator:
    def __init__(self, name, hp, max_hp, mp, max_mp, attack):
        self.name = name
        self.hp = hp            # 體力 (Health Point)
        self.max_hp = max_hp
        self.mp = mp            # 靈力 (Mana/Qi)
        self.max_mp = max_mp
        self.attack = attack    # 基礎攻擊力
        self.exp = 0            # 修為 (Experience)
        self.level = 1          # 境界 (Level)

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
        # 科學公式：升級閾值 = 當前等級 * 100
        threshold = self.level * 100
        if self.exp >= threshold:
            self.exp -= threshold
            self.level += 1
            self.max_hp += 20
            self.max_mp += 10
            self.attack += 5
            self.hp = self.max_hp # 升級回滿狀態
            self.mp = self.max_mp
            return True # 回傳升級訊號
        return False

# --- 2. 系統初始化 ---
st.set_page_config(page_title="軒轅仙俠錄", page_icon="🗡️")
st.title("🗡️ 軒轅仙俠錄 (Xianxia RPG)")

if 'player' not in st.session_state:
    # 初始屬性：體力100, 靈力50, 攻擊10
    st.session_state.player = Cultivator("少俠", 100, 100, 50, 50, 10)
    st.session_state.spirit_stones = 0  # 靈石 (原金幣)
    st.session_state.log = ["【系統】你踏入了這片上古神州大地..."]
    st.session_state.enemy = None
    st.session_state.in_combat = False

def add_log(message):
    st.session_state.log.insert(0, message) # 新訊息在最上方
    if len(st.session_state.log) > 8:
        st.session_state.log.pop()

# --- 3. 核心邏輯 ---

def explore():
    """遊歷江湖邏輯"""
    event = random.randint(1, 100)
    
    if event <= 30: # 30% 機遇
        stones = random.randint(5, 20)
        st.session_state.spirit_stones += stones
        add_log(f"💰 偶遇前人遺塚，拾得 {stones} 顆靈石。")
        # 恢復少量靈力
        recover = random.randint(5, 10)
        p = st.session_state.player
        p.mp = min(p.mp + recover, p.max_mp)
        
    elif event <= 50: # 20% 平安無事
        add_log("🍃 清風拂過，四周靈氣祥和，你運功調息。")
        
    else: # 50% 遭遇妖魔
        level = st.session_state.player.level
        # 動態難度：怪物強度隨玩家等級提升
        scaling = level * 5
        enemy_pool = [
            {"name": "孤魂野鬼", "hp": 30 + scaling, "atk": 5 + level},
            {"name": "黑风寨主", "hp": 60 + scaling, "atk": 10 + level},
            {"name": "千年樹妖", "hp": 100 + scaling, "atk": 15 + level}
        ]
        data = random.choice(enemy_pool)
        # 怪物不需要 MP，簡化處理
        st.session_state.enemy = Cultivator(data["name"], data["hp"], data["hp"], 0, 0, data["atk"])
        st.session_state.in_combat = True
        add_log(f"⚠️ 殺氣逼人！前方出現了【{st.session_state.enemy.name}】！")

def combat_round(skill_name):
    """戰鬥回合邏輯"""
    player = st.session_state.player
    enemy = st.session_state.enemy
    
    # --- 玩家回合 ---
    damage = 0
    cost = 0
    
    if skill_name == "普攻":
        damage = random.randint(player.attack, player.attack + 5)
        add_log(f"⚔️ 你使出基礎劍招，造成 {damage} 點傷害。")
        
    elif skill_name == "御劍術":
        cost = 10
        if player.consume_mp(cost):
            damage = random.randint(player.attack * 2, player.attack * 3)
            add_log(f"⚡ [御劍術] 劍氣縱橫！造成 {damage} 點暴擊！")
        else:
            add_log("🚫 靈力不足，無法施展御劍術！倉促間只能防禦。")
            
    elif skill_name == "軒轅一擊":
        cost = 30
        if player.consume_mp(cost):
            damage = random.randint(player.attack * 4, player.attack * 6)
            add_log(f"🔥 [軒轅一擊] 天地變色！造成 {damage} 點毀滅傷害！")
        else:
             add_log("🚫 靈力不足，無法施展奧義！")

    if damage > 0:
        enemy.take_damage(damage)

    # --- 判定勝利 ---
    if not enemy.is_alive():
        base_exp = 20 * player.level
        bonus_stones = random.randint(10, 50)
        
        st.session_state.spirit_stones += bonus_stones
        is_levelup = player.gain_exp(base_exp)
        
        add_log(f"🏆 勝負已分！獲得 {bonus_stones} 靈石，修為增加 {base_exp}。")
        if is_levelup:
            add_log(f"🌟 【境界突破】！你達到了 {player.level} 級！屬性大幅提升！")
            st.balloons() # 科學獎勵機制：視覺刺激
            
        st.session_state.enemy = None
        st.session_state.in_combat = False
        return

    # --- 怪物回合 ---
    enemy_dmg = random.randint(enemy.attack - 2, enemy.attack + 5)
    player.take_damage(enemy_dmg)
    add_log(f"👹 {enemy.name} 發起反撲，你受到 {enemy_dmg} 點傷害。")

    if not player.is_alive():
        add_log("💀 眼前一黑，你的修仙之路到此為止...")

def meditation():
    """修煉/恢復"""
    cost = 50
    if st.session_state.spirit_stones >= cost:
        st.session_state.spirit_stones -= cost
        p = st.session_state.player
        p.hp = p.max_hp
        p.mp = p.max_mp
        add_log("🧘 消耗靈石閉關修煉，狀態全滿！")
    else:
        add_log("❌ 靈石不足 (需 50)，無法購買丹藥修煉。")

def restart():
    st.session_state.clear()
    st.rerun()

# --- 4. 介面渲染 (UI Rendering) ---

# 狀態欄 (HUD)
p = st.session_state.player
c1, c2, c3, c4 = st.columns(4)
c1.metric("境界 (Level)", f"Lv.{p.level}")
c2.metric("體力 (HP)", f"{p.hp}/{p.max_hp}")
c3.metric("靈力 (MP)", f"{p.mp}/{p.max_mp}")
c4.metric("靈石", st.session_state.spirit_stones)

# 進度條
st.caption("體力")
st.progress(p.hp / p.max_hp)
st.caption("靈力")
st.progress(p.mp / p.max_mp)
st.caption(f"修為進度 ({p.exp}/{p.level*100})")
st.progress(min(p.exp / (p.level*100), 1.0))

st.markdown("---")

# 戰鬥/探索區域
if p.is_alive():
    if st.session_state.in_combat:
        st.subheader(f"⚔️ 遭遇強敵：{st.session_state.enemy.name}")
        st.write(f"敵方體力：{st.session_state.enemy.hp}")
        
        # 戰鬥選單
        col_a, col_b, col_c = st.columns(3)
        if col_a.button("普通攻擊"):
            combat_round("普攻")
            st.rerun()
        if col_b.button("御劍術 (消耗10靈力)"):
            combat_round("御劍術")
            st.rerun()
        if col_c.button("軒轅一擊 (消耗30靈力)"):
            combat_round("軒轅一擊")
            st.rerun()
            
    else:
        st.subheader("🗺️ 神州大地")
        c1, c2 = st.columns(2)
        if c1.button("🌲 遊歷江湖", use_container_width=True):
            explore()
            st.rerun()
        if c2.button("🧘 閉關修煉 (50靈石)", use_container_width=True):
            meditation()
            st.rerun()
else:
    st.error("勝敗乃兵家常事，大俠請重新來過。")
    if st.button("🔄 輪迴轉世"):
        restart()

st.markdown("---")
st.subheader("📜 江湖傳聞 (日誌)")
for msg in st.session_state.log:
    st.text(msg)
