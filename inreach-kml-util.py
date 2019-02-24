from pykml import parser
from pprint import pprint
from io import BytesIO
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import csv
from skyfield.api import Topos, load
from datetime import tzinfo, timedelta, datetime
from LatLon import LatLon, Latitude, Longitude
from dateutil import tz
import sys

def inreach_time_to_dt(utc_time):
    # 2/15/2019 11:10:30 PM
    tzutc = tz.gettz('UTC')
    dt = datetime.strptime(str(utc_time), '%m/%d/%Y %I:%M:%S %p')
    dt = dt.replace(tzinfo=tzutc)
    return dt

def inreach_dec_to_deg(lat, lon):
    # in -33.385798,150.282861
    # out '40.8939 N'
    latlon_pos = LatLon(lat, lon)
    # lat, lon = latlon_pos.to_string('d% %m% %S% %H')
    lat, lon = latlon_pos.to_string('D% %H')
    # print(lat, lon)
    return lat, lon

def iridium_positions(utc_dt, lat_deg, lon_deg, elevation_m):
    elevation = str(elevation_m).split(" ")
    ts = load.timescale()
    t = ts.utc(utc_dt)
    # team_position = Topos(lat_deg, lon_deg)
    team_position = Topos('42.3583 N', '71.0603 W', elevation_m=float(elevation[0]))
    print(team_position)
    stations_url = 'http://celestrak.com/NORAD/elements/iridium-NEXT.txt'
    satellites = load.tle(stations_url)
    print(satellites['IRIDIUM 161'])


    # for satellite in satellites:
        # sat = satellite.
    sat_pos_geocentric = satellites['IRIDIUM 161'].at(t)
    print(sat_pos_geocentric.position.km)
    subpoint = sat_pos_geocentric.subpoint()
    print('Latitude:', subpoint.latitude)
    print('Longitude:', subpoint.longitude)
    print('Elevation (m):', int(subpoint.elevation.m))
    bluffton = Topos('40.8939 N', '83.8917 W')
    difference = sat_pos_geocentric - bluffton
    print(difference)

    difference = sat_pos_geocentric - team_position
    print(difference)
    topocentric = difference.at(t)
    print(topocentric.position.km)
    alt, az, distance = topocentric.altaz()

    if alt.degrees > 0:
        print('The satellite {} is above the horizon').format(satellites['IRIDIUM 161'])

    print(alt)
    print(az)
    print(distance.km)
    



with open('explore.kml', 'rt') as f:
    doc = f.read()

kml = parser.parse(BytesIO(doc)).getroot()

#0 - Id int
#1 - Time UTC str
#2 - Time str
#3 - Name str
#4 - Map Display Name str
#5 - Device Type str
#6 - IMEI str
#7 - Incident Id str
#8 - Latitude float
#9 - Longitude float
#10 - Elevation str
#11 - Velocity str
#12 - Course str
#13 - Valid GPS Fix bool
#14 - In Emergency bool
#15 - Text str
#16 - Event str

out_kml_folder = KML.Folder()
out_csv = [ [ 'Id', 'Time UTC', 'Time', 'Name', 'Map Display Name', 'Device Type', 'IMEI', 'Incident Id', 'Latitude', 'Longitude', 'Elevation', 'Velocity', 'Text', 'Event' ] ]

for unit in kml.Document.Folder:
    print(unit.name)
    team_folder = KML.Folder()
    for placemark in unit.Placemark:
        try:
            event = placemark.ExtendedData.Data[16].value
            if event == "Text message received.":
                if placemark.ExtendedData.Data[2].value != '':
                    time = placemark.ExtendedData.Data[2].value
                else:
                    time = 'unknown datetime'
                placemark.name = unit.name + ' ' + time
                team_folder.name = unit.name
                team_folder.append(placemark)
                # skyfield
                utc_dt = inreach_time_to_dt(placemark.ExtendedData.Data[2].value)
                lat_deg, lon_deg = inreach_dec_to_deg(placemark.ExtendedData.Data[8].value, placemark.ExtendedData.Data[9].value)
                # print(utc_dt, lat_dms, lon_dms)
                iridium_positions(utc_dt, lat_deg, lon_deg, placemark.ExtendedData.Data[10].value)
                csv_row = [ placemark.ExtendedData.Data[0].value, placemark.ExtendedData.Data[1].value, placemark.ExtendedData.Data[2].value, placemark.ExtendedData.Data[3].value, placemark.ExtendedData.Data[4].value, placemark.ExtendedData.Data[5].value, placemark.ExtendedData.Data[6].value, placemark.ExtendedData.Data[7].value, placemark.ExtendedData.Data[8].value, placemark.ExtendedData.Data[9].value, placemark.ExtendedData.Data[10].value, placemark.ExtendedData.Data[11].value, placemark.ExtendedData.Data[15].value, placemark.ExtendedData.Data[16].value
                ]
                out_csv.append(csv_row)
        except AttributeError as e:
            print(e)
            sys.exit(1)
            pass
        except Exception as e:
            print(e)
            sys.exit(1)
            raise
    out_kml_folder.append(team_folder)
    

with open('out.kml', 'w') as f:
    f.write(etree.tostring(out_kml_folder, pretty_print=True))

with open('out.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(out_csv)

print('Done!')