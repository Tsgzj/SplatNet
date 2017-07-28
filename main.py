#!/bin/python

import requests
import json
import datetime

def get_timestamp(offset = 0):
    # use the latest time slot by default
    # The API may not be available right after the league has ended
    c = datetime.datetime.utcnow()

    time_slot = ""
    flag = 0
    if (c.minute < 10):
        flag = 1

    if (c.hour % 2 == 0):
        time_slot = c - datetime.timedelta(hours=2 + 2 * (offset + flag))
    else:
        time_slot = c - datetime.timedelta(hours=3 + 2 * (offset + flag))

    return time_slot.strftime("%y%m%d%HT")

def get_cookie():
    # TODO: get the cookie
    f = open("cookies", "r")
    return f.read()

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

def process_data(pData, pType = "weapon"):
    res = {}
    for m in pData:
        name = m[pType]
        if name in res:
            c = res[name][1]
            res[name] = [(res[name][0] * c + m['point']) / (float(c) + 1), c + 1]
        else:
            res[name] = [m['point'], 1]

    final = []
    for key, value in sorted(res.iteritems(), key = lambda(k, v): (v[1], k), reverse=True):
        final.append([key, value[1] / float(len(pData)), value[0]])

    return final

if __name__ == "__main__":
    f = open("SplatNetData_wp_" + "{:02d}{:02d}".format(datetime.datetime.utcnow().month, datetime.datetime.utcnow().day), "w")
    all_data = []
    for i in range(12):
        lg_data = parse_response(send_request(i))
        all_data.extend(lg_data)

    f.write(json.dumps(all_data)) #Save the data for research purpose
    f.close()

    # Just print out the info
    final_wp = process_data(all_data)
    print "Weapon"
    for item in final_wp:
        print "{:24s} {:7.3%} {:7.3f}".format(item[0], item[1], item[2])

    print "\nSub"
    final_sub = process_data(all_data, "sub")
    for item in final_sub:
        print "{:24s} {:7.3%} {:7.3f}".format(item[0], item[1], item[2])

    print "\nSpecial"
    final_spe = process_data(all_data, "special")
    for item in final_spe:
        print "{:24s} {:7.3%} {:7.3f}".format(item[0], item[1], item[2])
