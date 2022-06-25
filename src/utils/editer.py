import xml.etree.ElementTree as ET


def get_iblc():
    tree = ET.parse('./src/template/InfluxdbBackendListenerClient.jmx')
    root = tree.getroot()
    influxdb_backend_listener_client = root[0][1][2]
    return influxdb_backend_listener_client


def remake(jmx, new_jmx):
    tree = ET.parse(jmx)
    root = tree.getroot()
    root[0][1].append(get_iblc())
    tree.write(new_jmx)
