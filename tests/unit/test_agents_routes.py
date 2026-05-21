"""Agents APIルートのテスト"""
import pytest


class TestListAgents:

    def test_list_agents(self, client):
        resp = client.get("/api/v1/agents")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_contains_expected_fields(self, client):
        resp = client.get("/api/v1/agents")
        if len(resp.json()) > 0:
            agent = resp.json()[0]
            assert "id" in agent
            assert "name" in agent
            assert "enabled" in agent


class TestGetAgent:

    def test_get_existing(self, client):
        agents = client.get("/api/v1/agents").json()
        if agents:
            agent_id = agents[0]["id"]
            resp = client.get(f"/api/v1/agents/{agent_id}")
            assert resp.status_code == 200
            assert resp.json()["id"] == agent_id

    def test_get_nonexistent(self, client):
        resp = client.get("/api/v1/agents/nonexistent-agent")
        assert resp.status_code == 404
