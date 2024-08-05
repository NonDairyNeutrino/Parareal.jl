# This is an example of using the Parareal algorithm to solve the simple 
# initial value problem of d^2 u / dt^2 = -u with u(0) = u0, u'(0) = v0
# Author: Nathan Chapman
# Date: 7/10/24

using Plots, Distributed
addprocs(2)
@everywhere include("../src/Parareal.jl")
@everywhere using .Parareal

# DEFINE THE SECOND-ORDER INITIAL VALUE PROBLEM
# """
#     acceleration(position :: Float64, velocity :: Float64) :: Float64

# Define the acceleration in terms of the given differential equation.
# """
@everywhere function acceleration(position :: Float64, velocity :: Float64, k = 1) :: Float64
    return -k^2 * position # this encodes the differential equation u''(t) = -u
end

const INITIALPOSITION = 1.
const INITIALVELOCITY = 0.
const DOMAIN          = Interval(0., 2 * pi)
const IVP             = SecondOrderIVP(acceleration, INITIALPOSITION, INITIALVELOCITY, DOMAIN) # second order initial value problem

# DEFINE THE COARSE AND FINE PROPAGATION SCHEMES
const PROPAGATOR           = velocityVerlet
const COARSEDISCRETIZATION = 2^2 * Threads.nthreads()     # 1 region per core
const FINEDISCRETIZATION   = 2^1 * COARSEDISCRETIZATION

const COARSEPROPAGATOR = Propagator(PROPAGATOR, COARSEDISCRETIZATION)
const FINEPROPAGATOR   = Propagator(PROPAGATOR, FINEDISCRETIZATION)

ivpVector = [SecondOrderIVP((x, v) -> acceleration(x, v, k), INITIALPOSITION, INITIALVELOCITY, DOMAIN) for k in 1:nworkers()]
solutionVector = pmap(ivp -> parareal(ivp, COARSEPROPAGATOR, FINEPROPAGATOR), ivpVector, on_error = identity)

# discretizedDomain, discretizedRange = parareal(IVP, COARSEPROPAGATOR, FINEPROPAGATOR)

# plotting
plt = plot(
    solutionVector[1].domain, 
    [sol.range for sol in solutionVector],
    label = ["numeric: $k" for k in 1:nworkers()] |> permutedims,
    title = "coarse: $COARSEDISCRETIZATION, fine: $FINEDISCRETIZATION"
)
plot!(
    solutionVector[1].domain,
    [cos.(n * solutionVector[1].domain) for n in 1:nworkers()],
    label = ["analytic: $k" for k in 1:nworkers()] |> permutedims
)
display(plt)
readline()
# Dots to highlight numeric solution
# scatter!(solutionVector.domain, solution, label = "")