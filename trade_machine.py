from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from espn_api.basketball import League
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

#data to find correct league and setup the league item

s2d = 'AEApboKD%2FnlwG%2BlfJ7mkTaIlwEzl9o3%2BpFPpyxpT8qDvkyYGYmmK1MAKeTj71D3%2F4j24RcmtVKUvZ010Sf09X%2BAyvP%2FaZ3OkIre4vw%2BG14B1coddvbMaBOoqO2i%2BIdRaHcogthvrGBDc9WF5p0q5Linb0Al%2BLU1lSFGd91eFZxzSfiDbKWGUTr9MAX2nyVbuKivb5R5e4J6V78qafNoxnH4Vqxfb0N6PRS5kZtV35p6xL%2FXtMOp%2B8Be%2FVx6KlJPOKGLT%2FoonWDxM6Td%2Bk0heEMit6IbPZuM50Kcx58lHEOrmew%3D%3D'
swd = '{817F7C41-C9C5-43F7-BF7C-41C9C5F3F7EB}'
lidd = 780758162

league = League(league_id=lidd, year=2023, espn_s2 = s2d, swid = swd)

#setting up the stats we want to pull for each team
stats = ['PTS','BLK','STL','AST','OREB','DREB','TO','FGM','FTM','3PTM', 'FGA', '3PTA', 'FTA']

#creating a dictionary of each team, with each team's cumulated stat in the categories above, and cleaning it
avgs = dict()

for team in league.teams:
    avgs[team.team_name] = dict()
    for stat in stats:
        avgs[team.team_name][stat] = 0
    for player in team.roster:
        try: 
            for stat in player.stats['2023_total']['avg']:
                if stat in stats:
                    avgs[team.team_name][stat] += player.stats['2023_total']['avg'][stat]
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

teamcomp = 0
tradingdf = 0
tmpteam1 = dict()

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html', data=kys)

@app.route('/comp', methods=['POST','GET'])
def comp():
    #gather league id of two trading teams and show df with the stats from both teams

    myteam = league.teams[int(request.form['myteamid'])].team_name
    otherteam = league.teams[int(request.form['otherteamid'])].team_name
    teamcomp = cleandf.loc[[myteam, otherteam, 'mean', 'stddev']]
    #new df that just shows the stats of the players you are trading away
    trading = dict()
    players_giving = str(request.form['giving'])
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
    players_getting = str(request.form['getting'])
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
    comp = [teamcomp.loc[[myteam]],tmpteam1df]
    comp = pd.concat(comp)
    diffs = comp.diff()
    comp = comp.append(diffs)
    i = diffs.index.tolist()[1]
    return render_template('index.html', data=kys, data1=teamcomp.to_html(), data2=tradingdf.to_html(), data3=diffs.loc[[i]].to_html())
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')