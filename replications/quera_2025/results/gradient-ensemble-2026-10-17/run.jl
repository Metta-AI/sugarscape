using DiffABM, ForwardDiff, Random, SHA
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
for seed in 3:258
    primal = trajectory(theta,seed)
    objective = x -> trajectory(x,seed)
    config = ForwardDiff.JacobianConfig(objective, theta, ForwardDiff.Chunk{6}())
    ad = ForwardDiff.jacobian(objective,theta,config)
    @assert all(isfinite,ad)
    open(joinpath(output,"seed-$(seed).csv"),"w") do stream
        println(stream,"seed,time,parameter,step,primal,ad,plus,minus,fd")
        for step in [0.001,0.01,0.05], parameter in 1:6
            plus_theta=copy(theta); minus_theta=copy(theta)
            plus_theta[parameter]+=step; minus_theta[parameter]-=step
            plus=trajectory(plus_theta,seed); minus=trajectory(minus_theta,seed)
            for time in 1:25
                fd=(plus[time]-minus[time])/(2*step)
                println(stream,join((seed,time-1,parameter,step,primal[time],ad[time,parameter],plus[time],minus[time],fd),","))
            end
            flush(stream)
        end
    end
    println("COMPLETED_SEED=",seed); flush(stdout)
end
println("COMPLETE")
