// Specification-based fixed-parameter model from Stevenson (2021), Appendix A.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <numeric>
#include <map>
#include <random>
#include <stdexcept>
#include <vector>

struct Agent {
    int cell;
    int wealth = 0;
    int age = 0;
    bool alive = true;
    std::uint64_t id = 0;
    int infertility = 1;
    int birth_cost = 0;
};

int main(int argc, char** argv) {
    if (argc != 10) throw std::invalid_argument("Usage: simulate seed infertility birth-cost cycles record-every observations.csv initial-population heterogeneous traits.csv");
    const auto seed = std::stoull(argv[1]);
    const int infertility = std::stoi(argv[2]);
    const int birth_cost = std::stoi(argv[3]);
    const int cycles = std::stoi(argv[4]);
    const int record_every = std::stoi(argv[5]);
    if (infertility < 1 || birth_cost < 0 || cycles < 1 || record_every < 1) throw std::invalid_argument("Invalid parameters");
    if (std::filesystem::exists(argv[6])) throw std::invalid_argument("Observation output already exists");
    std::ofstream observations(argv[6]);
    observations.exceptions(std::ios::failbit | std::ios::badbit);
    observations.precision(17);
    observations << "cycle,kind,agent_id,count,wealth,mean_age\n";
    const int initial_population = std::stoi(argv[7]);
    const int heterogeneous = std::stoi(argv[8]);
    if (initial_population < 1 || initial_population > 2500 || (heterogeneous != 0 && heterogeneous != 1))
        throw std::invalid_argument("Invalid evolutionary parameters");
    if (std::filesystem::exists(argv[9])) throw std::invalid_argument("Trait output already exists");
    std::ofstream traits(argv[9]);
    traits.exceptions(std::ios::failbit | std::ios::badbit);
    traits << "cycle,kind,id,parent_id,infertility,birth_cost,count\n";
    std::mt19937_64 random(seed);
    std::array<int, 2500> resource;
    resource.fill(4);
    std::array<bool, 2500> occupied{};
    const int initial = std::uniform_int_distribution<int>(0, 2499)(random);
    std::vector<Agent> agents{{initial}};
    std::uint64_t next_id = 1;
    occupied[initial] = true;
    while (agents.size() < static_cast<std::size_t>(initial_population)) {
        int cell = std::uniform_int_distribution<int>(0, 2499)(random);
        if (occupied[cell]) continue;
        occupied[cell] = true;
        agents.push_back(Agent{cell, 0, 0, true, next_id++});
    }
    for (auto& agent : agents) {
        agent.infertility = heterogeneous ? infertility * std::uniform_int_distribution<int>(1, 10)(random) : infertility;
        agent.birth_cost = heterogeneous ? birth_cost * std::uniform_int_distribution<int>(0, 9)(random) : birth_cost;
        traits << 0 << ",initial," << agent.id << ",-1," << agent.infertility << ',' << agent.birth_cost << ",1\n";
    }
    const auto record_traits = [&traits](int cycle, const std::vector<Agent>& population) {
        std::map<std::pair<int, int>, int> counts;
        for (const auto& agent : population) ++counts[{agent.infertility, agent.birth_cost}];
        for (const auto& entry : counts)
            traits << cycle << ",joint,-1,-1," << entry.first.first << ',' << entry.first.second << ',' << entry.second << '\n';
    };
    record_traits(0, agents);
    std::array<std::array<int, 24>, 2500> visible{};
    for (int cell = 0; cell < 2500; ++cell) {
        int index = 0;
        for (int distance = 1; distance <= 6; ++distance) {
            visible[cell][index++] = (cell / 50) * 50 + (cell % 50 + distance) % 50;
            visible[cell][index++] = (cell / 50) * 50 + (cell % 50 + 50 - distance) % 50;
            visible[cell][index++] = ((cell / 50 + distance) % 50) * 50 + cell % 50;
            visible[cell][index++] = ((cell / 50 + 50 - distance) % 50) * 50 + cell % 50;
        }
    }
    std::cout << "cycle,population,wealth,mean_age,gini,landscape,births,deaths,growth,metabolism,death_loss,birth_loss,conservation_error\n";
    for (int cycle = 1; cycle <= cycles; ++cycle) {
        std::int64_t before = std::accumulate(resource.begin(), resource.end(), std::int64_t{0});
        for (const auto& agent : agents) before += agent.wealth;
        const auto existing = agents.size();
        std::vector<std::size_t> order(existing);
        std::iota(order.begin(), order.end(), 0);
        std::shuffle(order.begin(), order.end(), random);
        int births = 0, deaths = 0;
        std::int64_t metabolism = 0, death_loss = 0, birth_loss = 0;
        for (auto index : order) {
            auto& agent = agents[index];
            const int infertility = agent.infertility;
            const int birth_cost = agent.birth_cost;
            ++agent.age;
            int maximum = resource[agent.cell];
            int nearest = 0;
            std::vector<int> candidates{agent.cell};
            for (int position = 0; position < 24; ++position) {
                const int cell = visible[agent.cell][position];
                if (occupied[cell]) continue;
                const int distance = position / 4 + 1;
                if (resource[cell] > maximum || (resource[cell] == maximum && distance < nearest)) {
                    maximum = resource[cell]; nearest = distance; candidates.clear();
                }
                if (resource[cell] == maximum && distance == nearest) candidates.push_back(cell);
            }
            occupied[agent.cell] = false;
            agent.cell = candidates[std::uniform_int_distribution<std::size_t>(0, candidates.size() - 1)(random)];
            occupied[agent.cell] = true;
            agent.wealth += resource[agent.cell];
            resource[agent.cell] = 0;
            if (agent.wealth < 3) {
                death_loss += agent.wealth;
                agent.alive = false;
                occupied[agent.cell] = false;
                ++deaths;
                continue;
            }
            agent.wealth -= 3;
            metabolism += 3;
            if (agent.age >= 1 && agent.wealth >= birth_cost &&
                std::uniform_int_distribution<int>(1, infertility)(random) == 1) {
                std::vector<int> empty;
                for (int direction = 0; direction < 4; ++direction) {
                    int cell = visible[agent.cell][direction];
                    if (!occupied[cell]) empty.push_back(cell);
                }
                if (!empty.empty()) {
                    int cell = empty[std::uniform_int_distribution<std::size_t>(0, empty.size() - 1)(random)];
                    agent.wealth -= birth_cost;
                    occupied[cell] = true;
                    const auto parent_id = agent.id;
                    birth_loss += birth_cost;
                    agents.push_back(Agent{cell, 0, 0, true, next_id++, infertility, birth_cost});
                    const auto& child = agents.back();
                    traits << cycle << ",birth," << child.id << ',' << parent_id << ',' << child.infertility << ',' << child.birth_cost << ",1\n";
                    ++births;
                }
            }
        }
        agents.erase(std::remove_if(agents.begin(), agents.end(), [](const Agent& a) { return !a.alive; }), agents.end());
        std::int64_t growth = 0;
        for (auto& amount : resource) if (amount < 4) { ++amount; ++growth; }
        const auto landscape = std::accumulate(resource.begin(), resource.end(), std::int64_t{0});
        std::int64_t wealth = 0, ages = 0;
        std::vector<int> wealths;
        for (const auto& agent : agents) { wealth += agent.wealth; ages += agent.age; wealths.push_back(agent.wealth); }
        const auto error = landscape + wealth - before - growth + metabolism + death_loss + birth_loss;
        if (error != 0) throw std::logic_error("Resource conservation failed");
        if (agents.size() != existing + births - deaths) throw std::logic_error("Population balance failed");
        if (cycle % record_every == 0 || cycle == 1 || cycle == cycles || agents.empty()) {
            // Observe a copy of indices; sorting must not change activation or random draws.
            std::vector<std::size_t> ranked(agents.size());
            std::iota(ranked.begin(), ranked.end(), 0);
            const auto elite_count = (agents.size() + 9) / 10;
            std::partial_sort(ranked.begin(), ranked.begin() + elite_count, ranked.end(),
                [&agents](std::size_t left, std::size_t right) {
                    if (agents[left].wealth != agents[right].wealth) return agents[left].wealth > agents[right].wealth;
                    return agents[left].id < agents[right].id;
                });
            std::int64_t elite_age = 0, elite_wealth = 0;
            for (std::size_t i = 0; i < elite_count; ++i) {
                elite_age += agents[ranked[i]].age;
                elite_wealth += agents[ranked[i]].wealth;
            }
            observations << cycle << ",elite,-1," << elite_count << ',' << elite_wealth << ','
                         << (elite_count == 0 ? 0 : static_cast<double>(elite_age) / elite_count) << '\n';
            for (const auto& agent : agents) {
                if (agent.id < 30) observations << cycle << ",founder," << agent.id << ",1,"
                                                << agent.wealth << ',' << agent.age << '\n';
            }
            std::sort(wealths.begin(), wealths.end());
            double weighted = 0;
            for (std::size_t i = 0; i < wealths.size(); ++i) weighted += (i + 1.0) * wealths[i];
            const double n = agents.size();
            const double gini = wealth == 0 ? 0 : 2 * weighted / (n * wealth) - (n + 1) / n;
            std::cout.precision(17);
            std::cout << cycle << ',' << agents.size() << ',' << wealth << ',' << (n == 0 ? 0 : ages / n)
                      << ',' << gini << ',' << landscape << ',' << births << ',' << deaths << ',' << growth
                      << ',' << metabolism << ',' << death_loss << ',' << birth_loss << ',' << error << '\n';
        }
        record_traits(cycle, agents);
        if (agents.empty()) break;
    }
}
