from validation import validate_leg_group
from reconfiguration import reconfigure_leg_group
from utils import distance

def get_relative_positions(skeleton):
    positions = {}
    for part in skeleton:
        positions[part["name"]] = part["loc"]
    return positions

def convert_human_to_animal(input_data):
    height = input_data.get('height', 0)
    skeleton = input_data.get('skeleton', [])

    original_skel = skeleton.copy()
    positions = get_relative_positions(skeleton)

    part_mapping = {
        'hip': 'hip',
        'torso': 'torso',
        'neck': 'neck',
        'right_hip': 'right_hip_b',
        'right_knee': 'right_knee_b',
        'right_foot': 'right_foot_b',
        'left_hip': 'left_hip_b',
        'left_knee': 'left_knee_b',
        'left_foot': 'left_foot_b',
        'right_shoulder': 'right_hip_f',
        'right_elbow': 'right_knee_f',
        'right_hand': 'right_foot_f',
        'left_shoulder': 'left_hip_f',
        'left_elbow': 'left_knee_f',
        'left_hand': 'left_foot_f'
    }

    parent_mapping = {
        'right_hip_f': 'root',
        'left_hip_f': 'root',
        'right_hip_b': 'root',
        'left_hip_b': 'root'
    }

    included_parts = set(part_mapping.values())
    included_parts.add('root')

    new_skeleton = []

    torso_pos = positions.get('torso', [0, 0])
    hip_pos = positions.get('hip', [0, 0])

    forward_vector = [torso_pos[0] - hip_pos[0], torso_pos[1] - hip_pos[1]]
    neck_pos = [
        torso_pos[0] - forward_vector[0] * 0.3,
        torso_pos[1] - forward_vector[1] * 0.3
    ]

    for part in skeleton:
        name = part.get('name', '')
        if name not in part_mapping:
            continue

        new_name = part_mapping[name]
        if new_name not in included_parts:
            continue

        loc = part.get('loc', [])
        parent = part.get('parent', None)

        if new_name in parent_mapping:
            new_parent = parent_mapping[new_name]
        elif parent in part_mapping:
            new_parent = part_mapping[parent]
        else:
            new_parent = parent

        if new_name == 'neck':
            loc = neck_pos

        loc_copy = list(loc) if loc else []
        new_part = {
            'loc': loc_copy,
            'name': new_name,
            'parent': new_parent
        }
        new_skeleton.append(new_part)

    if 'root' not in [part.get('name') for part in new_skeleton]:
        hip_loc = positions.get('hip', [0, 0])
        new_skeleton.insert(0, {
            'loc': list(hip_loc),
            'name': 'root',
            'parent': None
        })

    leg_groups = [
        ("right_hip_f", "right_knee_f", "right_foot_f"),
        ("left_hip_f", "left_knee_f", "left_foot_f"),
        ("right_hip_b", "right_knee_b", "right_foot_b"),
        ("left_hip_b", "left_knee_b", "left_foot_b")
    ]

    valid_leg_refs = {}
    for group in leg_groups:
        hip_name, knee_name, foot_name = group
        if validate_leg_group(new_skeleton, hip_name, knee_name, foot_name):
            valid_leg_refs[hip_name] = (
                next(part['loc'] for part in new_skeleton if part['name'] == hip_name),
                next(part['loc'] for part in new_skeleton if part['name'] == knee_name),
                next(part['loc'] for part in new_skeleton if part['name'] == foot_name)
            )

    for group in leg_groups:
        hip_name, knee_name, foot_name = group
        if not validate_leg_group(new_skeleton, hip_name, knee_name, foot_name):
            reference_leg = None
            if "hip_f" in hip_name:
                other_side = "left_hip_f" if hip_name == "right_hip_f" else "right_hip_f"
                if other_side in valid_leg_refs:
                    reference_leg = valid_leg_refs[other_side]
            elif "hip_b" in hip_name:
                other_side = "left_hip_b" if hip_name == "right_hip_b" else "right_hip_b"
                if other_side in valid_leg_refs:
                    reference_leg = valid_leg_refs[other_side]

            new_skeleton = reconfigure_leg_group(new_skeleton, original_skel, hip_name, knee_name, foot_name, reference_leg, height)

    return {
        'height': height,
        'skeleton': new_skeleton,
        'width': input_data.get('width', 0)
    }
