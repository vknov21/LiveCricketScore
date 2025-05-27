import requests
from PyQt5 import QtWidgets, QtTest, QtCore
import sys
from MyMainWindow import MyMainWindow, BaseWorkerThread
# import gzip
import json
import logging

"""original_query = '''query CombinedQuery($matchID: String!, $innings: String) {
    #         last12Balls(matchID: $matchID, innings: $innings) {
    #             over {
    #                 isBall
    #                 overNumber
    #                 runs
    #                 type
    #             }
    #             overNumber
    #         }
    #         miniScoreCard(matchID: $matchID) {
    #             batting {
    #                 playerName
    #                 # sixes
    #                 # fours
    #                 playerMatchBalls
    #                 runs
    #                 playerOnStrike
    #                 # playerDismissalInfo
    #             }
    #             bowling {
    #                 playerName
    #                 playerTeam
    #                 wickets
    #                 # maiden
    #                 RunsConceeded
    #                 overs
    #             }
    #             # runRate
    #             # rRunRate
    #             liveScoreUrl
    #             data {
    #                 currentinningsNo
    #                 homeTeamName
    #                 awayTeamName
    #                 toss
    #                 matchStatus
    #                 statusMessage
    #                 # venue
    #                 matchResult
    #                 # startDate
    #                 isAbandoned
    #                 # playerOfTheMatchdDetails {
    #                 #     batsmanTab
    #                 #     playerID
    #                 #     playerTeamID
    #                 # }
    #                 # teamsWinProbability {
    #                 #     homeTeamShortName
    #                 #     homeTeamPercentage
    #                 #     awayTeamShortName
    #                 #     awayTeamPercentage
    #                 #     tiePercentage
    #                 # }
    #                 # matchScore {
    #                 #     teamShortName
    #                 #     teamScore {
    #                 #         inning
    #                 #         runsScored
    #                 #         wickets
    #                 #         overs
    #                 #         battingTeamShortName
    #                 #     }
    #                 # }
    #             }
    #         }
    #     }
# '''"""

REFRESH_TIMEOUT = 4000


