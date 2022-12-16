import numpy as np
import os
from pathlib import Path
import pickle
import datetime as dt
from coffee_roulette import utils

def create_coffee_roulette(
        roulette_name, 
        working_dir = None,
        participants = None
        ):
    """
    Creates a new coffee roulette project directory.
    
    This involves files for storing a meeting probability matrix 
    and a dictionary of participant names.

    This function only needs to be run once.
    
    PARAMETERS
    -------------
        roulette_name : string
            The name of the roulette instance

        working_dir : string, optional
            Path to the desired file directory.
            Defaults to the current working directory.
        
        participants : list, option
            Lists of participants.
            If None, the user is prompted to enter names.
    
    WRITES
    -------------
    working_dir/crParticipantDict.pkl
    working_dir/crProbMatrix.npy 
    working_dir/crConversationStarters.txt

    """
    rdate = dt.datetime.today().strftime("%Y-%m-%d")

    if working_dir == None:
        working_dir = "."
    wd = Path(working_dir).resolve()
    
    roulette_dir = wd/f"CoffeeRoulette-{roulette_name}"

    if os.path.exists(roulette_dir):
        raise ValueError("Coffee roulette already exists! Run another function or choose a different roulette name!")

    os.mkdir(roulette_dir)
    os.mkdir(Path(roulette_dir) / "results")
    
    # create participant dictionary (names and who they have met)
    crParticipantDict = {}
    if participants == None:
        id = 0
        while True:
            participant = input("Enter participant name or 'x' if you are done for now: ")
            if participant == 'x':
                break
            crParticipantDict[id] = (participant, [])    
            id += 1
    elif type(participants) == list:
        for id, participant in enumerate(participants):
            crParticipantDict[id] = (participant, [])  
    else:
        raise ValueError("Participants must be a flat list or None!")
    
    pickle.dump(crParticipantDict, open(roulette_dir/"crParticipantDict.p", "wb" ))
    
    # create pair probability matrix
    crProbMatrix = np.full((id, id), 1/(id-1))  
    np.fill_diagonal(crProbMatrix, 0)
    np.save(roulette_dir/"crProbMatrix.npy", crProbMatrix)

    # create a config file
    cfg_file, ruamelFile = utils.create_config_template()
    cfg_file["roulette_name"] = roulette_name
    cfg_file["roulette_date"] = rdate
    cfg_file["roulette_directory"] = str(roulette_dir)
    cfg_file["roulette_frequency"] = 3 # weeks
    cfg_file["roulette_times"] = [[9,12],[13,17]] # hours
    cfg_file["time_spacing"] = 30 # minutes
    cfg_file["name_prefix"] = '@' # for places with usernames (slack, discord, etc)
    cfg_file["meeting_purpose"] = 'have coffee'

    cfg_path = roulette_dir / "config.yaml"
    utils.write_config(cfg_path, cfg_file)

    lines = [
            'What is the most bizarre thing that you have ever eaten?',
            'What is the worst advice that you have ever taken?',
            'What is the magical power that you wish you had?',
            'If you could trade lives with one person, who would it be?',
            'What is one thing you would tell yourself 10 years ago?',
            'What is your biggest pet peeve?',
            'What about our society would surprise a time traveller?',
            'What is a funny prank you have played on someone?',
            'What is a secret talent you have?',
            'What is one embarrassing memory you have?',
            'If you could have dinner with one person, dead or alive, who would it be?',
        ]
    with open(roulette_dir/"crConversationStarters.txt", "w") as f:
        f.writelines(line + '\n' for line in lines)

    print(
        "\nA new project with name 'CoffeeRoulette-{roulette_name}-{date}' is created at {roulette_dir}.\nUse function 'generate_pairs' to run the first round of the coffee roulette.\nIf you wish to customise the conversation starters, edit the crConversationStarters.txt file in your roulette directory.\nYou can add and remove participants at any time by running the functions 'add_participants' and 'remove_participants' respectively."
    )

