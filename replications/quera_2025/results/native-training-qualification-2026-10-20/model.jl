using BlackBIRDS, DiffABM, PyTorchNormalizingFlows, Images
using Random, Serialization, SHA

struct PairedForwardDiff <: BlackBIRDS.ADTypes.AbstractADType end

function paired_value_and_jacobian(f, parameters)
    initial_rng = copy(Random.default_rng())
    fixed_randomness = x -> begin
        copy!(Random.default_rng(), initial_rng)
        f(x)
    end
    prototype = fixed_randomness(parameters)
    result = BlackBIRDS.DiffResults.JacobianResult(prototype, parameters)
    BlackBIRDS.ForwardDiff.jacobian!(result, fixed_randomness, parameters)
    return BlackBIRDS.DiffResults.value(result), BlackBIRDS.DiffResults.jacobian(result)
end

function BlackBIRDS.ChainRulesCore.rrule(::typeof(BlackBIRDS.diff_rand), ad::PairedForwardDiff, rebuild, parameters)
    value, jacobian = paired_value_and_jacobian(p -> BlackBIRDS.diff_rand(ad, rebuild, p), parameters)
    pullback = tangent -> (BlackBIRDS.ChainRulesCore.NoTangent(), BlackBIRDS.ChainRulesCore.NoTangent(),
                          BlackBIRDS.ChainRulesCore.NoTangent(), jacobian' * tangent[:])
    return value, pullback
end

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
model = BlackBIRDS.ABM(parameters=params, ad_backend=PairedForwardDiff(),
    loss=BlackBIRDS.GaussianMMDLoss(w=0.0001, n_samples=2), summarizer=summarizer)
parameters, rebuild = BlackBIRDS.Flux.destructure(model)
@assert parameters == [0.2, 0.8, 2.0, 5.0, 5.0, 2.0]
