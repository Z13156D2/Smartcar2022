# -*- coding: utf-8 -*-
import os

# front_cam = 0
# side_cam = 1
front_cam = "/dev/video0"
side_cam = "/dev/video1"
full_speed = 20
turn_speed = full_speed * 0.8
EMLARGE_RATIO = 1.2
# Resolve models from the checkout, with an override for external model storage.
model_prefix = os.path.join(
    os.path.abspath(os.path.expanduser(os.environ.get(
        "SMARTCAR_MODEL_ROOT", os.path.join(os.path.dirname(__file__), "..")
    ))), ""
)

CONTROLLER = "mc601"
# CONTROLLER = "wobot"

# mession config
# one more for background
MISSION_NUM = 9
MISSION_PERSON_NUM = 3
MISSION_BAN_NUM = 2
MISSION_NUM_NEW = 11#11
MISSION_SIGN_NEW = 7
mission_low = 0.3
mission_high = 0.75
MISS_DURATION = 200

mission_person_list = {
	0: 'background',
	1: 'badperson',
	2: 'badperson2'
}

ban_list = {
	0: 'background',
	1: 'ban'
}

mission_label_list = {
	0: "background",
	1: "daijun",
	2: "dingxiang",
	3: "dunhuang",
	4: "liangcao",
	5: "rab",
	6: "red_target",
	# 7: "zhangpeng",
	7: "campsite"
}
#
# mission_label_list_new = {
# 	0: 'background',
# 	1: 'alamutu',
# 	2: 'badperson',
# 	3: 'badperson2',
# 	4: 'dunhuang',
# 	5: 'friendship',
# 	6: 'goodperson',
# 	7: 'goodperson2',
# 	8: 'jsddb',
# 	9: 'purchase',
# 	10: 'trade'
# }
#
# mission_label_list_new = {
# 	0: 'background',
# 	1: 'alamutu',
# 	2: 'badperson',
# 	3: 'badperson2',
# 	4: 'goodperson2',
# 	5: 'dunhuang',
# 	6: 'frindship',
# 	7: 'goodperson',
# 	8: 'goodperson2',
# 	9: 'jsddb',
# 	10: 'purchase',
# 	11: 'trade'
# }

mission_label_list_new = {
	0: 'background',
	1: 'alamutu',
	2: 'badperson',
	3: 'badperson2',
	4: 'dunhuang',
	5: 'friendship',
	6: 'goodperson',
	7: 'goodperson2',
	8: 'jstdb',
	9: 'purchase',
	10: 'trade',
}
purchase_list = {
	0: 'background',
	1: 'blue',
	2: 'green',
	3: 'orange',
	4: 'red',
	5: 'yellow'
}

sign_new_list = {
	0: "background",
	1: "tower",
	2: "campsite",
	3: "protect",
	4: "purchase",
	5: "trade",
	6: "enjoy"
}

sign_new_list_1 = {
	0: "background",
	1: "trade",
	2: "protect",
	3: "tower",
	4: "purchase",
	5: "campsite",

}

# sign config
MAX_SIGN_PER_FRAME = 2
sign_list = {
	0: "background",
	1: "campsite",
	2: "cereal",
	3: "lump",
	4: "target",
	5: "tower",
	6: "enjoy"
}

cruise3 = {
    "model":model_prefix + "models/all_new_ban"#syq_s_6"#s_pro630"#add_1_629"
}

cruise2 = {
	"model":model_prefix + "models/all_new_p708_ban_f"#syq_1520"#add_1_629"#628"
 }

cruise = {
 	"model":model_prefix + "models/all_new_p708_ban"# all_plus629"#628_s"
 }

person_list = {
	0: 'background',
	1: 'badperson',
	2: 'badperson2',
	3: 'goodperson',
	4: 'goodperson2',
	# 5: 'friendship',
	# 6: 'goodperson',
	# 7: 'goodperson2',
	# 8: 'jsddb',
	# 9: 'purchase',
	# 10: 'trade'
}
task_person = {
    "model":model_prefix + "models/person_5",
	"threshold":0.5,
	"label_list":person_list,
}

# sign models
sign = {
	"model": model_prefix + "models/sign707",
	"threshold": 0.25,
	"label_list": sign_list,
	# label = 0 is background
	"class_num": 7
}

sign_new = {
	"model": model_prefix + "models/sign_off",
	"threshold": 0.5,
	"label_list": sign_new_list,
	# label = 0 is background
	"class_num": 7
}

sign_new_1 = {
	"model": model_prefix + "models/sign_1",
	"threshold": 0.5,
	"label_list": sign_new_list_1,
	# label = 0 is background
	"class_num": 6
}

sign_ban = {
    "model": model_prefix + "models/ban",
	"threshold": 0.25,
	"label_list": ban_list,
	# label = 0 is background
	"class_num": 2

}

task = {
	"model":model_prefix + "models/task715",
	"threshold":0.5,
	"label_list":mission_label_list,
	# "class_num": 6
}

task_new = {
	"model":model_prefix + "models/task415_un_1",
    #"model":model_prefix + "models/task610",
	"threshold":0.4,
	"label_list":mission_label_list_new,
	# "class_num": 6
}

task_purchase = {
    "model":model_prefix + "models/pur_one",
    # "model":model_prefix + "models/perchase",
	"threshold":0.4,
	"label_list":purchase_list,
	"class_num": 6
}

trade_two_list = {
	0: 'background',
	1: 'hetao',
	2: 'putao'
}

trade_two = {
    "model":model_prefix + "models/trade_fyh",
	"threshold":0.5,
	"label_list":trade_two_list,
	"class_num": 3
}



MISSION_TRADE_TWO_NUMBER = 5


# sign_threshold = 0.3;
# task_threshold = 0.4;
