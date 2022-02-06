"""
xfab.symmetry has a few function for calculation of symmetry
related stuff
"""

from __future__ import absolute_import
from __future__ import print_function
from xfab import tools
from six.moves import range
import numpy as np
from xfab import xfab_logging
from xfab import checks
logger = xfab_logging.get_module_level_logger(__name__)


def Umis(umat_1, umat_2, crystal_system):
    """Compute the misorientation between two rotation matrices.

    `umat_2` is seen in light of all the possible indistinguishable symmetries generated by the
    input `crystal_system`. For each symmetry a new rotation matrix can be created and compared
    to `umat_1`. The misorientations are computed as

        arccos( trace(umat_2 . umat_1.T) - 1)/2 )

    Args:
        umat_1 (:obj:numpy array): Rotation matrix to be compared to `umat_2`, ``shape=(3,3)``
        umat_2 (:obj:numpy array): Rotation matrix to be compared to `umat_2`, ``shape=(3,3)``
        crystal_system (:obj:int): crystal_system number must be one of 1: Triclinic, 2: Monoclinic,
            3: Orthorhombic, 4: Tetragonal, 5: Trigonal, 6: Hexagonal, 7: Cubic

    Returns:
        (:obj:numpy array): misorientation between `umat_1` and `umat_2` for each
            symmetry operation allowed by the input crystal system in units of degrees
            ``shape=(N,2)``.

    """
    if checks.is_activated():
        checks._check_rotation_matrix(umat_1)
        checks._check_rotation_matrix(umat_2)

    rot = ROTATIONS[crystal_system]
    misorientations = np.empty((len(rot), 2))

    # The below line of code is the faster equivalent of
    # lengths = [ 0.5 * trace( dot( r, dot( u1.T  , u2 ) ) - 0.5 for r in rot ]
    # Note that the trace is invariant under cyclic permutations.
    # Note that applying an element of rot upon an input orientation matrix
    # produces a new orientation matrix that, given the input crystal_system,
    # will appear to be identical to the starting orientation.
    # see xfab.symmetry.rotations() for further details.
    lengths = 0.5 * (rot * np.dot(umat_1.T, umat_2)).sum(axis=(1, 2)) - 0.5

    misorientations[:, 0] = np.arange(len(rot))
    misorientations[:, 1] = np.arccos(lengths.clip(-1, 1)) * 180./np.pi
    return misorientations


def add_perm(hkl, crystal_system):
    """
    apply the permutation according to the crystal system on the
    hkl and print the result
    """

    perm = permutations(crystal_system)
    nperm = perm.shape[0]

    for k in range(nperm):
        logger.debug(np.dot(perm[k],hkl))


def add_rot(umat, crystal_system):
    """
    apply the rotation according to the crystal system on the
    orientation matrix U and print the result
    """

    rot = rotations(crystal_system)
    nrot = rot.shape[0]

    for k in range(nrot):
        logger.debug(np.dot(umat, rot[k]))


