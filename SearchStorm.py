from netCDF4 import Dataset
from datetime import datetime, timedelta
import math
from haversine import haversine

#ALGORITMO SPAZIALE

def main():
    #DIMENSIONE AREA DI RICERCA
    SIZE = 25

    #CRITERI IDENTIFICAZIONE
    forward_speed = 10  # m/s
    slp_threshold = 1000  # hPa
    ws_threshold = 15  # m/s

    #CRITERI DATA
    start_date = datetime(2018, 10, 30, 0, 0, 0)
    stop_date = datetime(2018, 10, 30, 12, 0, 0)
    delta_hours = 1

    current_date = start_date
    L = []

    while current_date < stop_date:

        url = "/home/giangiui/Dropbox/Uni/Progetto/MedistormTracker/MEDIACANE_data/" + \
            "/wrf5_d01_" + \
              "{:04d}".format(current_date.year) + "{:02d}".format(current_date.month) + "{:02d}".format(
            current_date.day) + \
              "Z{:02d}".format(current_date.hour) + "{:02d}".format(current_date.minute) + ".nc"

        f = Dataset(url)
        lats = f.variables["latitude"][:]
        lons = f.variables["longitude"][:]
        slp = f.variables["SLP"][:][0]
        u10m = f.variables["U10M"][:][0]
        v10m = f.variables["V10M"][:][0]
        t2c = f.variables["T2C"][:][0]
        rh2 = f.variables["RH2"][:][0]
        uh = f.variables["UH"][:][0]

        for j in range(0, len(slp), SIZE):
            for i in range(0, len(slp[0]), SIZE):
                S = slp[j:j + SIZE, i:i + SIZE]
                iMin = None
                jMin = None
                for jj in range(0, len(S)):
                    for ii in range(0, len(S[0])):
                         if S[jj, ii] < slp_threshold:
                             iMin = i + ii
                             jMin = j + jj
                             ws = math.pow(u10m[jMin, iMin] * u10m[jMin, iMin] + v10m[jMin, iMin] * v10m[jMin, iMin],
                                           0.5)
                             if ws >= ws_threshold:
                                 L.append({"date": str(current_date), "lat": lats[jMin], "lon": lons[iMin],
                                           "data": {"slp": S[jj, ii], "ws": ws, "t2c": t2c[jMin, iMin],
                                                    "rh2": rh2[jMin, iMin],
                                                    "uh": uh[jMin, iMin]}})




        current_date = current_date + timedelta(hours=delta_hours)

    #ALGORITMO TEMPORALE
    # Input: L, velocità massima tempeste Umax, minima durata Tmin, criteri identificazione tempeste, Dmax distanza


    #CRITERI IDENTIFICAZIONE SUCCESSORE
    Umax = 15 #ms^-1
    mpsToKph = 3.6
    DMAX = Umax * mpsToKph * delta_hours

    #CRITERI IDENTIFICAZIONE TEMPESTA
    minDuration = 12  # hours
    maxSpeed = 30.0  # meters per second

    T = []
    current_date = start_date
    while current_date < stop_date:
        list_filtered = [item for item in L if (item['date'] == str(current_date))]
        for l in list_filtered:
            track = []
            track.append(l)
            continueC = True
            current_date_exam = current_date + timedelta(hours=delta_hours)
            while continueC == True:
                list_filtered_exam = [item for item in L if item['date'] == str(current_date_exam)]

                if list_filtered_exam:
                    for ll in list_filtered_exam:
                        current_distance = haversine((l["lat"], l["lon"]), (ll["lat"], ll["lon"]))
                        if current_distance < DMAX:
                            track.append(ll)
                            current_date_exam = current_date_exam + timedelta(hours=delta_hours)
                            break
                        else:
                            continueC = False
                else:
                    continueC = False

        if (len(track) >= 12):
            T.append(track)
        current_date = current_date + timedelta(hours=delta_hours)


    print(T)



if __name__ == "__main__":
    main()
