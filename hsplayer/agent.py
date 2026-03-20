from .models import WorldState,TreeNode,Tree
from hearthstone.cardxml import load
from .log_path import get_latest_log_path, parse_log
from .apis import generate
from .prompts import *
import jinja2
import json

from hsplayer import log_path

class Agent:
    world_state : WorldState

    def __init__(self, model: str = "local", log_path=None):
        self.db = load(locale="zhCN")[0]
        self.log_path = get_latest_log_path() if log_path is None else log_path
        self.game = parse_log(self.log_path)
        self.world_state = WorldState(self.game, self.db)
        self.memory = Memory()
        self.action_tree = Tree()
        self.current_node = self.action_tree.root
        self.response = None
        self.next_actions = {}
        self.model = model

    def reinit(self):
        self.game = parse_log(self.log_path)
        self.world_state = WorldState(self.game, self.db)

    def set_world_state(self, game):
        self.world_state = WorldState(game, self.db)

    def get_world_state(self):
        return self.world_state.export()
    
    def get_prompt(self):
        state = self.get_world_state()
        prompt = jinja2.Template(KILL_FULL).render(
            me = state["me"],
            opponent = state["opponent"],
            failures = self.failures(),
            path = self.get_action_history(self.current_node)
        )
        return prompt

    def generate_response(self, prompt, stream_output = False):
        self.next_actions = {}
        response_stream = generate(prompt, model=self.model, json_mode=True)
        full_response = ""            
        for chunk in response_stream:
            full_response += chunk
            yield chunk
        self.process_response(full_response)
        
    def process_response(self, response):
        try:
            self.response = json.loads(response)
            print("解析后的 JSON 对象:", self.response)
        except json.JSONDecodeError:
            print("无法解析响应为 JSON:", response)

        for action in self.response.get("actions", ""):
            node = self.add_action(self.current_node.id, action.strip())
            self.next_actions[node.id] = action.strip()

        # current_changed = False
        # new_node = self.current_node
        # for action in self.response.get("actions", ""):
        #     node = self.add_action(self.current_node.id, action.strip())
        #     if not current_changed:
        #         new_node = node
        #         current_changed = True
        # self.current_node = new_node

    def add_action(self, parent_id: int, action: str) -> TreeNode:
        parent_node = self.action_tree.search_id(parent_id)
        if parent_node is None:
            raise ValueError(f"未找到 ID 为 {parent_id} 的父节点")
        node = self.action_tree.add_node(parent_node, action)
        print(f"已添加行动: '{action}' 到父节点 ID {parent_id}")
        return node

    def delete_action(self, node_id: int):
        node = self.action_tree.search_id(node_id)
        if node is None:
            raise ValueError(f"未找到 ID 为 {node_id} 的节点")
        node.valid = False

    def set_action(self, node_id: int):
        node = self.action_tree.search_id(node_id)
        if node is None:
            raise ValueError(f"未找到 ID 为 {node_id} 的节点")
        self.current_node = node

    def get_action_history(self, node: TreeNode) -> str:
        return ",".join(self.action_tree.get_path(node))
    
    def export_action_tree(self, valid = True):
        return self.action_tree.export(valid)

    def failures(self):
        return [child.action for child in self.current_node.children if not child.valid]

class Memory():
    def __init__(self):
        self.acts = []