def permutations(crystal_system):

    """
    permutations returns the set of indistinguasible lattice permutations

    perm = permutations(crystal_system)
    hkl_new = perm*hkl

    crystal_system can be one of the following values
    1: Triclinic
    2: Monoclinic
    3: Orthorhombic
    4: Tetragonal
    5: Trigonal
    6: Hexagonal
    7: Cubic

    Henning Osholm Sorensen, Riso, 30/6/2006
    Implemented in python, 12/7/2008
    """

    if crystal_system < 1 or crystal_system > 7:
        raise ValueError('Crystal system shoud have a value between 1 and 7')

    if crystal_system == 1: # Triclinic
        perm = np.zeros((1, 3, 3))
        perm[0]  = [[ 1., 0, 0], [ 0, 1., 0], [ 0, 0, 1.]]

    if crystal_system == 2: # Monoclinic
        perm = np.zeros((2, 3, 3))
        perm[0]  = [[ 1, 0, 0], [ 0, 1, 0], [ 0, 0,  1]]
        perm[1]  = [[-1, 0, 0], [ 0, 1, 0], [ 0, 0, -1]]

    if crystal_system == 3: # Orthorhombic
        perm = np.zeros((4, 3, 3))
        perm[0]  = [[ 1, 0, 0], [ 0,  1, 0], [ 0, 0,  1]]
        perm[1]  = [[-1, 0, 0], [ 0, -1, 0], [ 0, 0,  1]]
        perm[2]  = [[-1, 0, 0], [ 0,  1, 0], [ 0, 0, -1]]
        perm[3]  = [[ 1, 0, 0], [ 0, -1, 0], [ 0, 0, -1]]

    if crystal_system == 4: # Tetragonal
        perm = np.zeros((8, 3, 3))
        perm[0]  = [[ 1,  0, 0], [ 0,  1, 0], [ 0, 0,  1]]
        perm[1]  = [[-1,  0, 0], [ 0, -1, 0], [ 0, 0,  1]]
        perm[2]  = [[ 0,  1, 0], [-1,  0, 0], [ 0, 0,  1]]
        perm[3]  = [[ 0, -1, 0], [ 1,  0, 0], [ 0, 0,  1]]
        perm[4]  = [[-1,  0, 0], [ 0,  1, 0], [ 0, 0, -1]]
        perm[5]  = [[ 1,  0, 0], [ 0, -1, 0], [ 0, 0, -1]]
        perm[6]  = [[ 0,  1, 0], [ 1,  0, 0], [ 0, 0, -1]]
        perm[7]  = [[ 0, -1, 0], [-1,  0, 0], [ 0, 0, -1]]

    if crystal_system == 5: # Trigonal
        perm = np.zeros((6, 3, 3))
        perm[0]  = [[ 1,  0, 0], [ 0,  1, 0], [ 0, 0,  1]]
        perm[1]  = [[ 0,  1, 0], [-1, -1, 0], [ 0, 0,  1]]
        perm[2]  = [[-1, -1, 0], [ 1,  0, 0], [ 0, 0,  1]]
        perm[3]  = [[ 0,  1, 0], [ 1,  0, 0], [ 0, 0, -1]]
        perm[4]  = [[ 1,  0, 0], [-1, -1, 0], [ 0, 0, -1]]
        perm[5]  = [[-1, -1, 0], [ 0,  1, 0], [ 0, 0, -1]]

    if crystal_system == 6: # Hexagonal
        perm = np.zeros((12, 3, 3))
        perm[0]  = [[ 1,  0, 0], [ 0,  1, 0], [ 0, 0,  1]]
        perm[1]  = [[ 0,  1, 0], [-1, -1, 0], [ 0, 0,  1]]
        perm[2]  = [[-1, -1, 0], [ 1,  0, 0], [ 0, 0,  1]]
        perm[3]  = [[-1,  0, 0], [ 0, -1, 0], [ 0, 0,  1]]
        perm[4]  = [[ 0, -1, 0], [ 1,  1, 0], [ 0, 0,  1]]
        perm[5]  = [[ 1,  1, 0], [-1,  0, 0], [ 0, 0,  1]]
        perm[6]  = [[ 0,  1, 0], [ 1,  0, 0], [ 0, 0, -1]]
        perm[7]  = [[ 1,  0, 0], [-1, -1, 0], [ 0, 0, -1]]
        perm[8]  = [[-1, -1, 0], [ 0,  1, 0], [ 0, 0, -1]]
        perm[9]  = [[ 0, -1, 0], [-1,  0, 0], [ 0, 0, -1]]
        perm[10] = [[-1,  0, 0], [ 1,  1, 0], [ 0, 0, -1]]
        perm[11] = [[ 1,  1, 0], [ 0, -1, 0], [ 0, 0, -1]]

    if crystal_system == 7: # Cubic
        perm = np.zeros((24, 3, 3))
        perm[0]  = [[ 1,  0,  0], [ 0,  1,  0], [ 0,  0,  1]]
        perm[1]  = [[ 1,  0,  0], [ 0, -1,  0], [ 0,  0, -1]]
        perm[2]  = [[ 1,  0,  0], [ 0,  0, -1], [ 0,  1,  0]]
        perm[3]  = [[ 1,  0,  0], [ 0,  0,  1], [ 0, -1,  0]]
        perm[4]  = [[-1,  0,  0], [ 0,  1,  0], [ 0,  0, -1]]
        perm[5]  = [[-1,  0,  0], [ 0, -1,  0], [ 0,  0,  1]]
        perm[6]  = [[-1,  0,  0], [ 0,  0, -1], [ 0, -1,  0]]
        perm[7]  = [[-1,  0,  0], [ 0,  0,  1], [ 0,  1,  0]]
        perm[8]  = [[ 0,  1,  0], [-1,  0,  0], [ 0,  0,  1]]
        perm[9]  = [[ 0,  1,  0], [ 0,  0, -1], [-1,  0,  0]]
        perm[10] = [[ 0,  1,  0], [ 1,  0,  0], [ 0,  0, -1]]
        perm[11] = [[ 0,  1,  0], [ 0,  0,  1], [ 1,  0,  0]]
        perm[12] = [[ 0, -1,  0], [ 1,  0,  0], [ 0,  0,  1]]
        perm[13] = [[ 0, -1,  0], [ 0,  0, -1], [ 1,  0,  0]]
        perm[14] = [[ 0, -1,  0], [-1,  0,  0], [ 0,  0, -1]]
        perm[15] = [[ 0, -1,  0], [ 0,  0,  1], [-1,  0,  0]]
        perm[16] = [[ 0,  0,  1], [ 0,  1,  0], [-1,  0,  0]]
        perm[17] = [[ 0,  0,  1], [ 1,  0,  0], [ 0,  1,  0]]
        perm[18] = [[ 0,  0,  1], [ 0, -1,  0], [ 1,  0,  0]]
        perm[19] = [[ 0,  0,  1], [-1,  0,  0], [ 0, -1,  0]]
        perm[20] = [[ 0,  0, -1], [ 0,  1,  0], [ 1,  0,  0]]
        perm[21] = [[ 0,  0, -1], [-1,  0,  0], [ 0,  1,  0]]
        perm[22] = [[ 0,  0, -1], [ 0, -1,  0], [-1,  0,  0]]
        perm[23] = [[ 0,  0, -1], [ 1,  0,  0], [ 0, -1,  0]]

    return perm


