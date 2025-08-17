from utils import distance, angle_between

def validate_leg_group(new_skel, hip_name, knee_name, foot_name, 
                       base_ratio_threshold=2.0, base_angle_threshold=150, 
                       similarity_tolerance=0.2, reference_leg=None):
    """
    Validate a leg group by checking ratio, angle, vertical ordering,
    and optionally similarity to a reference leg.
    """
    parts = {part['name']: part for part in new_skel}
    if hip_name not in parts or knee_name not in parts or foot_name not in parts:
        return False

    hip_loc = parts[hip_name]['loc']
    knee_loc = parts[knee_name]['loc']
    foot_loc = parts[foot_name]['loc']

    d_hip_knee = distance(hip_loc, knee_loc)
    d_knee_foot = distance(knee_loc, foot_loc)

    if d_hip_knee == 0:
        return False

    ratio = d_knee_foot / d_hip_knee
    knee_angle = angle_between(hip_loc, knee_loc, foot_loc)

    if "hip_f" in hip_name:
        ratio_threshold = 1.5
        angle_threshold = 160
    else:
        ratio_threshold = base_ratio_threshold
        angle_threshold = base_angle_threshold

    if ratio > ratio_threshold or knee_angle < angle_threshold:
        return False

    if knee_loc[1] < hip_loc[1] or foot_loc[1] < knee_loc[1]:
        return False

    if reference_leg is not None:
        ref_hip, ref_knee, ref_foot = reference_leg
        ref_d_hip_knee = distance(ref_hip, ref_knee)
        ref_d_knee_foot = distance(ref_knee, ref_foot)
        if ref_d_hip_knee == 0 or ref_d_knee_foot == 0:
            return False
        if abs(d_hip_knee - ref_d_hip_knee) / ref_d_hip_knee > similarity_tolerance:
            return False
        if abs(d_knee_foot - ref_d_knee_foot) / ref_d_knee_foot > similarity_tolerance:
            return False

    return True
