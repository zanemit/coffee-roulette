# coffee-roulette
coffee_roulette is a pseudo-random pair generator. It ensures unique pairings among the subjects in each round and optionally suggests a conversation starter and a meeting time. 

The code was written for the Coffee Roulette initiative organised by the Research Culture Working Group, Community subgroup, at the Sainsbury Wellcome Centre between January 2021 and November 2022. 

To use the code:
1. install and import the package
```
git clone https://github.com/zanemit/coffee-roulette.git
pip install -e .
import coffee_roulette as cr
```
2. create a coffee roulette project (code inspired by [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut))
Participants can be supplied as a list or entered one-by-one through user prompts.
```
cr.create_coffee_roulette(roulette_name, working_dir = None, participants = None)
```
This initialises:
    - a matrix of meeting probabilities `crProbMatrix.npy`
    - a dictionary that stores active participants and their conversation starters `crParticipantDict.pickle`
    - a configuration file `config.yaml` that stores project directory and a range of meeting parameters(frequency, duration, purpose) that affect the printed results
    - a conversation starter file `crConversationStarters.txt` that users are advised to populate further

3. get pairs
```
cr.get_pairs(cfg_path, conv_starters=True, random_time=True, exclude_nonrandom=None)
```
This prints the generated pairs and stores them in the `\results` folder.
