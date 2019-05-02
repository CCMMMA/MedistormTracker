from netCDF4 import Dataset
from datetime import datetime, timedelta
from haversine import haversine
import json
import math


def main():
    domain="d01"
    SIZE = 10
    forward_speed = 10  # m/s
    slp_threshold = 1000  # hPa
    ws_threshold = 10  # m/s
    start_date = datetime(2018, 10, 29, 0, 0, 0)
    stop_date = datetime(2018, 10, 31, 0, 0, 0)
    delta_hours = 1

    current_date=start_date

    T=[]

    while current_date < stop_date:



        L=[]


        url="http://193.205.230.6:8080/opendap/hyrax/opendap/wrf5/"+domain+"/archive/" + \
            "{:04d}".format(current_date.year) + "/" + \
            "{:02d}".format(current_date.month) + "/" + \
            "{:02d}".format(current_date.day) + "/wrf5_"+domain+"_" + \
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
                S=slp[j:j+SIZE, i:i+SIZE]
                iMin = None
                jMin = None
                slp_min = 1e37
                for jj in range(0, len(S)):
                    for ii in range(0, len(S[0])):
                        if S[jj, ii] < slp_min:
                            slp_min = S[jj, ii]
                            iMin = i+ii
                            jMin = j+jj

                if slp_min < slp_threshold:
                    ws = math.pow(u10m[jMin, iMin]*u10m[jMin, iMin]+v10m[jMin, iMin]*v10m[jMin, iMin], 0.5)
                    #if "d01" in domain:
                    #    ws = math.pow(u10m[jMin, iMin] * u10m[jMin, iMin] + v10m[jMin, iMin] * v10m[jMin, iMin], 0.5)
                    #else:
                    #    try:
                    #        ws = (math.pow(u10m[jMin - 1, iMin - 1] * u10m[jMin - 1, iMin - 1] + v10m[jMin - 1, iMin - 1] * v10m[jMin - 1, iMin - 1], 0.5) + \
                    #             math.pow(u10m[jMin - 0, iMin - 1] * u10m[jMin - 0, iMin - 1] + v10m[jMin - 0, iMin - 1] * v10m[jMin - 0, iMin - 1], 0.5) + \
                    #             math.pow(u10m[jMin + 1, iMin - 1] * u10m[jMin + 1, iMin - 1] + v10m[jMin + 1, iMin - 1] * v10m[jMin + 1, iMin - 1], 0.5) + \
                    #             math.pow(u10m[jMin + 1, iMin - 0] * u10m[jMin + 1, iMin - 0] + v10m[jMin + 1, iMin - 0] * v10m[jMin + 1, iMin - 0], 0.5) + \
                    #             math.pow(u10m[jMin + 1, iMin + 1] * u10m[jMin + 1, iMin + 1] + v10m[jMin + 1, iMin + 1] * v10m[jMin + 1, iMin + 1], 0.5) + \
                    #             math.pow(u10m[jMin + 0, iMin + 1] * u10m[jMin + 0, iMin + 1] + v10m[jMin + 0, iMin + 1] * v10m[jMin + 0, iMin + 1], 0.5) + \
                    #             math.pow(u10m[jMin - 1, iMin + 1] * u10m[jMin - 1, iMin + 1] + v10m[jMin - 1, iMin + 1] * v10m[jMin - 1, iMin + 1], 0.5) + \
                    #             math.pow(u10m[jMin - 1, iMin + 0] * u10m[jMin - 1, iMin + 0] + v10m[jMin - 1, iMin + 0] * v10m[jMin - 1, iMin + 0], 0.5) + \
                    #             math.pow(u10m[jMin - 0, iMin + 0] * u10m[jMin - 0, iMin + 0] + v10m[jMin - 0, iMin + 0] * v10m[jMin - 0, iMin + 0], 0.5))/9
                    #    except:
                    #        ws = math.pow(u10m[jMin, iMin]*u10m[jMin, iMin]+v10m[jMin, iMin]*v10m[jMin, iMin], 0.5)

                    if ws >= ws_threshold:

                        geoJsonFeature={
                          "type": "Feature",
                          "properties": {
                              "date": str(current_date),
                              "type": "storm",
                              "track": -1,
                              "slp": float(slp_min),
                              "ws": float(ws),
                              "t2c": float(t2c[jMin, iMin]),
                              "rh2": float(rh2[jMin, iMin]),
                              "uh": float(uh[jMin, iMin])
                          },
                          "geometry": {
                            "type": "Point",
                            "coordinates": [
                              float(lons[iMin]),
                              float(lats[jMin])
                            ]
                          }
                        }


                        L.append(geoJsonFeature)

        #for l in L:
        #    print l

        geoJsonFeatureCollection={
            "type": "FeatureCollection",
            "features": L
        }

        with open("/Users/raffaelemontella/Desktop/medistormtracker/output_"+domain+"_" + \
            "{:04d}".format(current_date.year) + "{:02d}".format(current_date.month) + "{:02d}".format(current_date.day) + \
            "Z{:02d}".format(current_date.hour) + "{:02d}".format(current_date.minute)+".json", "w") as text_file:
            text_file.write(json.dumps(geoJsonFeatureCollection, indent=4, sort_keys=True))
        #print json.dumps(geoJsonFeatureCollection)

        T.append(geoJsonFeatureCollection)

        current_date = current_date+timedelta(hours=delta_hours)


    #print "------------------------"
    #print()
#    tracks=[]
#    for t in range(1, len(T["features"])):
#        for cL in T[t]:
#            for pL in T[t-1]:
#
#                current_forward_speed = haversine((cL["lat"], cL["lon"]), (pL["lat"], pL["lon"]))*0.277777777777778 # m/s
#                print str(current_forward_speed) + " *** " + str(cL) + " - " + str(pL)
#
#                if current_forward_speed <= forward_speed:
#                    track_id = pL["track"]
#                    if track_id == -1:
#                        tracks.append([pL])
#                        track_id=len(tracks)-1
#                        pL["track"] = track_id
#                    cL["track"] = pL["track"]
#                    tracks[cL["track"]].append(cL)

#    print tracks


if __name__ == "__main__":
    main()