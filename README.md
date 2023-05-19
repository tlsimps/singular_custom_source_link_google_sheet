# singular_custom_source_link_google_sheet

Pulls data from https://docs.google.com/spreadsheets/d/11nXbVf3LymFzu5vfdWQKaes2NzoJiS_xDIHYe6rxZyY/edit#gid=1659652832 sheet - request access

**NOT MEANT FOR USE IN PRODUCTION** - this is meant to be used as an example only of how to dynamically call the Singular Links API using some provided app data

**Use Case** - I have a new app(s) that I want to launch. The Marketing Team has already set up partner configurations for all partners and has added app info to the Sheet. 
I want to quickly create links for all of these partners, for the provided apps

1. Loads App and Bundle ID data from Google sheet - then checks to see which partners are configured in Singular's Partner Configuration
2. Uses Singular Links Helper APIs IDs to get required IDs and builds Tracking Link Creation API request
3. Creates Partner links for all Partners set up in Singular's Partner Configuration for the provided App/Bundle IDs
4. Writes links from API resonse to the Generated Links tab
