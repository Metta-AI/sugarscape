"""Build an explicitly conditional inherited-trait extension of the pinned fixed model."""

import argparse
import difflib
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("output", type=Path)
args = parser.parse_args()
original = Path(__file__).with_name("simulate.cpp").read_text()
assert (
    hashlib.sha256(original.encode()).hexdigest()
    == "17803df8b61cfded16718e4895cf574cae77aa514e57a79f99413d7173d49fbc"
)
source = original
changes = [
    ("#include <numeric>", "#include <numeric>\n#include <map>"),
    (
        "    std::uint64_t id = 0;",
        "    std::uint64_t id = 0;\n    int infertility = 1;\n    int birth_cost = 0;",
    ),
    ("if (argc != 7)", "if (argc != 10)"),
    (
        "record-every observations.csv",
        "record-every observations.csv initial-population heterogeneous traits.csv",
    ),
    (
        "    std::mt19937_64 random(seed);",
        """    const int initial_population = std::stoi(argv[7]);
    const int heterogeneous = std::stoi(argv[8]);
    if (initial_population < 1 || initial_population > 2500 || (heterogeneous != 0 && heterogeneous != 1))
        throw std::invalid_argument("Invalid evolutionary parameters");
    if (std::filesystem::exists(argv[9])) throw std::invalid_argument("Trait output already exists");
    std::ofstream traits(argv[9]);
    traits.exceptions(std::ios::failbit | std::ios::badbit);
    traits << "cycle,kind,id,parent_id,infertility,birth_cost,count\\n";
    std::mt19937_64 random(seed);""",
    ),
    (
        "    occupied[initial] = true;",
        """    occupied[initial] = true;
    while (agents.size() < static_cast<std::size_t>(initial_population)) {
        int cell = std::uniform_int_distribution<int>(0, 2499)(random);
        if (occupied[cell]) continue;
        occupied[cell] = true;
        agents.push_back(Agent{cell, 0, 0, true, next_id++});
    }
    for (auto& agent : agents) {
        agent.infertility = heterogeneous ? infertility * std::uniform_int_distribution<int>(1, 10)(random) : infertility;
        agent.birth_cost = heterogeneous ? birth_cost * std::uniform_int_distribution<int>(0, 9)(random) : birth_cost;
        traits << 0 << ",initial," << agent.id << ",-1," << agent.infertility << ',' << agent.birth_cost << ",1\\n";
    }
    const auto record_traits = [&traits](int cycle, const std::vector<Agent>& population) {
        std::map<std::pair<int, int>, int> counts;
        for (const auto& agent : population) ++counts[{agent.infertility, agent.birth_cost}];
        for (const auto& entry : counts)
            traits << cycle << ",joint,-1,-1," << entry.first.first << ',' << entry.first.second << ',' << entry.second << '\\n';
    };
    record_traits(0, agents);""",
    ),
    (
        "std::int64_t metabolism = 0, death_loss = 0;",
        "std::int64_t metabolism = 0, death_loss = 0, birth_loss = 0;",
    ),
    (
        "            auto& agent = agents[index];",
        """            auto& agent = agents[index];
            const int infertility = agent.infertility;
            const int birth_cost = agent.birth_cost;""",
    ),
    (
        "                    agents.push_back(Agent{cell, 0, 0, true, next_id++});",
        """                    const auto parent_id = agent.id;
                    birth_loss += birth_cost;
                    agents.push_back(Agent{cell, 0, 0, true, next_id++, infertility, birth_cost});
                    const auto& child = agents.back();
                    traits << cycle << ",birth," << child.id << ',' << parent_id << ',' << child.infertility << ',' << child.birth_cost << ",1\\n";""",
    ),
    ("births * birth_cost", "birth_loss"),
    (
        "        if (agents.empty()) break;",
        "        record_traits(cycle, agents);\n        if (agents.empty()) break;",
    ),
]
for before, after in changes:
    expected = 2 if before == "births * birth_cost" else 1
    assert source.count(before) == expected, before
    source = source.replace(before, after)
args.output.mkdir(parents=True, exist_ok=False)
(args.output / "simulate_evolution.cpp").write_text(source)
(args.output / "evolution.patch").write_text(
    "".join(
        difflib.unified_diff(
            original.splitlines(True),
            source.splitlines(True),
            fromfile="simulate.cpp",
            tofile="simulate_evolution.cpp",
        )
    )
)
