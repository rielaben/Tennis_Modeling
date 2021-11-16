import pandas as pd
pd.set_option('display.max_columns', None)

tennis_df = pd.DataFrame()
for year in range(2001, 2022):
    
    file = ""
    if year < 2013:
        file = f"{year}.xls"
        print(file)
    else:
        assert(year >= 2013)
        file = f"{year}.xlsx"
        print(file)
    
    year_df = pd.read_excel(file)
    year_df['Year'] = year
    tennis_df = tennis_df.append(year_df)

cols_list_drop = ['Best of', 'W1', 'L1',
       'W2', 'L2', 'W3', 'L3', 'W4', 'L4', 'W5', 'L5', 'Wsets', 'Lsets',
       'Comment', 'CBW', 'CBL', 'GBW', 'GBL', 'IWW', 'IWL', 'SBW', 'SBL',
        'B&WW', 'B&WL', 'EXW', 'EXL', 'PSW', 'PSL',
       'WPts', 'LPts', 'UBW', 'UBL', 'LBW', 'LBL', 'SJW', 'SJL', 'MaxW',
       'MaxL', 'AvgW', 'AvgL']

tennis_df = tennis_df.drop(cols_list_drop, axis=1)

tennis_df = tennis_df.dropna()

tennis_df.reset_index(inplace=True, drop=True)

tennis_df['WRank'] = tennis_df['WRank'].astype(int)
tennis_df['LRank'] = tennis_df['LRank'].astype(int)

tennis_df['B365W_prob'] = (1/tennis_df['B365W']).round(3)
tennis_df['B365L_prob'] = (1/tennis_df['B365L']).round(3)
tennis_df['B365_total_prob'] = tennis_df['B365W_prob'] + tennis_df['B365L_prob']
tennis_df['B365_diff_from_1'] = tennis_df['B365_total_prob'] - 1

# This takes VIM out to just get the real probabilities
tennis_df['real_prob_W'] = tennis_df['B365W_prob'] - (tennis_df['B365_diff_from_1']/2)
tennis_df['real_prob_L'] = tennis_df['B365L_prob'] - (tennis_df['B365_diff_from_1']/2)
tennis_df['real_total_prob'] = tennis_df['real_prob_W'] + tennis_df['real_prob_L']
tennis_df['real_diff_from_1'] = tennis_df['real_total_prob'] - 1

tennis_df_historical = tennis_df.copy()

def player_dict_generator(name, rank, prob):
    
    player_dict = {}
    player_dict['name'] = name
    player_dict['rank'] = rank
    player_dict['prob'] = prob
    
    return player_dict

def historical_match_data(player_name, date_of_match):
#     isolated all matches a player has played in (whole dataset)
    player_rank_history = tennis_df_historical.loc[(tennis_df_historical['Winner'] == player_name) | (tennis_df_historical['Loser'] == player_name)]
#     filter this so we're only looking at historical matches

    player_rank_history = player_rank_history.loc[player_rank_history['Date'] < date_of_match]
    
    return player_rank_history

def winning_percentage(player_df, player_name):
    
#     find where player wins, loses, then get percentage
    appears_winner = len(player_df.loc[player_df['Winner']==player_name])
    appears_loser = len(player_df.loc[player_df['Loser']==player_name])
    assert(appears_winner + appears_loser == len(player_df))
    winning_percentage = appears_winner/len(player_df)
    
    return winning_percentage

def winning_percentage_stats(player_history, player_name, court_type, surface_type, series_type):
    
#     isolate court type
    player_court_type = player_history.loc[player_history['Court']==court_type]
    
#     assert statements to check we isolated correctly
#     assert(len(set(player_court_type['Court']))==1)
#     assert(set(player_court_type['Court']).pop()==court_type)
    
#     repeat same as above for surface and series
    player_surface_type = player_history.loc[player_history['Surface']==surface_type]
    
#     assert(len(set(player_surface_type['Surface']))==1)
#     assert(set(player_surface_type['Surface']).pop()==surface_type)
    
    player_series_type = player_history.loc[player_history['Series']==series_type]
    
#     assert(len(set(player_series_type['Series']))==1)
#     assert(set(player_series_type['Series']).pop()==series_type)
    
    if (len(player_court_type) == 0) or (len(player_surface_type) == 0) or (len(player_series_type) == 0):
        return (None, None, None)
    else:
    #     put the above dataframes into the winning_percentage() function to calculate winning percentage
    #     based on these factors
        court_type_winning_pct = winning_percentage(
            player_df=player_court_type, 
            player_name=player_name)

        surface_type_winning_pct = winning_percentage(
            player_df=player_surface_type, 
            player_name=player_name)

        series_type_winning_pct = winning_percentage(
            player_df=player_series_type, 
            player_name=player_name)

        #print(player_name, court_type, surface_type, series_type)
    #     display(player_court_type)
    #     display(player_surface_type)
    #     display(player_series_type)

    #     return results as a tuple
        return court_type_winning_pct, surface_type_winning_pct, series_type_winning_pct

def player_stats(player, last_n_games, match_date, court_type, surface_type, series_type):
    
#     isolate player name, rank, win prob
    name = player['name']
    rank = player['rank']
    prob = player['prob']
    
