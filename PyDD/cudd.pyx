# file: cudd.pyx

from __future__ import print_function, unicode_literals
from libc.stdlib cimport malloc, free
from libc.stdio cimport FILE, stdout, fopen, fclose, fflush
from libc.string cimport strcpy
from libc.stdint cimport intptr_t, int32_t
cimport ccudd

import sys

UNIQUE_SLOTS = ccudd.CUDD_UNIQUE_SLOTS
CACHE_SLOTS = ccudd.CUDD_CACHE_SLOTS

REORDER_SAME = ccudd.CUDD_REORDER_SAME
REORDER_NONE = ccudd.CUDD_REORDER_NONE
REORDER_RANDOM = ccudd.CUDD_REORDER_RANDOM
REORDER_RANDOM_PIVOT = ccudd.CUDD_REORDER_RANDOM_PIVOT
REORDER_SIFT = ccudd.CUDD_REORDER_SIFT
REORDER_SIFT_CONVERGE = ccudd.CUDD_REORDER_SIFT_CONVERGE
REORDER_SYMM_SIFT = ccudd.CUDD_REORDER_SYMM_SIFT
REORDER_SYMM_SIFT_CONV = ccudd.CUDD_REORDER_SYMM_SIFT_CONV
REORDER_WINDOW2 = ccudd.CUDD_REORDER_WINDOW2
REORDER_WINDOW3 = ccudd.CUDD_REORDER_WINDOW3
REORDER_WINDOW4 = ccudd.CUDD_REORDER_WINDOW4
REORDER_WINDOW2_CONV = ccudd.CUDD_REORDER_WINDOW2_CONV
REORDER_WINDOW3_CONV = ccudd.CUDD_REORDER_WINDOW3_CONV
REORDER_WINDOW4_CONV = ccudd.CUDD_REORDER_WINDOW4_CONV
REORDER_GROUP_SIFT = ccudd.CUDD_REORDER_GROUP_SIFT
REORDER_GROUP_SIFT_CONV = ccudd.CUDD_REORDER_GROUP_SIFT_CONV
REORDER_ANNEALING = ccudd.CUDD_REORDER_ANNEALING
REORDER_GENETIC = ccudd.CUDD_REORDER_GENETIC
REORDER_LINEAR = ccudd.CUDD_REORDER_LINEAR
REORDER_LINEAR_CONVERGE = ccudd.CUDD_REORDER_LINEAR_CONVERGE
REORDER_LAZY_SIFT = ccudd.CUDD_REORDER_LAZY_SIFT
REORDER_EXACT = ccudd.CUDD_REORDER_EXACT

MTR_DEFAULT = ccudd.MTR_DEFAULT
MTR_FIXED = ccudd.MTR_FIXED

NO_ERROR = ccudd.CUDD_NO_ERROR
MEMORY_OUT = ccudd.CUDD_MEMORY_OUT
TOO_MANY_NODES = ccudd.CUDD_TOO_MANY_NODES
MAX_MEM_EXCEEDED = ccudd.CUDD_MAX_MEM_EXCEEDED
TIMEOUT_EXPIRED = ccudd.CUDD_TIMEOUT_EXPIRED
TERMINATION = ccudd.CUDD_TERMINATION
INVALID_ARG = ccudd.CUDD_INVALID_ARG
INTERNAL_ERROR = ccudd.CUDD_INTERNAL_ERROR
WRONG_PRECONDITIONS = ccudd.CUDD_WRONG_PRECONDITIONS

RESIDUE_DEFAULT = ccudd.CUDD_RESIDUE_DEFAULT
RESIDUE_MSB = ccudd.CUDD_RESIDUE_MSB
RESIDUE_TC = ccudd.CUDD_RESIDUE_TC

cdef class BDD
cdef class ADD
cdef class ZDD

@staticmethod
cdef MakeBDD(manager, ccudd.DdNode * node):
    bdd = BDD(manager)
    bdd._node = node
    ccudd.Cudd_Ref(node)
    return bdd

@staticmethod
cdef MakeADD(manager, ccudd.DdNode * node):
    add = ADD(manager)
    add._node = node
    ccudd.Cudd_Ref(node)
    return add

@staticmethod
cdef MakeZDD(manager, ccudd.DdNode * node):
    zdd = ZDD(manager)
    zdd._node = node
    ccudd.Cudd_Ref(node)
    return zdd

