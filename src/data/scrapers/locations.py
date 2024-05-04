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