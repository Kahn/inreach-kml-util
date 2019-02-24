from skyfield.api import Topos, load

ts = load.timescale()
t = ts.utc(2019, 2, 17, 11, 18, 7)
stations_url = 'http://celestrak.com/NORAD/elements/iridium-NEXT.txt'
satellites = load.tle(stations_url)
print(satellites['IRIDIUM 161'])
sat_pos_geocentric = satellites['IRIDIUM 161'].at(t)
print(sat_pos_geocentric.position.km)
subpoint = sat_pos_geocentric.subpoint()
print('Latitude:', subpoint.latitude)
print('Longitude:', subpoint.longitude)
print('Elevation (m):', int(subpoint.elevation.m))
bluffton = Topos('40.8939 N', '83.8917 W')
difference = sat_pos_geocentric - bluffton
print(difference)