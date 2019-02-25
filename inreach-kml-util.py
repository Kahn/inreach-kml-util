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
    # in 2/15/2019 11:10:30 PM
    tzutc = tz.gettz('UTC')
    dt = datetime.strptime(str(utc_time), '%m/%d/%Y %I:%M:%S %p')
    dt = dt.replace(tzinfo=tzutc)
    return dt

def inreach_dec_to_deg(lat, lon):
    # in -33.385798,150.282861
    # out '40.8939 N'
    latlon_pos = LatLon(lat, lon)
    lat, lon = latlon_pos.to_string('D% %H')
    return lat, lon

def get_iridium_passes(utc_dt, lat_deg, lon_deg, elevation_m):

    stations_url = 'http://celestrak.com/NORAD/elements/iridium-NEXT.txt'
    satellites = load.tle(stations_url)
    passes = []
    for sat in satellites:
        if "IRIDIUM" in str(sat):
            elevation = str(elevation_m).split(" ")
            ts = load.timescale()
            t = ts.utc(utc_dt)
            geocentric = satellites[sat].at(t)
            subpoint = geocentric.subpoint()
            team = Topos(lat_deg, lon_deg, elevation_m=float(elevation[0]))
            difference = satellites[sat] - team
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()
            if alt.degrees > 9:
                pass_details = {
                    "sat": sat,
                    "alt_deg": alt.degrees,
                    "az_deg": az.degrees,
                    "dist_km": distance.km
                }
                passes.append(pass_details)
    return passes


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
                placemark.name = unit.name
                # skyfield
                utc_dt = inreach_time_to_dt(placemark.ExtendedData.Data[2].value)
                lat_deg, lon_deg = inreach_dec_to_deg(placemark.ExtendedData.Data[8].value, placemark.ExtendedData.Data[9].value)
                passes = get_iridium_passes(utc_dt, lat_deg, lon_deg, placemark.ExtendedData.Data[10].value)
                placemark.description = "  ## Event details ##  \n"
                placemark.description += "Time: {}\n".format(placemark.ExtendedData.Data[2].value)    
                placemark.description += "Inreach text: {}\n".format(placemark.ExtendedData.Data[15].value)
                placemark.description += "\n"
                placemark.description += "  ## Orbital Details ##  \n"
                for p in passes:
                    placemark.description += "Satellite: {}\n".format(p['sat'])
                    placemark.description += "Elevation Angle degrees: {}\n".format(p['alt_deg'])
                    placemark.description += "Compass Heading degrees: {}\n".format(p['az_deg'])
                    placemark.description += "Path Distance Km: {}\n".format(p['dist_km'])

                team_folder.name = unit.name
                team_folder.append(placemark)

                csv_row = [ placemark.ExtendedData.Data[0].value, placemark.ExtendedData.Data[1].value, placemark.ExtendedData.Data[2].value, placemark.ExtendedData.Data[3].value, placemark.ExtendedData.Data[4].value, placemark.ExtendedData.Data[5].value, placemark.ExtendedData.Data[6].value, placemark.ExtendedData.Data[7].value, placemark.ExtendedData.Data[8].value, placemark.ExtendedData.Data[9].value, placemark.ExtendedData.Data[10].value, placemark.ExtendedData.Data[11].value, placemark.ExtendedData.Data[15].value, placemark.ExtendedData.Data[16].value
                ]
                out_csv.append(csv_row)
        except AttributeError as e:
            print(e)
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