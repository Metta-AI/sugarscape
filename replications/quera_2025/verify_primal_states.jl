using Serialization
root = abspath(ARGS[1])
observations = 0
for seed in 0:2
    ordinary = deserialize(joinpath(root,"seed-$(seed)-ordinary.jls"))
    differentiated = deserialize(joinpath(root,"seed-$(seed)-ad.jls"))
    @assert length(ordinary) == length(differentiated) == 6
    for component in 1:6
        @assert length(ordinary[component]) == length(differentiated[component]) == 25
        for time in 1:25
            a = ordinary[component][time]
            b = differentiated[component][time]
            @assert size(a) == size(b)
            @assert all(isfinite,a) && all(isfinite,b)
            @assert a == b
            global observations += length(a)
        end
    end
end
@assert observations == 405000
println("Exactly equal ordinary/AD state values: ",observations)
