using DiffABM
using DelimitedFiles
using Random
using SHA
using Serialization

# Buffer one CSV at a time to avoid a pipe write for every scalar field.
function compressed_csv(writer, path)
    buffer = IOBuffer()
    writer(buffer)
    open(pipeline(`gzip -n -c`, stdout=path), "w") do stream
        write(stream, take!(buffer))
    end
end

project = abspath(ARGS[1])
output = abspath(ARGS[2])
ensemble = abspath(ARGS[3])
profile = ARGS[4]
@assert profile in ["baseline", "perturbed"]
seeds = parse(Int, ARGS[5]):parse(Int, ARGS[6])
@assert first(seeds) >= 3 && last(seeds) <= 258
cases = profile == "baseline" ? [(seed, 0, 0.0, 0) for seed in seeds] :
    [(seed, parameter, step, direction) for seed in seeds for step in [0.001, 0.01, 0.05] for parameter in 1:6 for direction in [-1, 1]]
mkdir(output)
@assert bytes2hex(sha256(read(joinpath(project,"Manifest.toml")))) == "3b1cdef37a183be5822a4e3032fa3125ad3dee70ec231c387791c036bdbd2f81"
# Parse the original plain-text landscape without changing the pinned environment.
rows = [parse.(Float64, split(line)) for line in readlines(joinpath(project,"scripts/sugar-map.txt"))]
landscape = reduce(vcat, permutedims.(rows))
board_length = 50
board = landscape[:]
@assert length(board) == 2500
open(joinpath(output,"configuration.txt"),"w") do stream
    println(stream,"source_commit=9178eccd56dd352e3515e276239654239f8d3b41")
    println(stream,"grid=50;agents=100;stored_states=25;transitions=24;vision=1,3;probabilities=0.2,0.8")
    println(stream,"metabolism_beta=2,5;wealth_beta=5,2;regeneration=1;smoothing=Gaussian(1);gradient_horizon=10000")
    println(stream,"scope=$(profile) gradient-ensemble seeds$(first(seeds)):$(last(seeds)); independent realized-movement replay; no exact published calibration claim")
end
# Trace passive activation orders and initial parameters; retain native step code.
source = read(joinpath(project, "src/SugarScape.jl"), String)
step_source = split(split(source, "function sugarscape_abm_step!(")[2], "\nstruct SugarScapeParams")[1]
step_source = "function sugarscape_abm_step!(" * step_source
@eval DiffABM const replication_orders = Vector{Int}[]
@eval DiffABM const replication_initial = Any[]
step_source = replace(step_source,
    "    order = sample(1:length(agents), length(agents), replace = false)" =>
    "    isempty(replication_orders) && append!(replication_initial, agents)\n    order = sample(1:length(agents), length(agents), replace = false)\n    push!(replication_orders, copy(order))")
fingerprints = Dict{Tuple{String,Int},String}()
open(joinpath(output,"cases.csv"),"w") do stream
    println(stream,"case,seed,parameter,step,direction")
    for (seed, parameter, step, direction) in cases
        name = "seed-$(seed)-p$(parameter)-h$(step)-d$(direction)"
        println(stream,join((name,seed,parameter,step,direction),","))
    end
end
open(joinpath(output,"passive-parity.csv"),"w") do parity
println(parity,"case,seed,component,observations,sha256")
for mode in ["ordinary", "traced"]
    if mode == "traced"
        Base.include_string(DiffABM, step_source, "passive-order-trace.jl")
    end
for (seed, parameter, step, direction) in cases
    name = "seed-$(seed)-p$(parameter)-h$(step)-d$(direction)"
    theta = [0.2,0.8,2.0,5.0,5.0,2.0]
    if profile == "perturbed"
        theta[parameter] += direction * step
    end
params = SugarScapeParams(
    GeneratedBoard(board_length,board),
    RandomAgentInitializer(board_length, vision_distribution_probs=theta[1:2],
        metabolic_rate_bounds=theta[3:4],wealth_bounds=theta[5:6],
        neighborhood=VonNeumannNeighborhood(),discrete_sampler=DiffABM.ST(),vision_spacing=2),
    board_length,100,25,[1.0],10000,DiffABM.GaussianSmoothing(1.0))

    empty!(DiffABM.replication_orders)
    empty!(DiffABM.replication_initial)
    Random.seed!(seed)
    history = Base.invokelatest(abm_run, params)
    for component in 1:6
        buffer = IOBuffer()
        serialize(buffer, history[component])
        digest = bytes2hex(sha256(take!(buffer)))
        if mode == "ordinary"
            fingerprints[(name,component)] = digest
        else
            @assert fingerprints[(name,component)] == digest
            println(parity,join((name,seed,component,sum(length,history[component]),digest),","))
        end
    end
    if mode == "ordinary"
        continue
    end
    archived = readdlm(joinpath(ensemble,"seed-$(seed).csv"), ',', Float64; skipstart=1)
    @assert size(archived) == (450,9)
    for row in eachrow(archived)
        @assert row[1] == seed
        if profile == "baseline"
            @assert row[5] == sum(history[4][Int(row[2])+1])/100
        elseif row[3] == parameter && row[4] == step
            @assert row[direction == 1 ? 7 : 8] == sum(history[4][Int(row[2])+1])/100
        end
    end
    compressed_csv(joinpath(output,"$(name)-orders.csv.gz")) do stream
        println(stream,"transition,position,agent")
        for (transition, order) in enumerate(DiffABM.replication_orders), (position, agent) in enumerate(order)
            println(stream,join((transition,position,agent),","))
        end
    end
    compressed_csv(joinpath(output,"$(name)-parameters.csv.gz")) do stream
        println(stream,"agent,metabolism,vision_i,vision_j,mask")
        for (index, agent) in enumerate(DiffABM.replication_initial)
            for i in axes(agent.vision_matrix,1), j in axes(agent.vision_matrix,2)
                println(stream,join((index,agent.metabolic_rate,i,j,agent.vision_matrix[i,j]),","))
            end
        end
    end
    @assert length(history)==6 && all(length(h)==25 for h in history)
    boards,xs,ys,wealths,alive,occupied = history
    compressed_csv(joinpath(output,"$(name)-agents.csv.gz")) do stream
        println(stream,"time,agent,x,y,wealth,alive")
        for time in 1:25, agent in 1:100
            println(stream,join((time-1,agent,xs[time][agent],ys[time][agent],wealths[time][agent],alive[time][agent]),","))
        end
    end
    compressed_csv(joinpath(output,"$(name)-cells.csv.gz")) do stream
        println(stream,"time,x,y,sugar,occupied")
        for time in 1:25, x in 1:board_length, y in 1:board_length
            println(stream,join((time-1,x,y,boards[time][x,y],occupied[time][x,y]),","))
        end
    end
    println("COMPLETED_CASE=",name);flush(stdout)
end
end
end
open(joinpath(output,"sha256.txt"),"w") do stream
    for name in sort(readdir(output))
        if (endswith(name,".csv") || endswith(name,".csv.gz")) || endswith(name,".jls") || endswith(name,".jl") || name=="configuration.txt"
            println(stream,bytes2hex(sha256(read(joinpath(output,name)))),"  ",name)
        end
    end
end
println("COMPLETE")
