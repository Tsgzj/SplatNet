#!/bin/python

import requests
import json
import datetime

def get_timestamp(offset = 0):
    # use the latest time slot by default
    c = datetime.datetime.utcnow()
    time_slot = ""
    if (c.hour % 2 == 0):
        time_slot = c - datetime.timedelta(hours=2 + 2 * offset)
    else:
        time_slot = c - datetime.timedelta(hours=3 + 2 * offset)
    return time_slot.strftime("%y%m%d%HT")

def get_cookie():
    # TODO: get the cookie
    return "STAY FRESH"

def send_request(offset = 0):
    # Request
    # GET https://app.splatoon2.nintendo.net/api/league_match_ranking/[get_timestamp]/ALL
    # TODO: add support for multi-regions ?

    try:
        response = requests.get(
            url="https://app.splatoon2.nintendo.net/api/league_match_ranking/" + get_timestamp(offset) + "/ALL",
            headers={
                "Cookie": get_cookie(),
            },
        )
        return response.content

    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def parse_response(rData):
    data = json.loads(rData)
    rk = data['rankings']
    ranking = []
    for t in rk:
        p = t['point']
        for m in t['tag_members']:
            member = {}
            member['point'] = p
            member['weapon'] = m['weapon']['name']
            member['special'] = m['weapon']['special']['name']
            member['sub'] = m['weapon']['sub']['name']
            ranking.append(member)
    return ranking

if __name__ == "__main__":
    f = open("SplatNetData", "w") #removes the original file
    f.write(json.dumps(parse_response(send_request())))
    f.close()
