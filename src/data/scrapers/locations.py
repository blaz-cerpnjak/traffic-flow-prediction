from collections import namedtuple

Location = namedtuple("Location", ["Latitude", "Longitude"])

LOCATIONS = {
    "MB_LJ": Location(46.557644, 15.645585),
    "LJ_Karavanke": Location(46.050027, 14.506929),
    "LJ_MB": Location(46.050027, 14.506929),
    "LJ_KP": Location(46.050027, 14.506929),
    "LJ_obv_zunanji_krog": Location(46.050027, 14.506929),
    "LJ_obv_notranji_krog": Location(46.050027, 14.506929),
    "LJ_MP_Obrežje": Location(46.050027, 14.506929),
    "Karavanke_LJ": Location(46.439581, 14.88217),
    "MP_Obrežje_LJ": Location(46.845435, 15.685373),
    "KP_LJ": Location(45.547986, 13.730478),
}