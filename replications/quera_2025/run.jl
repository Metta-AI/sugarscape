using DiffABM
using Images
using Random
using SHA
using Serialization

project = abspath(ARGS[1])
output = abspath(ARGS[2])
mkdir(output)
@assert bytes2hex(sha256(read(joinpath(project,"Manifest.toml")))) == "3b1cdef37a183be5822a4e3032fa3125ad3dee70ec231c387791c036bdbd2f81"
# Parse the original plain-text landscape without changing the pinned environment.
rows = [parse.(Float64, split(line)) for line in readlines(joinpath(project,"scripts/sugar-map.txt"))]
landscape = reduce(vcat, permutedims.(rows))
board_length = 25
board = Images.imresize(landscape, (board_length,board_length))[:]
params = SugarScapeParams(
    GeneratedBoard(board_length,board),
    RandomAgentInitializer(board_length, vision_distribution_probs=[0.2,0.8],
        metabolic_rate_bounds=[2.0,5.0],wealth_bounds=[5.0,2.0],
        neighborhood=VonNeumannNeighborhood(),discrete_sampler=DiffABM.ST(),vision_spacing=5),
    board_length,100,50,[1.0],10000,DiffABM.GaussianSmoothing(1.0))
open(joinpath(output,"configuration.txt"),"w") do stream
    println(stream,"source_commit=9178eccd56dd352e3515e276239654239f8d3b41")
    println(stream,"grid=25;agents=100;stored_states=50;transitions=49;vision=1,6;probabilities=0.2,0.8")
    println(stream,"metabolism_beta=2,5;wealth_beta=5,2;regeneration=1;smoothing=Gaussian(1);gradient_horizon=10000")
    println(stream,"scope=Original-code forward pilot using calibration parameters; no gradient or calibration verdict")
end
for seed in 0:2
    Random.seed!(seed)
    history = abm_run(params)
    @assert length(history)==6 && all(length(h)==50 for h in history)
    serialize(joinpath(output,"seed-$(seed).jls"),history)
    boards,xs,ys,wealths,alive,occupied = history
    open(joinpath(output,"seed-$(seed)-agents.csv"),"w") do stream
        println(stream,"time,agent,x,y,wealth,alive")
        for time in 1:50, agent in 1:100
            println(stream,join((time-1,agent,xs[time][agent],ys[time][agent],wealths[time][agent],alive[time][agent]),","))
        end
    end
    open(joinpath(output,"seed-$(seed)-cells.csv"),"w") do stream
        println(stream,"time,x,y,sugar,occupied")
        for time in 1:50, x in 1:board_length, y in 1:board_length
            println(stream,join((time-1,x,y,boards[time][x,y],occupied[time][x,y]),","))
        end
    end
    println("COMPLETED_SEED=",seed);flush(stdout)
end
open(joinpath(output,"sha256.txt"),"w") do stream
    for name in sort(readdir(output))
        if endswith(name,".csv") || endswith(name,".jls") || endswith(name,".jl") || name=="configuration.txt"
            println(stream,bytes2hex(sha256(read(joinpath(output,name)))),"  ",name)
        end
    end
end
println("COMPLETE")
