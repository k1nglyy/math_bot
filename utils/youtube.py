import httpx  # Используем асинхронный HTTP-клиент


async def search_video(query: str) -> str:
    try:
        config_path = os.path.join("config", "youtube_api.json")

        with open(config_path) as f:
            API_KEY = json.load(f)['key']

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": f"{query} разбор ОГЭ",
                    "maxResults": 1,
                    "type": "video",
                    "key": API_KEY
                }
            )
            data = response.json()
            return f"https://youtu.be/{data['items'][0]['id']['videoId']}"

    except Exception as e:
        logging.error(f"YouTube API error: {str(e)}")
        return "❌ Не удалось получить видеоразбор"