def cricket_query(match_id, innings="1"):
    """Queries to the cricket.com website to get the scorecard and the current live score

    Args:
        match_id (int): Obtain the id from cricket.com website, mostly at the end of the url of the match
        innings (str, optional): Which inning you need the score of. Currently it gets obtained automatically, and assumed to be the first inning initially. Defaults to "1".
    """
    def clean_str(timeline):
        """Just cleans the '[' or string related symbols of python to create a cleaner over timeline

        Args:
            timeline (str): It's a dictionary of overs containing list of balls converted to string, like
            {'19': ['1', '0', '6']}

        Returns:
            str: The timeline for above will then returned in string as
            "19:1 0 6"
        """
        return timeline.replace("'", "").replace(" ", "").replace('"', '').replace("[", "").replace("]", "").replace(",", " ").replace("{", "").replace("}", "")

    def short_name(name, on_strike=False):
        split_name = name.split()
        split_name[-1] = " " + split_name[-1]
        for i in range(len(split_name) - 1):
            split_name[i] = split_name[i][0] if split_name[i][0].isupper() else ""
        return "".join(split_name) + ("*" if on_strike else "")

    def ball_type_run_conv(is_ball, runs, _type):
        """
        Converts the ball into its short form

        Args:
            is_ball (bool): _description_
            runs (str): Input the runs scored in the current ball
            _type (str): Inputs any extras thrown in the current ball

        Returns:
            str: Converted short form of the ball thrown
        """
        ball_converter = {
            "": None,
            "leg bye": "lb",
            "bye": "b",
            "six": None,
            "four": None,
            "wicket": "W",
            "wide": "wd",
            "no ball": "nb"
        }
        try:
            if ball_converter[_type] is None:
                return runs
            if runs != "0":
                return runs + ball_converter[_type]
            return ball_converter[_type]
        except Exception as e:
            print(e, "With args", is_ball, runs, _type)

    headers = {
        # 'Content-Encoding': 'gzip',
        # 'Connection': 'keep-alive',
        'content-type': 'application/json'
    }

    query = """query($id:String!,$i:String){l:last12Balls(matchID:$id,innings:$i){o:over{B:isBall r:runs t:type}n:overNumber}s:miniScoreCard(matchID:$id){rr:runRate rq:rRunRate bt:batting{n:playerName b:playerMatchBalls r:runs s:playerOnStrike}bo:bowling{n:playerName w:wickets r:RunsConceeded o:overs}scr:liveScoreUrl data{i:currentinningsNo t1:homeTeamName t2:awayTeamName t:toss s:matchStatus m:statusMessage}}}"""

    payload = {
        "query": query,
        "variables": {
            "id": str(match_id),
            "i": str(innings)
        }
    }
    json_data = json.dumps(payload).encode('utf-8')
    # compressed_data = gzip.compress(json_data)
    resp = requests.post("https://apiv2.cricket.com/cricket", headers=headers, data=json_data)
    resp = resp.json()
    # Obtains the match_scorecard, containing all the necessary information on the current match
    match_scorecard = resp["data"]["s"]
    if match_scorecard is None:
        raise BaseException(f"The match with provided URL or Match Code: {match_id} doesn't exist")
    overs = resp["data"]["l"]

    result = None
    matchStatus = match_scorecard["data"][0]["s"]
    current_inns = match_scorecard["data"][0]["i"]
    # Verified if the match has started yet or is it programmed to start later
    if matchStatus == "upcoming":
        return 1, ["Still To Play"]
    # If the match has already completed, add the result on the top of the scorecard
    elif matchStatus == "completed":
        result = match_scorecard["data"][0]["m"]
        result = result[:25] + "\n" + result[25:50].strip() + ("\n" + result[50:].strip() if result[50:] else "")
    # If the match is live on the first inning, and no ball has been thrown yet, then add the Toss information
    elif matchStatus == "live" and not overs and current_inns == "1":
        toss_res = match_scorecard["data"][0]["t"]
        return 1, [toss_res.replace(" and ", "\nand ")]
    # If the match is live on the second innings, and no ball has been thrown yet, then add the Target information
    elif matchStatus == "live" and not overs and current_inns == "2":
        return 1, [match_scorecard["data"][0]["m"], match_scorecard["scr"]]

    # If there are any sort of interruption in th match, whether due to Tea/Lunch Break or Rain delay, add those information
    if "Break" in match_scorecard["data"][0]["m"] or "Delay" in match_scorecard["data"][0]["m"]:
        result = match_scorecard["data"][0]["m"].split(' - ', maxsplit=1)[0]
    # If the current inning is not the latest, modify the data for the latest inning instead
    if current_inns != str(innings):
        return cricket_query(match_id, current_inns)
    # Fetches the teams playing the match
    team_1 = match_scorecard["data"][0]["t1"]
    team_2 = match_scorecard["data"][0]["t2"]
    # From the score like this: "PBKS-187/3-(18.3)", get the current playing team and the 
    # scorecard. That team will become the batting team and the other will be the bowling team
    team_on_play = match_scorecard["scr"].split("-", maxsplit=1)[0]
    # Fetches the Run Rate if the inning is 1st inning else the Required Run Rate
    # TODO: Need to make it work for the Test matches
    score = match_scorecard["scr"] + (" RR:" + match_scorecard["rr"] if innings == "1" else " RQ:" + match_scorecard["rq"])
    # Gets the batting and fielding team
    batting_team, fielding_team = (team_2, team_1) if team_on_play == team_2 else (team_1, team_2)

    # Uses short hand name of the batsman to compact the display and gets the runs and balls and also if the player is on strike
    batsman_live_score = [(short_name(batsman["n"], batsman["s"]) + " " + batsman["r"] + f" ({batsman['b']})") for batsman in match_scorecard["bt"]]
    # If two batsman are playing (another hasn't gotten out just now), then add the information of both player one at a line
    if len(batsman_live_score) == 2:
        batsmen_on_field = "...:" + batsman_live_score[0] + "\n...:" + batsman_live_score[1]
        # print("...:", batsman_live_score[0], "|", batsman_live_score[1], sep="")
    else:
        # If a batsman just got out, only add the current batsman's information
        batsmen_on_field = "...:" + batsman_live_score[0]
        # print("...:", batsman_live_score[0])

    # Similarly, shorten the Bowler's name and get the information for all overs thrown till now
    bowler = match_scorecard["bo"][0]
    bowler_bowling = fielding_team + ":" + short_name(bowler["n"]) + " " + bowler["w"] + "-" + bowler["r"] + f" ({bowler['o']})"
    # print(short_name(bowler["n"]) + " " + bowler["w"] + "-" + bowler["r"] + f" ({bowler['o']})")

    overs_timeline = {}
    # Creates the over timeline similar to what we see on TV
    for over in overs:
        overs_timeline[over["n"]] = clean_str(str([ball_type_run_conv(ball["B"], ball["r"], ball["t"]) for ball in over["o"]]))
        # print(over["n"], ":", clean_str(str([ball_type_run_conv(ball["B"], ball["r"], ball["t"]) for ball in over["o"]])), sep="", end="|", flush=True)
    # print("\b ")
    over_keys = list(overs_timeline.keys())
    # Only gets the last and second last over, and for second last only last 3 balls info are added and for current one, all ball information is added
    if len(overs) >= 2:
        overs_timeline[over_keys[-2]] = ",".join(overs_timeline[over_keys[-2]].split(" ")[-3:])
        overs_timeline[over_keys[-1]] = ",".join(overs_timeline[over_keys[-1]].split(" "))
    elif len(overs) == 1:
        overs_timeline[over_keys[-1]] = ",".join(overs_timeline[over_keys[-1]].split(" "))
    elif len(overs) == 0:
        overs_timeline = ""

    # If there are more than two, pop out the 3rd. Assumed, it won't be greater than the 3
    if len(overs_timeline) == 3:
        overs_timeline.pop(over_keys[-3])
    # Separate the overs by a '|' symbol and again clean the result
    overs_timeline = clean_str(str(overs_timeline).replace(", ", "|"))

    # To reduce the size of the window or the data displayed, prefer removing of the unneeded ones
    # line_by_line_data = [score, batsmen_on_field, bowler_bowling, overs_timeline]
    line_by_line_data = [score, batsmen_on_field, bowler_bowling, overs_timeline]
    if result:
        line_by_line_data = [result] + line_by_line_data
    elif current_inns == "2":
        # "m" is statusMessage, which gives either the chansing info (if match is live) or the result as above
        # return current_inns, ['\n'.join(match_scorecard["data"][0]["m"].split(" - "))] + line_by_line_data
        return current_inns, ["\n".join(match_scorecard["data"][0]["m"].split(' - '))] + line_by_line_data
    return current_inns, line_by_line_data


