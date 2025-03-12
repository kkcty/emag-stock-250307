import asyncio
from pathlib import Path

from scraper_utils.utils.browser_util import PersistentContextManager, ResourceType, MS1000


CWD = Path.cwd()


async def main():
    async with PersistentContextManager(
        executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',
        user_data_dir=CWD.joinpath('chrome_data'),
        channel='chrome',
        headless=False,
        abort_res_types=(ResourceType.MEDIA, ResourceType.IMAGE),
        default_navigation_timeout=60 * MS1000,
        default_timeout=60 * MS1000,
    ) as pcm:
        pass


if __name__ == '__main__':
    asyncio.run(main())
