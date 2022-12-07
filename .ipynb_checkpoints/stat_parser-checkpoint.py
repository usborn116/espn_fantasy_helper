#use pip install espn-api to get the espn api
from espn_api.basketball import League

s2 = input('Enter s2 of your league: ')
sw = input('Enter the SWID of your league: ')
lid = input('Enter your league;s ID: ')

#initializing league
league = League(league_id=lid, year=2023, espn_s2 = s2, swid = sw)

#stats we care about!
stats = ['PTS','BLK','STL','AST','OREB','DREB','GP','TO','FTM','3PTM','FT%']

totals = dict()

#collecting each team's total stats

for team in league.teams:
    for stat in team.stats:
        if stat in stats and stat not in totals:
            totals[stat] = dict()
            totals[stat][team] = team.stats[stat]
        elif stat in stats:
            totals[stat][team] = team.stats[stat]

#putting the data in a Pandas dataframe and analyzing that data

df = pd.DataFrame(totals)
df.describe()

#setting your team (change the index to be whatever your team's index is)
myteam = league.teams[6]

#cleaning up the stats, since there are a bunch of less important statistics
clean_stats = dict()
for stat in myteam.stats:
    if stat in stats:
        clean_stats[stat] = myteam.stats[stat]
print(clean_stats)

#creating a dictionary and getting a dataframe of the breakdown of stats for all players
allstats = dict()
for team in league.teams:
    for player in team.roster:
        try: 
            for stat in player.stats['2023_total']['avg']:
                if stat in stats and stat not in allstats:
                    allstats[stat] = dict()
                    allstats[stat][player] = player.stats['2023_total']['avg'][stat]
                elif stat in stats:
                    allstats[stat][player] = player.stats['2023_total']['avg'][stat]
        except:
            continue

dfstat = pd.DataFrame(allstats)
dfstat.describe()

#creating a dictionary and getting a dataframe of the breakdown of stats for all Centers

cstats = dict()
for team in league.teams:
    for player in team.roster:
        if player.position == 'C':
            try: 
                for stat in player.stats['2023_total']['avg']:
                    if stat in stats and stat not in cstats:
                        cstats[stat] = dict()
                        cstats[stat][player] = player.stats['2023_total']['avg'][stat]
                    elif stat in stats:
                        cstats[stat][player] = player.stats['2023_total']['avg'][stat]
            except:
                continue

cstat = pd.DataFrame(cstats)
cstat.describe()