class WorkerThread(BaseWorkerThread):
    def __init__(self, window):
        super().__init__(window)
        # With the Window initiation, asks for the URL or the 6 digit code that uniquely identifies the match
        match_id = input("Enter the URL of a match from the website: 'https://www.cricket.com/' or the 6-digit code: ").split("/")[-1]
        self.innings = 1
        self.wait_timeout = REFRESH_TIMEOUT  # 4 seconds of refresh rate. In actual it will be 4.4 seconds
        if len(match_id) == 6:
            self.match_id = int(match_id)
        else:
            self.match_id = int(match_id.split('-')[-1])

    def setLabelTextandAdjust(self, text, keep_aspect=False):
        QtCore.QMetaObject.invokeMethod(self.window.label, "setText", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, text))
        QtTest.QTest.qWait(400)
        if keep_aspect is False:
            self.window.label.adjustSize()
        self.resizeMainWindow(self.window.label.size().width(), self.window.label.size().height())

    def run(self):
        while True:
            try:
                innings, scorecard = cricket_query(match_id=self.match_id, innings=self.innings)
                self.innings = innings
                text = '\n'.join(scorecard)
                self.window.label.setStyleSheet("color: black;")
                self.setLabelTextandAdjust(text=text)
                QtTest.QTest.qWait(self.wait_timeout)
                self.window.label.setStyleSheet("color: green;")
            except Exception as e:
                logging.exception(e)
                QtTest.QTest.qWait(self.wait_timeout)


def scrollWheelEvent(workerThread, scroll_direction):
    # initiated = workerThread.is_initiated()
    # if initiated is False and scroll_direction == 'down':
    #     workerThread.more_info()
    # elif initiated is True and scroll_direction == 'up':
    #     workerThread.restore_layout()
    pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyMainWindow(workerThread=WorkerThread, sides=(175, 82), down_threshold=5,
                              scrollWheelCallable=scrollWheelEvent, up_threshold=3)
    MainWindow.show()
    sys.exit(app.exec_())
