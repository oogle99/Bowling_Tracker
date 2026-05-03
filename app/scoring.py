def collect_scores(form_data, bowlers=4):
    scores = {}

    for bowler in range(1, bowlers + 1):
        frames = []

        for frame in range(1, 11):
            if frame < 10:
                roll1 = form_data.get(f"bowler{bowler}_frame{frame}_roll1", "").strip()
                roll2 = form_data.get(f"bowler{bowler}_frame{frame}_roll2", "").strip()
                frames.append([roll1, roll2])
            else:
                roll1 = form_data.get(f"bowler{bowler}_frame10_roll1", "").strip()
                roll2 = form_data.get(f"bowler{bowler}_frame10_roll2", "").strip()
                roll3 = form_data.get(f"bowler{bowler}_frame10_roll3", "").strip()
                frames.append([roll1, roll2, roll3])

        scores[f"bowler{bowler}"] = frames

    return scores

def parse_roll(value, previous_roll=0):
    value = value.upper()

    if value == "X":
        return 10
    elif value == "-":
        return 0
    elif value == "/":
        return 10 - previous_roll
    elif value.isdigit():
        return int(value)
    else:
        return None
    
def parse_frame(frame):
    parsed = []

    if frame[0]:
        first = parse_roll(frame[0])
        parsed.append(first)
    else:
        return parsed

    if len(frame) > 1 and frame[1]:
        second = parse_roll(frame[1], first)
        parsed.append(second)

    if len(frame) > 2 and frame[2]:
        third = parse_roll(frame[2], parsed[-1])
        parsed.append(third)

    return parsed

def parse_scores(raw_scores):
    parsed_scores = {}

    for bowler, frames in raw_scores.items():
        parsed_scores[bowler] = [parse_frame(frame) for frame in frames]

    return parsed_scores

def flatten_frames(frames):
    rolls = []

    for frame in frames:
        rolls.extend(frame)

    return rolls

def calculate_score(frames):
    rolls = flatten_frames(frames)

    scores = []
    total = 0
    roll_index = 0

    for frame in range(10):
        if roll_index >= len(rolls):
            break

        # Strike
        if rolls[roll_index] == 10:
            if roll_index + 2 >= len(rolls):
                break

            total += 10 + rolls[roll_index + 1] + rolls[roll_index + 2]
            scores.append(total)
            roll_index += 1

        # Spare
        elif roll_index + 1 < len(rolls) and rolls[roll_index] + rolls[roll_index + 1] == 10:
            if roll_index + 2 >= len(rolls):
                break

            total += 10 + rolls[roll_index + 2]
            scores.append(total)
            roll_index += 2

        # Open frame
        elif roll_index + 1 < len(rolls):
            total += rolls[roll_index] + rolls[roll_index + 1]
            scores.append(total)
            roll_index += 2

        else:
            break

    return scores

def calculate_all_scores(parsed_scores):
    totals = {}

    for bowler, frames in parsed_scores.items():
        totals[bowler] = calculate_score(frames)

    return totals