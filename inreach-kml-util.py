from pykml import parser
from pprint import pprint
from io import BytesIO
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import csv

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
                csv_row = [ placemark.ExtendedData.Data[0].value, placemark.ExtendedData.Data[1].value, placemark.ExtendedData.Data[2].value, placemark.ExtendedData.Data[3].value, placemark.ExtendedData.Data[4].value, placemark.ExtendedData.Data[5].value, placemark.ExtendedData.Data[6].value, placemark.ExtendedData.Data[7].value, placemark.ExtendedData.Data[8].value, placemark.ExtendedData.Data[9].value, placemark.ExtendedData.Data[10].value, placemark.ExtendedData.Data[11].value, placemark.ExtendedData.Data[15].value, placemark.ExtendedData.Data[16].value
                ]
                out_csv.append(csv_row)
        except AttributeError as e:
            pass
        except Exception as e:
            print(e)
            raise
    out_kml_folder.append(team_folder)
    

with open('out.kml', 'w') as f:
    f.write(etree.tostring(out_kml_folder, pretty_print=True))

with open('out.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(out_csv)

print('Done!')