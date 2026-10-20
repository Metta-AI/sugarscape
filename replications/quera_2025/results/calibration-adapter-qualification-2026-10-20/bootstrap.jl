using Pkg
Pkg.develop([
    PackageSpec(path=joinpath(@__DIR__, "blackbirds")),
    PackageSpec(path="/Users/relh/Code/workspace/sugarscape-diffabm-jmlr"),
    PackageSpec(path="/Users/relh/Code/workspace/sugarscape-pytorch-flows-reference")
])
Pkg.instantiate(;allow_autoprecomp=false)
using BlackBIRDS, DiffABM, PyTorchNormalizingFlows, Images
println("COUPLED_PACKAGES_LOADED")
