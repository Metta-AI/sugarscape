using BlackBIRDS, DiffABM, PyTorchNormalizingFlows, Images
using Random, Serialization, SHA

output = joinpath(@__DIR__, "qualification-two-channel-runtime-python")
mkdir(output)
source = "/Users/relh/Code/workspace/sugarscape-diffabm-jmlr"
rows = [parse.(Float64, split(line)) for line in readlines(joinpath(source, "scripts/sugar-map.txt"))]
landscape = reduce(vcat, permutedims.(rows))
board = Images.imresize(landscape, (25, 25))[:]
params = SugarScapeParams(
    GeneratedBoard(25, board),
    RandomAgentInitializer(25, vision_distribution_probs=[0.2, 0.8],
        metabolic_rate_bounds=[2.0, 5.0], wealth_bounds=[5.0, 2.0],
        neighborhood=VonNeumannNeighborhood(), discrete_sampler=DiffABM.ST(), vision_spacing=5),
    25, 100, 50, [1.0], 10000, DiffABM.GaussianSmoothing(1.0))
summarizer = history -> permutedims(hcat([sum(w) / length(w) for w in history[4]], [sum(a) / length(a) for a in history[5]]))
model = BlackBIRDS.ABM(parameters=params, ad_backend=BlackBIRDS.AutoForwardDiff(),
    loss=BlackBIRDS.GaussianMMDLoss(w=0.0001, n_samples=2), summarizer=summarizer)
parameters, rebuild = BlackBIRDS.Flux.destructure(model)
@assert parameters == [0.2, 0.8, 2.0, 5.0, 5.0, 2.0]
Random.seed!(0)
history = abm_run(params)
y = summarizer(history)
serialize(joinpath(output, "observation.jls"), history)
boards, xs_state, ys_state, wealths, alive, occupied = history
open(joinpath(output,"seed-0-agents.csv"),"w") do io
    println(io,"time,agent,x,y,wealth,alive")
    for time in 1:50, agent in 1:100
        println(io,join((time-1,agent,xs_state[time][agent],ys_state[time][agent],wealths[time][agent],alive[time][agent]),","))
    end
end
open(joinpath(output,"seed-0-cells.csv"),"w") do io
    println(io,"time,x,y,sugar,occupied")
    for time in 1:50, x in 1:25, y in 1:25
        println(io,join((time-1,x,y,boards[time][x,y],occupied[time][x,y]),","))
    end
end

Random.seed!(0)
@assert rand(model) == y
Random.seed!(20261021)
xs = [rand(model), rand(model)]
Random.seed!(20261021)
value = BlackBIRDS.Distributions.logpdf(model, y)
@assert isfinite(value)
open(joinpath(output, "wealth.csv"), "w") do io
    println(io, "time,observed_wealth,observed_alive,simulation_1_wealth,simulation_1_alive,simulation_2_wealth,simulation_2_alive")
    for t in 1:50
        println(io, join((t-1, y[1,t], y[2,t], xs[1][1,t], xs[1][2,t], xs[2][1,t], xs[2][2,t]), ","))
    end
end
println("NATIVE_LOSS=", value); flush(stdout)
Random.seed!(20261021)
value_ad, gradients = BlackBIRDS.Zygote.withgradient(p -> BlackBIRDS.Distributions.logpdf(rebuild(p), y), parameters)
@assert isfinite(value_ad) && length(only(gradients)) == 6 && all(isfinite, only(gradients))
open(joinpath(output, "loss-and-gradient.csv"), "w") do io
    println(io, "native_loss,ad_loss,p1,p6,m_alpha,m_beta,w_alpha,w_beta")
    println(io, join((value, value_ad, only(gradients)...), ","))
end
Random.seed!(20261021)
open(joinpath(output, "native-jacobians.csv"), "w") do io
    println(io, "simulation,channel,time,value,p1,p6,m_alpha,m_beta,w_alpha,w_beta")
    for sample in 1:2
        sample_value, jacobian = BlackBIRDS.DifferentiationInterface.value_and_jacobian(
            p -> BlackBIRDS.diff_rand(BlackBIRDS.AutoForwardDiff(), rebuild, p),
            BlackBIRDS.AutoForwardDiff(), parameters)
        @assert size(sample_value) == (2,50) && size(jacobian) == (100,6)
        for t in 1:50, channel in 1:2
            println(io, join((sample,channel,t-1,sample_value[channel,t],jacobian[2*(t-1)+channel,:]...), ","))
        end
    end
end
flow = make_masked_affine_autoregressive_flow_torch(dim=6, n_layers=4, n_units=32)
samples = rand(flow, 20)
@assert size(samples) == (6, 20) && all(isfinite, samples)
open(joinpath(output, "flow-samples.csv"), "w") do io
    println(io, "p1,p6,m_alpha,m_beta,w_alpha,w_beta,log_density")
    for i in axes(samples,2)
        density = BlackBIRDS.Distributions.logpdf(flow, samples[:,i])
        @assert isfinite(density)
        println(io, join((samples[:,i]..., density), ","))
    end
end
open(joinpath(output, "scope.txt"), "w") do io
    println(io, "Unchanged author Sugarscape and BlackBIRDS native MMD/AD pipeline; six-dimensional flow sampling. No optimization, prior, posterior, historical loss configuration or paper-completion claim. GaussianMMDLoss(w=0.0001,n_samples=2), mean wealth and alive fraction over all initial agents, plus fixed seeds are declared qualification choices. Author initialization-law discrepancies remain unchanged.")
end
println("COUPLED_NATIVE_LOSS_GRADIENT_FLOW_COMPLETE"); flush(stdout)
