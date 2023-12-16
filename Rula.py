import pandas as pd
import ast

# -------------------------------------------------------------------------------------------------------
    # Ce qu'il y'a en commun aux deux Parties A et B (Activité musculaire et Score d'effort et de charge)
# -------------------------------------------------------------------------------------------------------
class Rula_muscle_and_force():
    def muscle_use_score(self, static_time):
        muscle_use_score_value = 0
        if static_time > 10:
            muscle_use_score_value += 1

        return muscle_use_score_value
        
    def force_score(self, charge, intermitence=True, static_posture=False, repetead = False):
        force_score_value = 0

        if charge <= 2 and intermitence:
            force_score_value += 0
        elif charge > 2 and charge < 10:
            if intermitence:
                force_score_value += 1
            elif static_posture or repetead:
                force_score_value += 2           
        elif charge >= 10 and repetead:
            force_score_value += 3  

        return force_score_value


# ---------------------------------------------------
    # A. Analyse du bras et du poignet
# ----------------------------------------------------  

class Rula_Arm_Wrist(Rula_muscle_and_force):

    def __init__(self) -> None:
        pass

    def shoulder_position(self, params):
        
        angle, is_raised, is_abducted, is_supported, in_extension = params['angle'], params['is_raised'], params['is_abducted'], params['is_supported'], params['in_extension']
        
        shoulder_score = 0

        if angle == 20:
            if in_extension:
                shoulder_score += 2
            else:
                shoulder_score += 1

        elif angle > 20 and angle <= 45:
            shoulder_score += 2
            
        elif angle > 45 and angle < 90:
            shoulder_score += 3

        elif angle > 90:
            shoulder_score += 4

        if is_raised:
            shoulder_score += 1

        if is_abducted:
            shoulder_score += 1

        if is_supported:
            shoulder_score -= 1
        
        return shoulder_score

    
    def elbow_position(self, params):

        angle, is_out_to_side = params['angle'], params['is_out_to_side']

        elbow_score = 0

        if (angle >= 0 and angle < 60) or (angle > 100):
            elbow_score += 2

        elif angle > 60 and angle < 100:
            elbow_score +=1
        
        if is_out_to_side:
            elbow_score+=1
        
        return elbow_score
    

    def wrist_position(self, params):

        angle, is_bent_from_midline = params['angle'], params['is_bent_from_midline']

        wrist_score = 0

        if angle == 0:
            wrist_score += 1

        elif angle < 15 and angle > 0:
            wrist_score += 2
        
        elif angle > 15:
            wrist_score += 3
        
        if is_bent_from_midline:
            wrist_score += 1

        return wrist_score
    
    def wrist_twist(self, params):

        mid_range_twist, complete_twist = params['mid_range_twist'], params['complete_twist']

        wrist_twist_score = 0

        if mid_range_twist:
            wrist_twist_score += 1

        elif complete_twist:
            wrist_twist_score += 2
        
        return wrist_twist_score

    def score_from_table_a(self, shoulder_score, elbow_score, wrist_score, wrist_twist_score):

        Table_A = pd.read_csv('Vrai_Table_A.csv', converters={'index': ast.literal_eval})                

        score = Table_A.loc[Table_A['index']==(shoulder_score, elbow_score-1, 
                                               wrist_score-1, wrist_twist_score-1),'score'].values[0]
        
        return score
    
    
    
    def rula_arm_score(self, params):
        
        shoulder_params = {
            'angle': params['shoulder_angle'],
            'is_raised': params['is_raised'],
            'is_abducted': params['is_abducted'],
            'is_supported': params['shoulder_is_supported'],
            'in_extension': params['shoulder_in_extension']
        }

        elbow_params = {
            'angle': params['elbow_angle'],
            'is_out_to_side': params['is_out_to_side']
        }

        wrist_params = {
            'angle': params['wrist_angle'],
            'is_bent_from_midline': params['is_bent_from_midline']
        }

        wrist_twist_params = {
            'mid_range_twist': params['mid_range_twist'],
            'complete_twist': params['complete_twist']
        }

        self.shoulder_score = self.shoulder_position(shoulder_params)
        self.elbow_score = self.elbow_position(elbow_params)
        self.wrist_score = self.wrist_position(wrist_params)
        self.wrist_twist_score = self.wrist_twist(wrist_twist_params)

        self.score_from_tab_a_value = self.score_from_table_a(self.shoulder_score, self.elbow_score, self.wrist_score, self.wrist_twist_score)
        self.muscle_use_score_value = self.muscle_use_score(params['static_time'])
        self.force_score_value = self.force_score(params['charge'], params['intermitence'], 
                                                  params['static_posture'], params['repetead'])

        self.rula_arm_score_value = self.score_from_tab_a_value + self.muscle_use_score_value + self.force_score_value

        return self.rula_arm_score_value

# ---------------------------------------------------
    # B. Analyse du tronc, de la nuque et des jambes
# ----------------------------------------------------  


