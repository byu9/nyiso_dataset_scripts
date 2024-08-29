from pathlib import Path
from urllib.request import urlretrieve

years = [2020, 2021, 2022, 2023]
months = list(range(1, 13))

fetch_urls = [
    f'http://mis.nyiso.com/public/csv/lfweather/{year:4}{month:02}01lfweather_csv.zip'
    for year in years
    for month in months
]

filenames = [
    Path(f'fetch_nyiso_weather/nyiso-{year}-{month}.zip')
    for year in years
    for month in months
]

for url, filename in zip(fetch_urls, filenames):
    if not filename.is_file():
        urlretrieve(url, filename=filename)
