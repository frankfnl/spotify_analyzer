# Spotify Analyzer

I have always wondered what my music listening habits are 🎵.
That's why I created this dashboard to get to know, understand and visualize 📈 the relationship with my favorite music.
From a personal overview, to listening patterns, and top tracks/artists.

Here, I present you my personal Spotify dashboard 🎉. An interactive web application built using Spotify's API data obtained via Python, transformed using Pandas and visualized with Plotly Dash.
The application is live on [Render](https://spotify-analyzer-b1vf.onrender.com/) and the code is available on my [Github](https://github.com/frankfnl/spotify_analyzer)


## Screenshots
![App Screenshot](/src/assets/screenshot.png)

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file. For more information please read [Spotify Authorization Code Flow](https://developer.spotify.com/documentation/web-api/tutorials/code-flow) documentation

`client_id` The Client ID generated after registering your application.

`client_secret` Client Secret needed to request an access token

`redirect_uri` The value of this parameter must exactly match the value of redirect_uri supplied when requesting the authorization code.

`refresh_token` A refresh token is a security credential that allows client applications to obtain new access tokens without requiring users to reauthorize the application.See [refreshing tokens](https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens)

`base_64` Base 64 encoded string that contains the client ID and client secret key. The field must have the format: Authorization: Basic <base64 encoded client_id:client_secret>

## Installation
Clone this repository and run pip to install the required packages (Python 3.9)

```python
py -m pip install requirements.txt
```

To start the app locally navigate to `src` and run with

```python
py -m app
```

## 🚀 About Me
🔬 From Biotech to Bytes 🐍

Former biotech engineer 🧪 now wandering through the world of Python 🐍 with a passion for decoding data into art 📊🎨. Catch me crafting code for harmonious music projects 🎶 and unraveling the secrets of life sciences 🧬 on this digital journey! 🚀 #BiotechByDayCoderByNight

- [@frankfnl](https://www.github.com/frankfnl)


## Acknowledgements
## Authors and acknowledgment
 - ![Francisco Nava Morales](https://img.shields.io/badge/Francisco%20Nava%20Morales-Author-green?style=flat)
 - [Awesome Readme Templates](https://awesomeopensource.com/project/elangosundar/awesome-README-templates)
 - [Charming Data](https://www.youtube.com/@CharmingData)