cdef class Cudd:
    """A class for decision diagrams.

    >>> mgr = Cudd()
    >>> x0 = mgr.bddVar()
    >>> x1 = mgr.bddVar()
    >>> f = x0 & ~x1
    >>> print(f)
    """
    cdef ccudd.DdManager * _manager
    cdef dict _varnames
    cdef dict _zvarnames

    def __cinit__(self, bddVars=0, zddVars=0, maxMem=0):
        """Create a CUDD manager."""
        self._manager = ccudd.Cudd_Init(bddVars,zddVars,
                                        ccudd.CUDD_UNIQUE_SLOTS,
                                        ccudd.CUDD_CACHE_SLOTS,
                                        maxMem)
        if self._manager is NULL:
            raise MemoryError(self.readErrorCode())
        self._varnames = {}
        self._zvarnames = {}

    def __dealloc__(self):
        """Destroy a CUDD manager."""
        ccudd.Cudd_Quit(self._manager)

    def size(self):
        """Return number of variables in manager."""
        return ccudd.Cudd_ReadSize(self._manager)

    def sizeZ(self):
        """Return number of ZDD variables in manager."""
        return ccudd.Cudd_ReadZddSize(self._manager)

    def readMemoryInUse(self):
        """Return number of bytes allocated to the manager."""
        return ccudd.Cudd_ReadMemoryInUse(self._manager)

    def reserve(self, amount):
        """Expand manager without creating variables."""
        if not ccudd.Cudd_Reserve(self._manager, amount):
            raise MemoryError(self.readErrorCode())

    def printInfo(self):
        """Print out statistics and settings for the CUDD manager."""
        sys.stdout.flush()
        ccudd.Cudd_PrintInfo(self._manager, stdout)
        fflush(stdout)

    def bddVar(self, index=None, name=None):
        """Return a BDD variable."""
        cdef ccudd.DdNode * var
        if index is None:
            var = ccudd.Cudd_bddNewVar(self._manager)
        else:
            var = ccudd.Cudd_bddIthVar(self._manager, index)
        if var is NULL:
            raise MemoryError(self.readErrorCode())
        if name is not None:
            self._varnames[ccudd.Cudd_NodeReadIndex(var)] = name
        return MakeBDD(self, var)

    def bddVariables(self):
        """Return list of BDD variables."""
        nvars = ccudd.Cudd_ReadSize(self._manager)
        return [MakeBDD(self, ccudd.Cudd_bddIthVar(self._manager, index))
                for index in range(nvars)]

    def getVariableName(self, index):
        """Return the name of a variable."""
        if index in self._varnames:
            return self._varnames[index]
        else:
            return str(index)

    def clearVariableNames(self):
        """Clear variable names."""
        self._varnames = {}

    def addVar(self, index=None, name=None):
        """Return an ADD variable."""
        cdef ccudd.DdNode * var
        if index is None:
            var = ccudd.Cudd_addNewVar(self._manager)
        else:
            var = ccudd.Cudd_addIthVar(self._manager, index)
        if var is NULL:
            raise MemoryError(self.readErrorCode())
        if name is not None:
            self._varnames[ccudd.Cudd_NodeReadIndex(var)] = name
        return MakeADD(self, var)

    def addVariables(self):
        """Return list of ADD variables."""
        nvars = ccudd.Cudd_ReadSize(self._manager)
        return [MakeADD(self, ccudd.Cudd_addIthVar(self._manager, index))
                for index in range(nvars)]

    def addConst(self, value):
        """Return an ADD constant."""
        cdef ccudd.DdNode * cnst = ccudd.Cudd_addConst(self._manager, value)
        return MakeADD(self, cnst)

    def zddVar(self, index=None, name=None):
        """Return a ZDD variable."""
        if index is None:
            index = ccudd.Cudd_ReadZddSize(self._manager)
        cdef ccudd.DdNode * var = ccudd.Cudd_zddIthVar(self._manager, index)
        if var is NULL:
            raise MemoryError(self.readErrorCode())
        if name is not None:
            self._zvarnames[index] = name
        return MakeZDD(self, var)

    def zddVariables(self):
        """Return list of ZDD variables."""
        nvars = ccudd.Cudd_ReadZddSize(self._manager)
        return [MakeZDD(self, ccudd.Cudd_zddIthVar(self._manager, index))
                for index in range(nvars)]

    def getZVariableName(self, index):
        """Return the name of a ZDD variable."""
        if index in self._zvarnames:
            return self._zvarnames[index]
        else:
            return str(index)

    def clearZVariableNames(self):
        """Clear ZDD variable names."""
        self._zvarnames = {}

    def zddVarsFromBddVars(self, multiplicity=1):
        if not ccudd.Cudd_zddVarsFromBddVars(self._manager, multiplicity):
            raise MemoryError(self.readErrorCode())

    def bddOne(self):
        """Return the true function."""
        cdef ccudd.DdNode * one = ccudd.Cudd_ReadOne(self._manager)
        if one is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, one)

    def bddZero(self):
        """Return the false function."""
        cdef ccudd.DdNode * zero = ccudd.Cudd_ReadLogicZero(self._manager)
        if zero is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, zero)

    def addOne(self):
        """Return the ADD function that is identically 1."""
        cdef ccudd.DdNode * one = ccudd.Cudd_ReadOne(self._manager)
        if one is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, one)

    def addZero(self):
        """Return the ADD function that is identically 0."""
        cdef ccudd.DdNode * zero = ccudd.Cudd_ReadZero(self._manager)
        if zero is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, zero)

    def plusInfinity(self):
        """Return the ADD function that is identically plus infinity."""
        cdef ccudd.DdNode * zero = ccudd.Cudd_ReadPlusInfinity(self._manager)
        if zero is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, zero)

    def minusInfinity(self):
        """Return the ADD function that is identically minus infinity."""
        cdef ccudd.DdNode * zero = ccudd.Cudd_ReadMinusInfinity(self._manager)
        if zero is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, zero)

    def background(self):
        """Return the ADD function that is the current background value."""
        cdef ccudd.DdNode * zero = ccudd.Cudd_ReadBackground(self._manager)
        if zero is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, zero)

    def setBackground(self, ADD bck):
        """Set the manager's background value."""
        ccudd.Cudd_SetBackground(self._manager, bck._node)

    def zddOne(self, topIndex=0):
        """Return the ZDD function that is identically 1."""
        cdef ccudd.DdNode * one = ccudd.Cudd_ReadZddOne(self._manager, topIndex)
        if one is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeZDD(self, one)

    def zddBase(self):
        """Return the ZDD base (negation of all variables)."""
        cdef ccudd.DdNode * base = ccudd.Cudd_ReadOne(self._manager)
        if base is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeZDD(self, base)

    def zddEmpty(self):
        """Return the ZDD empty."""
        cdef ccudd.DdNode * empty = ccudd.Cudd_ReadZero(self._manager)
        if empty is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeZDD(self, empty)

    def readStartTime(self):
        """Return the manager's start time."""
        return ccudd.Cudd_ReadStartTime(self._manager)

    def readElapsedTime(self):
        """Return the manager's elapsed time."""
        return ccudd.Cudd_ReadElapsedTime(self._manager)

    def setStartTime(self, st):
        """Set the manager's start time."""
        ccudd.Cudd_SetStartTime(self._manager, st)

    def resetStartTime(self):
        """Reset the manager's start time."""
        ccudd.Cudd_ResetStartTime(self._manager)

    def readTimeLimit(self):
        """Return the manager's time limit."""
        return ccudd.Cudd_ReadTimeLimit(self._manager)

    def setTimeLimit(self, lt):
        """Set the manager's time limit."""
        return ccudd.Cudd_SetTimeLimit(self._manager, lt)

    def updateTimeLimit(self):
        """Update the manager's time limit."""
        ccudd.Cudd_UpdateTimeLimit(self._manager)

    def increaseTimeLimit(self, increase):
        """Increase the manager's time limit."""
        ccudd.Cudd_IncreaseTimeLimit(self._manager, increase)

    def unsetTimeLimit(self):
        """Unset the manager's time limit."""
        ccudd.Cudd_UnsetTimeLimit(self._manager)

    def timeLimited(self):
        """Test whether the manager is time-limited."""
        return ccudd.Cudd_TimeLimited(self._manager)

    def readMaxLive(self):
        """Return the managere's maximum number of live nodes."""
        return ccudd.Cudd_ReadMaxLive(self._manager)

    def setMaxLive(self, maxLive):
        """Set the manager's maximum number of live nodes."""
        ccudd.Cudd_SetMaxLive(self._manager, maxLive)

    def readMaxMemory(self):
        """Return the manager's target maximum memory."""
        return ccudd.Cudd_ReadMaxMemory(self._manager)

    def setMaxMemory(self, maxMemory):
        """Set the manager's target maximum memory."""
        ccudd.Cudd_SetMaxMemory(self._manager, maxMemory)

    def srandom(self, seed=1):
        """Set the seed of the package's random number generator."""
        cdef int32_t s = seed
        ccudd.Cudd_Srandom(self._manager, s)

    def autodynEnable(self, method = ccudd.CUDD_REORDER_SIFT):
        """Enable dynamic variable reordering."""
        ccudd.Cudd_AutodynEnable(self._manager, method)

    def autodynDisable(self):
        """Disable dynamic variable reordering."""
        ccudd.Cudd_AutodynDisable(self._manager)

    def reorderingStatus(self):
        """Return the current reodering status and default method."""
        cdef ccudd.Cudd_ReorderingType method
        cdef bint status = ccudd.Cudd_ReorderingStatus(self._manager, &method)
        return (status, method)

    def reduceHeap(self, method = ccudd.CUDD_REORDER_SIFT, minsize = 0):
        """Invoke variable reordering."""
        cdef int res = ccudd.Cudd_ReduceHeap(self._manager, method, minsize)
        if res == 0:
            raise MemoryError(self.readErrorCode())
        return res

    def shuffleHeap(self, list permutation):
        """Permute variable order."""
        cdef int size = ccudd.Cudd_ReadSize(self._manager)
        if len(permutation) != size:
            raise TypeError("length of permutation ({0}) different ".format(len(permutation))
                            + "from number of variables ({0})".format(size))
        cdef int * p = <int *> malloc(size * sizeof(int))
        if p is NULL:
            raise MemoryError(self.readErrorCode())
        for i in range(size):
            v = permutation[i]
            if not 0 <= v < size:
                raise TypeError("{0} is not a valid variable index (not between 0 and {1})".format(v,size))
            p[i] = v
        cdef bint res = ccudd.Cudd_ShuffleHeap(self._manager, p)
        free(p)
        if not res:
            raise MemoryError(self.readErrorCode())

    def zddShuffleHeap(self, list permutation):
        """Permute ZDD variable order."""
        cdef int size = ccudd.Cudd_ReadZddSize(self._manager)
        if len(permutation) != size:
            raise TypeError("length of permutation ({0}) different ".format(len(permutation))
                            + "from number of variables ({0})".format(size))
        cdef int * p = <int *> malloc(size * sizeof(int))
        if p is NULL:
            raise MemoryError(self.readErrorCode())
        for i in range(size):
            v = permutation[i]
            if not 0 <= v < size:
                raise TypeError("{0} is not a valid variable index (not between 0 and {1})".format(v,size))
            p[i] = v
        cdef bint res = ccudd.Cudd_zddShuffleHeap(self._manager, p)
        free(p)
        if not res:
            raise MemoryError(self.readErrorCode())

    def enableReorderingReporting(self):
        """Enable reporting of variable reordering."""
        if not ccudd.Cudd_EnableReorderingReporting(self._manager):
            raise MemoryError(self.readErrorCode())

    def disableReorderingReporting(self):
        """Disable reporting of variable reordering."""
        if not ccudd.Cudd_DisableReorderingReporting(self._manager):
            raise MemoryError(self.readErrorCode())

    def reorderingReporting(self):
        """Test whether reordering reporting in enabled."""
        return ccudd.Cudd_ReorderingReporting(self._manager)

    def enableOrderingMonitoring(self):
        """Enable monitoring of variable order."""
        if not ccudd.Cudd_EnableOrderingMonitoring(self._manager):
            raise MemoryError(self.readErrorCode())

    def disableOrderingMonitoring(self):
        """Disable monitoring of variable order."""
        if not ccudd.Cudd_DisableOrderingMonitoring(self._manager):
            raise MemoryError(self.readErrorCode())

    def orderingMonitoring(self):
        """Test whether order monitoring is enabled."""
        return ccudd.Cudd_OrderingMonitoring(self._manager)

    def printBddOrder(self):
        """Print BDD variable order."""
        sys.stdout.flush()
        cdef char * tstr = "BDD"
        if not ccudd.Cudd_PrintGroupedOrder(self._manager, tstr, NULL):
            raise MemoryError(self.readErrorCode())
        fflush(stdout)

    def bddOrder(self):
        """Get BDD variable order."""
        nvars = ccudd.Cudd_ReadSize(self._manager)
        if len(self._varnames) == nvars:
            return [self._varnames[ccudd.Cudd_ReadInvPerm(self._manager, i)]
                    for i in range(nvars)]
        else:
            return [str(ccudd.Cudd_ReadInvPerm(self._manager, i))
                    for i in range(nvars)]

    def autodynEnableZdd(self, method = ccudd.CUDD_REORDER_SIFT):
        """Enable dynamic ZDD variable reordering."""
        ccudd.Cudd_AutodynEnableZdd(self._manager, method)

    def readReorderings(self):
        """Read the number of reorderings so far."""
        return ccudd.Cudd_ReadReorderings(self._manager)

    def maxReorderings(self, number = None):
        """Read and set maximum number of variable reorderings."""
        oldnumber = ccudd.Cudd_ReadMaxReorderings(self._manager)
        if number is not None:
            ccudd.Cudd_SetMaxReorderings(self._manager, number)
        return oldnumber

    def nextReordering(self, number = None):
        """Read and set threshold for next variable reordering."""
        oldnumber = ccudd.Cudd_ReadNextReordering(self._manager)
        if number is not None:
            ccudd.Cudd_SetNextReordering(self._manager, number)
        return oldnumber

    def autodynDisableZdd(self):
        """Disable dynamic ZDD variable reordering."""
        ccudd.Cudd_AutodynDisableZdd(self._manager)

    def reorderingStatusZdd(self):
        """Return the current ZDD reodering status and default method."""
        cdef ccudd.Cudd_ReorderingType method
        cdef bint status = ccudd.Cudd_ReorderingStatusZdd(self._manager, &method)
        return (status, method)

    def printZddOrder(self):
        """Print ZDD variable order."""
        sys.stdout.flush()
        cdef char * tstr = "ZDD"
        if not ccudd.Cudd_PrintGroupedOrder(self._manager, tstr, NULL):
            raise MemoryError(self.readErrorCode())
        fflush(stdout)

    def zddOrder(self):
        """Get ZDD variable order."""
        nvars = ccudd.Cudd_ReadZddSize(self._manager)
        if len(self._zvarnames) == nvars:
            return [self._zvarnames[ccudd.Cudd_ReadInvPermZdd(self._manager, i)]
                    for i in range(nvars)]
        else:
            return [str(ccudd.Cudd_ReadInvPermZdd(self._manager, i))
                    for i in range(nvars)]

    def zddReduceHeap(self, method = ccudd.CUDD_REORDER_SIFT, minsize = 0):
        """Invoke variable reordering."""
        cdef int res = ccudd.Cudd_zddReduceHeap(self._manager, method, minsize)
        if res == 0:
            raise MemoryError(self.readErrorCode())
        return res

    def zddRealignEnable(self):
        """Enable realignment of ZDD variable order to BDD order."""
        ccudd.Cudd_zddRealignEnable(self._manager)

    def zddRealignDisable(self):
        """Disable realignment of ZDD variable order to BDD order."""
        ccudd.Cudd_zddRealignDisable(self._manager)

    def zddRealignmentEnabled(self):
        """Test whether the realignment of ZDD order to BDD order is enabled."""
        return ccudd.Cudd_zddRealignmentEnabled(self._manager)

    def bddRealignEnable(self):
        """Enable realignment of BDD variable order to ZDD order."""
        ccudd.Cudd_bddRealignEnable(self._manager)

    def bddRealignDisable(self):
        """Disable realignment of BDD variable order to ZDD order."""
        ccudd.Cudd_bddRealignDisable(self._manager)

    def bddRealignmentEnabled(self):
        """Test whether the realignment of BDD order to ZDD order is enabled."""
        return ccudd.Cudd_bddRealignmentEnabled(self._manager)

    def readErrorCode(self):
        """Return the CUDD error code."""
        cdef int code = ccudd.Cudd_ReadErrorCode(self._manager)
        if code == NO_ERROR:
            return "no error"
        elif code == MEMORY_OUT:
            return "memory out"
        elif code == TOO_MANY_NODES:
            return "too many nodes"
        elif code == MAX_MEM_EXCEEDED:
            return "maximum memory exceeded"
        elif code == TIMEOUT_EXPIRED:
            return "timeout expired"
        elif code == TERMINATION:
            return "termination"
        elif code == INVALID_ARG:
            return "invalid argument"
        elif code == INTERNAL_ERROR:
            return "internal error"
        elif code == WRONG_PRECONDITIONS:
            return "preconditions violated"
        else:
            return "unknown error"

    def clearErrorCode(self):
        """Clear the manager's error code."""
        ccudd.Cudd_ClearErrorCode(self._manager)

    def sharingSize(self, list nodes):
        cdef int res
        cdef int n = len(nodes)
        cdef ccudd.DdNode * * f = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if f is NULL:
            raise MemoryError(self.readErrorCode())
        if type(nodes[0]) is BDD:
            for i in range(n):
                f[i] = (<BDD>nodes[i])._node
        elif type(nodes[0]) is ADD:
            for i in range(n):
                f[i] = (<ADD>nodes[i])._node
        else:
            for i in range(n):
                f[i] = (<ZDD>nodes[i])._node
        res = ccudd.Cudd_SharingSize(f, n)
        return res

    def dumpDot(self, list nodes, list node_names=None, file_path=None):
        """Write decision diagrams in dot format to standard output."""
        cdef bint res
        cdef char * * onames
        cdef int n = len(nodes)
        cdef FILE *fp
        if file_path is None:
            fp = stdout
            sys.stdout.flush()
        else:
            fp = fopen(file_path.encode('utf-8'), b'w')
        if n < 1:
            raise TypeError("number of nodes should be greater than 0")
        cdef ccudd.DdNode * * f = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if f is NULL:
            raise MemoryError("memory allocation failed")
        if type(nodes[0]) is BDD:
            for i in range(n):
                f[i] = (<BDD>nodes[i])._node
        elif type(nodes[0]) is ADD:
            for i in range(n):
                f[i] = (<ADD>nodes[i])._node
        else:
            for i in range(n):
                f[i] = (<ZDD>nodes[i])._node
        if node_names is None:
            onames = NULL
        else:
            if n != len(node_names):
                raise TypeError("Each node should be given a name")
            onames = <char * *> malloc(n * sizeof(char *))
            if onames is NULL:
                raise MemoryError("memory allocation failed")
            for i in range(n):
                utfname = node_names[i].encode('utf-8')
                one_name = <char *> malloc((len(utfname)+1) * sizeof(char))
                strcpy(one_name, utfname)
                onames[i] = one_name
        cdef int size
        cdef char * * variable_names
        if type(nodes[0]) is ZDD:
            size = ccudd.Cudd_ReadZddSize(self._manager)
            if len(self._zvarnames) == size:
                variable_names = <char * *> malloc(size * sizeof(char *))
                if variable_names is NULL:
                    raise MemoryError("memory allocation failed")
                for i in range(size):
                    utfname = self._zvarnames[i].encode('utf-8')
                    one_name = <char *> malloc((len(utfname)+1) * sizeof(char))
                    strcpy(one_name, utfname)
                    variable_names[i] = one_name
            else:
                variable_names = NULL
            res = ccudd.Cudd_zddDumpDot(self._manager, n, f,
                                        <const char * const *>variable_names,
                                        <const char * const *>onames, fp)
        else:
            size = ccudd.Cudd_ReadSize(self._manager)
            if len(self._varnames) == size:
                variable_names = <char * *> malloc(size * sizeof(char *))
                if variable_names is NULL:
                    raise MemoryError("memory allocation failed")
                for i in range(size):
                    utfname = self._varnames[i].encode('utf-8')
                    one_name = <char *> malloc((len(utfname)+1) * sizeof(char))
                    strcpy(one_name, utfname)
                    variable_names[i] = one_name
            else:
                variable_names = NULL
            res = ccudd.Cudd_DumpDot(self._manager, n, f,
                                     <const char * const *>variable_names,
                                     <const char * const *>onames, fp)
        if file_path is not None:
            fclose(fp)
        if variable_names is not NULL:
            for i in range(size):
                free(variable_names[i])
            free(variable_names)
        if onames is not NULL:
            for i in range(n):
                free(onames[i])
            free(onames)
        free(f)
        if not res:
            raise MemoryError(self.readErrorCode())

    def symmProfile(self, lower=0, upper=None):
        """Report on symmetric variables."""
        if upper is None:
            upper = ccudd.Cudd_ReadSize(self._manager) - 1
        ccudd.Cudd_SymmProfile(self._manager, lower, upper)

    def zddSymmProfile(self, lower=0, upper=None):
        """Report on ZDD symmetric variables."""
        if upper is None:
            upper = ccudd.Cudd_ReadZddSize(self._manager) - 1
        ccudd.Cudd_zddSymmProfile(self._manager, lower, upper)

    def makeTreeNode(self, low, size = 2, groupType = ccudd.MTR_FIXED):
        """Create a variable group."""
        cdef ccudd.MtrNode * res = ccudd.Cudd_MakeTreeNode(self._manager, low, size, groupType)
        if res is NULL:
            raise MemoryError(self.readErrorCode())

    def makeZddTreeNode(self, low, size = 2, groupType = ccudd.MTR_FIXED):
        """Create a ZDD variable group."""
        cdef ccudd.MtrNode * res = ccudd.Cudd_MakeZddTreeNode(self._manager, low, size, groupType)
        if res is NULL:
            raise MemoryError(self.readErrorCode())

    def xeqy(self, list x, list y):
        """Build BDD or ADD for the x==y function.

        Whether a BDD or an ADD is returned depends on the variables in
        the x and y lists.  It is an error to mix BDD and ADD variables.
        """
        cdef int n = len(x)
        if n < 1:
            raise TypeError("There should be at least one x variable")
        if len(y) != n:
            raise TypeError("The number of y variables should equal the number of x variables")
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * res
        if type(x[0]) is BDD:
            for i in range(n):
                xvars[i] = (<BDD>x[i])._node
                yvars[i] = (<BDD>y[i])._node
            res = ccudd.Cudd_Xeqy(self._manager, n, xvars, yvars)
        else:
            for i in range(n):
                xvars[i] = (<ADD>x[i])._node
                yvars[i] = (<ADD>y[i])._node
            res = ccudd.Cudd_addXeqy(self._manager, n, xvars, yvars)
        free(yvars)
        free(xvars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        if type(x[0]) is BDD:
            return MakeBDD(self, res)
        else:
            return MakeADD(self, res)

    def xgty(self, list x, list y):
        """Build BDD for the x>y function."""
        cdef int n = len(x)
        if n < 1:
            raise TypeError("There should be at least one x variable")
        if len(y) != n:
            raise TypeError("The number of y variables should equal the number of x variables")
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * res
        for i in range(n):
            xvars[i] = (<BDD>x[i])._node
            yvars[i] = (<BDD>y[i])._node
        res = ccudd.Cudd_Xgty(self._manager, n, NULL, xvars, yvars)
        free(yvars)
        free(xvars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def inequality(self, c, list x, list y):
        """Return the BDD for the function x - y >= c."""
        cdef n = len(x)
        if len(y) != n:
            raise TypeError("The two sets of variables should have the same size")
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        for i in range(n):
            xvars[i] = (<BDD>x[i])._node
            yvars[i] = (<BDD>y[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_Inequality(self._manager, n, <int>c, xvars, yvars)
        free(xvars)
        free(yvars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def disequality(self, c, list x, list y):
        """Return the BDD for the function x - y != c."""
        cdef n = len(x)
        if len(y) != n:
            raise TypeError("The two lists of variables should have the same length")
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        for i in range(n):
            xvars[i] = (<BDD>x[i])._node
            yvars[i] = (<BDD>y[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_Disequality(self._manager, n, <int>c, xvars, yvars)
        free(xvars)
        free(yvars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def interval(self, list x, lower, upper=None):
        """Return the BDD for the function lower <= x <= upper."""
        if upper is None:
            upper = lower
        if lower > upper:
            raise TypeError("lower bound ({0}) greater than ".format(lower)
                            + "upper bound ({0})".format(upper))
        cdef n = len(x)
        cdef ccudd.DdNode * * vars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if vars is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(n):
            vars[i] = (<BDD>x[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_bddInterval(self._manager, n, vars, lower, upper)
        free(vars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def cardinality(self, list x, lower, upper=None):
        """Compute the BDD for the function lower <= cardinality <= upper."""
        if upper is None:
            upper = lower
        if lower > upper:
            raise TypeError("lower bound ({0}) greater than ".format(lower)
                            + "upper bound ({0})".format(upper))
        cdef n = len(x)
        cdef ccudd.DdNode * * vars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if vars is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(n):
            if not isinstance(x[i], BDD):
                raise TypeError("The variable list is not a list of BDDs.")
            vars[i] = (<BDD>x[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_bddCardinality(self._manager, vars, n, lower, upper)
        free(vars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def fromCubeString(self, cubestring):
        """Return BDD from cube string."""
        cdef int size = ccudd.Cudd_ReadSize(self._manager)
        if len(cubestring) != size:
            raise TypeError("length of string different from number of variables")
        cdef int * carray = <int *> malloc(size * sizeof(int))
        if carray is NULL:
            raise MemoryError(self.readErrorCode())
        allowed = set(['0','1','2','-'])
        for (c,i) in zip(cubestring,range(size)):
            if not c in allowed:
                raise ValueError("unexpected character (%s) in string" % c)
            carray[i] = 2 if c == "-" else int(c)
        cdef ccudd.DdNode * res = ccudd.Cudd_CubeArrayToBdd(self._manager, carray)
        free(carray)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def fromLiteralList(self, list lits):
        """Return BDD from cube literal list."""
        cdef int size = ccudd.Cudd_ReadSize(self._manager)
        if len(lits) != size:
            raise TypeError("length of list different from number of variables")
        cdef int * carray = <int *> malloc(size * sizeof(int))
        if carray is NULL:
            raise MemoryError(self.readErrorCode())
        allowed = set([0,1,2])
        for i in range(len(lits)):
            l = lits[i]
            if not l in allowed:
                raise ValueError("unexpected literal (%d) in list" % l)
            carray[i] = l
        cdef ccudd.DdNode * res = ccudd.Cudd_CubeArrayToBdd(self._manager, carray)
        free(carray)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def conjoin(self, list bdds, list phase=None):
        """Return the conjunction of a set of BDDs with optional phases."""
        cdef int n = len(bdds)
        cdef ccudd.DdNode * * carray = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if carray is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(n):
            carray[i] = (<BDD>bdds[i])._node
        cdef int * cphase = NULL

        if phase is None:
            cphase = NULL
        else:
            if len(phase) != n:
                raise TypeError("lists of different length")
            cphase = <int *> malloc(n * sizeof(int))
            if cphase is NULL:
                raise MemoryError("memory allocation failed")
            allowed = set([0,1])
            for i in range(n):
                ph = phase[i]
                if not ph in allowed:
                    raise ValueError("unexpected phase (%d) in list" % ph)
                cphase[i] = ph

        cdef ccudd.DdNode * res = ccudd.Cudd_bddComputeCube(self._manager, carray,
                                                            cphase, n)
        free(carray)
        if cphase is not NULL:
            free(cphase)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeBDD(self, res)

    def Walsh(self, list x, list y):
        """Return the ADD of a Walsh matrix."""
        cdef int n = len(x)
        if len(y) != n:
            raise TypeError("The two lists of variables should have the same length")
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        for i in range(n):
            xvars[i] = (<ADD>x[i])._node
            yvars[i] = (<ADD>y[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_addWalsh(self._manager, xvars, yvars, n)
        free(xvars)
        free(yvars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, res)

    def Hamming(self, list x, list y):
        """Return the ADD of the Hamming distance between x and y."""
        cdef int n = len(x)
        if len(y) != n:
            raise TypeError("The two lists of variables should have the same length")
        if n < 1:
            raise TypeError("There should be at least one variable in each set")
        if type(x[0]) is ADD:
            x = [v.bddPattern() for v in x]
        if type(y[0]) is ADD:
            y = [v.bddPattern() for v in y]
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        for i in range(n):
            xvars[i] = (<BDD>x[i])._node
            yvars[i] = (<BDD>y[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_addHamming(self._manager, xvars, yvars, n)
        free(xvars)
        free(yvars)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, res)

    def residue(self, nbits, modulus, options=ccudd.CUDD_RESIDUE_DEFAULT, top=0):
        """Return the ADD of the residue modulo 'modulus.'"""
        cdef ccudd.DdNode * res = ccudd.Cudd_addResidue(self._manager, nbits,
                                                        modulus, options, top)
        if res is NULL:
            raise MemoryError(self.readErrorCode())
        return MakeADD(self, res)


cdef class BDD:
    """Class of Binary Decision Diagrams."""

    cdef Cudd _mgr
    cdef ccudd.DdNode * _node

    def __cinit__(self, manager):
        """Create a BDD."""
        self._mgr = manager
        self._node = NULL

    def __dealloc__(self):
        """Destroy a BDD."""
        if self._node is not NULL:
            #print("destructor called")
            ccudd.Cudd_RecursiveDeref(<ccudd.DdManager *>self._mgr._manager,
                                      self._node)

    def __repr__(self):
        """Return a factored form string for a BDD."""
        cdef int i
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        cdef char * * variable_names
        if len(self._mgr._varnames) == size:
            variable_names = <char * *> malloc(size * sizeof(char *))
            for i in range(size):
                utfname = self._mgr._varnames[i].encode('utf-8')
                one_name = <char *> malloc((len(utfname)+1) * sizeof(char))
                strcpy(one_name, utfname)
                variable_names[i] = one_name
        else:
            variable_names = NULL
        cdef char * str = ccudd.Cudd_FactoredFormString(dd, self._node,
                                                        <const char * const *>
                                                        variable_names)
        if variable_names is not NULL:
            for i in range(size):
                free(variable_names[i])
            free(variable_names)
        if str is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        i = 0
        while str[i] != b'\0':
            if str[i] == b'!':
                str[i] = b'~'
            i += 1
        cdef bytes py_str = <bytes> str
        free(str)
        return py_str.decode('utf-8', 'strict')

    def __hash__(self):
        """Return hash code for a BDD."""
        return int(<intptr_t> self._node)

    def negate(self):
        """Return the negation of the BDD."""
        cdef ccudd.DdNode * fnot = ccudd.Cudd_Not(self._node)
        if fnot is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, fnot)

    def __invert__(self):
        """Return the negation of the BDD."""
        return self.negate()

    def conjoin(self, BDD other, limit=None):
        """Return the conjunction with another BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        if limit is None:
            res = ccudd.Cudd_bddAnd(dd, self._node, other._node)
        else:
            res = ccudd.Cudd_bddAndLimit(dd, self._node, other._node, limit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def __and__(self, BDD other):
        """Return the conjunction with another BDD."""
        return self.conjoin(other)

    def iconjoin(self, BDD other):
        """Conjoin this BDD with another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddAnd(dd, self._node,
                                                    other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def __iand__(self, BDD other):
        """Conjoin this BDD with another."""
        return self.iconjoin(other)

    def disjoin(self, BDD other):
        """Return the disjunction with another BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * disj = ccudd.Cudd_bddOr(dd, self._node,
                                                    other._node)
        if disj is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, disj)

    def __or__(self, BDD other):
        """Return the disjunction with another BDD."""
        return self.disjoin(other)

    def __ior__(self, BDD other):
        """Disjoin this BDD with another."""
        return self.disjoin(other)

    def xor(self, BDD other):
        """Return the exclusive or with another BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * diff = ccudd.Cudd_bddXor(dd, self._node,
                                                     other._node)
        if diff is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, diff)

    def __xor__(self, BDD other):
        """Return the symmetric difference with another BDD."""
        return self.xor(other)

    def __ixor__(self, BDD other):
        """Take symmetric difference of this BDD with another."""
        return self.xor(other)

    def xnor(self, BDD other, limit=None):
        """Return the exclusive NOR with another BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        if limit is None:
            res = ccudd.Cudd_bddXnor(dd, self._node, other._node)
        else:
            res = ccudd.Cudd_bddXnorLimit(dd, self._node, other._node,
                                         limit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def iff(self, BDD other, limit=None):
        """Return the equivalence with another BDD."""
        return self.xnor(other, limit)

    def implies(self, BDD other, limit=None):
        """Return the OR of the negation with another BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        if limit is None:
            res = ccudd.Cudd_bddAnd(dd, self._node, ccudd.Cudd_Not(other._node))
        else:
            res = ccudd.Cudd_bddAndLimit(dd, self._node,
                                         ccudd.Cudd_Not(other._node), limit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, ccudd.Cudd_Not(res))

    def ite(self, BDD g, BDD h, limit=None):
        """Perform the if-then-else operation."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        if limit is None:
            res = ccudd.Cudd_bddIte(dd, self._node, g._node, h._node)
        else:
            res = ccudd.Cudd_bddIteLimit(dd, self._node, g._node, h._node,
                                         limit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def intersect(self, BDD other):
        """Return a function included in the intersection of this BDD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        res = ccudd.Cudd_bddIntersect(dd, self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def intersectionCube(self, BDD other):
        """Return a cube included in the intersection of this BDD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        res = ccudd.Cudd_bddIntersectionCube(dd, self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def closestCube(self, BDD other):
        """Find a cube of f at minimum Hamming distance from the minterms of g."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int distance
        res = ccudd.Cudd_bddClosestCube(dd, self._node, other._node, &distance)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res), distance

    def compare(self, BDD other, int op):
        """Compare this BDD to another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if op == 2:   # ==
            return self._node == other._node
        elif op == 3: # !=
            return self._node != other._node
        elif op == 1: # <=
            return ccudd.Cudd_bddLeq(dd, self._node, other._node)
        elif op == 4: # >
            return self._node != other._node and ccudd.Cudd_bddLeq(dd, other._node, self._node)
        elif op == 0: # <
            return self._node != other._node and ccudd.Cudd_bddLeq(dd, self._node, other._node)
        else:         # >=
            return ccudd.Cudd_bddLeq(dd, other._node, self._node)

    def __richcmp__(self, other, op):
        """Compare this BDD to another."""
        return self.compare(other, op)

    def isOne(self):
        """Test whether this BDD is the true function."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return self._node == ccudd.Cudd_ReadOne(dd)

    def isZero(self):
        """Test whether this BDD is the false function."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return self._node == ccudd.Cudd_ReadLogicZero(dd)

    def __bool__(self):
        """Test whether this BDD is not the false function."""
        return not self.isZero()

    def isConstant(self):
        """Test whether this BDD is a constant function."""
        return ccudd.Cudd_IsConstant(self._node)

    def isNonConstant(self):
        """Test whether this BDD is a non-constant function."""
        return ccudd.Cudd_IsNonConstant(self._node)

    def isVar(self):
        """Test whether this BDD is a variable."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_bddIsVar(dd, self._node)

    def display(self, numVars=None, detail=2, name=None):
        """Display this BDD."""
        if name:
            print(name, end='')
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        if not ccudd.Cudd_PrintDebug(dd, self._node, numVars, detail):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)

    def summary(self, numVars=None, mode=0, name=None):
        """Print a summary of this BDD."""
        if name:
            print(name, end='')
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        if not ccudd.Cudd_PrintSummary(dd, self._node, numVars, mode):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)

    def cubes(self, epilog=None):
        """Print a disjoint-cube cover of this BDD."""
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if not ccudd.Cudd_PrintMinterm(dd, self._node):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)
        if epilog is not None:
            print(epilog)

    def printCover(self, BDD upper_bound=None):
        """Print a disjunctive normal form cover of this BDD."""
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if upper_bound is None:
            upper_bound = self
        if not ccudd.Cudd_bddPrintCover(dd, self._node, upper_bound._node):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)

    def interpolate(self, BDD upper_bound):
        """Compute an interpolant between this BDD and upper_bound."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * ip = ccudd.Cudd_bddInterpolate(dd, self._node,
                                                           upper_bound._node)
        if ip is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, ip)

    def generate_primes(self, BDD upper_bound=None):
        """Generate prime implicants of this BDD."""
        if upper_bound is None:
            upper_bound = self
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        cdef int * cube
        cdef ccudd.DdGen * gen = ccudd.Cudd_FirstPrime(dd, self._node,
                                                       upper_bound._node, &cube)
        if gen is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        while not ccudd.Cudd_IsGenEmpty(gen):
            yield [cube[i] for i in range(size)]
            ccudd.Cudd_NextPrime(gen, &cube)
        ccudd.Cudd_GenFree(gen)

    def generate_cubes(self):
        """Generate cubes of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        cdef int * cube
        cdef ccudd.CUDD_VALUE_TYPE value
        cdef ccudd.DdGen * gen = ccudd.Cudd_FirstCube(dd, self._node,
                                                      &cube, &value)
        if gen is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        while not ccudd.Cudd_IsGenEmpty(gen):
            yield [cube[i] for i in range(size)]
            ccudd.Cudd_NextCube(gen, &cube, &value)
        ccudd.Cudd_GenFree(gen)

    def pickOneCube(self):
        """Pick a cube from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        cdef char * cubestring = <char *> malloc(size * sizeof(char))
        if cubestring is NULL:
            raise MemoryError("memory allocation failed")
        cdef int res = ccudd.Cudd_bddPickOneCube(dd, self._node,
                                                 cubestring)
        if not res:
            raise ValueError(self._mgr.readErrorCode())
        retstring = [cubestring[i] for i in range(size)]
        free(cubestring)
        return retstring

    def pickOneMinterm(self, list vars=None):
        """Pick a minterm from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * * cvars
        cdef int nvars
        if vars is None:
            nvars = ccudd.Cudd_ReadSize(dd)
            cvars = <ccudd.DdNode * *> malloc(nvars * sizeof(ccudd.DdNode *))
            if cvars is NULL:
                raise MemoryError("memory allocation failed")
            for index in range(nvars):
                cvars[index] = ccudd.Cudd_bddIthVar(dd, index)
        else:
            nvars = len(vars)
            cvars = <ccudd.DdNode * *> malloc(nvars * sizeof(ccudd.DdNode *))
            for i in range(nvars):
                if not vars[i].isVar():
                    free(cvars)
                    raise TypeError("Found a non-variable at position {0}".format(i))
                cvars[i] = (<BDD>vars[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_bddPickOneMinterm(dd, self._node, cvars, nvars)
        free(cvars)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def pickCube(self):
        """Pick a cube from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddPickCube(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def existAbstract(self, BDD cube, limit=None):
        """Existentially quantify variables from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        if limit is None:
            res = ccudd.Cudd_bddExistAbstract(dd, self._node, cube._node)
        else:
            res = ccudd.Cudd_bddExistAbstractLimit(dd, self._node, cube._node,
                                                   limit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def univAbstract(self, BDD cube):
        """Universally quantify variables from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddUnivAbstract(dd, self._node,
                                                             cube._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def andAbstract(self, BDD other, BDD cube, limit=None):
        """Conjoin to another BDD and existentially quantify variables."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        if limit is None:
            res = ccudd.Cudd_bddAndAbstract(dd, self._node, other._node,
                                            cube._node)
        else:
            res = ccudd.Cudd_bddAndAbstractLimit(dd, self._node, other._node,
                                                 cube._node, limit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def booleanDiff(self, BDD var):
        """Compute the Boolean difference w.r.t. a variable."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int idx = var.index()
        cdef ccudd.DdNode * res = ccudd.Cudd_bddBooleanDiff(dd, self._node, idx)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def compose(self, BDD other, int index):
        """Substitute a variable with a function."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddCompose(dd, self._node,
                                                        other._node, index)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def vectorCompose(self, list vars, list vector):
        """Simultaneously substitute a list of variables."""
        cdef int ns = len(vars)
        if len(vector) != ns:
            raise TypeError("The number of functions should equal the number of variables")
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        if ns > size:
            raise TypeError("More substitutions than existing BDD variables")
        cdef ccudd.DdNode * * functions = <ccudd.DdNode * *> malloc(size * sizeof(ccudd.DdNode *))
        if functions is NULL:
            raise MemoryError("memory allocation failed")
        # Here we rely on the fact that projection functions need no referencing.
        for index in range(size):
            functions[index] = ccudd.Cudd_bddIthVar(dd, index)
        for i in range(ns):
            if not vars[i].isVar():
                free(functions)
                raise TypeError("Found a non-variable at position {0}".format(i))
            functions[vars[i].index()] = (<BDD>vector[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_bddVectorCompose(dd, self._node, functions)
        free(functions)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def swapVariables(self, list current_vars, list new_vars):
        """Swap two lists of variables."""
        if len(current_vars) != len(new_vars):
            raise TypeError("The two lists of variables should have the same length")
        cdef int n = len(current_vars)
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        for i in range(n):
            xvars[i] = (<BDD>current_vars[i])._node
            yvars[i] = (<BDD>new_vars[i])._node
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddSwapVariables(dd, self._node,
                                                              xvars, yvars, n)
        free(xvars)
        free(yvars)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def permute(self, permutation):
        """Return BDD with permuted variables."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        if len(permutation) != size:
            raise TypeError("length of permutation ({0}) different ".format(len(permutation))
                            + "from number of variables ({0})".format(size))
        cdef int * p = <int *> malloc(size * sizeof(int))
        if p is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(size):
            v = permutation[i]
            if not 0 <= v < size:
                raise TypeError("{0} is not a valid variable index (not between 0 and {1})".format(v,size))
            p[i] = v
        cdef ccudd.DdNode * res = ccudd.Cudd_bddPermute(dd, self._node, p)
        free(p)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def cofactor(self, BDD cube):
        """Cofactor w.r.t. set of literals (signed variables)."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_Cofactor(dd, self._node,
                                                      cube._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def isCube(self):
        """Test whether this BDD is a conjunction of literals."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_CheckCube(dd, self._node)

    def dual(self):
        """Return dual of BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddDual(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def isDual(self, BDD other):
        """Check if BDD is dual to another BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_bddAreDual(dd, self._node, other._node)

    def isSelfDual(self):
        """Check if BDD is self-dual."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_bddAreDual(dd, self._node, self._node)

    def constrain(self, BDD constraint):
        """Apply the 'constrain' generalized cofactor.""" 
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddConstrain(dd, self._node,
                                                          constraint._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def restrict(self, BDD constraint):
        """Apply the 'restrict' generalized cofactor."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddRestrict(dd, self._node,
                                                         constraint._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def npAnd(self, BDD constraint, limit=None):
        """Apply the 'non-polluting-and' generalized cofactor."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        if limit is None:
            res = ccudd.Cudd_bddNPAnd(dd, self._node, constraint._node)
        else:
            res = ccudd.Cudd_bddNPAndLimit(dd, self._node, constraint._node, limit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def LIcompaction(self, BDD constraint):
        """Apply the 'LI compaction' generalized cofactor."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddLICompaction(dd, self._node,
                                                             constraint._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def squeeze(self, BDD ub):
        """Apply the 'squeeze' generalized cofactor."""
        if not ub >= self:
            raise TypeError("invalid upper bound")
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddSqueeze(dd, self._node,
                                                        ub._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def minimize(self, BDD constraint):
        """Apply the 'minimize' generalized cofactor."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddMinimize(dd, self._node,
                                                         constraint._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def charToVect(self):
        """Compute a vector of BDDs whose image is this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * * vect = <ccudd.DdNode * *> ccudd.Cudd_bddCharToVect(dd, self._node)
        if vect is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        cdef int n = ccudd.Cudd_ReadSize(dd)
        res = [MakeBDD(self._mgr, vect[i]) for i in range(n)]
        free(vect)
        return res

    def probabilities(self):
        """Return variable probabilities."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef double * vect = ccudd.Cudd_CofMinterm(dd, self._node)
        cdef int n = ccudd.Cudd_ReadSize(dd)
        # The factor of 2 is to account for the lack of one variable
        # in each cofactor.
        res = [vect[i]/(vect[n]*2.0) for i in range(n)]
        free(vect)
        return res

    def support(self):
        """Compute the cube of the variables in the support of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_Support(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def varIsDependent(self, BDD var):
        """Test whether var is dependent in this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_bddVarIsDependent(dd, self._node, var._node)

    def varsAreSymmetric(self, int index1, int index2):
        """Test whether variables are symmetric in this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_VarsAreSymmetric(dd, self._node, index1, index2)

    def size(self):
        """Return the size of this BDD."""
        return ccudd.Cudd_DagSize(self._node)

    def index(self):
        """Return the index of the root of this BDD."""
        return ccudd.Cudd_NodeReadIndex(self._node)

    def eval(self, values):
        """Evaluate this BDD for specified values of the variables."""
        cdef int n = len(values)
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        if n != size:
            raise TypeError("number of values ({0}) different ".format(n) +
                            "from number of variables ({0})".format(size))
        cdef int * inputs = <int *> malloc(n * sizeof(int))
        if inputs is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(n):
            if not values[i] in range(2):
                free(inputs)
                raise TypeError("non-binary value ({0}) ".format(values[i]) +
                                "in position {0}".format(i))
            inputs[i] = values[i]
        cdef ccudd.DdNode * res = ccudd.Cudd_Eval(dd, self._node, inputs)
        free(inputs)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def isDecreasing(self, i):
        """Return True if and only if this BDD is decreasing in index i."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_Decreasing(dd, self._node, i)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return res == ccudd.Cudd_ReadOne(dd)

    def isIncreasing(self, i):
        """Return True if and only if this BDD is increasing in index i."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_Increasing(dd, self._node, i)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return res == ccudd.Cudd_ReadOne(dd)

    def isPositive(self):
        """Return True if and only if this BDD is increasing in all variables."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_bddPositive(dd, self._node)

    def isNegative(self):
        """Return True if and only if this BDD is decreasing in all variables."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_bddNegative(dd, self._node)

    def makePrime(self, BDD f):
        """Expand this cube BDD to a prime implicant of f."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddMakePrime(dd, self._node, f._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def maximallyExpand(self, BDD ub, BDD f):
        """Expand this BDD to the disjunction of primes of (f and ub)."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddMaximallyExpand(dd, self._node, ub._node, f._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)
        pass

    def largestPrimeUnate(self, BDD phaseBDD):
        """Find largest prime implicant of a unate function."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddLargestPrimeUnate(dd, self._node, phaseBDD._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)
        pass

    def essential(self):
        """Return the cube of the essential variables of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_FindEssential(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def isEssential(self, BDD var):
        """Test whether a variable is essential in this BDD."""
        if (~var).isVar():
            phase = False
        elif not var.isVar():
            raise TypeError("parameter is not a variable")
        else:
            phase = True
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int idx = var.index()
        return ccudd.Cudd_bddIsVarEssential(dd, self._node, idx, phase)

    def solveEqn(self, list unknowns, verify=False):
        """Solve the equation F=0 for the unknowns."""
        Y = self._mgr.bddOne()
        for y in unknowns:
            Y &= y
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int n = len(unknowns)
        cdef ccudd.DdNode * * G = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if G is NULL:
            raise MemoryError("memory allocation failed")
        cdef int * yindex = NULL
        cdef ccudd.DdNode * consist = ccudd.Cudd_SolveEqn(dd, self._node, (<BDD>Y)._node, G, &yindex, n)
        if consist is NULL:
            free(yindex)
            raise MemoryError(self._mgr.readErrorCode())
        cdef ccudd.DdNode * ver
        if verify:
            ver = ccudd.Cudd_VerifySol(dd, self._node, G, yindex, n)
            if ver != consist:
                free(G)
                raise RuntimeError(self._mgr.readErrorCode())
        else:
            free(yindex)
        solutions = [MakeBDD(self._mgr, G[i]) for i in range(n)]
        free(G)
        return (MakeBDD(self._mgr, consist), solutions)

    def remapUnderApprox(self, numVars=0, threshold=0, quality=1.0):
        """Compute an underapproximation of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_RemapUnderApprox(dd, self._node, numVars, threshold, quality)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def remapOverApprox(self, numVars=0, threshold=0, quality=1.0):
        """Compute an overapproximation of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_RemapOverApprox(dd, self._node, numVars, threshold, quality)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def biasedUnderApprox(self, BDD bias, numVars=0, threshold=0, quality1=1.0, quality0=1.0):
        """Compute a biased underapproximation of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_BiasedUnderApprox(dd, self._node, bias._node, numVars, threshold, quality1, quality0)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def biasedOverApprox(self, BDD bias, numVars=0, threshold=0, quality1=1.0, quality0=1.0):
        """Compute a biased overapproximation of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_BiasedOverApprox(dd, self._node, bias._node, numVars, threshold, quality1, quality0)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def genConjDecomp(self):
        """Decompose this BDD conjunctively."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode ** conjuncts = NULL
        cdef int nc = ccudd.Cudd_bddGenConjDecomp(dd, self._node, &conjuncts)
        if nc == 0:
            raise MemoryError(self._mgr.readErrorCode())
        left = MakeBDD(self._mgr, conjuncts[0])
        if nc == 1:
            right = self._mgr.bddOne()
        else:
            right = MakeBDD(self._mgr, conjuncts[1])
        free(conjuncts)
        return (left,right)

    def varConjDecomp(self):
        """Decompose this BDD conjunctively."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode ** conjuncts = NULL
        cdef int nc = ccudd.Cudd_bddVarConjDecomp(dd, self._node, &conjuncts)
        if nc == 0:
            raise MemoryError(self._mgr.readErrorCode())
        left = MakeBDD(self._mgr, conjuncts[0])
        if nc == 1:
            right = self._mgr.bddOne()
        else:
            right = MakeBDD(self._mgr, conjuncts[1])
        free(conjuncts)
        return (left,right)

    def approxConjDecomp(self):
        """Decompose this BDD conjunctively."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode ** conjuncts = NULL
        cdef int nc = ccudd.Cudd_bddApproxConjDecomp(dd, self._node, &conjuncts)
        if nc == 0:
            raise MemoryError(self._mgr.readErrorCode())
        left = MakeBDD(self._mgr, conjuncts[0])
        if nc == 1:
            right = self._mgr.bddOne()
        else:
            right = MakeBDD(self._mgr, conjuncts[1])
        free(conjuncts)
        return (left,right)

    def iterConjDecomp(self):
        """Decompose this BDD conjunctively."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode ** conjuncts = NULL
        cdef int nc = ccudd.Cudd_bddIterConjDecomp(dd, self._node, &conjuncts)
        if nc == 0:
            raise MemoryError(self._mgr.readErrorCode())
        left = MakeBDD(self._mgr, conjuncts[0])
        if nc == 1:
            right = self._mgr.bddOne()
        else:
            right = MakeBDD(self._mgr, conjuncts[1])
        free(conjuncts)
        return (left,right)

    def subsetHeavyBranch(self, numVars=0, threshold=1):
        """Extract a dense subset from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_SubsetHeavyBranch(dd, self._node, numVars, threshold)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def supersetHeavyBranch(self, numVars=0, threshold=1):
        """Extract a dense subset from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_SupersetHeavyBranch(dd, self._node, numVars, threshold)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def subsetShortPaths(self, numVars=0, threshold=1, hardlimit=False):
        """Extract a dense subset from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_SubsetShortPaths(dd, self._node, numVars, threshold, hardlimit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def supersetShortPaths(self, numVars=0, threshold=1, hardlimit=False):
        """Extract a dense subset from this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_SupersetShortPaths(dd, self._node, numVars, threshold, hardlimit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def toADD(self):
        """Return the result of converting this BDD to an ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_BddToAdd(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def toZDD(self, BDD cube=None):
        """Return the result of converting this BDD to a ZDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * zdd
        if cube is None:
            zdd = ccudd.Cudd_zddPortFromBdd(dd, self._node)
        else:
            zdd = ccudd.Cudd_zddPortFromBddNegCof(dd, self._node, cube._node)
        if zdd is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, zdd)

    def leqUnless(self, BDD other, BDD dontcare):
        """Test whether this BDD is less than or equal to another with don't cares."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_bddLeqUnless(dd, self._node, other._node, dontcare._node)

    
    def isop(self, BDD upper, cover=False):
        """Return a BDD between this and upper with a simple DNF cover."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        cdef ccudd.DdNode * cov
        if cover:
            res = ccudd.Cudd_zddIsop(dd, self._node, upper._node, &cov)
        else:
            res = ccudd.Cudd_bddIsop(dd, self._node, upper._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        if cover:
            return (MakeBDD(self._mgr, res), MakeZDD(self._mgr, cov))
        else:
            return MakeBDD(self._mgr, res)

    def correlation(self, BDD other=None, list prob=None):
        """Return the correlation of this BDD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef double corr
        cdef double * weights
        cdef ccudd.DdNode * othernode
        if other is None:
            othernode = ccudd.Cudd_ReadOne(dd);
        else:
            othernode = other._node
        if prob is None:
            corr = ccudd.Cudd_bddCorrelation(dd, self._node, othernode)
        else:
            size = len(prob)
            nvars = ccudd.Cudd_ReadSize(dd)
            if size != nvars:
                raise TypeError(str(size) + " probabilities instead of " + str(nvars))
            weights = <double *> malloc(size * sizeof(double))
            for i in range(size):
                weights[i] = prob[i]
            corr = ccudd.Cudd_bddCorrelationWeights(dd, self._node, othernode, weights)
            free(weights)
        if corr == <double>ccudd.CUDD_OUT_OF_MEM:
            raise MemoryError(self._mgr.readErrorCode())
        return corr

    def probability(self, list prob=None):
        """Return the probability of this BDD begin true."""
        return self.correlation(None, prob)

    def shortestPath(self, list costs=None, findSupport=False):
        """Return a shortest path of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int * weights = NULL
        cdef int * support = NULL
        cdef int length
        cdef int nvars = ccudd.Cudd_ReadSize(dd)
        if costs is not None:
            n = len(costs)
            if n != nvars:
                raise TypeError(str(n) + " costs instead of " + str(nvars))
            weights = <int *> malloc(n * sizeof(int))
            for i in range(n):
                weights[i] = costs[i]
        if findSupport:
            support = <int *> malloc(nvars * sizeof(int))
        cdef ccudd.DdNode * res = ccudd.Cudd_ShortestPath(dd, self._node, weights, support, &length)
        free(weights)
        if res is NULL:
            free(support)
            raise MemoryError(self._mgr.readErrorCode())
        if findSupport:
            sprt = [support[i] for i in range(nvars)]
            free(support)
            return (MakeBDD(self._mgr, res), length, sprt)
        else:
            return (MakeBDD(self._mgr, res), length)
        
    def shortestLength(self, list costs=None):
        """Return the length of the shortest path."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int * weights
        if costs is None:
            weights = NULL
        else:
            n = len(costs)
            nvars = ccudd.Cudd_ReadSize(dd)
            if n != nvars:
                raise TypeError(str(n) + " costs instead of " + str(nvars))
            weights = <int *> malloc(n * sizeof(int))
            for i in range(n):
                weights[i] = costs[i]
        cdef int length = ccudd.Cudd_ShortestLength(dd, self._node, weights)
        free(weights)
        if length == ccudd.CUDD_OUT_OF_MEM:
            raise MemoryError(self._mgr.readErrorCode())
        return length

    def largestCube(self, findLength=False):
        """Return a largest cube of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int length
        cdef ccudd.DdNode * cube = ccudd.Cudd_LargestCube(dd, self._node, &length)
        if cube is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        if findLength:
            return (MakeBDD(self._mgr, cube), length)
        else:
            return MakeBDD(self._mgr, cube)

    def transfer(self, Cudd otherManager):
        """Tranfer this BDD to another manager."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdManager * otherDd = <ccudd.DdManager *>otherManager._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_bddTransfer(dd, otherDd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(otherManager, res)

    def printTwoLiteralClauses(self):
        """Print two literal clauses of this BDD to stdout."""
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        cdef char * * variable_names
        if len(self._mgr._varnames) == size:
            variable_names = <char * *> malloc(size * sizeof(char *))
            if variable_names is NULL:
                raise MemoryError("memory allocation failed")
            for i in range(size):
                utfname = self._mgr._varnames[i].encode('utf-8')
                one_name = <char *> malloc((len(utfname)+1) * sizeof(char))
                strcpy(one_name, utfname)
                variable_names[i] = one_name
        else:
            variable_names = NULL
        cdef bint res = ccudd.Cudd_PrintTwoLiteralClauses(dd, self._node, variable_names, stdout)
        if variable_names is not NULL:
            for i in range(size):
                free(variable_names[i])
            free(variable_names)
        fflush(stdout)
        if not res:
            raise MemoryError(self._mgr.readErrorCode())

    def twoLiteralClauses(self):
        """Return list of two-literal clauses of this BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        cdef ccudd.DdTlcInfo * tlc = ccudd.Cudd_FindTwoLiteralClauses(dd, self._node)
        if tlc is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        cdef unsigned var1
        cdef unsigned var2
        cdef int phase1
        cdef int phase2
        cdef int i = 0
        cl_lst = []
        while ccudd.Cudd_ReadIthClause(tlc, i, &var1, &var2, &phase1, &phase2):
            lit1 = self._mgr.bddVar(var1)
            if phase1 == 1:
                lit1 = ~lit1
            if var2 == ccudd.Cudd_ReadMaxIndex():
                lit2 = self._mgr.bddZero()
            else:
                lit2 = self._mgr.bddVar(var2)
                if phase2 == 1:
                    lit2 = ~lit2
            cl_lst.append(lit1 | lit2)
            i += 1
        ccudd.Cudd_tlcInfoFree(tlc)
        return cl_lst

    def count_as_double(self, numVars=None):
        """Return the number of minterms as a double."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        cdef double count = ccudd.Cudd_CountMinterm(dd, self._node, numVars)
        if count == <double>ccudd.CUDD_OUT_OF_MEM:
            raise MemoryError(self._mgr.readErrorCode())
        return count

    def count(self, numVars=None):
        """Return the number of minterms as an unbounded int."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        cdef int digits
        cdef ccudd.DdApaNumber apacount = ccudd.Cudd_ApaCountMinterm(dd, self._node, numVars, &digits)
        if apacount is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        # Convert.
        count = apacount[0]
        for i in range(1,digits):
            count <<= sizeof(ccudd.DdApaDigit) * 8
            count += apacount[i]
        ccudd.Cudd_FreeApaNumber(apacount)
        return count

    def cube(self):
        """Return a positional cube representation of a cube BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        numVars = ccudd.Cudd_ReadSize(dd)
        cube = <int *> malloc(numVars * sizeof(int))
        cdef int ret = ccudd.Cudd_BddToCubeArray(dd, self._node, cube);
        if ret == 0:
            free(cube)
            raise MemoryError(self._mgr.readErrorCode())
        cubelist = []
        for i in range(numVars):
            cubelist.append(cube[i])
        free(cube)
        return cubelist

    def cubeString(self):
        """Return a positional cube string of a cube BDD."""
        cubelist = self.cube()
        convert = lambda x : "-" if x == 2 else str(x)
        return "".join(map(convert, cubelist))

cdef class ADD:
    """Class of Algebraic Decision Diagrams."""

    cdef Cudd _mgr
    cdef ccudd.DdNode * _node

    def __cinit__(self, manager):
        """Create an ADD."""
        self._mgr = manager
        self._node = NULL

    def __dealloc__(self):
        """Destroy an ADD."""
        if self._node is not NULL:
            #print("destructor called")
            ccudd.Cudd_RecursiveDeref(<ccudd.DdManager *>self._mgr._manager,
                                      self._node)
    def generate_cubes(self):
        """Generate the cubes of this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        cdef int * cube
        cdef ccudd.CUDD_VALUE_TYPE value
        cdef ccudd.DdGen * gen = ccudd.Cudd_FirstCube(dd, self._node,
                                                      &cube, &value)
        if gen is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        while not ccudd.Cudd_IsGenEmpty(gen):
            yield ([cube[i] for i in range(size)], value)
            ccudd.Cudd_NextCube(gen, &cube, &value)
        ccudd.Cudd_GenFree(gen)

    def __repr__(self):
        """Return the truth table of this ADD as a string."""
        convert = lambda x: "-" if x == 2 else str(x)
        if self.isZero():
            return "the zero ADD"
        py_str = ""
        for cube in self.generate_cubes():
            py_str += "".join(map(convert,cube[0])) + " " + "{:g}".format(cube[1]) + "\n"
        return py_str

    def __hash__(self):
        """Return hash code for an ADD."""
        return int(<intptr_t> self._node)

    def compare(self, ADD other, int op):
        """Compare this ADD to another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if op == 2:   # ==
            return self._node == other._node
        elif op == 3: # !=
            return self._node != other._node
        elif op == 1: # <=
            return ccudd.Cudd_addLeq(dd, self._node, other._node)
        elif op == 4: # >
            return self._node != other._node and ccudd.Cudd_addLeq(dd, other._node, self._node)
        elif op == 0: # <
            return self._node != other._node and ccudd.Cudd_addLeq(dd, self._node, other._node)
        else:         # >=
            return ccudd.Cudd_addLeq(dd, other._node, self._node)

    def __richcmp__(self, other, op):
        """Compare this ADD to another."""
        return self.compare(other, op)

    def isOne(self):
        """Test whether this ADD is identically 1."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return self._node == ccudd.Cudd_ReadOne(dd)

    def isZero(self):
        """Test whether this ADD is identically 0."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return self._node == ccudd.Cudd_ReadZero(dd)

    def __bool__(self):
        """Test whether this ADD is not identically 0."""
        return not self.isZero()

    def isConstant(self):
        """Test whether this ADD is a constant function."""
        return ccudd.Cudd_IsConstant(self._node)

    def isNonConstant(self):
        """Test whether this ADD is a non-constant function."""
        return ccudd.Cudd_IsNonConstant(self._node)

    def isVar(self):
        """Test whether this ADD is a variable."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_addIsVar(dd, self._node)

    def index(self):
        """Return the index of the root of this ADD."""
        return ccudd.Cudd_NodeReadIndex(self._node)

    def size(self):
        """Return the size of this ADD."""
        return ccudd.Cudd_DagSize(self._node)

    def display(self, numVars=None, detail=2, name=None):
        """Display this ADD."""
        if name:
            print(name, end='')
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        if not ccudd.Cudd_PrintDebug(dd, self._node, numVars, detail):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)

    def summary(self, numVars=None, mode=0, name=None):
        """Print a summary of this ADD."""
        if name:
            print(name, end='')
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        if not ccudd.Cudd_PrintSummary(dd, self._node, numVars, mode):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)

    def countLeaves(self):
        """Return the number of leaves."""
        cdef int cnt = ccudd.Cudd_CountLeaves(self._node)
        if cnt == ccudd.CUDD_OUT_OF_MEM:
            raise MemoryError(self._mgr.readErrorCode())

    def ite(self, ADD g, ADD h):
        """Apply the if-then-else operation."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addIte(dd, self._node, g._node,
                                                    h._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def cofactor(self, ADD cube):
        """Return the cofactor this ADD w.r.t. a set of literals."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_Cofactor(dd, self._node,
                                                      cube._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def complement(self):
        """Return the complement of this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addCmpl(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __invert__(self):
        """Return the complement of this ADD."""
        return self.complement()

    def negate(self):
        """Return the additive inverse of this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addNegate(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __neg__(self):
        """Return the additive inverse of this ADD."""
        return self.negate()

    def plus(self, ADD other):
        """Return the sum of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addPlus,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __add__(self, ADD other):
        """Return the sum of this ADD and another."""
        return self.plus(other)

    def __iadd__(self, ADD other):
        """Add another ADD to this one."""
        return self.plus(other)

    def times(self, ADD other):
        """Return the product of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addTimes,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __mul__(self, ADD other):
        """Return the pointwise product of this ADD and another."""
        return self.times(other)

    def __and__(self, ADD other):
        """Return the conjunction of this ADD and another."""
        return self.times(other)

    def __imul__(self, ADD other):
        """Pointwise multiply another ADD with this one."""
        return self.times(other)

    def __iand__(self, ADD other):
        """Conjoin another ADD with this one."""
        return self.times(other)

    def divide(self, ADD other):
        """Return the pointwise division of this ADD by another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addDivide,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __div__(self, ADD other):
        """Return the pointwise division of this ADD by another."""
        return self.divide(other)

    def __truediv__(self, ADD other):
        """Return the pointwise division of this ADD by another."""
        return self.divide(other)

    def minus(self, ADD other):
        """Return the subtraction of another ADD from this one."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addMinus,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __sub__(self, ADD other):
        """Return the subtraction of another ADD from this one."""
        return self.minus(other)

    def __isub__(self, ADD other):
        """Subtract another ADD from this one."""
        return self.minus(other)

    def min(self, ADD other):
        """Return the pointwise minimum of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addMinimum,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def max(self, ADD other):
        """Return the pointwise maximum of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addMaximum,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def agreement(self, ADD other):
        """Return the ADD that is 1 iff this ADD agrees with another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addAgreement,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def disjoin(self, ADD other):
        """Return the disjunction of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addOr,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __or__(self, ADD other):
        """Return the disjunction of this ADD and another."""
        return self.disjoin(other)

    def __ior__(self, ADD other):
        """Disjoin another ADD to this one."""
        return self.disjoin(other)

    def nand(self, ADD other):
        """Return the NAND of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addNand,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def nor(self, ADD other):
        """Return the NOR of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addNor,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def xor(self, ADD other):
        """Return the symmetric difference of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addXor,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def __xor__(self, ADD other):
        """Return the symmetric difference of this ADD and another."""
        return self.xor(other)

    def __ixor__(self, ADD other):
        """Take the symetric difference of another ADD."""
        return self.xor(other)

    def xnor(self, ADD other):
        """Return the exclusive NOR of this ADD and another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addApply(dd, ccudd.Cudd_addXnor,
                                                      self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def iff(self, ADD other):
        """Return the equivalence of this ADD and another."""
        return self.xnor(other)

    def existAbstract(self, ADD cube):
        """Return the existential quantification of a set of variables."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addExistAbstract(dd, self._node,
                                                              cube._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def univAbstract(self, ADD cube):
        """Return the universal quantification of a set of variables."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addUnivAbstract(dd, self._node,
                                                             cube._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def log(self):
        """Return the pointwise logarithm of this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addMonadicApply(dd,
                                                             ccudd.Cudd_addLog,
                                                             self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def findMin(self):
        """Return the constant ADD that is the minimum of this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addMonadicApply(dd, ccudd.Cudd_addFindMin,
                                                             self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def findMax(self):
        """Return the constant ADD that is the maximum of this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addMonadicApply(dd, ccudd.Cudd_addFindMax,
                                                             self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def ithBit(self, int bit):
        """Extract the i-th bit from this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addIthBit(dd, self._node, bit)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def compose(self, ADD other, int index):
        """Substitute a function for a variable in this ADD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addCompose(dd, self._node,
                                                        other._node, index)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)
    
    def swapVariables(self, list current_vars, list new_vars):
        """Swap two lists of variables in this ADD."""
        if len(current_vars) != len(new_vars):
            raise TypeError("the two lists of variables should have the same length")
        cdef int n = len(current_vars)
        cdef ccudd.DdNode * * xvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if xvars is NULL:
            raise MemoryError("memory allocation failed")
        cdef ccudd.DdNode * * yvars = <ccudd.DdNode * *> malloc(n * sizeof(ccudd.DdNode *))
        if yvars is NULL:
            free(xvars)
            raise MemoryError("memory allocation failed")
        for i in range(n):
            xvars[i] = (<ADD>current_vars[i])._node
            yvars[i] = (<ADD>new_vars[i])._node
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addSwapVariables(dd, self._node,
                                                              xvars, yvars, n)
        free(xvars)
        free(yvars)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def permute(self, permutation):
        """Return ADD with permuted variables."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadSize(dd)
        if len(permutation) != size:
            raise TypeError("length of permutation ({0}) different ".format(len(permutation))
                            + "from number of variables ({0})".format(size))
        cdef int * p = <int *> malloc(size * sizeof(int))
        if p is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(size):
            v = permutation[i]
            if not 0 <= v < size:
                raise TypeError("{0} is not a valid variable index (not between 0 and {1})".format(v,size))
            p[i] = v
        cdef ccudd.DdNode * res = ccudd.Cudd_addPermute(dd, self._node, p)
        free(p)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def constrain(self, ADD constraint):
        """Apply the 'constrain' generalized cofactor."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addConstrain(dd, self._node,
                                                          constraint._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def restrict(self, ADD constraint):
        """Apply the 'restrict' generalized cofactor."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addRestrict(dd, self._node,
                                                         constraint._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def bddPattern(self):
        """Return the conversion of this ADD to a BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addBddPattern(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def bddThreshold(self, value):
        """Return the conversion of this ADD to a BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addBddThreshold(dd, self._node,
                                                             value)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def bddStrictThreshold(self, value):
        """Return the conversion of this ADD to a BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addBddStrictThreshold(dd, self._node,
                                                                   value)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def bddInterval(self, lower, upper):
        """Return the conversion of this ADD to a BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_addBddInterval(dd, self._node,
                                                            lower, upper)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def matrixMultiply(self, ADD other, list zvars):
        """Multiply this ADD (interpreted as a matrix) by another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int nz = len(zvars)
        cdef ccudd.DdNode * * Z = <ccudd.DdNode * *> malloc(nz * sizeof(ccudd.DdNode *))
        if Z is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(nz):
            Z[i] = (<ADD>zvars[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_addMatrixMultiply(dd, self._node,
                                                               other._node,
                                                               Z, nz)
        free(Z)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def triangle(self, ADD other, list zvars):
        """Perform a triangulation step."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int nz = len(zvars)
        cdef ccudd.DdNode * * Z = <ccudd.DdNode * *> malloc(nz * sizeof(ccudd.DdNode *))
        if Z is NULL:
            raise MemoryError("memory allocation failed")
        for i in range(nz):
            Z[i] = (<ADD>zvars[i])._node
        cdef ccudd.DdNode * res = ccudd.Cudd_addTriangle(dd, self._node,
                                                         other._node, Z, nz)
        free(Z)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeADD(self._mgr, res)

    def equalSupNorm(self, ADD other, tolerance=1e-9, pr=0):
        """Test whether this ADD is close to another in the sup norm."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return ccudd.Cudd_EqualSupNorm(dd, self._node, other._node, tolerance, pr)

    def count_as_double(self, numVars=None):
        """Return the number of minterms as a double."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        cdef double count = ccudd.Cudd_CountMinterm(dd, self._node, numVars)
        if count == <double>ccudd.CUDD_OUT_OF_MEM:
            raise MemoryError(self._mgr.readErrorCode())
        return count

    def count(self, numVars=None):
        """Return the number of minterms as an unbounded int."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadSize(dd)
        cdef int digits
        cdef ccudd.DdApaNumber apacount = ccudd.Cudd_ApaCountMinterm(dd, self._node, numVars, &digits)
        if apacount is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        # Convert.
        count = apacount[0]
        for i in range(1,digits):
            count <<= sizeof(ccudd.DdApaDigit) * 8
            count += apacount[i]
        ccudd.Cudd_FreeApaNumber(apacount)
        return count


cdef class ZDD:
    """Class of Zero-Suppressed Decision Diagrams."""

    cdef Cudd _mgr
    cdef ccudd.DdNode * _node

    def __cinit__(self, manager):
        """Create a ZDD."""
        self._mgr = manager
        self._node = NULL

    def __dealloc__(self):
        """Destroy a ZDD."""
        if self._node is not NULL:
            #print("destructor called")
            ccudd.Cudd_RecursiveDerefZdd(<ccudd.DdManager *>self._mgr._manager,
                                         self._node)

    def generate_paths(self):
        """Generate the paths of this ZDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int size = ccudd.Cudd_ReadZddSize(dd)
        cdef int * path
        cdef ccudd.DdGen * gen = ccudd.Cudd_zddFirstPath(dd, self._node,
                                                         &path)
        if gen is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        while not ccudd.Cudd_IsGenEmpty(gen):
            yield [path[i] for i in range(size)]
            ccudd.Cudd_zddNextPath(gen, &path)
        ccudd.Cudd_GenFree(gen)

    def __repr__(self):
        """Return the truth table of this ZDD as a string."""
        convert = lambda x: "-" if x == 2 else str(x)
        if self.isZero():
            return "the zero ZDD"
        py_str = ""
        for path in self.generate_paths():
            py_str += "".join(map(convert, path)) + "\n"
        return py_str

    def __hash__(self):
        """Return hash code for a ZDD."""
        return int(<intptr_t> self._node)

    def display(self, numVars=None, detail=2, name=None):
        """Display this ZDD."""
        if name:
            print(name, end='')
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadZddSize(dd)
        if not ccudd.Cudd_zddPrintDebug(dd, self._node, numVars, detail):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)

    def isOne(self, topIndex=0):
        """Test whether this ZDD is identically 1."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return self._node == ccudd.Cudd_ReadZddOne(dd, topIndex)

    def isZero(self):
        """Test whether this ZDD is identically 0."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        return self._node == ccudd.Cudd_ReadZero(dd)

    def __bool__(self):
        """Test whether this ZDD is not identically 0."""
        return not self.isZero()

    def index(self):
        """Return the index of the root of this ZDD."""
        return ccudd.Cudd_NodeReadIndex(self._node)

    def size(self):
        """Return the size of this ZDD."""
        return ccudd.Cudd_zddDagSize(self._node)

    def support(self):
        """Compute the BDD of the variables in the support of this ZDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_zddSupport(dd, self._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, res)

    def compare(self, ZDD other, int op):
        """Compare this ZDD to another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if op == 2:   # ==
            return self._node == other._node
        elif op == 3: # !=
            return self._node != other._node
        elif op == 1: # <=
            return ccudd.Cudd_zddDiffConst(dd, self._node, other._node) == ccudd.Cudd_ReadZero(dd)
        elif op == 4: # >
            return self._node != other._node and \
                ccudd.Cudd_zddDiffConst(dd, other._node, self._node) == ccudd.Cudd_ReadZero(dd)
        elif op == 0: # <
            return self._node != other._node and \
                ccudd.Cudd_zddDiffConst(dd, self._node, other._node) == ccudd.Cudd_ReadZero(dd)
        else:         # >=
            return ccudd.Cudd_zddDiffConst(dd, other._node, self._node) == ccudd.Cudd_ReadZero(dd)

    def __richcmp__(self, other, op):
        """Compare this ZDD to another."""
        return self.compare(other, op)

    def ite(self, ZDD g, ZDD h):
        """Apply the if-then-else operation."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_zddIte(dd, self._node, g._node,
                                                    h._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, res)

    def change(self, var):
        """Substitute var with its complement in this ZDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res = ccudd.Cudd_zddChange(dd, self._node, var)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, res)

    def intsec(self, ZDD other):
        """Return the conjunction with another ZDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * res
        res = ccudd.Cudd_zddIntersect(dd, self._node, other._node)
        if res is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, res)

    def __and__(self, ZDD other):
        """Return the conjunction with another ZDD."""
        return self.intsec(other)

    def __iand__(self, ZDD other):
        """Conjoin this ZDD with another."""
        return self.intsec(other)

    def union(self, ZDD other):
        """Return the disjunction with another ZDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * disj = ccudd.Cudd_zddUnion(dd, self._node,
                                                       other._node)
        if disj is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, disj)

    def __or__(self, ZDD other):
        """Return the disjunction with another ZDD."""
        return self.union(other)

    def __ior__(self, ZDD other):
        """Disjoin this ZDD with another."""
        return self.union(other)

    def diff(self, ZDD other):
        """Return the difference with another ZDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * diff = ccudd.Cudd_zddDiff(dd, self._node,
                                                      other._node)
        if diff is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, diff)

    def __invert__(self):
        """Return the negation of the ZDD."""
        return self._mgr.zddOne().diff(self)

    def xor(self, ZDD other):
        """Return the exclusive or with another ZDD."""
        return self.diff(other) | other.diff(self)

    def __xor__(self, ZDD other):
        """Return the symmetric difference with another ZDD."""
        return self.xor(other)

    def __ixor__(self, ZDD other):
        """Take symmetric difference of this ZDD with another."""
        return self.xor(other)

    def xnor(self, ZDD other):
        return ~self.xor(other)

    def iff(self, ZDD other):
        return self.xnor(other)

    def subset0(self, var):
        """Return the subset with var=0."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * s0 = ccudd.Cudd_zddSubset0(dd, self._node, var)
        if s0 is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, s0)

    def subset1(self, var):
        """Return the subset with var=1."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * s1 = ccudd.Cudd_zddSubset1(dd, self._node, var)
        if s1 is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, s1)

    def toBDD(self, BDD cube=None):
        """Return the result of converting this ZDD to a BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef int bddsize = ccudd.Cudd_ReadSize(dd)
        cdef int zddsize = ccudd.Cudd_ReadZddSize(dd)
        if bddsize != zddsize:
            raise TypeError("number of BDD variables ({0}) different ".format(bddsize)
                            + "from number of ZDD variables ({0})".format(zddsize))
        cdef ccudd.DdNode * bdd
        if cube is None:
            bdd = ccudd.Cudd_zddPortToBdd(dd, self._node)
        else:
            bdd = ccudd.Cudd_zddPortToBddNegCof(dd, self._node, cube._node)
        if bdd is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, bdd)

    def product(self, ZDD other):
        """Return the product of this cover with another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * prod = ccudd.Cudd_zddProduct(dd, self._node,
                                                         other._node)
        if prod is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, prod)

    def unateProduct(self, ZDD other):
        """Return the product of this unate cover with another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * prod = ccudd.Cudd_zddUnateProduct(dd, self._node,
                                                              other._node)
        if prod is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, prod)

    def weakDiv(self, ZDD other):
        """Divide this cover by another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * div = ccudd.Cudd_zddWeakDiv(dd, self._node,
                                                        other._node)
        if div is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, div)

    def unateWeakDiv(self, ZDD other):
        """Divide this unate cover by another."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * div = ccudd.Cudd_zddDivide(dd, self._node,
                                                       other._node)
        if div is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, div)

    def complement(self):
        """Return the complement of this cover."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * compl = ccudd.Cudd_zddComplement(dd, self._node)
        if compl is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeZDD(self._mgr, compl)

    def makeBddFromCover(self):
        """Return the result of converting this cover to a BDD."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        cdef ccudd.DdNode * bdd = ccudd.Cudd_MakeBddFromZddCover(dd, self._node)
        if bdd is NULL:
            raise MemoryError(self._mgr.readErrorCode())
        return MakeBDD(self._mgr, bdd)

    def printCover(self):
        """Print the cover represented by this ZDD."""
        sys.stdout.flush()
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if not ccudd.Cudd_zddPrintCover(dd, self._node):
            raise MemoryError(self._mgr.readErrorCode())
        fflush(stdout)

    def count_as_double(self, numVars=None):
        """Return the number of minterms as a double."""
        cdef ccudd.DdManager * dd = <ccudd.DdManager *>self._mgr._manager
        if numVars is None:
            numVars = ccudd.Cudd_ReadZddSize(dd)
        cdef double count = ccudd.Cudd_zddCountMinterm(dd, self._node, numVars)
        if count == <double>ccudd.CUDD_OUT_OF_MEM:
            raise MemoryError(self._mgr.readErrorCode())
        return count
