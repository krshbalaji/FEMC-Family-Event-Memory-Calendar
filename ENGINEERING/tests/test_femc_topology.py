import pytest
from ENGINEERING.source.femc.api import FEMCApi
from ENGINEERING.source.femc.models import Confidence, RelationshipType




def test_parent_child_family_topology_resolution():
    api = FEMCApi()

    parent_person = api.identity.create_person("Parent Person")
    parent_account = api.identity.create_account("parent_user", "parent@example.com", parent_person.id)

    child_person = api.identity.create_person("Child Person")
    child_account = api.identity.create_account("child_user", "child@example.com", child_person.id)

    context = api.identity.create_family_context("Parent Child Family", member_ids=[parent_account.id, child_account.id], created_by_id=parent_account.id)
    session = api.create_session(parent_account.id)

    rel = api.create_relationship_for_session(
        session_id=session.session_id,
        source_person_id=parent_person.id,
        target_person_id=child_person.id,
        relationship_type=RelationshipType.PARENT,
        confidence=Confidence.HIGH,
    )

    topology = api.get_family_topology_for_session(session.session_id, context.id)
    assert topology.context.id == context.id
    assert len(topology.members) == 2

    member_person_ids = {m.person.id for m in topology.members if m.person}
    assert parent_person.id in member_person_ids
    assert child_person.id in member_person_ids

    assert len(topology.relationships) == 1
    assert topology.relationships[0].id == rel.id
    assert topology.relationships[0].relationship_type == RelationshipType.PARENT
    assert topology.relationships[0].source_person_id == parent_person.id
    assert topology.relationships[0].target_person_id == child_person.id


def test_partner_and_sibling_family_topology_resolution():
    api = FEMCApi()

    person_a = api.identity.create_person("Partner A")
    account_a = api.identity.create_account("partner_a", "partner_a@example.com", person_a.id)

    person_b = api.identity.create_person("Partner B")
    account_b = api.identity.create_account("partner_b", "partner_b@example.com", person_b.id)

    person_c = api.identity.create_person("Sibling C")
    account_c = api.identity.create_account("sibling_c", "sibling_c@example.com", person_c.id)

    context = api.identity.create_family_context("Multi-Relation Family", member_ids=[account_a.id, account_b.id, account_c.id], created_by_id=account_a.id)
    session = api.create_session(account_a.id)

    partner_rel = api.create_relationship_for_session(
        session_id=session.session_id,
        source_person_id=person_a.id,
        target_person_id=person_b.id,
        relationship_type=RelationshipType.PARTNER,
    )

    sibling_rel = api.create_relationship_for_session(
        session_id=session.session_id,
        source_person_id=person_b.id,
        target_person_id=person_c.id,
        relationship_type=RelationshipType.SIBLING,
    )

    topology = api.get_family_topology_for_session(session.session_id, context.id)
    assert topology.context.id == context.id
    assert len(topology.members) == 3
    assert len(topology.relationships) == 2

    rel_types = {r.relationship_type for r in topology.relationships}
    assert RelationshipType.PARTNER in rel_types
    assert RelationshipType.SIBLING in rel_types


def test_unauthorized_account_cannot_inspect_other_family_topology():
    api = FEMCApi()

    owner_person = api.identity.create_person("Owner")
    owner_account = api.identity.create_account("owner", "owner@example.com", owner_person.id)
    context_a = api.identity.create_family_context("Family A", member_ids=[owner_account.id], created_by_id=owner_account.id)

    outsider_person = api.identity.create_person("Outsider")
    outsider_account = api.identity.create_account("outsider", "outsider@example.com", outsider_person.id)
    api.identity.create_family_context("Family B", member_ids=[outsider_account.id], created_by_id=outsider_account.id)
    outsider_session = api.create_session(outsider_account.id)

    with pytest.raises(PermissionError):
        api.get_family_topology_for_session(outsider_session.session_id, context_a.id)
