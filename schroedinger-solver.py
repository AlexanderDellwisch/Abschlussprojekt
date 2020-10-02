"routines for solving a time independant 1D-Schroedinger-equation"
import numpy as np
import scipy.interpolate as inter
import os.path
import numpy.linalg as linalg
# from scipy.linalg import eigh_tridiagonal
# import eigh_tridiagonal
_TOLERANCE = 0.000001

def main(filename=''):
    """solver for Schroedinger-equation

    Args:
        filename:
            name of inputfile in subdirectory 'input'
    """
    while not filename:
        filename = input("please insert name of input file: ")
# falls hier nix eingegeben wurde muss das programm trotzdem irgendwas bekommen

    newdata = _read_input(filename)
    potential, delta, mass = _potential_generator(newdata)
    hamiltonian = _hamiltonmatrix_generator(potential, delta, mass)
#    eigenvalues, eigenvectors = _hamiltonmatrix_solver(potential, mass, delta,
# newdata)
    eigenvalues, eigenvectors = _hamiltonmatrix_solver(hamiltonian, newdata)

#    np.transpose(eigenvectors)
    sortedvectors = eigenvectors[:, eigenvalues.argsort()]
#    sortedvectors = eigenvectors[eigenvalues.argsort()]
#    np.transpose(sortedvectors)

    eigenvalues.sort()
    energs = np.transpose(eigenvalues[int(newdata[2, 0])-1:int(newdata[2, 1])])

    np.savetxt("energies.dat",energs)

#    with open("energies.dat", "w") as fp:
        # ein ew pro zeile
#        fp.write(str(energs))

    wanted_waves = sortedvectors[:, int(newdata[2, 0])-1:int(newdata[2, 1])]
    wavefuncs_x = potential[:, 0]
    wavefuncs_x.shape = (len(potential), 1)
    wavefuncts = np.concatenate((wavefuncs_x, wanted_waves), axis=1)

    np.savetxt("wavefunctions.dat", wavefuncts)

#    with open("wavefunctions.dat", "w") as fp:
#        print(newdata[2, 0], newdata[2, 1])
    print(wavefuncts[0:2000:50, :])
#        fp.write(str(wavefuncts))

def _read_input(filename):
    """reads input file and produces according variables

    Args:
        filename:
            name of inputfile in subdirectory 'input'

    Returns:
        newdata: an array containing the following variables as rows:
            -mass: mass of particle
            -xMin_xMax: touple of lower and upper boundaries
            -nPoint: number of X-values
            -interpolation: type of interpolation as number form 0 to 2
            -number of given Points for interpolation
            -points: matrix with set poits of curve
    """
    alldata = []

    directory = "input"
    file_location = os.path.join(directory, filename)
    with open(file_location) as fp:
        for line in fp:
            alldata.append(line.strip())
    dataline_y = 0
    for dataline in alldata:
        alldata[dataline_y] = dataline.split("#")[0].strip().split()
# removes annotation of input data and splits lines into lists of
# individual inputs
        dataline_y += 1

    if alldata[3] == ['linear']:
        alldata[3] = [0]
    elif alldata[3] == ['polinomial']:
        alldata[3] = [1]
    elif alldata[3] == ['cspline']:
        alldata[3] = [2]
    #else:
        #alldata[3]
        #raise some kind of input error

    newdata = np.zeros((len(alldata), 3))
    line_y = 0
    for line in alldata:
        line_x = 0
        for coll in alldata[line_y]:
            newdata[line_y, line_x] = alldata[line_y][line_x]
            line_x += 1
        line_y += 1

    return newdata


def _potential_generator(newdata):
    """generates points of potential curve

    Args:
        newdata: an array containing the user-input

    Returns:
        potential: Matrix with corresponding x and V(x) values
        of potential curve
        delta: difference between neighboring x-values
        mass: mass of particle, extracted from input-array
    """
    yy, xx = newdata.shape
    base = newdata[5:yy+1, 0:2]
    x_data = []
    y_data = []

    pointcount = 0
    for item in base:
        x_data.append(base[pointcount, 0])
        y_data.append(base[pointcount, 1])
        pointcount += 1

# check if that works with floats
    if newdata[3, 0]:
        if newdata[3, 0] == 1:
            Vx = np.polyfit(x_data, y_data, yy - 6)
        else:
            Vx = inter.CubicSpline(x_data, y_data)
    else:
        Vx = inter.interp1d(x_data, y_data, kind='linear')

    potential = np.zeros((int(newdata[1, 2]), 2))
    XX_values = np.linspace(int(newdata[1, 0]), int(newdata[1, 1]),
                            int(newdata[1, 2]), endpoint=True)
    delta = XX_values[1] - XX_values[0]

    pointcount = 0
    for item in XX_values:
        potential[pointcount, 0] = item
        potential[pointcount, 1] = Vx(item)
        pointcount += 1

    mass = newdata[0, 0]
    return potential, delta, mass


def _hamiltonmatrix_generator(potential, delta, mass):
    """generates the hamilton matrix

    Args:
        potential: Matrix with corresponding x and V(x) values
        of potential curve
        delta: difference between neighboring x-values
        mass: mass of particle

    Returns:
        hamiltonian: hamilton-matrix
    """
    V_diskr = []
    for pair in potential:
        V_diskr.append(pair[1])

    content = []
    aa = 1 / (mass * (delta**2))

    content.append(aa * V_diskr[0])
    for columns in range(0, len(V_diskr)-1):
        content.append(-0.5 * aa)
        for num in range(0, len(V_diskr)-2):
            content.append(0)
        content.append(-0.5 * aa)
        content.append(aa * V_diskr[columns+1])
    hamiltonian = np.array(content)
    hamiltonian.shape = (len(V_diskr), len(V_diskr))

    return hamiltonian


def _hamiltonmatrix_solver(hamiltonian, newdata):
# def _hamiltonmatrix_solver(potential, mass, delta, newdata):
    """procedure to produce eigenvalues and corresponding eigenvectors
    of hamilton matrix

    Args:
        hamiltonian: hamilton matrix

    Returns:
        eigenvalues: list of aquired eigevalues
        eingenvectors: list of eigenvectors
    """
#    from scipy.sparse.linalg import eigsh
#    eigenvalues, eigenvectors = eigsh(hamiltonian, newdata[2, 1], which='SM')

    eigenvalues, eigenvectors = linalg.eig(hamiltonian)

#    aa = 1 / (mass * (delta**2))
#    eigenvalues, eigenvectors = eigh_tridiagonal(aa * potential[:, 1],
#                              np.ones(len(potential)-1) * -0.5 * aa, select='i',
#                              select_range=(newdata[2, 0], newdata[2, 1]), tol=_TOLERANCE)

    return eigenvalues, eigenvectors


def _expvalues_calculator(unknown):
    """will calculate sigma and uncertainty

    Args:

    Returns:

    """
    return sigma, uncertainty
# output should be file not variable

# def _data_saver(eigenvalues, eigenvectors):


if __name__ == '__main__':
    main()
