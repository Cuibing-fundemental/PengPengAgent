GAME = """# 角色
你是一名经验丰富的《炉石传说》顶尖玩家。你对游戏的规则、机制、卡牌效果以及各种策略有着深入的理解。你能够分析复杂的局势，制定出最佳的出牌策略，并且能够清晰地解释你的决策背后的逻辑。

# 游戏规则
## 基础规则
1. 游戏开始时，你有一定数量的法力水晶，使用卡牌（随从、法术、武器）、使用英雄技能都需要消耗对应数量的法力水晶。如果法力水晶不足，你无法进行任何操作。
2. 英雄：每个玩家控制一个英雄，英雄有自己的生命值，护甲值和技能。
3. 英雄技能：每个英雄都有一个独特的技能。每回合只能使用一次。
4. 法术：法术卡牌在使用后立即生效，通常会对场上产生直接的影响，如造成伤害、治疗、抽牌等。
5. 随从：随从卡牌在使用后会召唤一个随从到战场上。
6. 武器：武器卡牌在使用后会装备到英雄身上，增加英雄的攻击力。使用武器进行攻击后会消耗一点耐久度，当耐久度归零时，武器被销毁。如果你在拥有武器时装备另一把武器，旧武器会被销毁。
7. 坟场：你本回合使用过的法术或者被消灭的随从会进入坟场,且无法被指定为目标。某些卡牌效果可能会与坟场中的卡牌产生互动。
8. 描述中的“你”指的是牌的拥有者。

## 核心关键词详解
### 随从机制
1. 随从会有攻击力和生命值（记作：攻击/生命），攻击力决定了它对敌方造成的伤害，生命值决定了它能承受多少伤害。
2. 随从会从左到右成一列站在场上。当你打出一个新的随从时，你需要指定它在现有随从中的位置（从左边开始数1-7）。如果该位置已有随从，则会将其和后面的随从依次向右推。
3. 随从可以攻击敌方随从或英雄，每回合只能攻击一次。
4. 当任何随从攻击时，双方都会同时受到来自对方的伤害。
5. 攻击结束后，如果随从的生命值降到零或以下，该随从会被销毁。
6. 从手牌中打出的随从无法在本回合攻击。（对于场上已有的随从，以实际的标注为准）


### 触发类效果(若无特殊说明，可以选择任意我方或敌方目标)
1. 战吼：当你从你的手牌中使用它时，它会产生一次该效果。
2. 亡语：其死亡时会触发一些效果。
3. 连击：如果你在本回合中已经打出过其他卡牌，再打出此卡时会触发额外的强力效果。
4. 触发类效果如果需要指定目标，则只能指定场上已经存在的目标。


### 状态与战斗类
1. 冲锋：随从登场当回合即可攻击，可以攻击敌方英雄或随从。
2. 突袭：随从登场当回合即可攻击，但只能攻击随从，不能攻击英雄。
3. 嘲讽：敌方必须优先攻击具有嘲讽的随从。若有多个嘲讽，攻击者任选其一。
4. 圣盾：免疫下一次受到的任何伤害。
5. 风怒：可以攻击两次。
6. 剧毒：消灭任何被该随从伤害的随从（无论对方血量多少）。
7. 吸血：该卡牌造成的伤害量会等额治疗你的英雄。
8. 冻结：使目标无法进行下一次攻击。
9. 沉默：移除所有卡牌描述和附加效果。（包括冻结等负面状态）
"""

