# 這是純數據檔案，不包含運算邏輯

# --- 物品資料庫 ---
ITEMS_DB = {
    # 階級 I
    "粗布衣": {"slot": "body", "type": "hp", "val": 10, "price": 10},
    "麻布長衫": {"slot": "body", "type": "hp", "val": 15, "price": 20},
    "木棍": {"slot": "weapon", "type": "atk", "val": 5, "price": 10},
    # ... (在此處貼上你那 100 多個裝備) ...
    "傳國玉璽": {"slot": "artifact", "type": "int", "val": 100, "price": 99999, "desc": "受命於天，既壽永昌。"},
}

# --- 武將資料庫 ---
GENERALS_DB = [
    {"name": "關羽", "loc": "荊州", "type": "war", "stats": {"hp": 300, "atk": 98, "int": 75}, "drop": "青龍偃月刀", 
     "dialogs": ["吾觀顏良文醜，如插標賣首耳！"]},
    # ... (在此處貼上你的武將列表) ...
]
