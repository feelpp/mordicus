# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

from Mordicus.Modules.Safran.External.pyumat import py3umat
from Mordicus import GetTestPath

import numpy as np
import pickle
import os


def test():

    initFolder = os.getcwd()

    folder = GetTestPath() + "Modules/Safran/External/pyumat"

    os.chdir(folder)

    names = ["plas.mat", "pla2.mat"]

    results = []

    for i in range(len(names)):

        cmname = names[i]

        nstatv = 25
        ndi = 3
        nshr = 3
        ntens = ndi + nshr

        stress = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        statev = np.zeros(nstatv)

        ddsdde = np.zeros((6, 6), dtype=float)

        sse = 0.0
        spd = 0.0
        scd = 0.0

        rpl = 0.0
        ddsddt = np.zeros(ntens)
        drplde = np.zeros(ntens)
        drpldt = 0.0

        stran = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        r2 = 2
        dstran = np.array(
            [
                -0.00033628699737546665,
                2.1847656995628707e-05,
                2.1847656995562933e-05,
                r2 * -0.00010904596632688759,
                r2 * -0.0001090459663269204,
                r2 * 1.1680782975309023e-06,
            ]
        )

        time = np.array([0.0, 1.0])
        dtime = 1
        temp = 20.0
        dtemp = 0.0
        predef = np.zeros(1)
        dpred = np.zeros(1)

        nprops = 1
        props = np.zeros(nprops)
        coords = np.zeros(3, dtype=float)
        drot = np.zeros((3, 3), dtype=float)
        pnewdt = 1.0
        celent = 1.0
        dfgrd0 = np.zeros((3, 3), dtype=float)
        dfgrd1 = np.zeros((3, 3), dtype=float)
        noel = -1
        npt = -1
        kslay = 1
        kspt = 1
        kstep = np.array([1, 1, 0, 0], dtype=int)
        kinc = 1

        ddsddeNew = py3umat.umat(
            stress=stress,
            statev=statev,
            ddsdde=ddsdde,
            sse=sse,
            spd=spd,
            scd=scd,
            rpl=rpl,
            ddsddt=ddsddt,
            drplde=drplde,
            drpldt=drpldt,
            stran=stran,
            dstran=dstran,
            time=time,
            dtime=dtime,
            temp=temp,
            dtemp=dtemp,
            predef=predef,
            dpred=dpred,
            cmname=cmname,
            ndi=ndi,
            nshr=nshr,
            ntens=ntens,
            nstatv=nstatv,
            props=props,
            nprops=nprops,
            coords=coords,
            drot=drot,
            pnewdt=pnewdt,
            celent=celent,
            dfgrd0=dfgrd0,
            dfgrd1=dfgrd1,
            noel=noel,
            npt=npt,
            kslay=kslay,
            kspt=kspt,
            kstep=kstep,
            kinc=kinc,
        )

        # convert local tangent matrix in Abaqus conventions to Zebulon conventions
        ddsddeNew[3:, :] *= np.sqrt(2.0)
        ddsddeNew[:, 3:] *= np.sqrt(2.0)
        p = [0, 1, 2, 3, 5, 4]
        ddsddeNew = ddsddeNew[:, p]
        ddsddeNew = ddsddeNew[p, :]

        allData = {
            "stress": stress,
            "statev": statev,
            "sse": sse,
            "spd": spd,
            "scd": scd,
            "rpl": rpl,
            "ddsddt": ddsddt,
            "drplde": drplde,
            "drpldt": drpldt,
            "stran": stran,
            "dstran": dstran,
            "time": time,
            "dtime": dtime,
            "temp": temp,
            "dtemp": dtemp,
            "predef": predef,
            "dpred": dpred,
            "cmname": cmname,
            "ndi": ndi,
            "nshr": nshr,
            "ntens": ntens,
            "nstatv": nstatv,
            "props": props,
            "nprops": nprops,
            "coords": coords,
            "drot": drot,
            "pnewdt": pnewdt,
            "celent": celent,
            "dfgrd0": dfgrd0,
            "dfgrd1": dfgrd1,
            "noel": noel,
            "npt": npt,
            "kslay": kslay,
            "kspt": kspt,
            "kstep": kstep,
            "kinc": kinc,
            "ddsdde": ddsddeNew,
        }

        res = []
        for a in allData:
            res.append([a, allData[a]])
        res = sorted(res, key=lambda x: (x[0]))
        results.append(res)

    imput = open("ref/FullTestpython3.res", "rb")
    ref = pickle.load(imput)

    refdiff = []
    for j in range(len(names)):
        for i in range(len(res)):
            if type(results[0][i][1]) != type("str"):
                if np.linalg.norm(ref[0][i][1]) > 0:
                    refdiff.append(
                        np.linalg.norm(results[0][i][1] - ref[0][i][1])
                        / np.linalg.norm(ref[0][i][1])
                    )
                else:
                    refdiff.append(np.linalg.norm(results[0][i][1] - ref[0][i][1]))

    print("Relative difference =", np.linalg.norm(refdiff))

    os.system("rm -rf Zmat.msg")

    os.chdir(initFolder)

    if np.linalg.norm(refdiff) < 1.0e-12:
        return "ok"


if __name__ == "__main__":
    print(test())  # pragma: no cover
