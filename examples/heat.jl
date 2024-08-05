# This is an example of using the Parareal algorithm to solve the simple 
# initial value problem of du/dt = u with u(0) = u0
# Author: Nathan Chapman
# Date: 6/29/24

using Plots
using Distributed
addprocs(2)
# when invoking julia with the -p flag, Distributed is
# automatically loaded and scoped
@everywhere include("../src/Parareal.jl")
@everywhere using .Parareal

# DEFINE THE INITIAL VALUE PROBLEM
# the derivative function defined in terms of time and the value of the function
@everywhere function der(t, u, k = 1)
    return k * u # this encodes the differential equation du/dt = u
end
const INITIALVALUE = 1.0
const DOMAIN       = Interval(0., 1.)
# const ivp          = FirstOrderIVP(der, INITIALVALUE, DOMAIN)

# first we must initialize the algorithm with a coarse solution
# Discretization is the number of sub-domains to use for each time interval
const PROPAGATOR           = euler
const COARSEDISCRETIZATION = Threads.nthreads() # 1 region per core
const FINEDISCRETIZATION   = 100

const COARSEPROPAGATOR = Propagator(PROPAGATOR, COARSEDISCRETIZATION)
const FINEPROPAGATOR   = Propagator(PROPAGATOR, FINEDISCRETIZATION)

f(k) = (t, u) -> der(t, u, k)

# discretizedDomain, solution = parareal(ivp, COARSEPROPAGATOR, FINEPROPAGATOR)
ivpVector = [FirstOrderIVP(f(k), INITIALVALUE, DOMAIN) for k in 1:nworkers()]
solutionVector = pmap(ivp -> parareal(ivp, COARSEPROPAGATOR, FINEPROPAGATOR), ivpVector, on_error = identity)
# display(solutionVector)

plot(
    solutionVector[1].domain, 
    [sol.range for sol in solutionVector],
    label = ["numeric: $k" for k in 1:nworkers()] |> permutedims,
    title = "coarse: $COARSEDISCRETIZATION, fine: $FINEDISCRETIZATION"
)
plot!(
    solutionVector[1].domain,
    [exp.(n * solutionVector[1].domain) for n in 1:nworkers()],
    label = ["analytic: $k" for k in 1:nworkers()] |> permutedims
)
# Dots to highlight numeric solution
# scatter!(solutionVector.domain, solution, label = "")