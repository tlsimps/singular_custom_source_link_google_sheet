# singular_custom_source_link_google_sheet

Pulls data from https://docs.google.com/spreadsheets/d/13QUZ12vs3XyfC7VwMwLXRKSYOkP7b232w05gRcoPYz4/edit#gid=0 sheet  - request access

**NOT MEANT FOR USE IN PRODUCTION** - this is meant to be used as an example only of how to dynamically call the Singular Links API using some provided app data

**Use Case** - Use source data with some information like Apps, bundle IDs, Platform, Tracker Name, desired redirect and deep linking behavior to dynamically create Custom Source Links using the Singular Links API. 

1. Loads data from Google sheet
2. Groups data by Custom Source, App Name and Tracker Name - if more than 1 platform (iOS + Android) then a single link for both ios and android will be created. Else separate links are created for iOS and Android
3. Uses Singular Links Helper APIs IDs to get required IDs and builds Tracking Link Creation API request
4. Creates Partner links for all Partners set up in Singular's Partner Configuration for the provided App/Bundle IDs
5. Writes links from API resonse to the Generated Links tab
