from hearthstone import entities as hse
from hearthstone.enums import Zone, GameTag, CardType, Race
from typing import Optional, List, Dict, Any
import re
  
CARD_TYPE_DISPLAY_NAMES = {
    CardType.HERO: "英雄",
    CardType.MINION: "随从",
    CardType.SPELL: "法术",
    CardType.WEAPON: "武器",
    CardType.HERO_POWER: "英雄技能",
    CardType.INVALID: "未知类型"
}

CARD_RACE_NAMES = {
Race.INVALID: "无效",
Race.BLOODELF: "血精灵",
Race.DRAENEI: "德莱尼",
Race.DWARF: "矮人",
Race.GNOME: "侏儒",
Race.GOBLIN: "地精",
Race.HUMAN: "人类",
Race.NIGHTELF: "暗夜精灵",
Race.ORC: "兽人",
Race.TAUREN: "牛头人",
Race.TROLL: "巨魔",
Race.UNDEAD: "亡灵",
Race.WORGEN: "狼人",
Race.GOBLIN2: "地精",
Race.MURLOC: "鱼人",
Race.DEMON: "恶魔",
Race.SCOURGE: "天灾",
Race.MECHANICAL: "机械",
Race.ELEMENTAL: "元素",
Race.OGRE: "食人魔",
Race.BEAST: "野兽",
Race.TOTEM: "图腾",
Race.NERUBIAN: "蛛魔",
Race.PIRATE: "海盗",
Race.DRAGON: "龙",
Race.BLANK: "无",
Race.ALL: "所有",
Race.EGG: "蛋",
Race.QUILBOAR: "野猪人",
Race.CENTAUR: "半人马",
Race.FURBOLG: "熊怪",
Race.HIGHELF: "高等精灵",
Race.TREANT: "树人",
Race.OWLKIN: "枭兽",
Race.HALFORC: "半兽人",
Race.LOCK: "锁",
Race.NAGA: "纳迦",
Race.OLDGOD: "上古之神",
Race.PANDAREN: "熊猫人",
Race.GRONN: "戈隆",
Race.CELESTIAL: "天神",
Race.GNOLL: "豺狼人",
Race.GOLEM: "魔像",
Race.HARPY: "鹰身人",
Race.VULPERA: "狐人"
}


class Card:
    def __init__(self, card:hse.Card, db):
        self.id = card.id
        self.alias = card.card_id
        data = db.get(self.alias, None)
        self.name = getattr(data, 'name', '未知卡牌') if data else "未知卡牌"
        self.description = getattr(data, 'description', '未知描述') if data else "未知描述"

        type = CardType(getattr(data, 'type',CardType.INVALID))
        self.type = CARD_TYPE_DISPLAY_NAMES.get(type,type.name)
        self.cost = card.tags.get(GameTag.COST, 0)
        self.exhausted = card.tags.get(GameTag.EXHAUSTED, 0) == 1

        self.raw_health = getattr(data, 'health', None) if data else None
        self.raw_attack = getattr(data, 'atk', None) if data else None

        self.race = getattr(data, 'race', None) if data else None
        if self.race is not None:
            self.race = CARD_RACE_NAMES.get(self.race, self.race)

        pattern = r'<b>|</b>|\$'
        self.description = re.sub(pattern, '', self.description)
        self.description = re.sub(r"\n", ' ', self.description)

        

    def export(self) -> dict:
        dictionary = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "cost": self.cost,
            "exhausted": self.exhausted
        }
        if self.raw_attack is not None and self.raw_health !=0:
            dictionary["raw_attack"] = self.raw_attack
            dictionary["raw_health"] = self.raw_health
        if self.race !=  CARD_RACE_NAMES.get(Race.INVALID, "无效"):
            dictionary["description"] += f" ({self.race})"
        return dictionary

class Minion(Card):
    def __init__(self, minion:hse.Card, db):
        super().__init__(minion, db)
        self.attack = minion.tags.get(GameTag.ATK, 0)
        self.health = minion.tags.get(GameTag.HEALTH, 0) - minion.tags.get(GameTag.DAMAGE, 0)
              
        self.exhausted = minion.tags.get(GameTag.EXHAUSTED, 0) == 1
        self.just_played = minion.tags.get(GameTag.JUST_PLAYED, 1) == 1
        self.charge = minion.tags.get(GameTag.CHARGE, 0) == 1
        self.special_charge = minion.tags.get(GameTag.NON_KEYWORD_CHARGE, 0) == 1
        self.attackable_by_rush = minion.tags.get(GameTag.ATTACKABLE_BY_RUSH, 0) == 1
        self.frozen = minion.tags.get(GameTag.FROZEN, 0) == 1
        self.attackable = not self.exhausted 
        self.silence = minion.tags.get(GameTag.SILENCED, 0) == 1

    def export(self):
        data = super().export()
        data.update({
            "attack": self.attack,
            "health": self.health,
            "attackable": self.attackable,
            "attackable_by_rush": self.attackable_by_rush
            })
        if self.frozen:
            data["description"] += " (已被冻结)"
        if self.silence:
            data["description"] += " (已被沉默)"
        return data

