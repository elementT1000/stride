SAGITTAL_JOINTS = [
    {'Arm': ['Shoulder', 'Elbow']},
    {'Hip': ['Shoulder', 'Hip', 'Knee']},
    {'Knee': ['Hip', 'Knee', 'Ankle']},
    #set up two arctans and subtract them
    {'Ankle': ['Ankle', 'Knee']},
    {'Heel': ['Heel', 'Ball_of_Foot']},
    {'Toe': ['Heel', 'Ball_of_Foot', 'Big_Toe']}
]

SAGITTAL_SETTINGS = [
    {'Arm': ['vertical']},
    {'Hip': ['hinge', 1]},
    {'Knee': ['hinge', 0]},
    #set up two arctans and subtract them
    # {'Ankle': ['Knee', 'Ankle', 'Heel', 'Ball_of_Foot']},
    {'Toe': ['hinge', 1, 1]}
]