#     get player historical data, calculate days since last match
#     player_history = historical_match_data(player_name=name)
    player_history = historical_match_data(
        player_name=name,
        date_of_match=match_date
    )
    
    if len(player_history) < last_n_games:
        return None
        
    else:
    #     .date()
        player_last_match = player_history.iloc[-1]['Date']
        #print(match_date, player_last_match)
        player_days_since_last_match = (match_date - player_last_match).days

    #     find player last n games (to calculate win percentage for recent matches)
        player_last_n_games = player_history[-last_n_games:]

    #     get player win pct
        player_win_pct = winning_percentage(
            player_df=player_last_n_games,
            player_name=name)

    #     get player win percentage on the court the match is on, the sruface type of the match, and the series type
        player_court_type_win_pct, player_surface_type_win_pct, player_series_type_win_pct = winning_percentage_stats(
            player_history=player_history, 
            player_name=name, 
            court_type=court_type,
            surface_type=surface_type,
            series_type=series_type
        )
        
        if (player_court_type_win_pct, player_surface_type_win_pct, player_series_type_win_pct) == (None, None, None):
            return None
        else:
    #     return all this info for the player
            ret_dict = {
                'name':name,
                'rank':rank,
                'prob':prob,
                'days_since_last_match': player_days_since_last_match,
                'win_pct': player_win_pct,
                'court_type_win_pct':player_court_type_win_pct,
                'surface_type_win_pct':player_surface_type_win_pct,
                'series_type_win_pct':player_series_type_win_pct
            }

            return ret_dict

from datetime import date

# this creates the dataset we can use for ML
# with feature engineering

def ML_df_function(df, start_row=None, end_row=None):

#     set up return DF with our new formatted data
#     to find what columns to put for final_df:
#     display(returned_row.keys())
    final_columns = ['ATP', 'Location', 'Tournament', 'Date', 'Year', 'Series', 'Court', 'Surface', 
                     'Round', 'HR_win?', 'diff_rank', 'diff_prob', 'diff_days_since_last_match', 
                     'diff_win_pct', 'diff_court_type_win_pct', 'diff_surface_type_win_pct', 
                     'diff_series_type_win_pct']
    final_df = pd.DataFrame(columns = final_columns)


#     iterate through rows of df, for each row we need to do manipulation
#     IMPORTANT: we are only looking at 5 rows
    for i in range(start_row,end_row):

#         create dictionary to return the new row
        returned_row = {}
        returned_row['ATP'] = df.loc[i,'ATP']
        returned_row['Location'] = df.loc[i,'Location']
        returned_row['Tournament'] = df.loc[i,'Tournament']
        returned_row['Date'] = df.loc[i,'Date']
        returned_row['Year'] = df.loc[i,'Year']
        returned_row['Series'] = df.loc[i,'Series']
        returned_row['Court'] = df.loc[i,'Court']
        returned_row['Surface'] = df.loc[i,'Surface']
        returned_row['Round'] = df.loc[i,'Round']


#         display original df row
#         display(row.to_frame().T)

#         get date of the match
        date_of_match = df.loc[i,'Date']

#         set up information about the winner and loser
        winner = player_dict_generator(
            name=df.loc[i,'Winner'], 
            rank=df.loc[i,'WRank'], 
            prob=df.loc[i,'real_prob_W'])


        loser = player_dict_generator(
            name=df.loc[i,'Loser'], 
            rank=df.loc[i,'LRank'], 
            prob=df.loc[i,'real_prob_L'])


#         figure out the higher and lower rank
        higher_rank = {}
        lower_rank = {}
        if winner['rank'] < loser['rank']:
            higher_rank = winner
            lower_rank = loser
        else:
            higher_rank = loser
            lower_rank = winner



#         get player stats for higher and lower rank
        higher_ranked_player_stats = player_stats(
            player=higher_rank, 
            last_n_games=10,
            match_date = df.loc[i,'Date'],
            court_type=df.loc[i,'Court'],
            surface_type=df.loc[i,'Surface'],
            series_type=df.loc[i,'Series']

        )

        lower_ranked_player_stats = player_stats(
            player=lower_rank, 
            last_n_games=10,
            match_date = df.loc[i,'Date'],
            court_type=df.loc[i,'Court'],
            surface_type=df.loc[i,'Surface'],
            series_type=df.loc[i,'Series']
        )
        
        if (higher_ranked_player_stats == None) or (lower_ranked_player_stats == None):
            i += 1
        else:
    #         display(higher_ranked_player_stats)
    #         display(lower_ranked_player_stats)

    #         for each stat, append this to the returned fr (row to be 
    #         added to new ML df)


            hr_name = higher_ranked_player_stats['name']
    #         print(hr_name)
            winner = df.loc[i,'Winner']
    #         print(winner)

            if hr_name == winner:
                returned_row['HR_win?']=1
            else:
                returned_row['HR_win?']=0

    #         print(hr_name==winner)
    #         deletes name so we are only taking diff on numeric columns
            del higher_ranked_player_stats['name']
            del lower_ranked_player_stats['name']


            value_keys = list(higher_ranked_player_stats.keys())
    #         display(value_keys)
    #         print("VALUES")
            high_rank_list = list(higher_ranked_player_stats.values())
            low_rank_list = list(lower_ranked_player_stats.values())

    #         display(high_rank_list)
    #         display(low_rank_list)
            diffs = [a_i - b_i for a_i, b_i in zip(high_rank_list, low_rank_list)]
    #         print("diffs")
    #         display(diffs)


            for key, diff in zip(value_keys, diffs):
                returned_row[f'diff_{key}'] = diff


            # display(returned_row.keys())
            final_df = final_df.append(returned_row, ignore_index=True)
    return final_df


        
ML_dataframe = ML_df_function(
    df=tennis_df, 
    start_row=0, end_row=5000
)

print(len(ML_dataframe))