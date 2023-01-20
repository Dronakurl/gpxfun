import numpy as np
import math

def x_coord_of_point(D, j):
    return ( D[0,j]**2 + D[0,1]**2 - D[1,j]**2 ) / ( 2*D[0,1] )

def coords_of_point(D, j):
    x = x_coord_of_point(D, j)
    if D[0,j]**2 - x**2>0:
        return np.array([x, math.sqrt( D[0,j]**2 - x**2 )])
    else:
        print(f"Warnung, in positions_from_distm wird eine Wurzel negative {D[0,j]**2 - x**2}")
        return np.array([x,0])
    
def calculate_positions(D):
    (m, n) = D.shape
    P = np.zeros( (n, 2) )
    tr = ( min(min(D[2,0:2]), min(D[2,3:n])) / 2)**2
    P[1,0] = D[0,1]
    P[2,:] = coords_of_point(D, 2)
    for j in range(3,n):
        P[j,:] = coords_of_point(D, j) 
        if abs( np.dot(P[j,:] - P[2,:], P[j,:] - P[2,:]) - D[2,j]**2 ) > tr:
            P[j,1] = - P[j,1]
    return P 
             
