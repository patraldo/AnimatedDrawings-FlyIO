from utils import distance, validate_y_within_bounds

def candidate_search_for_joint(original_skel, expected_position, exclude_names, tolerance=30):
    """
    Search original_skel for the joint closest to expected_position
    excluding joints with names in exclude_names.
    """
    best_candidate = None
    best_distance = float('inf')
    for part in original_skel:
        part_name = part.get('name')
        if part_name in exclude_names:
            continue
        loc = part.get('loc', [])
        if not loc:
            continue
        d = distance(loc, expected_position)
        if d < best_distance and d < tolerance:
            best_distance = d
            best_candidate = part
    return best_candidate

def reconfigure_leg_group(new_skel, original_skel, hip_name, knee_name, foot_name, reference_leg=None, height=None):
    parts = {part['name']: part for part in new_skel}
    if hip_name not in parts:
        return new_skel
    hip_loc = parts[hip_name]['loc']

    # Reconfigure Knee
    if reference_leg:
        ref_knee_offset = [reference_leg[1][0] - reference_leg[0][0],
                           reference_leg[1][1] - reference_leg[0][1]]
        expected_knee = [hip_loc[0] + ref_knee_offset[0], hip_loc[1] + ref_knee_offset[1]]
    else:
        expected_knee = [hip_loc[0], hip_loc[1] + 20]

    expected_knee = validate_y_within_bounds(expected_knee, height)
    candidate_knee = candidate_search_for_joint(original_skel, expected_knee, exclude_names={hip_name, foot_name})
    if candidate_knee:
        new_knee_loc = candidate_knee.get('loc', expected_knee)
        new_knee_loc = validate_y_within_bounds(new_knee_loc, height)
        found = False
        for part in new_skel:
            if part['name'] == knee_name:
                part['loc'] = new_knee_loc
                found = True
                break
        if not found:
            new_skel.append({'loc': new_knee_loc, 'name': knee_name, 'parent': hip_name})
    else:
        new_knee_loc = expected_knee
        for part in new_skel:
            if part['name'] == knee_name:
                part['loc'] = new_knee_loc

    # Reconfigure Foot
    if reference_leg:
        ref_foot_offset = [reference_leg[2][0] - reference_leg[1][0],
                           reference_leg[2][1] - reference_leg[1][1]]
        expected_foot = [new_knee_loc[0] + ref_foot_offset[0], new_knee_loc[1] + ref_foot_offset[1]]
    else:
        expected_foot = [new_knee_loc[0], new_knee_loc[1] + 20]

    expected_foot = validate_y_within_bounds(expected_foot, height)
    candidate_foot = candidate_search_for_joint(original_skel, expected_foot, exclude_names={hip_name, knee_name})
    if candidate_foot:
        new_foot_loc = candidate_foot.get('loc', expected_foot)
        new_foot_loc = validate_y_within_bounds(new_foot_loc, height)
        updated = False
        for part in new_skel:
            if part['name'] == foot_name:
                part['loc'] = new_foot_loc
                updated = True
                break
        if not updated:
            new_skel.append({'loc': new_foot_loc, 'name': foot_name, 'parent': knee_name})
    else:
        for part in new_skel:
            if part['name'] == foot_name:
                part['loc'] = expected_foot
                break

    print(f"Reconfigured leg group: {hip_name}, {knee_name}, {foot_name} using candidate search.")
    return new_skel
