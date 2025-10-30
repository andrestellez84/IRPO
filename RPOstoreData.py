from xlwings import *


def capturaReq(J,T,libro):

    REQ = {}
    for j in J:
        anterior=0
        for t in T:
            REQ[(j,t)] = anterior+int(libro.sheets['Requirement'].range(j+1,t+1).value)
            anterior = REQ[(j,t)]
    return REQ

def capturaQ_QT_CU(W,J,libro):
    Q = {}
    QT = {}
    CU = {}
    for w in W:
        for j in J:
            Q[(w, j)] = int(libro.sheets['Qualified'].range(w + 1, j + 1).value)
            QT[(w, j)] = int(libro.sheets['QualifiedTrain'].range(w + 1, j + 1).value)
            CU[(w, j)] = libro.sheets['costAllocate'].range(w + 1, j + 1).value
    return Q,QT,CU

def capturaR(W,T,libro):
    R = {}
    for w in W:
        anterior = 0
        for t in T:
            R[(w,t)]=anterior+int(libro.sheets['Ready'].range(w+1,t+1).value)
            anterior = R[(w,t)]
    return R

def capturarLeadTimesyCostos(J,libro):
    LH = {}
    LT = {}
    CG = {}
    CH = {}
    CT = {}
    for j in J:
        LH[j] = int(libro.sheets['leadtime'].range(j+1, 2).value)
        LT[j] = int(libro.sheets['leadtime'].range(j+1, 3).value)
        CG[j] = libro.sheets['costs'].range(j+1, 2).value
        CH[j] = libro.sheets['costs'].range(j+1, 3).value
        CT[j] = libro.sheets['costs'].range(j+1, 4).value

    return LH,LT,CG,CH,CT

def CapturarInfoMIP():
    libro = Book('RPOdata.xlsx')
    W = [x for x in range(1,int(libro.sheets['conjuntos'].range('b2').value)+1)]
    J = [x for x in range(1,int(libro.sheets['conjuntos'].range('b3').value)+1)]
    T = [x for x in range(1,int(libro.sheets['conjuntos'].range('b4').value)+1)]
    hglobal = int(libro.sheets['escalares'].range('b1').value)
    REQ = capturaReq(J,T,libro)
    Q, QT, CU=capturaQ_QT_CU(W,J,libro)
    R = capturaR(W,T,libro)
    LH, LT, CG, CH, CT=capturarLeadTimesyCostos(J,libro)

    return W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT,CU, hglobal

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

def CapturarInfoTransport(W, Hbipart, Cbipart, Q, QT, Jm, T, REQm, hglobal):
    J=Jm
    REQ=REQm
    #W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal=CapturarInfoMIP()
    #W, Hbipart, Gbipart, Ibipart, Jbipart, Cbipart, Q, QT=CapturarInfoBipartite()
    C={}
    for i in W:
        for j in J:
            C[(i,j)]=Cbipart[(i,j+.1)]

    for j in J:
        if Hbipart != []:
            C[("h",j)]=Cbipart[(len(W)+1,j+.1)]
    for j in J:
        C[("g", j)] =Cbipart[(j+.1,j+.1)]
    magnitudeT=len(T)
    I =W+ ['h', 'g']
    D={}
    for j in J:
        D[j]=REQ[(j,magnitudeT)]
    POsitions=sum([REQ[(j,magnitudeT)] for j in J])
    return W, I, J, C ,Q ,QT, hglobal, POsitions,D
#-----------------------------------------------------------------------------------------------------------------------


#W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT,CU, hglobal=CapturarInfoMIP()
