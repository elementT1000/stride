import os
home = os.environ["T4_DIR"]

sagittal_config_file = home + r'\product\stride\root_dir\config_files\sag_config.yaml'
anterior_config_file = home + r'\product\stride\root_dir\config_files\af_config.yaml'
posterior_config_file = home + r'\product\stride\root_dir\config_files\pf_config.yaml'

SAGITTAL_JOINTS = [
    {'Arm': ['Shoulder', 'Elbow']},
    {'Elbow': ['Elbow']},
    {'Hip': ['Shoulder', 'Hip', 'Knee']},
    {'Knee': ['Hip', 'Knee', 'Ankle']},
    {'Ankle': ['Ankle', 'Knee']},
    {'Heel': ['Heel', 'Ball_of_Foot']},
    {'Toe': ['Heel', 'Ball_of_Foot', 'Big_Toe']},
    {'Ank': ['Ankle']}
]

ANTERIOR_FRONTAL_JOINTS = [
    #{'afWaist': ['LeftWaistline', 'RightWaistline']}, #Ignore ant. waistline for now due to data issues
    {'afLeftThigh': ['LeftWaistline', 'LeftVastusLat']}, #hip ad/ab + knee var/val
    {'afLeftShin': ['LeftCoLig', 'LeftAnkle']}, #knee var/val similar to heel in sagittal joints
    {'afLeftAnkle': ['LeftCoLig', 'LeftAnkle', 'Left1Prox']},
    {'afLeftFoot': ['Left1Prox', 'Left5Prox']},
    {'afRightThigh': ['RightWaistline', 'RightVastusLat']}, #hip ad/ab + knee var/val
    {'afRightShin': ['RightCoLig', 'RightAnkle']},
    {'afRightAnkle': ['RightCoLig', 'RightAnkle', 'Right1Prox']},
    {'afRightFoot': ['Right1Prox', 'Right5Prox']}
]

POSTERIOR_FRONTAL_JOINTS = [
    {'pfWaist': ['LeftWaistLine', 'RightWaistLine']}, 
    {'pfLeftFemurHead': ['LeftFemurHead', 'LeftKnee']}, 
    {'pfLeftKnee': ['LeftFemurHead', 'LeftKnee', 'LeftAnkle']},
    {'pfLeftAnkle': ['LeftKnee', 'LeftAnkle', 'LeftHeel']},
    {'pfRightFemurHead': ['RightFemurHead', 'RightKnee']}, 
    {'pfRightKnee': ['RightFemurHead', 'RightKnee', 'RightAnkle']},
    {'pfRightAnkle': ['RightKnee', 'RightAnkle', 'RightHeel']}
]

CALCULATION_PARAMS = {
    "Arm": {"orientation": "vertical",},
    "Hip": {"orientation": "hinge", "anticlockwise": "default"},
    "Knee": {"orientation": "hinge", "anticlockwise": "alt",},
    "Ankle": {"orientation": "neutral", "anticlockwise": "default"},
    "Heel": {"orientation": "neutral", "anticlockwise": "default"},
    "Toe": {"orientation": "hinge", "anticlockwise": "default", "dev_from_straight": True,},
}