using DiffABM, ForwardDiff, DiffResults, Random, SHA
project = "/Users/relh/Code/workspace/sugarscape-diffabm-jmlr"
output = @__DIR__
@assert bytes2hex(sha256(read(joinpath(project,"Manifest.toml")))) == "3b1cdef37a183be5822a4e3032fa3125ad3dee70ec231c387791c036bdbd2f81"
rows = [parse.(Float64, split(line)) for line in readlines(joinpath(project,"scripts/sugar-map.txt"))]
board = reduce(vcat, permutedims.(rows))[:]
@assert length(board) == 2500
function trajectory(theta, seed)
    Random.seed!(seed)
    initializer = RandomAgentInitializer(50, vision_distribution_probs=theta[1:2],
        metabolic_rate_bounds=theta[3:4], wealth_bounds=theta[5:6],
        neighborhood=VonNeumannNeighborhood(), discrete_sampler=DiffABM.ST(), vision_spacing=2)
    params = SugarScapeParams(GeneratedBoard(50,board),initializer,50,100,25,[1.0],10000,DiffABM.GaussianSmoothing(1.0))
    history = abm_run(params)
    return [sum(wealth)/100 for wealth in history[4]]
end
theta = [0.2,0.8,2.0,5.0,5.0,2.0]
for seed in 0:2
    objective = x -> trajectory(x,seed)
    primal = objective(theta)
    config = ForwardDiff.JacobianConfig(objective,theta,ForwardDiff.Chunk{6}())
    result = DiffResults.JacobianResult(primal,theta)
    ForwardDiff.jacobian!(result,objective,theta,config)
    ad_primal=DiffResults.value(result)
    ad=DiffResults.jacobian(result)
    open(joinpath(output,"seed-$(seed).csv"),"w") do stream
        println(stream,"seed,time,primal,ad_primal,g1,g2,g3,g4,g5,g6")
        for time in 1:25
            println(stream,join(vcat([seed,time-1,primal[time],ad_primal[time]],ad[time,:]),","))
        end
    end
    @assert primal == ad_primal
    println("PRIMAL_EQUAL_SEED=",seed);flush(stdout)
end
println("COMPLETE")
