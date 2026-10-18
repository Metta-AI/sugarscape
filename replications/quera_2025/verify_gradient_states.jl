using Serialization
using DelimitedFiles
using SHA

root, trace, ensemble, output = abspath.(ARGS)
@assert !ispath(output)
state_values = 0
trace_values = 0
gradient_records = 0
aggregate_differences = 0
maximum_aggregate_difference = 0.0
hashes = String[]
for seed in 3:258
    ordinary = deserialize(joinpath(root,"seed-$(seed)-ordinary.jls"))
    differentiated = deserialize(joinpath(root,"seed-$(seed)-ad.jls"))
    @assert length(ordinary) == length(differentiated) == 6
    for component in 1:6
        @assert length(ordinary[component]) == length(differentiated[component]) == 25
        for time in 1:25
            a, b = ordinary[component][time], differentiated[component][time]
            @assert size(a) == size(b)
            @assert length(a) == (component in [1,6] ? 2500 : 100)
            @assert all(isfinite,a) && all(isfinite,b) && a == b
            global state_values += length(a)
        end
    end
    agents = readdlm(joinpath(trace,"seed-$(seed)-agents.csv"),',',Float64;skipstart=1)
    cells = readdlm(joinpath(trace,"seed-$(seed)-cells.csv"),',',Float64;skipstart=1)
    @assert size(agents) == (2500,6) && size(cells) == (62500,5)
    for time in 1:25, agent in 1:100
        row = (time-1)*100+agent
        @assert agents[row,1:2] == [time-1,agent]
        for component in 2:5
            @assert agents[row,component+1] == ordinary[component][time][agent]
            global trace_values += 1
        end
    end
    for time in 1:25, x in 1:50, y in 1:50
        row = (time-1)*2500+(x-1)*50+y
        @assert cells[row,1:3] == [time-1,x,y]
        @assert cells[row,4] == ordinary[1][time][x,y]
        @assert cells[row,5] == ordinary[6][time][x,y]
        global trace_values += 2
    end
    current = readdlm(joinpath(root,"seed-$(seed).csv"),',',Float64;skipstart=1)
    archived = readdlm(joinpath(ensemble,"seed-$(seed).csv"),',',Float64;skipstart=1)
    @assert size(current) == (25,10) && size(archived) == (450,9)
    @assert current[:,1] == fill(seed,25) && current[:,2] == collect(0:24)
    @assert all(isfinite,current)
    for time in 1:25
        wealth = ordinary[4][time]
        @assert current[time,3] == sum(wealth)/100
        @assert current[time,4] == foldl(+,wealth)/100
        global aggregate_differences += current[time,3] != current[time,4]
        global maximum_aggregate_difference = max(maximum_aggregate_difference,abs(current[time,3]-current[time,4]))
    end
    for row in eachrow(archived)
        time, parameter = Int(row[2])+1, Int(row[3])
        @assert row[1] == seed
        @assert current[time,3] == row[5]
        @assert current[time,4+parameter] == row[6]
        global gradient_records += 1
    end
    for name in ["seed-$(seed)-ordinary.jls", "seed-$(seed)-ad.jls", "seed-$(seed).csv"]
        push!(hashes, bytes2hex(sha256(read(joinpath(root,name)))) * "  " * name)
    end
end
@assert state_values == trace_values == 34560000
@assert gradient_records == 115200
mkdir(output)
write(joinpath(output,"sha256.txt"),join(hashes,"\n")*"\n")
write(joinpath(output,"summary.txt"),"seeds=256\nordinary_ad_state_values=$(state_values)\nprior_trace_state_values=$(trace_values)\narchived_gradient_records=$(gradient_records)\nmaximum_state_error=0\naggregate_differences=$(aggregate_differences)\nmaximum_aggregate_difference=$(maximum_aggregate_difference)\naggregate_reductions_exact=true\n")
println(read(joinpath(output,"summary.txt"),String))
