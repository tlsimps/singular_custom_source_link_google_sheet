#Author: Travis Simpson
#last update 2023/05/19
#Tracking link creatiion - custom link types only

#Pulls data from https://docs.google.com/spreadsheets/d/13QUZ12vs3XyfC7VwMwLXRKSYOkP7b232w05gRcoPYz4/edit#gid=0 sheet 
#Groups data by Custom Source, App Name and Tracker Name - if more than 1 platform (iOS + Android) then a single link for both ios and android will be created
#Else separate links are created for iOS and Android
#Created links are also written to the Generated Links tab
#Shows example of how to get IDs from Helper APIs to build Tracking Link Creation API request -- NOT MEANT FOR USE IN PRODUCTION - this is meant to be used as an example only

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import requests
import json
import yaml
import datetime

# Google Sheet Auth
service_account_file = "/Users/your/path/client_secret.json"
sheet_file_key = "13QUZ12vs3XyfC7VwMwLXRKSYOkP7b232w05gRcoPYz4"
creds = Credentials.from_service_account_file(service_account_file, scopes=['https://www.googleapis.com/auth/spreadsheets'])
sheets_service = build("sheets", "v4", credentials=creds)

# Get data from the Google Sheet
sheet_data = sheets_service.spreadsheets().values().get(spreadsheetId=sheet_file_key, range='Tracking Link Creation Tool!A5:H').execute()
data = sheet_data.get("values", [])
columns = data[0]

# Load to df and clean
df = pd.DataFrame(data[1:], columns=columns)
df_jc = ['App Name', 'Platform', 'Bundle ID']
df[df_jc] = df[df_jc].apply(lambda x: x.str.lower())

#links api endpoints
api_key = '<your Singular Reporting API Key>'
create_link_url = "https://api.singular.net/api/v1/singular_links/links"
domains_url = "https://api.singular.net/api/v1/singular_links/domains"
apps_url = "https://api.singular.net/api/v1/singular_links/apps"

# Get app data and join to Sheet df
apps_response = requests.get(url=apps_url, headers={'Authorization': api_key})
app_data = apps_response.json()
available_apps_df = pd.DataFrame(app_data['available_apps'])
avail_apps_jc = ['app', 'app_platform', 'app_longname']
available_apps_df[avail_apps_jc] = available_apps_df[avail_apps_jc].apply(lambda x: x.str.lower())

merged_df = df.merge(available_apps_df, left_on = df_jc, right_on = avail_apps_jc)

#link subdomain mapping by app-- maybe handle in Google sheet instead?
app_subdomain = {
    'TLS Sample Apps' : 'seteam',
    'Android Sample App' : 'seobjc'
}
for app in app_data['available_apps']:
    if app['app'] in app_subdomain:
        app_subdomain[int(app['app_id'])] = app_subdomain.pop(app['app'])


#get link domains -- don't need this with the links dictionary above
domains_response = requests.get(url=domains_url, headers={'Authorization': api_key})
links_data = domains_response.json()

df_result = pd.DataFrame()

for _, group in merged_df.groupby(['Custom Source', 'app', 'Tracker Name']):
    if len(group) >= 2:
        payload = {
            "app_id": int(group['app_id'].iloc[0]),
            "link_type": "custom",
            "source_name": group['Custom Source'].iloc[0],
            "tracking_link_name": group['Custom Source'].iloc[0].replace(" ","") + "_" + group['Tracker Name'].iloc[0],
            "link_subdomain": app_subdomain[group['app_id'].iloc[0]],
            "link_dns_zone": "sng.link",
            "destination_fallback_url": "https://www.example.com/",
            "ios_redirection": {
                "app_site_id": int(group.loc[group['Platform'] == 'ios', 'app_site_id'].iloc[0]),
                "destination_url": group.loc[group['Platform'] == 'ios', 'store_url'].iloc[0], 
                "destination_deeplink_url": group.loc[group['Platform'] == 'ios', 'deep link'].iloc[0],
                "destination_deferred_deeplink_url": group.loc[group['Platform'] == 'ios', 'deep link'].iloc[0]
            },
            "android_redirection": {
                "app_site_id": int(group.loc[group['Platform'] == 'android', 'app_site_id'].iloc[0]),
                "destination_url": group.loc[group['Platform'] == 'android', 'store_url'].iloc[0], 
                "destination_deeplink_url": group.loc[group['Platform'] == 'android', 'deep link'].iloc[0],
                "destination_deferred_deeplink_url": group.loc[group['Platform'] == 'android', 'deep link'].iloc[0]
            },
            "enable_reengagement": "true",
            "link_parameter": {
                "_forward_params": "1",
                "_smtype": "3",
                "pcn": "my_campaign_name",
                "pscn": "my_sub_campaign_name",
                "wpcn": "my_campaign_name",
                "wpscn": "my_sub_campaign_name",
            }
        }
    else:
        row = group.iloc[0]
        platform_key = "ios_redirection" if row['Platform'] == "ios" else "android_redirection"
        payload = {
            "app_id": int(row['app_id']),
            "link_type": "custom",
            "source_name": group['Custom Source'].iloc[0],
            "tracking_link_name": row['Custom Source'].replace(" ","") + "_" + row['Tracker Name'],
            "link_subdomain": app_subdomain[row['app_id']],
            "link_dns_zone": "sng.link",
            "destination_fallback_url": "https://www.example.com/",
            platform_key: {
                "app_site_id": int(row['app_site_id']),
                "destination_url": row['store_url'], 
                "destination_deeplink_url": row['deep link'],
                "destination_deferred_deeplink_url": row['deep link']
            },
            "enable_reengagement": "true",
            "link_parameter": {
                "_forward_params": "1",
                "_smtype": "3",
                "pcn": "my_campaign_name",
                "pscn": "my_sub_campaign_name",
                "wpcn": "my_campaign_name",
                "wpscn": "my_sub_campaign_name",
            }
        }

    payload = json.dumps(payload)

    print("payload:",payload)
    response = requests.request("POST", create_link_url, headers={'Authorization': api_key}, data=payload)
    response_data = yaml.safe_load(response.text)
    print('response_data:',response_data)

    # Update df_result
    if 'ios_redirection' in payload and 'android_redirection' in payload:
        platform = 'ios and android'
    elif 'ios_redirection' in payload:
        platform = 'ios'
    elif 'android_redirection' in payload:
        platform = 'android'
    else:
        platform = ''

    df_result = df_result.append({
        'source_name': group['Custom Source'].iloc[0],
        'app_name': group['app'].iloc[0],
        'platform': platform,
        'tracking_link_id': response_data['tracking_link_id'] if 'error' not in response_data else None,
        'tracking_link_name': response_data['tracking_link_name'] if 'error' not in response_data else None,
        'click_tracking_link': response_data['click_tracking_link'] if 'error' not in response_data else None,
        'short_link': response_data['short_link'] if 'error' not in response_data else None,
        'impression_tracking_link': response_data['impression_tracking_link'] if 'error' not in response_data else None,
        'error_code': response_data['error']['code'] if 'error' in response_data else None,
        'error_message': response_data['error']['message'] if 'error' in response_data else None,
        'creation_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, ignore_index=True)
    print('df_result:',df_result)

    # Write df_result to Google Sheet
    values = df_result.T.reset_index().T.values.tolist()
    body = {
        "values": values,
    }

    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_file_key, range="Generated Links", valueInputOption="RAW", body=body
    ).execute()
