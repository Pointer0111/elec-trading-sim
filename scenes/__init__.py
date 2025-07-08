from . import scene1

SCENE_TITLES = {
    1: "Single-price Clearing Market",
    # 2: "Pay-as-Bid Market",
    # ... add more as needed
}

def get_default_params(scene_id):
    if scene_id == 1:
        return scene1.default_params.copy()
    # elif scene_id == 2:
    #     return scene2.default_params.copy()
    # ...
    return {}

def get_scene_module(scene_id):
    if scene_id == 1:
        return scene1
    # elif scene_id == 2:
    #     return scene2
    # ...
    return None 