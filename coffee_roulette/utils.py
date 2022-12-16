import os
import numpy as np
from ruamel.yaml import YAML
from pathlib import Path

def create_config_template():
    """
    Creates a template for the config.yaml file.
    Code inspired by DeepLabCut https://github.com/DeepLabCut/DeepLabCut/blob/master/AUTHORS
    """
    yaml_str = """\
    # Roulette definitions
        roulette_name:
        roulette_date:
        roulette_directory:
        \n
    # Pairing parameters
        roulette_frequency:
        roulette_times:
        time_spacing:
        \n
    # Printing parameters
        name_prefix: 
        \n    
    """

    ruamelFile = YAML()
    cfg_file = ruamelFile.load(yaml_str)
    return cfg_file, ruamelFile

def read_config(cfg_path :str) -> dict:
    """
    Reads the roulette config file
    """
    ruamelFile = YAML()
    cfg_path = Path(cfg_path)
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            cfg = ruamelFile.load(f)
    else:
        raise FileNotFoundError("Config file not found!")
    return cfg

def write_config(cfg_path :str, cfg :dict):
    """
    Writes the roulette config file
    """
    with open(cfg_path, "w") as f:
        cfg_file, ruamelFile = create_config_template()
        for key in cfg.keys():
            cfg_file[key] = cfg[key]
        ruamelFile.dump(cfg_file, f)

def edit_config(cfg_path, edits):
    cfg = read_config(cfg_path)
    for key, value in edits.items():
        cfg[key] = value
        #TBC

def get_meeting_times(bounds :list, spacing :int) -> list:
    """
    Generates a list of meeting times given time slot bounds
    and meeting spacings

    PARAMETERS
    -------------
    bounds : list of lists of ints
        [[9,12],[13,17]] or [[900,1200],[1300,1700]]
        = meeting slots 9-12 and 13-17
    spacing : int
        meeting spacing in minutes

    """
    bounds = np.asarray(bounds)

    # check that bounds consist of nested arrays
    if not all(isinstance(b, np.ndarray) for b in bounds):
        raise ValueError("Ill-defined bounds! Bounds must be a list of lists!")

    # check that bounds are integers
    if not all(isinstance(x, np.int32) for b in bounds for x in b):
        raise ValueError("Ill-defined bounds! Bounds must be defined by integers!")

    if not all(i < j for i, j in zip(bounds.flatten(), bounds.flatten()[1:])):
        raise ValueError("Ill-defined bounds! Bounds must be strictly increasing!")

    # check that bounds notation is consistent
    item_lengths = np.asarray([len(str(x)) for b in bounds for x in b])
    if np.all(item_lengths<=2):
        print("Nice! Bounds are defined in full hours!")
        bounds = bounds.astype(np.float64)
    elif np.all((item_lengths>2) & (item_lengths<=4)):
        print("Nice! Bounds are defined in hours and minutes!")
        bounds = bounds//100 + bounds%100/60
    else:
        raise ValueError("Ill-defined bounds! Bounds must denote full hours [[9,12]] or hours and minutes [[900,1200]] *and* be consistent!")

    # check that spacing is an integer
    if not isinstance(spacing, int):
        raise ValueError("Spacing must be an integer!")

    import datetime as dt
    times_list = []
    for b in bounds:
        b0 = dt.timedelta(hours = b[0])
        b1 = dt.timedelta(hours = b[1])
        bx = b0
        while bx < b1:
            times_list.append(bx)
            bx += dt.timedelta(minutes = spacing)

    return times_list