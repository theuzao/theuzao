"""Generate a 3x3 collage with the user's weekly top Last.fm albums."""

import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw


USERNAME = "driptoohard"
GRID_SIZE = 3
TILE_SIZE = 300
OUTPUT = Path(__file__).with_name("lastfm-year.png")
API_URL = "https://ws.audioscrobbler.com/2.0/"


def request_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "theuzao-github-profile/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def top_albums(api_key: str) -> list[dict]:
    query = urllib.parse.urlencode(
        {
            "method": "user.gettopalbums",
            "user": USERNAME,
            "period": "7day",
            "limit": GRID_SIZE * GRID_SIZE,
            "api_key": api_key,
            "format": "json",
        }
    )
    payload = json.loads(request_bytes(f"{API_URL}?{query}"))
    if "error" in payload:
        raise RuntimeError(payload.get("message", "Last.fm API error"))
    return payload.get("topalbums", {}).get("album", [])


def cover_url(album: dict) -> str | None:
    images = album.get("image", [])
    for image in reversed(images):
        url = image.get("#text", "")
        if url:
            return url
    return None


def fallback_tile() -> Image.Image:
    tile = Image.new("RGB", (TILE_SIZE, TILE_SIZE), "#121212")
    draw = ImageDraw.Draw(tile)
    center = TILE_SIZE // 2
    draw.ellipse(
        (center - 38, center - 38, center + 38, center + 38),
        outline="#535353",
        width=5,
    )
    draw.ellipse(
        (center - 7, center - 7, center + 7, center + 7),
        fill="#535353",
    )
    return tile


def album_tile(album: dict) -> Image.Image:
    url = cover_url(album)
    if not url:
        return fallback_tile()
    try:
        image = Image.open(io.BytesIO(request_bytes(url))).convert("RGB")
        return image.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS)
    except (OSError, urllib.error.URLError):
        return fallback_tile()


def generate() -> None:
    api_key = os.environ.get("LASTFM_API_KEY")
    if not api_key:
        raise SystemExit("LASTFM_API_KEY is not configured")

    try:
        albums = top_albums(api_key)
    except Exception as error:
        raise SystemExit(f"Could not fetch Last.fm albums: {type(error).__name__}") from None

    if not albums:
        raise SystemExit(f"No weekly albums found for {USERNAME}")

    size = GRID_SIZE * TILE_SIZE
    collage = Image.new("RGB", (size, size), "#121212")
    for index in range(GRID_SIZE * GRID_SIZE):
        tile = album_tile(albums[index]) if index < len(albums) else fallback_tile()
        x = (index % GRID_SIZE) * TILE_SIZE
        y = (index // GRID_SIZE) * TILE_SIZE
        collage.paste(tile, (x, y))

    collage.save(OUTPUT, "PNG", optimize=True)
    print(f"INFO: generated {OUTPUT.name} with {len(albums)} weekly albums")


if __name__ == "__main__":
    generate()