class Rula_Neck_Tronc_Leg(Rula_muscle_and_force):

    def __init__(self) -> None:
        pass

    def neck_position(self, params):

        angle, in_extension, is_bending, is_twisted = params['angle'], params['in_extension'], params['is_bending'], params['is_twisted']

        neck_score = 0

        if angle >= 0 and angle <= 10:
            neck_score += 1

        elif angle > 10 and angle <= 20:
            neck_score += 2
        
        elif angle > 20:
            neck_score += 3
        
        elif in_extension:
            neck_score += 4
        
        if is_bending:
            neck_score += 1
        
        if is_twisted:
            neck_score += 1

        return neck_score
    
    def trunck_position(self, params):

        angle, is_twisted, is_bending = params['angle'], params['is_twisted'], params['is_bending']

        trunck_score = 0

        if angle == 0:
            trunck_score += 1

        elif angle > 0 and angle <= 20:
            trunck_score += 2
        
        elif angle > 20 and angle <= 60:
            trunck_score += 3
        
        elif angle > 60:
            trunck_score += 4
        
        if is_twisted:
            trunck_score += 1
        
        if is_bending:
            trunck_score += 1

        return trunck_score
    
    def leg_position(self, params):
        is_supported = params['is_supported']

        leg_score = 0

        if is_supported:
            leg_score += 1
        else:
            leg_score += 2

        return leg_score
    
    def score_from_table_b(self, neck_score, trunck_score, leg_score):

        Table_B = pd.read_csv('Vrai_Table_B.csv', converters={'index': ast.literal_eval})                

        score = Table_B.loc[Table_B['index']==(neck_score, trunck_score-1, 
                                               leg_score-1),'score'].values[0]
        
        return score

    def rula_neck_trunck_leg_score(self, params):
        
        neck_params = {
            'angle': params['neck_angle'],
            'in_extension': params['neck_in_extension'],
            'is_bending': params['neck_is_bending'],
            'is_twisted': params['neck_is_twisted']
        }

        trunck_params = {
            'angle': params['trunck_angle'],
            'is_twisted': params['trunk_is_twisted'],
            'is_bending': params['trunk_is_bending']
        }

        leg_params = {
            'is_supported': params['leg_is_supported']
        }

        self.neck_score = self.neck_position(neck_params)
        self.trunck_score = self.trunck_position(trunck_params)
        self.leg_score = self.leg_position(leg_params)

        self.score_from_tab_b_value = self.score_from_table_b(self.neck_score, self.trunck_score, self.leg_score)
        self.muscle_use_score_value = self.muscle_use_score(params['static_time'])
        self.force_score_value = self.force_score(params['charge'], params['intermitence'], 
                                                  params['static_posture'], params['repetead'])

        self.rula_neck_trunck_leg_score_value = self.score_from_tab_b_value + self.muscle_use_score_value + self.force_score_value

        return self.rula_neck_trunck_leg_score_value

# -------------------------------------------------------
    # Détermination du score final à partir de la table C 
# ------------------------------------------------------- 

def score_final_from_table_c(params):
    

    Rula_arm_wrist = Rula_Arm_Wrist()
    Rula_neck_trunck_leg = Rula_Neck_Tronc_Leg()

    # print("Score from table A: " ,Rula_arm_wrist.score_from_tab_a_value)
    # print("Score from table B: " ,Rula_neck_trunck_leg.score_from_tab_b_value)


    rula_arm_score_value = Rula_arm_wrist.rula_arm_score(params)
    rula_neck_trunck_leg_score_value = Rula_neck_trunck_leg.rula_neck_trunck_leg_score(params)

    if rula_arm_score_value > 8:
        rula_arm_score_value = 8
    
    if rula_neck_trunck_leg_score_value > 7:
        rula_neck_trunck_leg_score_value = 7

    Table_C = pd.read_csv('Table_c.csv', index_col=0)

    rula_final_score = Table_C[f'{rula_neck_trunck_leg_score_value}'][rula_arm_score_value]

    return rula_final_score

# ------------------------------------
    # Etablissement des Paramètres 
# ------------------------------------

params = {
    'shoulder_angle': 30,
    'elbow_angle': 40,
    'wrist_angle': 15,
    'trunck_angle': 30,
    'neck_angle': 15,
    'static_time': 0,
    'charge': 5,
    'mid_range_twist': True,
    'complete_twist': False,
    'is_raised': False,
    'is_abducted': False,
    'shoulder_is_supported': False,
    'shoulder_in_extension': False,
    'is_out_to_side': False,
    'is_bent_from_midline': False,
    'neck_is_twisted': False,
    'neck_is_bending': False,
    'neck_in_extension': False,
    'trunk_is_twisted': False,
    'trunk_is_bending': False,
    'leg_is_supported': False,   
    'intermitence': True,
    'static_posture': False,
    'repetead': False   
}



print(f'Le Score final de la méthode RULA pour cette posture est: {score_final_from_table_c(params)}')

# On devrait obtenir 7 comme score final de RULA pour ces paramètres (voir video youtube https://www.youtube.com/watch?v=Ubmd5niUrFQ&t=238s  minute 9:40)