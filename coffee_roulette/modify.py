import numpy as np
from pathlib import Path
import os
import pickle
from coffee_roulette import utils

def add_participants(cfg_path :str, 
                     participants =[]):  
    """
    Adds new participants to the matrix and dictionary.
    ---
    PARAMETERS:
    -------------
      cfg_path : string
        Full path to the config.yaml file
      participants : list of strings 
        Names of participants to be added
    """  
    cfg = utils.read_config(cfg_path)
    roulette_dir = Path(cfg["roulette_directory"]).resolve()

    # load files    
    crProbMatrix = np.load(roulette_dir/"crProbMatrix.npy")
    crParticipantDict = pickle.load(open(roulette_dir/"crParticipantDict.p", "rb" ))
    
    for name in participants:
        i = crProbMatrix.shape[0]
        
        # update participant matrix
        crProbMatrix = np.hstack((crProbMatrix, np.full((i,1), 1)))
        crProbMatrix = np.vstack((crProbMatrix, np.full((1, i+1), 1)))
        np.fill_diagonal(crProbMatrix, 0)
        
        # update participant dictionary
        crParticipantDict[i] = (name, [])
    
    for i in range(crProbMatrix.shape[0]):
        i_not0 = np.nonzero(crProbMatrix[i,:])[0]
        crProbMatrix[i,:][crProbMatrix[i,:]>0] = 1/len(i_not0)
        
    np.save(roulette_dir/"crProbMatrix.npy", crProbMatrix)
    pickle.dump(crParticipantDict, open(roulette_dir/"crParticipantDict.p", "wb" ))

def remove_participants(cfg_path : str, 
                        participants = []):
    """
    creates (or adds to) a file containing participants that have quit
    1. find participant ID based on their name (value[0])
    2. add it to a file and save
    3. keep it in other files to avoid messing up other IDs
    4. add the IDs from the "removed" file to user_ids at the start of get_pairs()
    
    PARAMETERS:
    -------------
      cfg_path : string
        Full path to the config.yaml file
      participants : [string] 
        Names of participants to be removed
    """
    cfg = utils.read_config(cfg_path)
    roulette_dir = Path(cfg["roulette_directory"]).resolve()

    # load participantDict
    crParticipantDict = pickle.load(open(roulette_dir /"crParticipantDict.p", "rb" ))
    crParticipantArray = np.asarray(list(crParticipantDict.values()), dtype=object).flatten().reshape(-1,2)
    all_participants = crParticipantArray[:,0]
    
    # load existing removedDict file
    removed_participant_path = roulette_dir  / "crRemovedParticipantDict.pkl"
    if os.path.exists(removed_participant_path):
        crRemovedParticipantDict = pickle.load(open(removed_participant_path, "rb" ))
    else:
        crRemovedParticipantDict = {}
    
    for p in participants:
        p_id = np.argwhere(all_participants == p)[0][0]
        prev_meetings = crParticipantDict[p_id][1]
        crRemovedParticipantDict[p_id] = (p, prev_meetings)
    
    pickle.dump(crRemovedParticipantDict, open(removed_participant_path, "wb" ))

def print_participants(cfg_path :str):
    cfg = utils.read_config(cfg_path)
    roulette_dir = Path(cfg["roulette_directory"]).resolve()
    crParticipantDict = pickle.load(open(roulette_dir /"crParticipantDict.p", "rb" ))
    if os.path.exists(roulette_dir  / "crRemovedParticipantDict.pkl"):
        crRemovedParticipantDict = pickle.load(open(roulette_dir  / "crRemovedParticipantDict.pkl", "rb" ))
    else:
        crRemovedParticipantDict = {}

    from tabulate import tabulate
    for d, d_title in zip(
                    [crParticipantDict, crRemovedParticipantDict],
                    ["Active participants", "Removed participants"]    
                    ):
        participant_ids = list(d.keys())
        participant_names = [p[0] for p in d.values()]
        table = np.asarray([participant_ids, participant_names]).T
        print(d_title)
        print(tabulate(table))
        

