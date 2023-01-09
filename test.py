import pandas as pd
import numpy as np
import os
import os.path as op

def open_sequence(subnum, current_session):
    
    data = pd.read_csv(f"{subnum}_seq_{current_session}.csv", sep=',', header=0, encoding='utf8')
    seq = list(data['trial_keys'])
    ty = list(data['trial_type'])
    
    return seq, ty
     
s, n = open_sequence("03", 1)

def get_session_starts(blocks_in_session, trials_in_block):
    """Return with a list of numbers indicating the first trials of the different sessions."""

    sessionstarts = None
    
    if sessionstarts == None:
        sessionstarts = [1]
        epochs_cumulative = []
        session_no = 0
        e_temp = 0
        for e in range(blocks_in_session):
            e_temp += e
            session_no += 1
            epochs_cumulative.append(e_temp)

        for e in epochs_cumulative:
            sessionstarts.append(e * trials_in_block * blocks_in_session+ 1)

        del sessionstarts[0]
        
    return sessionstarts

c = get_session_starts(160, 20)

d = {}

for i in range(11):
    for e in range(2):
        d[e] = i


workdir_path = os.getcwd()

images = []
files_list = os.listdir(op.join(workdir_path, 'ASRT', 'stimuli'))
for img in files_list:
    if '.tiff' in img:
        images.append(img)
images.sort()

fname = op.join(workdir_path, 'ASRT', 'stimuli', images[0])  