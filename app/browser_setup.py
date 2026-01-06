"""Browser configuration and runtime setup utilities."""

from nodriver import Config, Tab, cdp

from app.observability import get_logger

logger = get_logger(__name__)


def build_browser_config(profile_suffix: str | None = None) -> Config:
    """Build a standard browser configuration for Nodriver.

    This function creates a `Config` object with a predefined set of
    Chromium arguments optimized for headless scraping. An optional
    profile suffix can be provided to isolate browser profiles when
    running multiple concurrent workers.

    Args:
        profile_suffix (str | None): Optional suffix used to create a
            unique user data directory for the browser profile.

    Returns:
        Config: A Nodriver browser configuration instance.
    """
    suffix = f"-{profile_suffix}" if profile_suffix else ""
    return Config(
        headless=True,
        user_data_dir=f"./chrome-profile-fb{suffix}",
        args=[
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-sync",
            "--disable-extensions",
        ],
    )


async def set_mobile_emulation(tab: Tab):
    """Apply mobile device emulation settings to a browser tab.

    This function configures the tab to emulate a mobile-like environment
    by overriding the User-Agent, accepted languages, platform, and
    viewport/device metrics. It is typically used to force mobile layouts
    and mobile-specific behavior on target websites.

    Args:
        tab (Tab): The Nodriver tab instance to configure.
    """
    logger.info("Setting mobile viewport and UA")

    await tab.send(
        cdp.emulation.set_user_agent_override(
            user_agent=(
                "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/18.5 Safari/605.1.15'"
            ),
            accept_language="it-IT,it;q=0.9",
            platform="MacIntel",
        )
    )

    await tab.send(
        cdp.emulation.set_device_metrics_override(
            width=1024,
            height=1366,
            device_scale_factor=2,
            mobile=True,
            screen_orientation=cdp.emulation.ScreenOrientation(
                type_="portraitPrimary",
                angle=0,
            ),
        )
    )


async def enable_network_optimizations(tab: Tab):
    """Enable network optimizations and block unnecessary resources.

    This function enables the Chrome DevTools Network domain and blocks
    the loading of common heavy resources such as images, videos, fonts,
    and known static CDN assets. The goal is to reduce bandwidth usage,
    speed up page loads, and minimize memory/CPU consumption during
    scraping.

    Args:
        tab (Tab): The Nodriver tab instance to configure.
    """
    await tab.send(cdp.network.enable())
    await tab.send(
        cdp.network.set_blocked_ur_ls(
            urls=[
                "*.jpg",
                "*.png",
                "*.webp",
                "*.mp4",
                "*.avi",
                "*.woff",
                "*.woff2",
                "https://static.xx.fbcdn.net/*",
            ]
        )
    )