def rotations(crystal_system):

    """
    rotations returns the set of unitary rotation matrices
    corresponding to the indistinguasible lattice permutations
    The values of the function only differ from permutations for
    trigonal and hexagonal crystal systems

    rot = rotations(crystal_system)
    U_new = U*rot

    U_new*B*perm*hkl = U*B*hkl, so U_new = U*B*perminv*Binv and
    rot = B*perminv*Binv. If B or perm is diagonal, rot = perminv.
    perminv included in perm, but to get the i'th entry of rot
    to correspond to the i'th entry of perm one must use perminv.

    crystal_system can be one of the following values
    1: Triclinic
    2: Monoclinic
    3: Orthorhombic
    4: Tetragonal
    5: Trigonal
    6: Hexagonal
    7: Cubic

    Jette Oddershede, Riso, 8/2/2010
    """

    if crystal_system < 1 or crystal_system > 7:
        raise ValueError('Crystal system shoud have a value between 1 and 7')

    if crystal_system == 1: # Triclinic
        rot = permutations(crystal_system)
        for i in range(len(rot)):
            rot[i] = rot[i].T

    if crystal_system == 2: # Monoclinic
        rot = permutations(crystal_system)
        for i in range(len(rot)):
            rot[i] = rot[i].T

    if crystal_system == 3: # Orthorhombic
        rot = permutations(crystal_system)
        for i in range(len(rot)):
            rot[i] = rot[i].T

    if crystal_system == 4: # Tetragonal
        rot = permutations(crystal_system)
        for i in range(len(rot)):
            rot[i] = rot[i].T

    if crystal_system == 5: # Trigonal
        perm = permutations(crystal_system)
        B = tools.form_b_mat([1.,1.,1.,90.,90.,120.])
        Binv = np.linalg.inv(B)
        rot = np.zeros((6, 3, 3))
        for i in range(len(perm)):
            rot[i] = np.dot(B,np.dot(np.linalg.inv(perm[i]),Binv))

    if crystal_system == 6: # Hexagonal
        perm = permutations(crystal_system)
        B = tools.form_b_mat([1.,1.,1.,90.,90.,120.])
        Binv = np.linalg.inv(B)
        rot = np.zeros((12, 3, 3))
        for i in range(len(perm)):
            rot[i] = np.dot(B,np.dot(np.linalg.inv(perm[i]),Binv))

    if crystal_system == 7: # Cubic
        rot = permutations(crystal_system)
        for i in range(len(rot)):
            rot[i] = rot[i].T

    return rot

ROTATIONS = [None] + [np.ascontiguousarray(rotations(i)) for i in range(1,8)]

