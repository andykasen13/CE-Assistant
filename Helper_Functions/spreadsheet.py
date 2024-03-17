import re
import pandas
from Helper_Functions.mongo_silly import *


sheet_link = 'https://docs.google.com/spreadsheets/d/1oAUw5dZdqZa1FWqrBV9MQQTr8Eq8g33zwEb49vk3hrk/edit#gid=2053407537'

async def get_sheet_url(url):

    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

    # Replace using regex
    new_url = re.sub(pattern, replacement, url)

    return new_url



async def csv_conversion():
    new_url = await get_sheet_url(sheet_link)


    data_frame = pandas.read_csv(new_url)
    slimmed_df = data_frame.loc[:, ["sh_appid", "sh_median"]]


    await dataframe_to_dict(slimmed_df)




async def dataframe_to_dict(slimmed_df):
    final_data = {}
    final_data['_id'] = mongo_ids['steamhunters']


    for index, row in slimmed_df.iterrows():
        final_data[str(int(row["sh_appid"]))] = row['sh_median']


    dump = await dump_mongo('steamhunters', final_data)
    del dump
