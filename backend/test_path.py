"""Test the path progress endpoint."""
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as c:
        r = await c.get("http://127.0.0.1:8000/api/v1/paths/")
        paths = r.json()
        if not paths:
            print("No paths found")
            return
        pid = paths[0]["id"]
        print("Path ID:", pid)

        login = await c.post(
            "http://127.0.0.1:8000/api/v1/auth/login",
            data={"username": "demo@lumina.dev", "password": "demopass123"},
        )
        token = login.json()["access_token"]

        r2 = await c.get(
            f"http://127.0.0.1:8000/api/v1/paths/{pid}",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = r2.json()
        print(f"Path: {data['title']}")
        for lv in data["levels"]:
            print(f"  {lv['level_name']}: unlocked={lv['unlocked']} progress={lv['progress_pct']}%")

asyncio.run(test())
