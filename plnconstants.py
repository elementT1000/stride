SAGITTAL_JOINTS = [
    {'Arm': ['Shoulder', 'Elbow']},
    {'Hip': ['Shoulder', 'Hip', 'Knee']},
    {'Knee': ['Hip', 'Knee', 'Ankle']},
    {'Ankle': ['Ankle', 'Knee']},
    {'Heel': ['Heel', 'Ball_of_Foot']},
    {'Toe': ['Heel', 'Ball_of_Foot', 'Big_Toe']}
]

CALCULATION_PARAMS = {
    "Arm": {"orientation": "vertical",},
    "Hip": {"orientation": "hinge", "anticlockwise": "default"},
    "Knee": {"orientation": "hinge", "anticlockwise": "alt",},
    "Ankle": {"orientation": "neutral", "anticlockwise": "default"},
    "Heel": {"orientation": "neutral", "anticlockwise": "default"},
    "Toe": {"orientation": "hinge", "anticlockwise": "default", "dev_from_straight": True,},
}

ANTERIOR_FRONTAL_JOINTS = [
    #{'afWaist': ['LeftWaistline', 'RightWaistline']}, #Ignore ant. waistline for now due to data issues
    {'afLeftThigh': ['LeftWaistline', 'LeftVastusLat']}, #hip ad/ab + knee var/val
    {'afLeftShin': ['LeftCoLig', 'LeftAnkle']},
    {'afLeftAnkle': ['LeftAnkle', 'Left1Prox']},
    {'afLeftFoot': ['Left1Prox', 'Left5Prox']},
    {'afRightThigh': ['RightWaistline', 'RightVastusLat']}, #hip ad/ab + knee var/val
    {'afRightShin': ['RightCoLig', 'RightAnkle']},
    {'afRightAnkle': ['RightAnkle', 'Right1Prox']},
    {'afRightFoot': ['Right1Prox', 'Right5Prox']}
]

POSTERIOR_FRONTAL_JOINTS = [
    {'pfWaist': ['LeftWaistLine', 'RightWaistLine']}, 
    {'pfLeftFemurHead': ['LeftFemurHead', 'LeftKnee']}, #hip ad/ab + knee var/val
    {'pfLeftKnee': ['LeftFemurHead', 'LeftKnee', 'LeftAnkle']},
    {'pfLeftAnkle': ['LeftKnee', 'LeftAnkle', 'LeftHeel']},
    {'pfRightFemurHead': ['RightFemurHead', 'RightKnee']}, #hip ad/ab + knee var/val
    {'pfRightKnee': ['RightFemurHead', 'RightKnee', 'RightAnkle']},
    {'pfRightAnkle': ['RightKnee', 'RightAnkle', 'RightHeel']}
]