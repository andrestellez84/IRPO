from random import *
import csv
import subprocess
from pathlib import Path
import re
from datetime import datetime
limiteQ=65.2232916751999
limiteQT=62.7142565888

## from rpo.storedata-------------------------------------------------------------------------------
def CapturarInfoBIP(W, Jm, T, REQm, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal):
    #W, Jm, T, REQm, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal = CapturarInfoMIP()

    J=[]
    REQ={}
    DUR = {}

    for jm in Jm:
        cantidad=REQm[(jm,len(T))]
        for j in range(1,cantidad+1):
            J.append(jm+j/10)

    for j in J:
        for t in T:
            valor=REQm[(int(j),t)]
            if valor>0: valor=1
            REQ[(j,t)]=valor

    for j in Jm:
        DUR[j]=sum([REQ[(j+0.1,t)] for t in T])

    return W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT,CU, hglobal,DUR

def CapturarInfoBipartite(W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal, DUR):
    C={}
    #W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal, DUR = CapturarInfoBIP()
    H, G = [len(W) + x + 1 for x in range(hglobal)], J
    I = W + H + G

    for i in W:
        for j in J:
            dispo=sum([ R[(i,t)] for t in T])
            quali=Q[(i,int(j))] * ( CG[int(j)] * max(0,DUR[int(j)] - dispo) + CU[(i,int(j))] )
            train=QT[(i,int(j))] * ( CG[int(j)] * max(0,DUR[int(j)] - dispo + LT[int(j)] ) + CT[int(j)] )
            C[(i,j)]= quali + train

    for i in H:
        for j in J:
            C[(i, j)] = CG[int(j)] * max(0,DUR[int(j)] - len(T) + LH[int(j)] ) + CH[(int(j))]

    for i in G:
        for j in J:
            C[(i, j)] = int(i==j)*DUR[int(j)]*CG[int(j)]

    return W, H, G, I, J, C, Q, QT
## from rpo.storedata-------------------------------------------------------------------------------

