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

LOCATION_NAMES = {
    "MB_LJ": "Maribor - Ljubljana",
    "LJ_Karavanke": "Ljubljana - Karavanke",
    "LJ_MB": "Ljubljana - Maribor",
    "LJ_KP": "Ljubljana - Koper",
    "LJ_obv_zunanji_krog": "Ljubljana - obvoznica zunanji krog",
    "LJ_obv_notranji_krog": "Ljubljana - obvoznica notranji krog",
    "LJ_MP_Obrežje": "Ljubljana - MP Obrežje",
    "Karavanke_LJ": "Karavanke - Ljubljana",
    "MP_Obrežje_LJ": "MP Obrežje - Ljubljana",
    "KP_LJ": "Koper - Ljubljana",
}

HIGHWAY_LOCATIONS_COORDINATES = {
    "malecnik_ac": Location(46.5557564, 15.6981626),
    "ptujska_ac": Location(46.4994856, 15.678947),
    "hoce_ac": Location(46.500798, 15.6628986),
    "preloge_ac": Location(46.3660994, 15.5012708),
    "pletovarje_ac": Location(46.286597, 15.4227163),
    "gotovlje_ac": Location(46.2589978, 15.1554611),
    "lopata_ac": Location(45.7829672, 14.9012091),
    "vransko_ac": Location(46.2432712, 14.9502677),
    "jasovnik_ac": Location(46.2120134, 14.8992972),
    "psata_ac": Location(46.0993913, 14.6010713),
    "lj_vch_obvoznica": Location(46.0500268, 14.5069289),
    "drenov_gric_ac": Location(45.9963943, 14.3284194),
    "verd_ac": Location(45.9546421, 14.3011108),
    "ravbarkomanda_ac": Location(45.7846181, 14.2224807),
    "cebulovica_ac": Location(45.705303, 13.9909601),
    "laze_ac": Location(45.7352111, 14.0690637),
    "dekani_ac": Location(45.5483275, 13.8103444),
    "bertoki_hc": Location(45.5453198, 13.7665528),
}

HIGHWAY_LOCATIONS = {
    "malecnik_ac": {
        "direction_mb": "Malečnik AC : MB",
        "direction_lj": "Malečnik AC : Dragučova"
    },
    "ptujska_ac": {
        "direction_mb": "Ptujska AC : Slivnica",
        "direction_lj": "Ptujska AC : Maribor - Slivnica"
    },
    "hoce_ac": {
        "direction_mb": "Hoče AC : Fram - Slivnica",
        "direction_lj": "Hoče AC : Slivnica - Fram"
    },
    "preloge_ac": {
        "direction_mb": "Preloge AC : Slov. Konjice - Slov.",
        "direction_lj": "Preloge AC : Slov. Bistrica - Slov."
    },
    "pletovarje_ac": {
        "direction_mb": "Pletovarje AC : Dramlje - Slovenske Konjice",
        "direction_lj": "Pletovarje AC : Slovenske Konjice - Dramlje"
    },
    "gotovlje_ac": {
        "direction_mb": "Gotovlje : smer MB",
        "direction_lj": "Gotovlje : smer LJ"
    },
    "lopata_ac": {
        "direction_mb": "Lopata AC : Arja vas - Celje",
        "direction_lj": "Lopata AC : Celje - Arja vas"
    },
    "vransko_ac": {
        "direction_mb": "Vransko AC : Vransko - Šentrupert",
        "direction_lj": "Vransko AC : Šentrupert - Vransko"
    },
    "jasovnik_ac": {
        "direction_mb": "Jasovnik AC : Trojane - Vransko",
        "direction_lj": "Jasovnik AC : Vransko - Trojane"
    },
    "psata_ac": {
        "direction_mb": "Pšata AC : smer MB",
        "direction_lj": "Pšata AC : smer LJ"
    },
    "lj_vch_obvoznica": {
        "direction_mb": "LJ (vzh. obvoznica) : smer Zadobrova",
        "direction_mb": "LJ (vzh. obvoznica) : smer Malence"
    },
    "drenov_gric_ac": {
        "direction_lj": "Drenov Grič AC : Vrhnika - Brezovica",
        "direction_kp": "Drenov Grič AC : Brezovica - Vrhnika"
    },
    "verd_ac": {
        "direction_lj": "Verd AC : smer LJ",
        "direction_kp": "Verd AC : smer KP"
    },
    "ravbarkomanda_ac": {
        "direction_lj": "Ravbarkomanda AC : Postojna - Unec",
        "direction_kp": "Ravbarkomanda AC : Unec - Postojna"
    },
    "cebulovica_ac": {
        "direction_lj": "Čebulovica AC : Gabrk - Senožeče",
        "direction_kp": "Čebulovica AC : Senožeče - Gabrk"
    },
    "laze_ac": {
        "direction_lj": "Laze AC : Unec - Logatec",
        "direction_kp": "Laze AC : Logatec - Unec"
    },
    "dekani_ac": {
        "direction_lj": "Dekani AC : Črni Kal - Srmin",
        "direction_kp": "Dekani AC : Črni Kal - Srmin"
    },
    "bertoki_hc": {
        "direction_kp": "Bertoki HC : Bertoki - Koper",
    },
}