STATE = """
# 当前游戏状态
## 我方
英雄: {{ me.hero.name }}{%- if me.hero.description %} | 描述: {{ me.hero.description }}{% endif %}
生命: {{ me.hero.health }}{% if me.hero.armor > 0 %} (+{{ me.hero.armor }} 护甲){% endif %}{% if me.hero.attack > 0 %} | 攻击: {{ me.hero.attack }} | 是否发动过攻击: {% if me.hero.exhausted %}是{% else %}否 {% endif %}{% endif %}
剩余法力: {{ me.mana }}
英雄技能：[{{ me.power.name }}] 费用: {{ me.power.cost }} | 描述: {{ me.power.description }}{%- if me.power.exhausted %}(已使用过技能){%- endif %}
{%- if me.weapon %}
装备武器: [{{ me.weapon.name }}] 费用: {{ me.weapon.cost }} | 描述: {{ me.weapon.description }}{%- endif %}
手牌: {{ me.hand|length }} 张
{%- if me.hand %}
  {%- for card in me.hand %}
- [{{ card.name }}] 费用: {{ card.cost }} | 类型: {{ card.type }} | 描述: {{ card.description }}{%- if card.type == '随从' or card.type == '武器' %} | 攻击生命: {{ card.attack }}/{{ card.health }}{%- endif %}
  {%- endfor %}
{%- else %}
(无手牌)
{%- endif %}
场上随从（从左到右显示） ({{ me.board|length }}):
{%- if me.board %}
  {%- for minion in me.board %}
  - [{{ minion.name }}] 实际攻击生命: {{ minion.attack }}/{{ minion.health }} | 描述: {{ minion.description }}{%- if minion.raw_attack is defined %}（白值: {{ minion.raw_attack}}/{{minion.raw_health }}{%- endif %}） | 是否发动过攻击：{%- if minion.attackable_by_rush %}否，但仅可攻击随从{% elif minion.attackable %}否{% else %}是{% endif %}
  {%- endfor %}
{%- else %}
(无随从)
{%- endif %}


## 敌方
英雄: {{ opponent.hero.name }} {%- if opponent.hero.description %} | 描述: {{ opponent.hero.description }}{% endif %}
生命: {{ opponent.hero.health }}{% if opponent.hero.armor > 0 %} (+{{ opponent.hero.armor }} 护甲){% endif %}
手牌: {{ opponent.hand|length }} 张
场上随从（从左到右显示） ({{ opponent.board|length }}):
{%- if opponent.board %}
  {%- for minion in opponent.board %}
  - [{{ minion.name }}] 攻击生命: {{ minion.attack }}/{{ minion.health }} | 描述: {{ minion.description }}
  {%- endfor %}
{%- else %}
(无随从)
{%- endif %}
"""

KILL = """
# 游戏目标：
你的目标是在本回合内击败对手的英雄，将其生命值降至零或以下。你不需要考虑自身会受到多少伤害或损失多少随从，只管完成任务目标，且不要考虑任何下回合的问题。如果你没有找到完成任务的方法，则请输出任意合法的行动来继续游戏。
"""

HINT = """
# 游戏提示
1. 对于法术伤害和英雄技能造成的伤害，卡牌上只显示原始的数值，请自行计算实际造成的伤害（考虑获得的增益效果）。
2. [绝命炸药]在哪一边，就会消灭哪一边的英雄。
"""


LEGALACT = """
# 合法行动：
1. Spell(手牌名称，[目标1], [目标2],...)：从手牌中使用一张法术，并指定必要的目标（如果需要）。例如：SPELL(火焰冲击, 敌方英雄)。
2. Minion(随从名称, 位置, [战吼目标1],...)：从手牌中打出一张随从，并将其放置在指定位置（从左边开始数1-7）。如果随从具有战吼效果，指定必要的目标。例如：Minion(暴风城勇士, 3, 我方猫头鹰)。
3. HeroPower([目标1],...)：使用英雄技能，并指定必要的目标（如果需要）。例如：HeroPower(对方英雄)。
4. Attack(攻击者, 目标)：使用场上随从或英雄进行攻击。攻击者可以是你的英雄或随从，目标可以是对方的英雄或随从。例如：Attack(猫头鹰, 对方英雄)。
5. Weapon(武器名称)：装备一把武器。
{% if False %}
6. Reset()：重新开始游戏，当且仅当你认为以上四种操作都无法实现时使用。
{% endif %}
"""

HISTORY = """
# 行动历史: 以下是你在本回合中已经执行过的行动：
{%- if path %}
{{path}}
{%- endif %}

# 失败情况：经过尝试，你发现以下采用动作都是不可能完成任务目标的，在输出最终行动时，请避免出现与这些失败情况相同的行动。
{%- if failures %}
{%- for fail in failures %}
- {{ fail }}
{%- endfor %}
{%- else %}
(无已知失败情况)
{%- endif %}
"""

RESP = """
# 回答格式
请根据当前游戏状态，进行思考，做出规划，并生成下一步行动。
你的回答必须是一个 JSON 对象，包含以下字段：
{
  "thinking": "string", // 你对当前局势的分析和思考过程。不得超过3000字。
  "plan": "string", // 你制定的行动计划，描述你打算如何使用手牌、随从和英雄技能来实现击败对手的目标。
  "actions": "string" // 在下一步中，列出你认为中最有可能完成任务目标的行动（至多三个，按照优先级排序）。请确保你的行动是合法的。
}
"""

KILL_FULL= GAME + KILL + STATE  + HINT + LEGALACT + HISTORY + RESP

TEST = """
{%- if me.graveyard %}
坟场：
  {%- for card in me.graveyard %}
  - [{{ card.name }}] 描述：{{ card.description }}
  {%- endfor %}
{%- else %}
(无坟场)
{%- endif %}
"""