##from marcos runner-----------------------------------------------------------------------------------
def solve_optimal(name, weighted_edges, *, solver_report=False):
    print("inicia resolucion mediante matching tools(marcos)",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    r"""
    Find a min-weight one-side perfect matching, in a weighted bipartite
    graph, the instance is represented by `weighted_edges`, which is a list
    where each element is a weighted edge in the form
    (left_vertex, right_vertex, weight). The number of vertices in each
    side of the graph will be infered from the edges.

    Args:
        name (str): prefix for the input and output solver files.
        weighted_edges (list[tuple]): list of weghted edges.
        solver_report (bool=Flase): `True` if we want the output of the
            solver to be shown in the console.

    Returns:
        list[tuple]: The weighted edges of the optimum matching, each
            edge in the form (u, v, weight).
    """
    # Path of the folder to store the results
    results_path = Path()
    # Path of the generated instance
    instance_path = results_path / f"{name}_instance.graph"
    # Path of the output file
    result_path = results_path / f"{name}_solution.txt"
    # Path of the solver
    solver_path = Path('../MarcosEmbead/bipartite_matchings_tool.exe')

    # Generamos el archivo de la instancia.
    with instance_path.open(mode="w", encoding="utf8") as instance_file:
        instance_str = "\n".join([f"{a[0]},{a[1]},{a[2]}" for a in weighted_edges])
        instance_file.write(instance_str + '\n')

    # Ejecutamos el comando para usar el solver externo e interceptamos la salida para mostrarla en consola
    # y guardarla en la variable 'log'.
    log = ""
    comando = [solver_path, instance_path, result_path, "-minweight", "-s_doub"]
    process = subprocess.Popen(comando, stdout=subprocess.PIPE, universal_newlines=True, shell=False)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if solver_report:
                print(output, end="")
            log += output

    # Load the matching solution to return it as a list of weighted edges
    with result_path.open(mode="r", encoding="utf8") as solution_file:
        matching_str = solution_file.read()

    # Weighted edges iterator
    matching_iter = re.finditer(r'(.+),(.+),(.+)', matching_str)

    # Return the weighted matching, scaling down the weights
    salida=[]
    for a in matching_iter:
        origen=verDecimal(float(a.group(1)))
        destino=verDecimal(float(a.group(2)))
        peso=float(a.group(3))
        salida.append([origen,destino,peso])
    return salida

def verDecimal(num):
    if num-int(num)==0:
        return int(num)
    else:
        return num
##from marcos runner------------------------------------------------------------------------------------

def crearDatosbase(archivoMS,semilla):
    seed(semilla)
    datosMS = open(archivoMS, "r+").readlines()
    for d in range(1,len(datosMS)):
        datosMS[d]= [d]+[float(x) for x in datosMS[d].split(',')[1:]]

    W=[x for x in range(1,len(datosMS))]
    J=[x for x in range(1,len(datosMS[1]))]
    T=[x for x in range(1,26+1)]

    # REQ_jt
    REQ={}
    posiciones=0
    for j in J:
        inicio=1
        if random() >= 0.8:
            inicio = randint(1, 26)
        cantidad=RandomeReq()
        posiciones+=cantidad
        for t in T:
            if t>=inicio:
                REQ[(j,t)]=cantidad
            else:
                REQ[(j, t)] = 0
            pass

    # Q_wj, QT_wj
    Q={}
    QT = {}
    for w in W:
        for j in J:
            if datosMS[w][j]>limiteQ: #59.57919224 equivale al 80%
                Q[(w,j)]=1
                QT[(w, j)] = 0
            elif datosMS[w][j]<limiteQT: #53.34104194 equivale a percenti del 50%
                Q[(w,j)]=0
                QT[(w, j)] = 0
            else:
                Q[(w,j)]=0
                QT[(w, j)] = 1


    #R_wt
    R={}
    for w in W:
        llegada=1
        if random() >= 0.8:
            llegada=randint(1,26)
        for t in T:
            if t>=llegada:
                R[(w,t)]= 1
            else:
                R[(w, t)] = 0

    #CU_wj
    CU={}
    for w in W:
        for j in J:
            if datosMS[w][j]>limiteQ:
                #CU[(w,j)]=1+ceil((1-datosMS[w][j])*66.66)
                CU[(w, j)] =101-datosMS[w][j]
            else:
                CU[(w,j)]=0

        # LH_j, LT_j
        # CG_j, CH_j, CT_j
    LH = {}
    LT = {}
    CT = {}
    CH = {}
    CG = {}
    for j in J:
        LH[j] = randint(4, 12)
        LT[j] = randint(1, 6)
        CT[j] = 2*max(CU[(w,j)] for w in W)
        CH[j] = 4*max(CU[(w,j)] for w in W)
        CG[j] = 8*max(CU[(w,j)] for w in W)

    hglobal=int(0.05*posiciones)
    return W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT,CU, hglobal, datosMS

def dictToFile(dicName,dictionary, filename):
    with open(filename, 'a') as file:
        file.write(f"\n{dicName}\n")
        for key, value in dictionary.items():
            file.write(f"{key}: {value}\n")
        file.close()

def dictToMarcosFile(dictionary, filename):
    with open(filename, 'w') as file:
        for key, value in dictionary.items():
            var1,var2=key
            file.write(f"{var1},{var2},{value}\n")
        file.close()

def dictToMarcosList(dictionary):
    lista=[]
    for key, value in dictionary.items():
        var1, var2 = key
        lista.append((var1, var2,value))
    return  lista

def RandomeReq():

    rand_num = random()
    if rand_num < 0.9:
        return 1
    elif rand_num >= 0.95:
        return 3
    else:
        return 2

def CrearArchivoSAlida(archivoMS,semilla):
    print("inicia captura de MS y creacion problema",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal,datosMS = crearDatosbase(archivoMS,semilla)
    #print(datosMS)
    W2, J2, T2, REQ2, Q2, QT2, LH2, LT2, R2, CG2, CH2, CT2, CU2, hglobal2=W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal
    nombres =['REQ', 'Q', 'QT', 'LH', 'LT', 'R', 'CG', 'CH', 'CT', 'CU']
    diccionarios=[REQ, Q, QT, LH, LT, R, CG, CH, CT, CU]
    #texto = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    texto="parametersFile"

    with open(texto+ ".txt", 'w') as file:
        file.write(f"{archivoMS},semilla={semilla}\n")
        file.write(f"W,J,T,hglobal\n")
        file.write(f"{len(W)},{len(J)},{len(T)},{hglobal}\n")
        file.close()
        for n in range(len(nombres)):
            dictToFile(nombres[n],diccionarios[n], texto+ ".txt")

    print("inicia transformacion a bipartita",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT,CU, hglobal,DUR=CapturarInfoBIP(W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal)
    W, H, G, I, J, C, Q, QT=CapturarInfoBipartite(W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal, DUR)

    C2= {}
    for llave,valor in C.items():
        if valor!=0:
            C2[llave]=valor

    with open(texto+ "-graph.txt", 'w') as file:
        file.write(f"{archivoMS},semilla={semilla}\n")
        file.write(f"W={W}\n")
        file.write(f"H={H}\n")
        file.write(f"J={J}\n")
        file.close()
        dictToFile("CostoArcos",C2, texto+ "-graph.txt")

    #dictToMarcosFile(C2, texto + "_instance.graph")
    marcosList=dictToMarcosList(C2)

    return W2, J2, T2, REQ2, Q2, QT2, LH2, LT2, R2, CG2, CH2, CT2, CU2, hglobal2,datosMS,marcosList

def computeJObsData(outvector,W,T,  REQ, Q, LH, LT,R, CG,datosMS):
    print("inicia calculo de metricas por posicion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    outvector = sorted(outvector, key=lambda x: x[1])
    periodos=len(T)
    Recursos=len(W)
    positions=len(outvector)
    jobs=int(outvector[-1][1])

    tabla=[['periodos',periodos,'Recursos',Recursos,'positions',positions,'jobs',jobs],['pos','job','perStart','perToFill','ResAsig','ResType','ResRedy','ResStart','LedTime','Filled','Gap','AsigC','GapC','TotC','MS']]

    for res,pos,TotC in outvector:
        job=int(pos)

        perStart =0
        for t in T:
            if REQ[(job,t)]>0 and perStart==0:
                perStart=t

        perToFill = periodos -perStart+1

        LedTime = 0
        ResStart = 0
        ResRedy = 0
        if res==pos:
            ResAsig="Gap"
            ResType = "G"
            Filled = 0
            Gap=perToFill

        elif res>Recursos:
            ResAsig="Hire"
            ResType = "H"
            LedTime = LH[job]
            ResStart = max(LedTime+1,perStart)
            Filled = min(perToFill,periodos-ResStart+1)
            Gap=perToFill-Filled

        else:
            ResAsig =res
            ResRedy = 0
            for t in T:
                if R[(res, t)] > 0 and ResRedy == 0:
                    ResRedy = t

            if Q[(res,job)]==1:
                ResType = "Q"

            else:
                ResType = "T"
                LedTime = LT[job]
            ResStart = max(LedTime+ResRedy,perStart)
            Filled = min(perToFill,periodos-ResStart+1)
            Gap=perToFill-Filled

        GapC = Gap*CG[job]
        AsigC=TotC-GapC
        MS=0
        if ResType=="T" or ResType=="Q":
            MS=datosMS[ResAsig][job]
        vector=[pos,job,perStart,perToFill,ResAsig,ResType,ResRedy,ResStart,LedTime,Filled,Gap,AsigC,GapC,TotC,MS]

        tabla.append(vector)
    return tabla

def computeVisualization(tabla,T):
    print("inicia calculo de metricas visual", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    tablaVisual=[["pos","resource","type","match","cost"]+T]
    for trabajo in tabla[2:]:
        ResourceStart=trabajo[7]
        JobStart=trabajo[2]
        vector=[trabajo[0],trabajo[4],trabajo[5],trabajo[-1],trabajo[-2]]
        for t in T:
            if t<JobStart:
                vector+=[" "]
            elif trabajo[5]=="G" or (JobStart<=t and t<ResourceStart):
                vector+=[0]
            else:
                vector += [1]
        tablaVisual.append(vector)

    return tablaVisual

def createCSVout(data,nombre):
    # Specify the file name for the CSV file
    csv_filename = nombre+".csv"

    # Open the CSV file in write mode
    with open(csv_filename, mode='w', newline='') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)

        # Write the data to the CSV file row by row
        for row in data:
            csv_writer.writerow(row)

    print(f"archivo '{csv_filename}' terminado.")

def computeKPI(tablatrabajos,R,W,J,hglobal):
    print("inicia calculo de KPI", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    tablaKPI=[["demand","manmonths","% of requirement"]]
    requeridas=sum( x[3] for x in tablatrabajos[2:])
    tablaKPI.append(["requirement",requeridas])
    llenadas=sum( x[9] for x in tablatrabajos[2:])
    tablaKPI.append(["Asigned",llenadas, llenadas/requeridas ])
    llenadasQ=sum( x[9] for x in tablatrabajos[2:] if x[5]=="Q")
    tablaKPI.append(["Asigned_Q",llenadasQ, llenadasQ/requeridas ])
    llenadasT=sum( x[9] for x in tablatrabajos[2:] if x[5]=="T")
    tablaKPI.append(["Asigned_T",llenadasT, llenadasT/requeridas ])
    llenadasH=sum( x[9] for x in tablatrabajos[2:] if x[5]=="H")
    tablaKPI.append(["Asigned_H",llenadasH, llenadasH/requeridas ])
    vacias=sum( x[10] for x in tablatrabajos[2:])
    tablaKPI.append(["unasigned",vacias, vacias/requeridas ])
    tablaKPI.append([""])

    tablaKPI.append(["capacity","manmonths","% of installed"])
    CapInstal=sum(R.values())
    tablaKPI.append(["installed(internal)",CapInstal ])
    CapUsedQT=sum( x[9] for x in tablatrabajos[2:] if (x[5]=="Q" or x[5]=="T"))
    tablaKPI.append(["used(internal)", CapUsedQT,CapUsedQT/CapInstal])
    timeTrain=sum( x[8] for x in tablatrabajos[2:] if (x[5]=="T"))
    tablaKPI.append(["used for training(internal)", timeTrain,timeTrain/CapInstal])
    idles=CapInstal-CapUsedQT-timeTrain
    tablaKPI.append(["idle", idles,idles/CapInstal])
    hiredMM=sum( x[9] for x in tablatrabajos[2:] if (x[5]=="H"))
    tablaKPI.append(["increase(Hire)", hiredMM,hiredMM/CapInstal])
    hiredLT=sum( x[8] for x in tablatrabajos[2:] if (x[5]=="H"))
    tablaKPI.append(["leadtime(Hire)", hiredLT])
    tablaKPI.append([""])

    tablaKPI.append(["resources","value"])
    trabajadores=len(W)
    tablaKPI.append(["available Workers(internal)", trabajadores])
    trabajadoresQ=sum( 1 for x in tablatrabajos[2:] if (x[5]=="Q"))
    tablaKPI.append(["asigned Workers_Q(internal)", trabajadoresQ])
    MS_Q=sum( x[14] for x in tablatrabajos[2:] if (x[5]=="Q"))
    ratioQ=0
    if trabajadoresQ !=0:
        ratioQ=MS_Q/trabajadoresQ
    tablaKPI.append(["average MS Workers_Q(internal)",ratioQ])
    trabajadoresT=sum( 1 for x in tablatrabajos[2:] if (x[5]=="T"))
    tablaKPI.append(["asigned Workers_T(internal)", trabajadoresT])
    MS_T=sum( x[14] for x in tablatrabajos[2:] if (x[5]=="T"))
    ratioT=0
    if trabajadoresT !=0:
        ratioT=MS_T/trabajadoresT
    tablaKPI.append(["average MS Workers_T(internal)",ratioT])
    idelWorkers=trabajadores-trabajadoresT-trabajadoresQ
    tablaKPI.append(["idel Workers(internal)", idelWorkers])
    contratados=sum( 1 for x in tablatrabajos[2:] if (x[5]=="H"))
    tablaKPI.append(["asigned hired Workers", contratados])
    tablaKPI.append(["hire limit", hglobal])
    puestos=len(tablatrabajos[2:])
    tablaKPI.append(["positions", puestos])
    puestovacios=sum( 1 for x in tablatrabajos[2:] if (x[5]=="G"))
    tablaKPI.append(["unfilled positions", puestovacios])

    workersTardeQ = 0
    workersPeriodsTardeQ=0
    workersTardeH = 0
    workersPeriodsTardeH = 0
    workersTardeT = 0
    workersPeriodsTardeT = 0
    AverageRdyT=0
    AverageLT=0

    for x in tablatrabajos[2:]:
        if (x[5]=="Q") and (x[7]-x[2]>0):
            workersTardeQ += 1
            workersPeriodsTardeQ += x[7]-x[2]
        if (x[5]=="T") and (x[7]-x[2]>0):
            workersTardeT += 1
            workersPeriodsTardeT += x[7]-x[2]
            AverageRdyT += x[6]
            AverageLT += x[8]
        if (x[5]=="H") and (x[7]-x[2]>0):
            workersTardeH += 1
            workersPeriodsTardeH += x[7]-x[2]
    if workersTardeQ>0:
        workersPeriodsTardeQ=workersPeriodsTardeQ/workersTardeQ
    if workersTardeT>0:
        AverageRdyT = AverageRdyT/workersTardeT
        AverageLT = AverageLT/workersTardeT
        workersPeriodsTardeT=workersPeriodsTardeT/workersTardeT
    if workersTardeH>0:
        workersPeriodsTardeH=workersPeriodsTardeH/workersTardeH


    tablaKPI.append(["Worker Late Q", workersTardeQ])
    tablaKPI.append(["Avg periods late Q", workersPeriodsTardeQ])
    tablaKPI.append(["Worker Late T", workersTardeT])
    tablaKPI.append(["Avg periods late T", workersPeriodsTardeT])

    tablaKPI.append(["Avg readinesss for late T", AverageRdyT])
    tablaKPI.append(["Avg trainTime for late T", AverageLT])

    tablaKPI.append(["Worker Late H", workersTardeH])
    tablaKPI.append(["Avg periods late H", workersPeriodsTardeH])

    tablaKPI.append(["Assign cost", sum( x[11] for x in tablatrabajos[2:]) ])
    tablaKPI.append(["Gap cost", sum( x[12] for x in tablatrabajos[2:]) ])
    tablaKPI.append(["total cost", sum( x[12] for x in tablatrabajos[2:]) ])

    return tablaKPI

#------------------------------------------------------------------------------------------------

semilla=0
archivoMS='C:/Users/L03533939/Desktop/PyChProyects/pythonProject/RPO/MatchingScoreV8.csv' #los MS deben ser valores entre 0 y 100
W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal, datosMS, marcosList = CrearArchivoSAlida(archivoMS,semilla)

outvector=solve_optimal('parametersMarcos', marcosList)


tablatrabajos=computeJObsData(outvector,W,T,  REQ, Q, LH, LT,R, CG,datosMS)
createCSVout(tablatrabajos,"OutRPO_Positions_optimal")
tablaVisual=computeVisualization(tablatrabajos,T)
createCSVout(tablaVisual,"OutRPO_PositionsVisual_optimal")
tablaKPI=computeKPI(tablatrabajos,R,W,J,hglobal)
createCSVout(tablaKPI,"OutRPO_KPI_optimal")
print("fin",datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