class Hero(Minion):
    def __init__(self, hero:hse.Card, db):
        super().__init__(hero, db)
        self.max_health = hero.tags.get(GameTag.HEALTH, 0)
        self.health = self.max_health-hero.tags.get(GameTag.DAMAGE, 0)
        self.armor = hero.tags.get(GameTag.ARMOR, 0)
        self.cost = hero.tags.get(GameTag.COST, 0)
    
    def export(self):
        data = super().export()
        data.update({
            "health": self.health,
            "armor": self.armor
        })
        return data

class Weapon(Card):
    def __init__(self, weapon:hse.Card, db):
        super().__init__(weapon, db)
        self.attack = weapon.tags.get(GameTag.ATK, 0)
        self.health = weapon.tags.get(GameTag.DURABILITY, 0)
    def export(self):
        data = super().export()
        data.update({
            "attack": self.attack,
            "health": self.health
        })
        return data
    
class Player:
    hand : List[Card]
    board : List[Minion]
    weapon : Optional[Card]
    hero : Optional[Hero]
    power: Optional[Card]

    def __init__(self, player: hse.Player,db):
        self.player_id = player.id
        self.hand = []
        self.board = []
        self.graveyard = []
        self.power = None
        self.weapon = None

        self.hero = Hero(player.hero, db)

        hand_cards = list(player.in_zone(Zone.HAND))
        for card in hand_cards:
            if card.type == CardType.MINION:
                self.hand.append(Minion(card, db))
            else:
                self.hand.append(Card(card, db))

        board_minions = list(player.in_zone(Zone.PLAY))
        board_minions.sort(key=lambda c: c.tags.get(GameTag.ZONE_POSITION, 0))
        for minion in board_minions:
            if minion.type == CardType.MINION:
                self.board.append(Minion(minion, db))
        self.max_mana = player.tags.get(GameTag.RESOURCES, 0)
        self.used_mana = player.tags.get(GameTag.RESOURCES_USED, 0)
        self.temp_mana = player.tags.get(GameTag.TEMP_RESOURCES, 0)

        grave = list(player.in_zone(Zone.GRAVEYARD))
        for card in grave:
            if card.tags.get(GameTag.RARITY, None) is None:
                continue
            if card.type == CardType.MINION:
                self.graveyard.append(Minion(card, db))
            else:
                self.graveyard.append(Card(card, db))
        
        
    def add_hand(self, card:hse.Card):
        pass

    def export(self):
        return {
            "hero": self.hero.export() if self.hero else None,
            "mana": self.max_mana-self.used_mana+self.temp_mana,
            "max_mana": self.max_mana,
            "hand": [card.export() for card in self.hand],
            "board": [minion.export() for minion in self.board],
            "weapon": self.weapon.export() if self.weapon else None,
            "graveyard": [card.export() for card in self.graveyard],
            "power": self.power.export() if self.power else None,
        }

class WorldState:
    def __init__(self, game:hse.Game, db):
        self.players: List[Player] = [
            Player(game.players[0], db),
            Player(game.players[1], db)
        ]

        for e in game.entities:
            if e.type == CardType.HERO_POWER:
                controller = e.tags.get(GameTag.CONTROLLER, None)-1
                if controller is not None and 0 <= controller < len(self.players):
                    self.players[controller].power = Card(e, db)
            if e.type == CardType.WEAPON:
                controller = e.tags.get(GameTag.CONTROLLER, None)-1
                if controller is not None and 0 <= controller < len(self.players):
                    self.players[controller].weapon = Weapon(e, db)

    @property
    def me(self) -> Player:
        return self.players[0]
    
    @property
    def opponent(self) -> Player:
        return self.players[1]
    
    def export(self):
        return {
            "me": self.me.export(),
            "opponent": self.opponent.export()
        }
    
class TreeNode:
    def __init__(self, action: str, id):
        self.id = id
        self.action = action
        self.valid = True
        self.children: List['TreeNode'] = []
        self.parent: Optional['TreeNode'] = None  

    def __repr__(self):
        return f"TreeNode(action='{self.action}', children={len(self.children)})"

class Tree:
    def __init__(self):
        self.root = TreeNode("[begin]", id=0)
        self.count = 1
        self.map = {0: self.root}

    def add_node(self, parent: TreeNode, action: str) -> TreeNode:
        """在指定父节点下添加一个新节点"""
        for child in parent.children:
            if not child.valid and child.action == action:
                child.valid = True
                return child
        new_node = TreeNode(action, id=self.count)
        self.map[self.count] = new_node
        self.count += 1
        parent.children.append(new_node)
        new_node.parent = parent
        return new_node
    
    def search_id(self, id) -> Optional[TreeNode]:
        """根据 ID 查找节点"""
        return self.map.get(id, None)
    
    def get_path(self, node: TreeNode) -> List[str]:
        """获取从根节点到指定节点的路径（行动序列）"""
        path = []
        current = node
        while current is not None:
            path.append(current.action)
            current = current.parent
        return list(reversed(path))
    
    def export(self,valid = True):
        """导出树的结构为嵌套字典"""
        def export_node(node: TreeNode):
            return {
                "id": node.id,
                "action": node.action,
                "children": [export_node(child) for child in node.children if child.valid or not valid]
            }
        return export_node(self.root)