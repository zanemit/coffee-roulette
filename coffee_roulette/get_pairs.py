from pathlib import Path
import numpy as np
import pickle
import os
import datetime as dt
import random
from coffee_roulette import utils


def get_pairs(
    cfg_path, conv_starters=True, random_time=True, exclude_nonrandom=None
):
    """
    Generates pairs of participants based on the probability matrix
    such that people can only be paired with those they have not been
    paired with before.

    Prints the freshly generated pairs and, in case of an
    odd number of participants, the name of the left-out person.

    PARAMETERS
    -------------
        cfg_path : string
            Full path to the config.yaml file
        conv_starters : bool, optional
            Whether to include suggested conversation starters in the output file
            Default is True
        random_time : bool, optional
            Whether to include a random meeting time within the next
            config["roulette_frequency"] weeks at times config["roulette_times"].
            Use edit_config() to edit the config file programmatically.
            Defaults to True
        exclude_nonrandom : int or string, optional
            Participant id or name to exclude
            Find out participant ids and names by running print_participants()
            Defaults to None, which excludes someone randomly
    """
    cfg = utils.read_config(cfg_path)
    roulette_dir = Path(cfg["roulette_directory"]).resolve()

    everyone_matched = False
    iteration = 1
    output_list = []
    while not everyone_matched:
        print(f"Running the iteration #{iteration}...")
        # load_files
        crProbMatrix = np.load(roulette_dir / "crProbMatrix.npy")
        crParticipantDict = pickle.load(
            open(roulette_dir / "crParticipantDict.p", "rb")
        )

        used_ids = np.empty(0)
        participant_number = crProbMatrix.shape[0]

        if os.path.exists(roulette_dir / "crRemovedParticipantDict.p"):
            crRemovedParticipantDict = pickle.load(
                open(roulette_dir / "crRemovedParticipantDict.p", "rb")
            )
            used_ids = np.append(
                used_ids, list(crRemovedParticipantDict.keys())
            )
            used_ids = used_ids.flatten()
            participant_number = participant_number - len(
                crRemovedParticipantDict
            )

        # if odd number of participants, have the participant id'ed by exclude_nonrandom sit the round out
        if participant_number % 2 == 1 and exclude_nonrandom != None:
            used_ids = np.append(used_ids, [exclude_nonrandom])
            participant_number = participant_number - len(exclude_nonrandom)

        # set up meeting timeframes
        if random_time:
            weeks = cfg["roulette_frequency"]
            times = cfg["roulette_times"]
            spacing = cfg["time_spacing"]

            t = dt.date.today()  # the day the code is run
            start_date = t + dt.timedelta(days=1)
            day_number = int(7 * weeks)  # days until the next draw

            reasonable_times = utils.get_meeting_times(times, spacing)

        for p in range(int(participant_number / 2)):
            unused_ids = np.setdiff1d(
                np.arange(crProbMatrix.shape[0]), used_ids
            )
            max_val_remaining_crProbMatrix = crProbMatrix[
                np.repeat(unused_ids, unused_ids.shape),
                np.tile(unused_ids, unused_ids.shape),
            ].max()
            i, j = np.where(crProbMatrix == max_val_remaining_crProbMatrix)
            for x in used_ids:
                ids_to_remove = np.where(i == x)
                i = np.delete(i, ids_to_remove)
                j = np.delete(j, ids_to_remove)
                jds_to_remove = np.where(j == x)
                i = np.delete(i, jds_to_remove)
                j = np.delete(j, jds_to_remove)
            id = np.random.choice(len(i))
            output_str = f"- @{crParticipantDict[i[id]][0]} will {cfg['meeting_purpose']} with @{crParticipantDict[j[id]][0]}"

            # generate a random meeting time
            if random_time:
                meeting_weekday = "Saturday"
                while (
                    meeting_weekday == "Saturday"
                    or meeting_weekday == "Sunday"
                ):
                    random_number_of_days = random.randrange(day_number)
                    meeting_date = start_date + dt.timedelta(
                        random_number_of_days
                    )
                    meeting_weekday = meeting_date.strftime("%A")
                meeting_time = random.choice(reasonable_times)
                output_str += f". Perhaps on {meeting_date.strftime('%A')}, {meeting_date.strftime('%B %d')}, at {':'.join(str(meeting_time).split(':')[:2])}?"

            # generate a conversation starter
            if conv_starters:
                # find conv starters not used by either participant
                used_conv_starters = (
                    crParticipantDict[i[id]][1] + crParticipantDict[j[id]][1]
                )
                all_conv_starters = np.arange(
                    len(
                        open(
                            roulette_dir / "crConversationStarters.txt"
                        ).readlines()
                    )
                )
                available_conv_starters = np.setdiff1d(
                    all_conv_starters, used_conv_starters
                )

                # pick a random question
                if available_conv_starters.shape[0] > 0:
                    q_id = np.random.choice(available_conv_starters)
                    with open(
                        roulette_dir / "crConversationStarters.txt", "r"
                    ) as text_file:
                        for l, line in enumerate(text_file):
                            if l == q_id:
                                question = line
                else:
                    print(
                        "All conversation starters have been used! Add more!"
                    )
                    break
                # add the question id to participants' conversation starter history
                crParticipantDict[i[id]][1].append(q_id)
                crParticipantDict[j[id]][1].append(q_id)
                output_str += f" Suggested conversation starter: {question} "

            # check that the last pairing has not met already
            if (
                crProbMatrix[i[id], j[id]] != 0
            ):  # all good - these people have not met yet!
                print(output_str)
                output_list.append(output_str)
                used_ids = np.concatenate((used_ids, [i[id], j[id]]))
                crProbMatrix[i[id], j[id]] = 0
                crProbMatrix[j[id], i[id]] = 0
                if p == (int(participant_number / 2)) - 1:
                    print(f"Success! Number of iterations needed: {iteration}")
                    everyone_matched = True
            else:  # problem! break out of the for loop, start over!
                iteration += 1
                break

    # print a line about an unpaired participant if the total number is odd and exclusion is random
    if participant_number % 2 == 1:
        unpaired_id = np.setdiff1d(np.arange(crProbMatrix.shape[0]), used_ids)
        unpaired_str = f"{crParticipantDict[unpaired_id[0]][0]} was not paired with anyone this time!"
        print(unpaired_str)
        output_list.append(unpaired_str)

    # recompute probabilities and update the matrix
    for row in range(crProbMatrix.shape[0]):
        nonzeros = crProbMatrix[row] != 0
        crProbMatrix[row, nonzeros] = 1 / nonzeros.sum()

    rdate = dt.datetime.today().strftime("%Y-%m-%d")
    rtime = dt.datetime.today().strftime("%H%M%S")

    with open(
        roulette_dir / "results" / f"{rdate}_crPairings_{rtime}.txt", "w"
    ) as f:
        f.writelines(line + "\n" for line in output_list)
    np.save(roulette_dir / "crProbMatrix.npy", crProbMatrix)
    pickle.dump(
        crParticipantDict, open(roulette_dir / "crParticipantDict.p", "wb")
    )
