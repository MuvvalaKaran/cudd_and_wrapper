# file: ccudd.pxd

cdef extern from "stdio.h":
    ctypedef struct FILE:
        pass

from libc.stdint cimport uint32_t, int32_t

ctypedef enum Cudd_ResidueType:
    CUDD_RESIDUE_DEFAULT, CUDD_RESIDUE_MSB, CUDD_RESIDUE_TC

cdef extern from "mtr.h":
    ctypedef struct MtrNode:
        pass

    cdef extern int MTR_DEFAULT
    cdef extern int MTR_FIXED

cdef extern from "cudd.h":
    ctypedef struct DdManager:
        pass
    ctypedef struct DdNode:
        pass
    ctypedef struct DdGen:
        pass
    ctypedef struct DdTlcInfo:
        pass
    ctypedef double CUDD_VALUE_TYPE
    ctypedef DdNode * (*DD_AOP)(DdManager *, DdNode **, DdNode **)
    ctypedef DdNode * (*DD_MAOP)(DdManager *, DdNode *)
    ctypedef uint32_t DdApaDigit
    ctypedef DdApaDigit * DdApaNumber

    cdef extern int CUDD_OUT_OF_MEM
    cdef extern int CUDD_UNIQUE_SLOTS
    cdef extern int CUDD_CACHE_SLOTS

    ctypedef enum Cudd_ReorderingType:
        CUDD_REORDER_SAME, CUDD_REORDER_NONE, CUDD_REORDER_RANDOM,
        CUDD_REORDER_RANDOM_PIVOT, CUDD_REORDER_SIFT,
        CUDD_REORDER_SIFT_CONVERGE, CUDD_REORDER_SYMM_SIFT,
        CUDD_REORDER_SYMM_SIFT_CONV, CUDD_REORDER_WINDOW2,
        CUDD_REORDER_WINDOW3, CUDD_REORDER_WINDOW4,
        CUDD_REORDER_WINDOW2_CONV, CUDD_REORDER_WINDOW3_CONV,
        CUDD_REORDER_WINDOW4_CONV, CUDD_REORDER_GROUP_SIFT,
        CUDD_REORDER_GROUP_SIFT_CONV, CUDD_REORDER_ANNEALING,
        CUDD_REORDER_GENETIC, CUDD_REORDER_LINEAR,
        CUDD_REORDER_LINEAR_CONVERGE, CUDD_REORDER_LAZY_SIFT,
        CUDD_REORDER_EXACT

    ctypedef enum Cudd_ErrorType:
        CUDD_NO_ERROR, CUDD_MEMORY_OUT,
        CUDD_TOO_MANY_NODES, CUDD_MAX_MEM_EXCEEDED,
        CUDD_TIMEOUT_EXPIRED, CUDD_TERMINATION,
        CUDD_INVALID_ARG, CUDD_INTERNAL_ERROR,
        CUDD_WRONG_PRECONDITIONS


    DdManager * Cudd_Init(unsigned int numVars, unsigned int numVarsZ,
                          size_t numSlots, size_t cacheSize,
                          size_t maxMemory)
    void Cudd_Quit(DdManager * manager)
    bint Cudd_PrintInfo(DdManager * manager, FILE *fp)
    Cudd_ErrorType Cudd_ReadErrorCode(DdManager * manager)
    void Cudd_ClearErrorCode(DdManager * manager)
    int Cudd_ReadSize(DdManager * manager)
    unsigned int Cudd_ReadMaxIndex()
    size_t Cudd_ReadMemoryInUse(DdManager * manager)
    bint Cudd_Reserve(DdManager * manager, int amount)
    DdNode * Cudd_bddNewVar(DdManager * manager)
    DdNode * Cudd_bddIthVar(DdManager * manager, int index)
    DdNode * Cudd_ReadOne(DdManager * manager)
    DdNode * Cudd_ReadLogicZero(DdManager * manager)
    DdNode * Cudd_ReadZero(DdManager * manager)
    DdNode * Cudd_ReadPlusInfinity(DdManager * manager)
    DdNode * Cudd_ReadMinusInfinity(DdManager * manager)
    DdNode * Cudd_ReadBackground(DdManager * manager)
    void Cudd_SetBackground(DdManager * manager, DdNode * bck)
    unsigned long Cudd_ReadStartTime(DdManager * manager)
    unsigned long Cudd_ReadElapsedTime(DdManager * manager)
    void Cudd_SetStartTime(DdManager * manager, unsigned long st)
    void Cudd_ResetStartTime(DdManager * manager)
    unsigned long Cudd_ReadTimeLimit(DdManager * manager)
    unsigned long Cudd_SetTimeLimit(DdManager * manager, unsigned long tl)
    void Cudd_UpdateTimeLimit(DdManager * manager)
    void Cudd_IncreaseTimeLimit(DdManager * manager, unsigned long increase)
    void Cudd_UnsetTimeLimit(DdManager * manager)
    bint Cudd_TimeLimited(DdManager * manager)
    size_t Cudd_ReadMaxLive(DdManager * manager)
    void Cudd_SetMaxLive(DdManager * manager, size_t maxLive)
    size_t Cudd_ReadMaxMemory(DdManager * manager)
    size_t Cudd_SetMaxMemory(DdManager * manager, size_t maxMemory)
    void Cudd_Srandom(DdManager * manager, int32_t seed)
    void Cudd_AutodynEnable(DdManager * manager, Cudd_ReorderingType method)
    void Cudd_AutodynDisable(DdManager * manager)
    unsigned int Cudd_ReadReorderings(DdManager * manager)
    unsigned int Cudd_ReadMaxReorderings(DdManager * manager)
    void Cudd_SetMaxReorderings(DdManager * manager, unsigned int mr)
    bint Cudd_ReorderingStatus(DdManager * manager, Cudd_ReorderingType * method)
    size_t Cudd_ReadNextReordering(DdManager * manager)
    void Cudd_SetNextReordering(DdManager * manager, size_t next)
    int Cudd_ReduceHeap(DdManager * manager, Cudd_ReorderingType heuristic,
                        int minsize)
    bint Cudd_ShuffleHeap(DdManager * manager, int * permutation)
    bint Cudd_EnableReorderingReporting(DdManager * manager)
    bint Cudd_DisableReorderingReporting(DdManager * manager)
    bint Cudd_ReorderingReporting(DdManager * manager)
    bint Cudd_EnableOrderingMonitoring(DdManager * manager)
    bint Cudd_DisableOrderingMonitoring(DdManager * manager)
    bint Cudd_OrderingMonitoring(DdManager * manager)
    bint Cudd_PrintGroupedOrder(DdManager * manager, const char * str, void * data)
    int Cudd_ReadInvPerm(DdManager * manager, int i)
    int Cudd_ReadInvPermZdd(DdManager * manager, int i)
    bint Cudd_DumpDot (DdManager * manager, int n, DdNode * * f,
                       const char * const * inames, const char * const * onames,
                       FILE * fp)
    void Cudd_SymmProfile(DdManager * manager, int lower, int upper)

    void Cudd_Ref(DdNode * f)
    void Cudd_RecursiveDeref(DdManager * manager, DdNode *f)
    DdNode * Cudd_Not(DdNode * f)
    DdNode * Cudd_bddAnd(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_bddAndLimit(DdManager * manager, DdNode * f, DdNode * g,
                              unsigned int limit)
    DdNode * Cudd_bddOr(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_bddXor (DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_bddXnor(DdManager * manager, DdNode * f, DdNode * g);
    DdNode * Cudd_bddXnorLimit(DdManager * manager, DdNode * f, DdNode * g,
                               unsigned int limit)
    DdNode * Cudd_bddIte(DdManager * manager, DdNode * f, DdNode * g, DdNode * h)
    DdNode * Cudd_bddIteLimit(DdManager * manager, DdNode * f, DdNode * g,
                              DdNode * h, unsigned int limit)
    DdNode * Cudd_bddIntersect(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_bddIntersectionCube(DdManager * manager, DdNode * f,
                                      DdNode * g)
    bint Cudd_PrintDebug(DdManager * manager, DdNode * f, int n, int pr)
    bint Cudd_PrintSummary(DdManager * manager, DdNode * f, int n, int mode)
    bint Cudd_PrintMinterm(DdManager * manager, DdNode * node)
    bint Cudd_bddPrintCover(DdManager * manager, DdNode * l, DdNode * u)
    char * Cudd_FactoredFormString(DdManager * manager, DdNode * f,
                                   const char * const * varnames)
    DdNode * Cudd_bddInterpolate(DdManager * manager, DdNode * l, DdNode * u)
    bint Cudd_bddLeq (DdManager * manager, DdNode * f, DdNode * g)
    bint Cudd_bddIsVar(DdManager * manager, DdNode * f)
    bint Cudd_addIsVar(DdManager * manager, DdNode * f)
    bint Cudd_IsConstant(DdNode * f)
    bint Cudd_IsNonConstant(DdNode * f)
    DdGen * Cudd_FirstPrime(DdManager * manager, DdNode * l, DdNode * u,
                            int ** cube)
    bint Cudd_NextPrime(DdGen * gen, int ** cube)
    DdGen * Cudd_FirstCube(DdManager * manager, DdNode * f, int ** cube,
                           CUDD_VALUE_TYPE * value)
    bint Cudd_NextCube(DdGen * gen, int ** cube, CUDD_VALUE_TYPE * value)
    DdNode * Cudd_bddComputeCube(DdManager * manager, DdNode ** vars, int * phase,
                                 int n)
    bint Cudd_IsGenEmpty(DdGen * gen)
    bint Cudd_GenFree(DdGen * gen)
    int Cudd_bddPickOneCube(DdManager * manager, DdNode * node, char * string)
    DdNode * Cudd_bddPickOneMinterm(DdManager * manager, DdNode * f,
                                    DdNode ** vars, int n)
    DdNode * Cudd_bddPickCube(DdManager * manager, DdNode * f)
    DdNode * Cudd_CubeArrayToBdd(DdManager * manager, int * array)
    DdNode * Cudd_bddExistAbstract(DdManager * manager,
                                   DdNode * f, DdNode * cube)
    DdNode * Cudd_bddExistAbstractLimit(DdManager * manager, DdNode * f,
                                        DdNode * cube, unsigned int limit)
    DdNode * Cudd_bddUnivAbstract(DdManager * manager,
                                  DdNode * f, DdNode * cube)
    DdNode * Cudd_bddAndAbstract(DdManager * manager, DdNode * f,
                                 DdNode * g, DdNode * cube)
    DdNode * Cudd_bddAndAbstractLimit(DdManager * manager, DdNode * f,
                                      DdNode * g, DdNode * cube,
                                      unsigned int limit)
    DdNode * Cudd_bddBooleanDiff(DdManager * manager, DdNode * f, int x)
    DdNode * Cudd_bddCompose(DdManager * manager, DdNode * f, DdNode * g, int v)
    DdNode * Cudd_bddVectorCompose(DdManager * manager, DdNode * f,
                                   DdNode ** vector)
    DdNode * Cudd_bddSwapVariables(DdManager * manager, DdNode * f, DdNode ** x,
                                   DdNode ** y, int n)
    DdNode * Cudd_bddPermute(DdManager * manager, DdNode * node, int * permut)
    DdNode * Cudd_Cofactor(DdManager * manager, DdNode * f, DdNode * g)
    bint Cudd_CheckCube(DdManager * manager, DdNode * g)
    DdNode * Cudd_bddDual(DdManager * manager, DdNode * f)
    bint Cudd_bddAreDual(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_bddConstrain(DdManager * manager, DdNode * f, DdNode * c)
    DdNode * Cudd_bddRestrict(DdManager * manager, DdNode * f, DdNode * c)
    DdNode * Cudd_bddNPAnd(DdManager * manager, DdNode * f, DdNode * c)
    DdNode * Cudd_bddNPAndLimit(DdManager * manager, DdNode * f, DdNode * c,
                                unsigned int limit)
    DdNode ** Cudd_bddCharToVect(DdManager * manager, DdNode * f)
    DdNode * Cudd_bddLICompaction(DdManager * manager, DdNode * f, DdNode * c)
    DdNode * Cudd_bddSqueeze(DdManager * manager, DdNode * l, DdNode * u)
    DdNode * Cudd_bddMinimize(DdManager *dd, DdNode *f, DdNode *c)
    DdNode * Cudd_Support(DdManager * manager, DdNode * f)
    bint Cudd_bddVarIsDependent (DdManager * manager, DdNode * f, DdNode * var)
    int Cudd_DagSize(DdNode * f)
    int Cudd_SharingSize(DdNode ** nodeArray, int n)
    bint Cudd_VarsAreSymmetric(DdManager * manager, DdNode * f,
                               int index1, int index2)
    unsigned int Cudd_NodeReadIndex(DdNode *node)
    DdNode * Cudd_Xeqy(DdManager * manager, int N, DdNode ** x, DdNode ** y)
    DdNode * Cudd_Xgty(DdManager * manager, int N, DdNode ** z, DdNode ** x,
                       DdNode ** y)
    DdNode * Cudd_Inequality(DdManager * manager, int N, int c, DdNode ** x,
                             DdNode ** y)
    DdNode * Cudd_Disequality(DdManager * manager, int N, int c, DdNode ** x,
                              DdNode ** y)
    DdNode * Cudd_bddInterval(DdManager * manager, int N, DdNode ** x,
                              unsigned int lowerB, unsigned int upperB)
    DdNode * Cudd_bddClosestCube(DdManager * manager, DdNode * f, DdNode * g,
                                 int * distance);
    DdNode * Cudd_Eval(DdManager * manager, DdNode * f, int * inputs)
    DdNode * Cudd_Decreasing(DdManager * manager, DdNode * f, int i)
    DdNode * Cudd_Increasing(DdManager * manager, DdNode * f, int i)
    bint Cudd_bddPositive(DdManager * manager, DdNode * f)
    bint Cudd_bddNegative(DdManager * manager, DdNode * f)
    DdNode * Cudd_bddMakePrime(DdManager * manager, DdNode * cube, DdNode * f)
    DdNode * Cudd_bddMaximallyExpand(DdManager * manager, DdNode * lb,
                                     DdNode * ub, DdNode * f)
    DdNode * Cudd_bddLargestPrimeUnate(DdManager * manager, DdNode * f,
                                       DdNode * phaseBdd)
    DdNode * Cudd_FindEssential(DdManager * manager, DdNode * f)
    bint Cudd_bddIsVarEssential(DdManager * manager, DdNode * f, int idx, bint phase)
    DdNode * Cudd_bddCardinality(DdManager * manager, DdNode ** vars,
                                 int N, int lb, int ub);
    double * Cudd_CofMinterm(DdManager * manager, DdNode * node);
    DdNode * Cudd_SolveEqn(DdManager * manager, DdNode * F, DdNode * Y,
                           DdNode ** G, int ** yIndex, int n);
    DdNode * Cudd_VerifySol(DdManager * manager, DdNode * F, DdNode ** G,
                            int * yIndex, int n);
    DdNode * Cudd_RemapUnderApprox(DdManager * manager, DdNode * f, int numVars,
                                   int threshold, double quality)
    DdNode * Cudd_RemapOverApprox(DdManager * manager, DdNode * f, int numVars,
                                  int threshold, double quality)
    DdNode * Cudd_BiasedUnderApprox(DdManager * manager, DdNode * f, DdNode * b,
                                    int numVars, int threshold,
                                    double quality1, double quality0)
    DdNode * Cudd_BiasedOverApprox(DdManager * manager, DdNode * f, DdNode * b,
                                   int numVars, int threshold,
                                   double quality1, double quality0)
    int Cudd_bddGenConjDecomp(DdManager * manager, DdNode * f,
                              DdNode *** conjuncts)
    int Cudd_bddVarConjDecomp(DdManager * manager, DdNode * f,
                              DdNode *** conjuncts)
    int Cudd_bddApproxConjDecomp(DdManager * manager, DdNode * f,
                                 DdNode *** conjuncts)
    int Cudd_bddIterConjDecomp(DdManager * manager, DdNode * f,
                               DdNode *** conjuncts)
    bint Cudd_bddLeqUnless(DdManager * manager, DdNode * f, DdNode * g,
                           DdNode * D)
    double Cudd_bddCorrelation(DdManager * manager, DdNode * f, DdNode * g)
    double Cudd_bddCorrelationWeights(DdManager * manager, DdNode * f,
                                      DdNode * g, double * prob)
    DdNode * Cudd_ShortestPath(DdManager * manager, DdNode * f, int * weight,
                               int * support, int * length)
    DdNode * Cudd_LargestCube(DdManager * manager, DdNode * f, int * length)
    int Cudd_ShortestLength(DdManager * manager, DdNode * f, int * weight)
    DdNode * Cudd_SubsetHeavyBranch(DdManager * manager, DdNode * f, int numVars,
                                    int threshold)
    DdNode * Cudd_SupersetHeavyBranch(DdManager * manaager, DdNode * f, int numVars,
                                      int threshold)
    DdNode * Cudd_SubsetShortPaths(DdManager * manager, DdNode * f, int numVars,
                                   int threshold, int hardlimit)
    DdNode * Cudd_SupersetShortPaths(DdManager * manager, DdNode * f, int numVars,
                                     int threshold, int hardlimit)
    DdNode * Cudd_bddTransfer(DdManager * ddSource, DdManager * ddDestination, DdNode * f)
    DdNode * Cudd_BddToAdd(DdManager * manager, DdNode * B)
    DdTlcInfo * Cudd_FindTwoLiteralClauses(DdManager * manager, DdNode * f)
    bint Cudd_PrintTwoLiteralClauses(DdManager * manager, DdNode * f, char ** names, FILE * fp)
    bint Cudd_ReadIthClause(DdTlcInfo * tlc, int i, unsigned * var1, unsigned * var2,
                            int * phase1, int * phase2)
    void Cudd_tlcInfoFree(DdTlcInfo * tlc)
    int Cudd_BddToCubeArray(DdManager * manager, DdNode * cube, int * array)
    DdNode * Cudd_addNewVar(DdManager * manager)
    DdNode * Cudd_addIthVar(DdManager * manager, int i)
    DdNode * Cudd_addConst(DdManager * manager, CUDD_VALUE_TYPE c)
    int Cudd_CountLeaves(DdNode * node)
    bint Cudd_addLeq(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_addIte(DdManager * manager, DdNode * f, DdNode * g, DdNode * h)
    DdNode * Cudd_addCmpl(DdManager * manager, DdNode * f)
    DdNode * Cudd_addNegate(DdManager * manager, DdNode * f)
    DdNode * Cudd_addApply(DdManager * manager, DD_AOP op, DdNode * f,
                           DdNode * g)
    DdNode * Cudd_addPlus(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addTimes(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addDivide(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addMinus(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addMinimum(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addMaximum(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addAgreement(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addOr(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addNand(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addNor(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addXor(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addXnor(DdManager * manager, DdNode ** f, DdNode ** g)
    DdNode * Cudd_addExistAbstract(DdManager * manager, DdNode * f,
                                   DdNode * cube)
    DdNode * Cudd_addUnivAbstract(DdManager * manager, DdNode * f, DdNode * cube)
    DdNode * Cudd_addMonadicApply(DdManager * manager, DD_MAOP op, DdNode * f)
    DdNode * Cudd_addLog(DdManager * manager, DdNode * f)
    DdNode * Cudd_addFindMax(DdManager * manager, DdNode * f)
    DdNode * Cudd_addFindMin(DdManager * manager, DdNode * f)
    DdNode * Cudd_addIthBit(DdManager * manager, DdNode * f, int bit)
    DdNode * Cudd_addCompose(DdManager * manager, DdNode * f, DdNode * g, int v)
    DdNode * Cudd_addSwapVariables(DdManager * manager, DdNode * f,
                                   DdNode ** x, DdNode ** y, int n)
    DdNode * Cudd_addPermute(DdManager * manager, DdNode * node, int * permut)
    DdNode * Cudd_addConstrain(DdManager * manager, DdNode * f, DdNode * c)
    DdNode * Cudd_addRestrict(DdManager * manager, DdNode * f, DdNode * c)
    DdNode * Cudd_addBddPattern(DdManager * manager, DdNode * f)
    DdNode * Cudd_addBddThreshold(DdManager * manager, DdNode * f,
                                  CUDD_VALUE_TYPE value)
    DdNode * Cudd_addBddStrictThreshold(DdManager * manager, DdNode * f,
                                        CUDD_VALUE_TYPE value)
    DdNode * Cudd_addBddInterval(DdManager * manager, DdNode * f,
                                 CUDD_VALUE_TYPE lower, CUDD_VALUE_TYPE upper)
    DdNode * Cudd_addMatrixMultiply(DdManager * manager, DdNode * A, DdNode * B,
                                    DdNode ** z, int nz)
    DdNode * Cudd_addTriangle(DdManager * manager, DdNode * f, DdNode * g,
                              DdNode ** z, int nz)
    DdNode * Cudd_addWalsh(DdManager * manager, DdNode ** x, DdNode ** y, int n)
    DdNode * Cudd_addXeqy(DdManager * manager, int N, DdNode ** x, DdNode ** y)
    DdNode * Cudd_addHamming(DdManager * manager, DdNode ** xVars,
                             DdNode ** yVars, int nVars)
    DdNode * Cudd_addResidue(DdManager * manager, int n, int m, int options,
                             int top)
    bint Cudd_EqualSupNorm(DdManager * manager, DdNode * f, DdNode * g,
                           CUDD_VALUE_TYPE tolerance, int pr)
    DdNode * Cudd_zddIthVar(DdManager * manager, int i)
    bint Cudd_zddVarsFromBddVars(DdManager * manager, int multiplicity)
    DdNode * Cudd_ReadZddOne(DdManager * manager, int i)
    int Cudd_ReadZddSize(DdManager * manager)
    void Cudd_AutodynEnableZdd(DdManager * manager, Cudd_ReorderingType method)
    void Cudd_AutodynDisableZdd(DdManager * manager)
    bint Cudd_ReorderingStatusZdd(DdManager * manager,
                                  Cudd_ReorderingType * method)
    bint Cudd_zddRealignmentEnabled(DdManager * manager)
    void Cudd_zddRealignEnable(DdManager * manager)
    void Cudd_zddRealignDisable(DdManager * manager)
    bint Cudd_bddRealignmentEnabled(DdManager * manager)
    void Cudd_bddRealignEnable(DdManager * manager)
    void Cudd_bddRealignDisable(DdManager * manager)
    void Cudd_RecursiveDerefZdd(DdManager * manager, DdNode * n)
    DdGen * Cudd_zddFirstPath(DdManager * manager, DdNode * f, int ** path);
    bint Cudd_zddNextPath(DdGen * gen, int ** path)
    int Cudd_zddCount(DdManager * manager, DdNode * P)
    double Cudd_zddCountDouble(DdManager * manager, DdNode * P)
    DdNode * Cudd_zddProduct(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_zddUnateProduct(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_zddWeakDiv(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_zddDivide(DdManager * manager, DdNode * f, DdNode * g)
    DdNode * Cudd_zddComplement(DdManager * manager, DdNode * node)
    DdNode * Cudd_zddIsop(DdManager * manager, DdNode * L, DdNode * U,
                          DdNode ** zdd_I)
    DdNode * Cudd_bddIsop(DdManager * manager, DdNode * L, DdNode * U)
    DdNode * Cudd_MakeBddFromZddCover(DdManager * manager, DdNode * node)
    int Cudd_zddDagSize(DdNode * p_node)
    double Cudd_zddCountMinterm(DdManager * manager, DdNode * node, int path)
    DdNode * Cudd_zddPortFromBdd(DdManager * manager, DdNode * B)
    DdNode * Cudd_zddPortFromBddNegCof(DdManager * manager, DdNode * B, DdNode * cube)
    DdNode * Cudd_zddPortToBdd(DdManager * manager, DdNode * f)
    DdNode * Cudd_zddPortToBddNegCof(DdManager * manager, DdNode * f, DdNode * cube)
    int Cudd_zddReduceHeap(DdManager * manager, Cudd_ReorderingType heuristic,
                            int minsize)
    bint Cudd_zddShuffleHeap(DdManager * manager, int * permutation)
    DdNode * Cudd_zddIte(DdManager * manager, DdNode * f, DdNode * g, DdNode * h)
    DdNode * Cudd_zddUnion(DdManager * manager, DdNode * P, DdNode * Q)
    DdNode * Cudd_zddIntersect(DdManager * manager, DdNode * P, DdNode * Q)
    DdNode * Cudd_zddDiff(DdManager * manager, DdNode * P, DdNode * Q)
    DdNode * Cudd_zddDiffConst(DdManager * manager, DdNode * P, DdNode * Q)
    DdNode * Cudd_zddSubset1(DdManager * manager, DdNode * P, int var)
    DdNode * Cudd_zddSubset0(DdManager * manager, DdNode * P, int var)
    DdNode * Cudd_zddChange(DdManager * manager, DdNode * P, int var)
    void Cudd_zddSymmProfile(DdManager * manager, int lower, int upper)
    bint Cudd_zddPrintMinterm(DdManager * manager, DdNode * node)
    bint Cudd_zddPrintCover(DdManager * manager, DdNode * node)
    bint Cudd_zddPrintDebug(DdManager * manager, DdNode * f, int n, int pr)
    DdGen * Cudd_zddFirstPath(DdManager * manager, DdNode * f, int ** path)
    char * Cudd_zddCoverPathToString(DdManager * manager, int * path, char * str)
    DdNode * Cudd_zddSupport(DdManager * manager, DdNode * f)
    bint Cudd_zddDumpDot(DdManager * manager, int n, DdNode ** f,
                         char ** inames, char ** onames, FILE * fp)
    MtrNode * Cudd_MakeTreeNode(DdManager * manager, unsigned int low,
                                unsigned int size, unsigned int type)
    MtrNode * Cudd_MakeZddTreeNode(DdManager * manager, unsigned int low,
                                   unsigned int size, unsigned int type)
    double Cudd_CountMinterm(DdManager * manager, DdNode * node, int nvars)
    DdApaNumber Cudd_ApaCountMinterm(const DdManager * manager, DdNode * node,
                                     int nvars, int * digits)
    void Cudd_FreeApaNumber(DdApaNumber number)
    double Cudd_zddCountMinterm(DdManager * manager, DdNode * node, int path)
