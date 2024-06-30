# This is an example of using the Parareal algorithm to solve the simple 
# initial value problem of du/dt = u with u(0) = u0
# Author: Nathan Chapman
# Date: 6/29/24
using Plots

# FRAMEWORK OF A PROBLEM
"""
    Interval(lb, ub)

An object with lower and upper bounds.
"""
struct Interval
    lb :: Float64
    ub :: Float64
end

"""
    InitialValueProblem(der, initialValue, domain)

An object representing an initial value problem
"""
struct InitialValueProblem
    der :: Function
    initialValue :: Number
    domain :: Interval
end

"""
    partition(domain :: Interval, discretization :: Int)

Partition an interval into a given number of mostly disjoint sub-domains.
"""
function partition(domain :: Interval, discretization :: Int) :: Vector{Interval}
    subdomains = Vector{Interval}(undef, COARSEDISCRETIZATION)
    step       = (domain.ub - domain.lb) / COARSEDISCRETIZATION
    for i in 0:COARSEDISCRETIZATION - 1
        subdomains[i + 1] = Interval(domain.lb + i * step, domain.lb + (i + 1) * step)
    end
    return subdomains
end

# BEGIN DEFINING PROBLEM AT HAND

# begin by defining the initial value problem:
# the derivative function defined in terms of time and the value of the function
function der(t, u)
    return u # this encodes the differential equation du/dt = u
end

const INITIALVALUE = 1
const DOMAIN       = Interval(0, 1)

ivp = InitialValueProblem(der, INITIALVALUE, DOMAIN)

# now that the problem has been defined
# give it to the parareal algorithm

# first we must initialize the algorithm with a coarse solution

# Discretization is the number of sub-domains to use for each time interval
const COARSEDISCRETIZATION = 2^3
const SUBDOMAINS = partition(ivp.domain, COARSEDISCRETIZATION)

# here we define the underlying propagator e.g. euler, RK4, velocity verlet, etc.
"""
    euler(point, slope, step)

The Euler method of numerical integration.
"""
function euler(point, slope, step)
    return point + step * slope
end

function coarsePropagate(domain :: Interval, initialValue :: Float64)
    
end
