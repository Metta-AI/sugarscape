include(joinpath(@__DIR__, "model.jl"))
using BlackBIRDS.DynamicPPL: @model
using DelimitedFiles
const D = BlackBIRDS.Distributions
const O = BlackBIRDS.Optimisers
const B = BlackBIRDS.Bijectors
const torch = PyTorchNormalizingFlows.torch

root = @__DIR__
@assert isfile(joinpath(root, "optimization-terminal.json"))
output = joinpath(root, "predictive")
mkdir(output)
torch.set_num_threads(1)
Random.seed!(0)
observation = rand(model)
writedlm(joinpath(output, "observation.csv"), observation, ',')
@assert read(joinpath(output, "observation.csv")) == read(joinpath(root, "pathwise", "observation.csv"))

@model function inference(abm, y)
    p1 ~ D.Uniform(0.0, 1.0)
    m_alpha ~ D.Uniform(0.1, 10.0)
    m_beta ~ D.Uniform(0.1, 10.0)
    w_alpha ~ D.Uniform(0.1, 10.0)
    w_beta ~ D.Uniform(0.1, 10.0)
    y ~ abm([p1, 1 - p1, m_alpha, m_beta, w_alpha, w_beta])
end

Random.seed!(20261022)
torch.manual_seed(20261022)
problem = inference(model, observation)
flow = make_masked_affine_autoregressive_flow_torch(dim=5, n_layers=4, n_units=32)
transformed = B.transformed(flow, B.inverse(B.bijector(problem)))
initial, reconstruct = O.destructure(transformed)
for method in ["pathwise", "vargrad"]
    stored = vec(readdlm(joinpath(root, method, "initial-parameters.csv"), ',', Float32))
    @assert initial == stored
end

for distribution in ["prior", "pathwise", "vargrad", "truth"]
    if distribution == "prior"
        prior_rng = Random.Xoshiro(20261026)
        draws = hcat([vcat(rand(prior_rng, D.Uniform(0, 1)),
            [rand(prior_rng, D.Uniform(0.1, 10)) for _ in 1:4]) for _ in 1:1000]...)
    elseif distribution == "truth"
        draws = repeat([0.2, 2.0, 5.0, 5.0, 2.0], 1, 1000)
    else
        best = vec(readdlm(joinpath(root, distribution, "best-parameters.csv"), ',', Float32))
        posterior = reconstruct(best)
        torch.manual_seed(20261024)
        draws = hcat([rand(posterior) for _ in 1:1000]...)
    end
    @assert size(draws) == (5, 1000) && all(isfinite, draws)
    open(joinpath(output, "$distribution-parameters.csv"), "w") do io
        println(io, "sample,p1,p6,m_alpha,m_beta,w_alpha,w_beta")
        for i in 1:1000
            x = draws[:,i]
            @assert 0 < x[1] < 1 && all(0.1 .< x[2:5] .< 10)
            println(io, join((i,x[1],1-x[1],x[2:5]...), ','))
        end
    end
    open(joinpath(output, "$distribution-trajectories.csv"), "w") do io
        println(io, "sample,seed,time,mean_wealth,alive_fraction")
        for i in 1:1000
            x = draws[:,i]
            Random.seed!(9999+i)
            trajectory = rand(model([x[1], 1-x[1], x[2:5]...]))
            @assert size(trajectory) == (2,50) && all(isfinite, trajectory)
            for t in 1:50
                println(io, join((i,9999+i,t-1,trajectory[1,t],trajectory[2,t]), ','))
            end
        end
    end
    println("PREDICTIVE_DISTRIBUTION_COMPLETE=$distribution")
    flush(stdout)
end
println("FULL_PREDICTIVE_COMPLETE")
