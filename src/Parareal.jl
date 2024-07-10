module Parareal

export euler, verlet                 # integration.jl
export Interval, InitialValueProblem # structs.jl
export parareal                      # Parareal.jl

include("integration.jl")
include("ivp.jl")
include("convergence.jl")
include("discretization.jl")
include("propagation.jl")

"""
    parareal(
        ivp                  :: InitialValueProblem,
        propagator           :: Function,
        coarseDiscretization :: Int,
        fineDiscetization    :: Int
    )

Numerically solve the given initial value problem in parallel using a given
propagator and discretizations.
"""
function parareal(
    ivp                  :: InitialValueProblem,
    propagator           :: Function,
    coarseDiscretization :: Int,
    fineDiscetization    :: Int)
    # Some notes on terminology and consistency
    # IVP.................A structure representing an initial value problem
    #                     consisting of a derivative function, an initial value
    #                     and a domain (see Domain below)
    # Domain..............the interval on which an IVP is defined
    # Subdomain...........a domain that is a subset of another domain
    # Discretized Domain..a vector of points, all of which are in a domain
    # Range...............
    # Discretized Range...a vector of points corresponding to the output of the
    #                     solution function
    # Solution............an ordered pair of the discretized domain and the
    #                     discretized range that satisfies the original IVP
    # Propagator..........a structure consisting of a numerical integrator
    #                     and the number of points on which to evaluate

    # create a bunch of sub-intervals on which to parallelize
    subDomains       = partition(ivp.domain, coarseDiscretization)
    coarsePropagator = Propagator(propagator, coarseDiscretization)
    finePropagator   = Propagator(propagator, fineDiscetization)
    # INITIAL PROPAGATION
    # effectively creating an initial value for each sub-interval
    # same as the end of the loop but with all correctors equal to zero
    discretizedDomain, discretizedRange = propagate(ivp, coarsePropagator)
    # create a bunch of smaller initial value problems that can be solved in parallel
    subProblems = InitialValueProblem.(ivp.der, discretizedRange[1:end-1], subDomains)

    # allocate space
    subSolutionCoarse = similar(subDomains, Vector{Vector{Float64}})
    subSolutionFine   = similar(subDomains, Vector{Vector{Float64}})
    correctors        = similar(discretizedRange)
    # LOOP PHASE
    for iteration in 1:coarseDiscretization # while # TODO: add convergence criterion
        # println("Iteration $iteration")

        # PARALLEL COARSE
        Threads.@threads for i in eachindex(subProblems)
            # println("Coarse subdomain $i is running on thread ", Threads.threadid())
            subSolutionCoarse[i] = propagate(subProblems[i], coarsePropagator)
        end

        # PARALLEL FINE
        Threads.@threads for i in eachindex(subProblems)
            # println("Fine subdomain $i is running on thread ", Threads.threadid())
            subSolutionFine[i] = propagate(subProblems[i], finePropagator)
        end

        # CORRECTORS
        for i in eachindex(subProblems)
            correctors[i] = subSolutionFine[i][2][end] - subSolutionCoarse[i][2][end]
        end
        # CORRECTION PHASE
        _, discretizedRange = propagate(ivp, coarsePropagator, correctors)
        subProblems         = InitialValueProblem.(ivp.der, discretizedRange[1:end-1], subDomains)
    end
    return [discretizedDomain, discretizedRange]
end
end
