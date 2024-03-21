import re
import pandas
from Helper_Functions.mongo_silly import *


sheet_link = 'https://docs.google.com/spreadsheets/d/1oAUw5dZdqZa1FWqrBV9MQQTr8Eq8g33zwEb49vk3hrk/edit#gid=2053407537'
sheet_link_2 = 'https://docs.google.com/spreadsheets/d/1BIxKr3vqiQ909u1xCZbJR-RgDdPBocoMafy0Ov7ep04/edit#gid=0'

async def get_sheet_url(url : str):
    """Get the sheet data as a csv from any google sheet url `url`!"""
    # Regular expression to match and capture the necessary part of the URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'

    # Replace function to construct the new URL for CSV export
    # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
    replacement = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'

    # Replace using regex
    new_url = re.sub(pattern, replacement, url)

    return new_url

async def csv_conversion_roles() -> tuple[str, str]:
    """Limits the Role Sheet's .csv file to the two columns we need and returns the :class:`tuple` of values needed."""
    # grab the correct url
    new_url = await get_sheet_url(sheet_link_2)

    # read and slim the data as a .csv
    data_frame = pandas.read_csv(new_url)
    slimmed_df = data_frame.iloc[:, [2, 3]]

    # get it as a dict
    return await dataframe_to_dict_roles(slimmed_df)

async def dataframe_to_dict_roles(slimmed_df : pandas.DataFrame) -> tuple[str, str] :
    """Converts Role Sheet :class:`DataFrame` and turns it into a :class:`tuple`."""
    final_data : list[tuple[str, str]] = []
    for index, row in slimmed_df.iterrows():
        final_data.append((str(row[0]), str(row[1])))
    return final_data

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
