from netCDF4 import Dataset
from datetime import datetime, timedelta
import math


def main():
    SIZE = 25
    forward_speed = 10 # m/s
    slp_threshold = 1000  # hPa
    ws_threshold = 15  # m/s
    start_date = datetime(2018, 10, 29, 0, 0, 0)
    stop_date = datetime(2018, 10, 31, 0, 0, 0)
    delta_hours = 1

    current_date=start_date

    T=[]

    while current_date < stop_date:



        L=[]


        url="http://193.205.230.6:8080/opendap/hyrax/opendap/wrf5/d01/archive/" + \
            "{:04d}".format(current_date.year) + "/" + \
            "{:02d}".format(current_date.month) + "/" + \
            "{:02d}".format(current_date.day) + "/wrf5_d01_" + \
            "{:04d}".format(current_date.year) + "{:02d}".format(current_date.month) + "{:02d}".format(current_date.day) + \
            "Z{:02d}".format(current_date.hour) + "{:02d}".format(current_date.minute)+".nc"
        #print url
        f = Dataset(url)
        lats = f.variables["latitude"][:]
        lons = f.variables["longitude"][:]
        slp = f.variables["SLP"][:][0]
        u10m = f.variables["U10M"][:][0]
        v10m = f.variables["V10M"][:][0]
        t2c = f.variables["T2C"][:][0]
        rh2 = f.variables["RH2"][:][0]
        uh = f.variables["UH"][:][0]

        for j in range(0,len(slp),SIZE):
            for i in range(0,len(slp[0]),SIZE):
                S=slp[j:j+SIZE,i:i+SIZE]
                iMin=None
                jMin=None
                slp_min=1e37
                for jj in range(0,len(S)):
                    for ii in range(0, len(S[0])):
                        if S[jj, ii] < slp_min:
                            slp_min=S[jj, ii]
                            iMin=i+ii
                            jMin=j+jj
                if slp_min < slp_threshold:
                    ws=math.pow(u10m[jMin, iMin]*u10m[jMin, iMin]+v10m[jMin, iMin]*v10m[jMin, iMin], 0.5)
                    if ws >= ws_threshold:
                        L.append({"date": str(current_date), "lat": lats[jMin], "lon": lons[iMin], "data": { "slp":slp_min, "ws": ws, "t2c": t2c[jMin,iMin],"rh2":rh2[jMin,iMin], "uh":uh[jMin,iMin]}})

        for l in L:
            print l

        T.append(L)
        current_date = current_date+timedelta(hours=delta_hours)


if __name__ == "__main__":
    main()