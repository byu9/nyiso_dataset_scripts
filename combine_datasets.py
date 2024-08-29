from glob import glob

import pandas as pd

pd.set_option('display.max_columns', None)


def read_load_fragments():
    fragment_filenames = glob('unpack_nyiso_load/*.csv')
    fragments = [
        pd.read_csv(filename, index_col='Time Stamp', parse_dates=['Time Stamp'])
        for filename in fragment_filenames
    ]
    dataset = pd.concat(fragments, axis='index')

    dataset = dataset.tz_localize('America/New_York', ambiguous=(dataset['Time Zone'] == 'EDT'))
    dataset.index.name = 'Local Time'
    dataset.drop(columns=['Time Zone', 'PTID'], inplace=True)

    return dataset


def read_weather_fragments():
    fragment_filenames = glob('unpack_nyiso_weather/*.csv')
    fragments = [
        pd.read_csv(filename, index_col='Forecast Date', parse_dates=['Forecast Date'])
        for filename in fragment_filenames
    ]
    dataset = pd.concat(fragments, axis='index')

    dataset = dataset.tz_localize('America/New_York')
    dataset.index.name = 'Local Time'

    dataset = dataset[dataset['Vintage'] == 'Forecast']
    dataset = dataset[['Station ID', 'Max Temp', 'Min Temp', 'Max Wet Bulb', 'Min Wet Bulb']]

    return dataset


weather_station_zones = pd.DataFrame.from_dict({
    'ALB': 'CAPITL',  # Albany, Albany County
    'ART': 'MHK VL',  # Watertown, Jefferson County
    'BGM': 'CENTRL',  # Binghampton, Broome County
    'BUF': 'WEST',  # Buffalo, Erie County
    'ELM': 'CENTRL',  # Elmira, Chemung County
    'ELZ': 'GENESE',  # Wellsville, Allegany County
    'FOK': 'LONGIL',  # Westhampton Beach, Suffolk County
    'FRG': 'LONGIL',  # Farmingdale, Nassau County
    'GFL': 'CAPITL',  # Glens Falls, Warren County
    'HPN': 'DUNWOD',  # White Plains, Westchester County
    'IAG': 'WEST',  # Niagara Falls, Niagara County
    'ISP': 'LONGIL',  # Islip, Suffolk County
    'ITH': 'CENTRL',  # Ithaca, Tompkins County
    'JFK': 'N.Y.C.',  # JFK airport, Queens County
    'LGA': 'HUD VL',  # LaGuardia airport, Hudson County
    'MSS': 'MHK VL',  # Massena, St. Lawrence County
    'MSV': 'MHK VL',  # Monticello, Sullivan County
    'NYC': 'N.Y.C.',  # NYC - Central Park, Kings County
    'PLB': 'NORTH',  # Plattsburgh, Clinton County
    'POU': 'HUD VL',  # Poughkeepsie , Dutchess County
    'ROC': 'GENESE',  # Rochester, Monroe County
    'SLK': 'MHK VL',  # Saranac Lake, Franklin County
    'SWF': 'HUD VL',  # Newburgh, Orange County
    'SYR': 'CENTRL',  # Syracuse , Onondaga County
    'UCA': 'MHK VL',  # Rome, Oneida County
}, orient='index')

weather_data = read_weather_fragments()
weather_data = weather_data.merge(weather_station_zones, left_on='Station ID', right_index=True)
weather_data = weather_data.drop(columns='Station ID')
weather_data = weather_data.rename(columns={0: 'Zone'})
weather_data = weather_data.reset_index().groupby(['Local Time', 'Zone']).mean()
weather_data = weather_data.reset_index()

load_data = read_load_fragments().rename(columns={'Name': 'Zone'})
load_data = load_data.merge(weather_data, how='left', left_on=['Local Time', 'Zone'],
                            right_on=['Local Time', 'Zone']).set_index('Local Time')

load_data = pd.pivot(load_data, columns='Zone')
load_data.columns = load_data.columns.swaplevel()

filenames = {
    'N.Y.C.': 'NYC',
    'CAPITL': 'CAPITL',
    'CENTRL': 'CENTRL',
    'DUNWOD': 'DUNWOD',
    'GENESE': 'GENESE',
    'HUD VL': 'HUD_VL',
    'LONGIL': 'LONGIL',
    'MHK VL': 'MHK_VL',
    'NORTH': 'NORTH',
    'WEST': 'WEST'
}

for zone, filename in filenames.items():
    zonal = load_data[zone]
    zonal.to_csv(f'combine_datasets/{filename}.csv')
