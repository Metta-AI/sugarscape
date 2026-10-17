"""Explicit experimental correction: one resource balance per group hierarchy."""

import math

import organization

native_find_trader = organization.rules.find_trader


def shared_accumulations(self, meta):
    root = meta
    ancestry = set()
    reverse = meta.model.ml.reverse_groups
    while root.unique_id in reverse and reverse[root.unique_id]["trades"]:
        assert root.unique_id not in ancestry, "Cyclic group hierarchy"
        ancestry.add(root.unique_id)
        parents = reverse[root.unique_id]["trades"]
        assert len(parents) == 1, "Multiple resource-owning parents"
        root = meta.model.ml.groups[next(iter(parents))]
    pending = [root]
    groups, members = {}, {}
    while pending:
        group = pending.pop()
        assert group.unique_id not in groups, "Repeated group in hierarchy"
        groups[group.unique_id] = group
        for child in group.sub_agents.values():
            if child.type == "group":
                pending.append(child)
            else:
                assert child.type == "agent"
                members[child.unique_id] = child
    assert members
    balances = {
        id(agent.accumulations): agent.accumulations for agent in members.values()
    }
    if len(balances) == 1:
        pool = next(iter(balances.values()))
    else:
        pool = {
            key: math.fsum(float(value[key]) for value in balances.values())
            for key in [1, 2]
        }
    assert all(math.isfinite(float(value)) for value in pool.values())
    for agent in members.values():
        agent.accumulations = pool
    for group in groups.values():
        group.policy.accumulations = pool
    return pool


def external_traders(self, agent, meta):
    return [
        partner
        for partner in native_find_trader(self, agent, meta)
        if partner.accumulations is not agent.accumulations
    ]


organization.rules.calc_accumulations = shared_accumulations
organization.rules.find_trader = external_traders
