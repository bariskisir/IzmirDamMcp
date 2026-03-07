import os, httpx, pytz, json
from datetime import datetime
from fastmcp import FastMCP
from unicode_tr import unicode_tr

mcp = FastMCP("IzmirDamMcp")

def turkish_lower(text: str) -> str:
    """Turkish-aware lowercase conversion using unicode_tr library."""
    return unicode_tr(text).lower()

@mcp.tool()
async def get_izmir_dam_status(date: str | None = None, dam_name: str | None = None):
    """Get status for Izmir dams."""
    if not date:
        date = datetime.now(pytz.timezone("Europe/Istanbul")).date().isoformat()
    
    cache_dir = "/tmp/.cache"
    os.makedirs(cache_dir, exist_ok=True)
    cp = os.path.join(cache_dir, f"{date}.json")
    if os.path.exists(cp):
        print(f"Cache hit: {date}")
        with open(cp, "r", encoding="utf-8") as f: data = json.load(f)
    else:
        print(f"API fetch: {date}")
        url = f"https://izsu.gov.tr/api/proxy/DamWaterStatus/WithInfoList?date={date}"
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(url, timeout=15)
                res.raise_for_status()
                data = res.json().get("data", [])
                with open(cp, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {str(e)}"
    
    if dam_name:
        search_query = turkish_lower(dam_name)
        data = [d for d in data if search_query in turkish_lower(d.get("damWellFacility", {}).get("name", ""))]
    return data

if __name__ == "__main__":
    mcp.run()
