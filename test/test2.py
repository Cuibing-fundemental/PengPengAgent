import os
import re
from datetime import datetime
from hsplayer.prompts import *
import jinja2

log_path = "/mnt/e/game/hearthstone/logs"
folders = [f for f in os.listdir(log_path) if os.path.isdir(os.path.join(log_path, f)) and f.startswith("Hearthstone_")]

if not folders:
    print("未找到任何匹配的文件夹")
else:
    # 定义一个函数来提取时间
    def get_folder_time(folder_name):
        # 使用正则提取 YYYY_MM_DD_HH_MM_SS 部分
        # 格式: Hearthstone_2026_03_15_16_54_45
        match = re.search(r"Hearthstone_(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})", folder_name)
        if match:
            time_str = match.group(1)
            # 将字符串转换为 datetime 对象
            return datetime.strptime(time_str, "%Y_%m_%d_%H_%M_%S")
        return datetime.min # 如果格式不对，给一个最小时间

    # 根据提取的时间进行排序，reverse=True 表示降序（最新的在前面）
    latest_folder = max(folders, key=get_folder_time)
    
    latest_path = os.path.join(log_path, latest_folder)
    latest_path = os.path.join(latest_path, "Power.log")
    # print(f"最新的文件夹是: {latest_folder}")
    # print(f"完整路径: {latest_path}")


from hslog import LogParser
from hslog.export import EntityTreeExporter
from hearthstone.enums import CardType, Zone, GameTag
from hearthstone.cardxml import load

from hsplayer.models import Player, WorldState
db, _ = load(locale="zhCN")

parser = LogParser()

with open(latest_path, encoding="utf-8") as f:
    parser.read(f)

packet_tree = parser.games[-1]

exporter = EntityTreeExporter(packet_tree)
exporter.export()
game = exporter.game
# player = Player(game.players[0], db)

# print(game.players[0].tags)
# print(game.tags)
game_init = False
state = WorldState(game, db)
if game_init :
    state.players[0].used_mana = 0


state_str = jinja2.Template(KILL_FULL).render(state.export())

print(state.export())
# print(state_str)
# print(state.players[0].board[0].export())