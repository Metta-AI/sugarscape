include(joinpath(@__DIR__, "model.jl"))
using BlackBIRDS.DynamicPPL: @model
using LinearAlgebra, DelimitedFiles
const O = BlackBIRDS.Optimisers
const D = BlackBIRDS.Distributions
const V = BlackBIRDS.AdvancedVI
const B = BlackBIRDS.Bijectors
const torch = PyTorchNormalizingFlows.torch

method, output = ARGS[1:2]
epochs = parse(Int, ARGS[3])
@assert method in ["pathwise", "VarGrad"]
mkdir(output)
torch.set_num_threads(1)
Random.seed!(0)
observed = rand(model)
Random.seed!(1)
validation = rand(model)
writedlm(joinpath(output, "observation.csv"), observed, ',')
writedlm(joinpath(output, "validation.csv"), validation, ',')

@model function inference(abm, y)
    p1 ~ D.Uniform(0.0, 1.0)
    m_alpha ~ D.Uniform(0.1, 10.0)
    m_beta ~ D.Uniform(0.1, 10.0)
    w_alpha ~ D.Uniform(0.1, 10.0)
    w_beta ~ D.Uniform(0.1, 10.0)
    y ~ abm([p1, 1 - p1, m_alpha, m_beta, w_alpha, w_beta])
end

struct UnitGradient <: O.AbstractRule end
O.init(::UnitGradient, x) = nothing
function O.apply!(::UnitGradient, state, x, gradient)
    scale = norm(gradient)
    @assert isfinite(scale) && scale > 0
    return state, gradient ./ scale
end

Random.seed!(20261022)
torch.manual_seed(20261022)
problem = inference(model, observed)
flow = make_masked_affine_autoregressive_flow_torch(dim=5, n_layers=4, n_units=32)
transformed = B.transformed(flow, B.inverse(B.bijector(problem)))
initial, reconstruct = O.destructure(transformed)
writedlm(joinpath(output, "initial-parameters.csv"), initial, ',')
objective = method == "pathwise" ?
    V.RepGradELBO(5, entropy=V.MonteCarloEntropy()) : V.ScoreGradELBO(5)
optimizer = O.OptimiserChain(UnitGradient(), O.AdamW(0.0005, (0.9, 0.99), 0.01, 1e-8; couple=true))
best = Ref(Inf)
best_epoch = Ref(0)
started = time()
open(joinpath(output, "epochs.csv"), "w") do io
    println(io, "epoch,training_elbo,validation_loss,gradient_norm,elapsed_seconds")
end
function record_epoch(; stat, state, params, averaged_params, restructure, gradient)
    @assert all(isfinite, params) && all(isfinite, gradient) && isfinite(stat.elbo)
    q = restructure(params)
    saved_rng = copy(Random.default_rng())
    saved_torch = torch.get_rng_state().clone()
    Random.seed!(20261023)
    torch.manual_seed(20261023)
    validation_loss = 0.0
    open(joinpath(output, "validation-samples-$(stat.iteration).csv"), "w") do io
        println(io, "sample,p1,p6,m_alpha,m_beta,w_alpha,w_beta,negative_log_likelihood")
        for sample in 1:5
            x = rand(q)
            physical = [x[1], 1-x[1], x[2:5]...]
            loss = -D.logpdf(model(physical), validation)
            @assert isfinite(loss)
            validation_loss += loss / 5
            println(io, join((sample,physical...,loss), ','))
        end
    end
    copy!(Random.default_rng(), saved_rng)
    torch.set_rng_state(saved_torch)
    writedlm(joinpath(output, "parameters-$(stat.iteration).csv"), params, ',')
    writedlm(joinpath(output, "gradient-$(stat.iteration).csv"), gradient, ',')
    if validation_loss < best[]
        best[] = validation_loss
        best_epoch[] = stat.iteration
        writedlm(joinpath(output, "best-parameters.csv"), params, ',')
    end
    open(joinpath(output, "epochs.csv"), "a") do io
        println(io, join((stat.iteration,stat.elbo,validation_loss,norm(gradient),time()-started), ','))
        flush(io)
    end
    println("EPOCH=$(stat.iteration) METHOD=$method VALIDATION=$validation_loss")
    flush(stdout)
    return (; validation_loss)
end

final, _, stats, _ = V.optimize(
    BlackBIRDS.DynamicPPL.LogDensityFunction(problem), objective, transformed, epochs;
    adtype=BlackBIRDS.AutoZygote(), optimizer, callback=record_epoch, show_progress=false)
@assert length(stats) == epochs
open(joinpath(output, "completion.txt"), "w") do io
    println(io, "method=$method")
    println(io, "epochs=$epochs")
    println(io, "best_epoch=$(best_epoch[])")
    println(io, "best_validation=$(best[])")
    println(io, "elapsed_seconds=$(time()-started)")
end
println("TRAINING_QUALIFICATION_COMPLETE")
