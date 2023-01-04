from espn_api.basketball import League
import pandas as pd
import sqlite3

#data to find correct league and setup the league item

s2d = str(input("Paste your league's s2 ID here:\n"))
swd = str(input("Paste your league's swID here:\n"))
lidd = int(input("Paste your league's ID here:\n"))

league = League(league_id=lidd, year=2023, espn_s2 = s2d, swid = swd)

#setting up the stats we want to pull for each team
stats = ['PTS','BLK','STL','AST','OREB','DREB','TO','FGM','FTM','3PTM', 'FGA', '3PTA', 'FTA']

#creating a dictionary of each team, with each team's cumulated stat in the categories above, and cleaning it

avgs = dict()

for team in league.teams:
    avgs[team] = dict()
    for stat in stats:
        avgs[team][stat] = 0
    for player in team.roster:
        try: 
            for stat in player.stats['2023_total']['avg']:
                if stat in stats:
                    avgs[team][stat] += player.stats['2023_total']['avg'][stat]
        except:
            continue
            
df = pd.DataFrame(avgs)
df = df.transpose()
df['AFG%'] = (df['3PTM']*0.5+df['FGM'])/df['FGA']
df['A/TO'] = df['AST']/df['TO']
df['FT%'] = df['FTM']/df['FTA']
df.loc['mean'] = df.mean()
df.loc['stddev'] = df.std()
cleandf = df[['PTS', 'BLK','STL','AST','OREB','DREB','FTM','3PTM','AFG%','A/TO','FT%']]

#creating a dict to show each team's index number and showing that dictionary for reference

kys = dict()
i = 0
for row in df.itertuples():
    if i < 12:
        kys[row.Index] = i
        i += 1
        
def print_id():
    print('This is each team ID:')
    for k in kys:
        print(k, ':', kys[k])

print_id()

#gather league id of two trading teams and show df with the stats from both teams

myteam = league.teams[int(input('What is your team ID?\n'))]
otherteam = league.teams[int(input("What is your trade partner's team ID?\n"))]
team_comp = cleandf.loc[[myteam, otherteam, 'mean', 'stddev']]
print('This is how the teams compare:')
print(team_comp)

#new df that just shows the stats of the players you are trading away
trading = dict()
players_giving = input("Enter the players you are trading, separated by a comma, with no spaces in between\n")
to_trade = players_giving.split(',')

for player in to_trade:
    player = player.strip()
    trading[player] = dict()
    for stat in league.player_info(name = player).stats['2023_total']['avg']:
        if stat in stats:
            trading[player][stat] = league.player_info(name = player).stats['2023_total']['avg'][stat]
            
tradingdf = pd.DataFrame(trading)
tradingdf = tradingdf.transpose()
tradingdf['AFG%'] = (tradingdf['3PTM']*0.5+tradingdf['FGM'])/tradingdf['FGA']
tradingdf['A/TO'] = tradingdf['AST']/tradingdf['TO']
tradingdf['FT%'] = tradingdf['FTM']/tradingdf['FTA']
tradingdf = tradingdf[['PTS', 'BLK','STL','AST','OREB','DREB','FTM','3PTM','AFG%','A/TO','FT%']]

print('These are your player\'s stats:')
print(tradingdf)

#new dataframe of my team that shows the stats if I traded away certain players
tmpteam1 = dict()

for stat in stats:
    tmpteam1[stat] = 0

for player in league.teams[5].roster:
    if player.name not in to_trade:
        try: 
            for stat in player.stats['2023_total']['avg']:
                if stat in stats:
                    tmpteam1[stat] += player.stats['2023_total']['avg'][stat]
        except:
            continue
tmpteam1df = pd.DataFrame(tmpteam1, index=[league.teams[5].team_name])
tmpteam1df

#new dataframe of my team that shows the stats if I added certain players in a trade
players_getting = input("Enter the players you are getting, separated by a comma, with no spaces in between\n")
to_attain = players_getting.split(',')
for player in to_attain:
    player = player.strip()
    for stat in league.player_info(name = player).stats['2023_total']['avg']:
        if stat in stats:
            tmpteam1[stat] += league.player_info(name = player).stats['2023_total']['avg'][stat]
            
tmpteam1df = pd.DataFrame(tmpteam1, index=[league.teams[5].team_name])
tmpteam1df['AFG%'] = (tmpteam1df['3PTM']*0.5+tmpteam1df['FGM'])/tmpteam1df['FGA']
tmpteam1df['A/TO'] = tmpteam1df['AST']/tmpteam1df['TO']
tmpteam1df['FT%'] = tmpteam1df['FTM']/tmpteam1df['FTA']
tmpteam1df = tmpteam1df[['PTS', 'BLK','STL','AST','OREB','DREB','FTM','3PTM','AFG%','A/TO','FT%']]

#created df that shows how my categories change after the trade
comp = [team_comp.loc[[myteam]],tmpteam1df]
comp = pd.concat(comp)
diffs = comp.diff()
comp = comp.append(diffs)
print('This is how your team is affected:')
i = diffs.index.tolist()[1]
print(diffs.loc[[i]])