import json
import os

class StateManager:
    def __init__(self, config_path='config.json', state_path='state.json'):
        self.config_path = config_path
        self.state_path = state_path

    def load_config(self):
        if not os.path.exists(self.config_path):
            return {"target_funds": []}
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_state(self):
        if not os.path.exists(self.state_path):
            return {"fund_states": []}
        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_state(self, state):
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
