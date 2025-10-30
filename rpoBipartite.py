from RPO.RPOstoreData import *
from gurobipy import *
from otherFiles.AlimentacionDeDatos import subIn
from xlwings import *



def crearModeloBipartite(W, H, G, I, J, C, Q, QT):
    # conjuntos: W,H,G,I,J
    # parametros globales: C_ij, Q_wj, QT_wj,
    # variables globales:a_i,j
    a = {}

    modelo=Model('RPOBipartite')
    crearvariables(modelo,I, J, a)

    constSatisfyDemand(modelo,W, H, G, J, Q, QT,a)
    constControlOfer(modelo,W, H, G, J, Q, QT,a)

    objetivo = createObjective( I, J, C, a)

    modelo.setObjective(objetivo, GRB.MINIMIZE)
    modelo.write('test.lp')

    modelo.setParam('OutputFlag', 0)
    modelo.optimize()

    print("Bipartite objective:", modelo.ObjVal," runtime:",modelo.Runtime)
    return modelo,a

def crearvariables(modelo,I, J, a):
    for i in I:
        for j in J:
                sub = subIn(i, j)
                a[(i, j)] = modelo.addVar(lb=0,ub=1, name='a' + sub)#si el nodo oferta i  se asigna al de demanda j
    return

def constSatisfyDemand(modelo,W, H, G, J, Q, QT,a):
    for j in J:
        empleados = quicksum( int(Q[(i,int(j))]+QT[(i,int(j))]==1)*a[(i, j)] for i in W)
        contratados = quicksum(a[(i, j)] for i in H)
        gaps = quicksum(int(i==j)*a[(i, j)] for i in G)

        modelo.addConstr(empleados + contratados + gaps == 1, name='demand' + subIn(j) )
    return

def constControlOfer(modelo,W, H, G, J, Q, QT,a):
    for i in W:
        ladoIzq=quicksum( int(Q[(i,int(j))]+QT[(i,int(j))]==1)*a[(i, j)] for j in J)
        modelo.addConstr(ladoIzq <= 1, name='oferW' + subIn(i))

    for i in H:
        ladoIzq=quicksum( a[(i, j)] for j in J)
        modelo.addConstr(ladoIzq <= 1, name='oferH' + subIn(i))

    for i in G:
        ladoIzq=quicksum(int(i==j)*a[(i, j)] for j in J)
        modelo.addConstr(ladoIzq <= 1, name='oferG' + subIn(i))

    return

def createObjective( I, J, C, a):
    costo=quicksum(C[(i,j)]*a[(i,j)] for j in J for i in I)
    objetivo=costo

    return objetivo

def imprimirExcel(modelo,W, H, G, I, J, a):
    tabla=[[]]
    #tabla=[['' for x in range(3)] for j in range(len(J)+1)]
    tabla[0]=['objetivo='+str(modelo.objVal),'asignado']
    #for j in range(len(J)):
     #   tabla[j+1][0]='job ' + str(J[j])

    for j in J:
        for i in I:
            if a[(i, j)].X==1:
                if i in W:
                    texto='w'+str(i)
                if i in H:
                    texto='h'
                if i in G:
                    texto='g'
        tabla.append(['job'+ str(j),texto])

    Book('RPOdata.xlsx').sheets['salidaBipartite'].range('A1').expand().clear_contents()
    Book('RPOdata.xlsx').sheets['salidaBipartite'].range(1, 1).value = tabla
    return

def correrDesdeExcelbipartite():
    # conjuntos: W, J, T, #parametros globales: REQ_jt, Q_wj, QT_wj, LH_j, LT_j, R_wt, CG_j, CH_j, CT_j,CU_wj, hglobal
    W, Jm, T, REQm, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal = CapturarInfoMIP()
    W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT,CU, hglobal,DUR=CapturarInfoBIP(W, Jm, T, REQm, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal)
    W, H, G, I, J, C, Q, QT=CapturarInfoBipartite(W, J, T, REQ, Q, QT, LH, LT, R, CG, CH, CT, CU, hglobal, DUR)
    modelo,a=crearModeloBipartite(W, H, G, I, J, C, Q, QT)
    imprimirExcel(modelo,W, H, G, I, J, a)
    return
#--------------------------------------------------------------------------------------------------

#correrDesdeExcelbipartite()