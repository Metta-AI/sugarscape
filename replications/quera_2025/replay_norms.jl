using LinearAlgebra, DelimitedFiles, SHA

native, epoch_file, destination = ARGS
@assert !ispath(destination)
lines = readlines(epoch_file)
@assert split(lines[1], ',') == [
    "epoch", "training_elbo", "validation_loss", "gradient_norm", "elapsed_seconds",
]
@assert length(lines) == 5001
println("Julia ", VERSION, "; ", BLAS.get_config())
open(destination, "w") do output
    println(output, "epoch,native_float32_norm,recorded_float32_norm,float64_norm,gradient_sha256")
    for (epoch, line) in enumerate(lines[2:end])
        fields = split(line, ',')
        @assert parse(Int, fields[1]) == epoch
        path = joinpath(native, "gradient-$epoch.csv")
        gradient = vec(readdlm(path, Float32))
        @assert length(gradient) == 19114 && all(isfinite, gradient)
        actual = norm(gradient)
        recorded = parse(Float32, fields[4])
        @assert actual == recorded "Native Float32 norm mismatch at epoch $epoch"
        @assert isfinite(actual) && actual > 0
        reference = norm(Float64.(gradient))
        println(output, join((epoch, actual, recorded, reference, bytes2hex(sha256(read(path)))), ','))
        if epoch % 500 == 0
            flush(output)
            println("verified_norms=$epoch")
            flush(stdout)
        end
    end
end
println("ALL_5000_FLOAT32_NORMS_EXACT")
