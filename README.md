# 🚲 Bike Route Analyzer 
## What's the fastest way from A to B?
An app to analyze routes in gpx format to identify the most common starting and end points and analyze:
- duration of each routes
- speed 
- "Crow Speed", i.e. the crow distance divided by time

... across:
- common start/end-point combinations (called "startendcluster" in the app) 
- common routes for these combinations (called "clusters" in the app)
- temperature
- weekday
- season
- time of the day

The app is currently only tested with `gpx` files, recorded and downloaded from [https://www.bikecitizens.net/de/](bikecitizens.net), a wonderful app with easy recording functionality.

## Screenshot
![Screenshot](https://github.com/Dronakurl/gpxfun/blob/main/Screenshot%20from%202023-03-12%2023-45-47.png?raw=true)

## Installation
The python dependencies are shown in the file `pyproject.toml`. You can install and run with `poetry`:
```
poetry install
poetry run gunicorn app:app -b :8080
```
You can also install and run with `pip`:
```
pip install -r requirements.txt 
gunicorn app:app -b :8080
```
With `python app.py`, you can run the application in dash debug mode

## Todos
### Data
- test other sources than bike citizens
- data augmentation
- generate random test data
- include fitbit data

### Analyzers
- tree models
- classification models
- SVC-algorithm, infer insights on features by probing predictions

### GUI
- Accordion GUI for the workflow on the left panel
- Show single paths in a map when clicking on individual data
- Better coloring for Start and end
- Label Start/End clusters by getting addresses
- get average path for each cluster 
