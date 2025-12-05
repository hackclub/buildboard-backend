from dataclasses import dataclass
from enum import Enum


class UTMCampaign(str, Enum):
    POSTER = "poster"
    WELCOME_EMAIL = "welcome_email"
    NEWSLETTER = "newsletter"
    SLACK = "slack"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"


@dataclass
class UTMConfig:
    source: str
    medium: str
    campaign: str


UTM_CONFIGS: dict[UTMCampaign, UTMConfig] = {
    UTMCampaign.POSTER: UTMConfig(
        source="instagram",
        medium="qr_code",
        campaign="poster",
    ),
    UTMCampaign.WELCOME_EMAIL: UTMConfig(
        source="email",
        medium="transactional",
        campaign="welcome",
    ),
    UTMCampaign.NEWSLETTER: UTMConfig(
        source="email",
        medium="newsletter",
        campaign="weekly_digest",
    ),
    UTMCampaign.SLACK: UTMConfig(
        source="slack",
        medium="message",
        campaign="referral",
    ),
    UTMCampaign.TWITTER: UTMConfig(
        source="twitter",
        medium="social",
        campaign="referral",
    ),
    UTMCampaign.INSTAGRAM: UTMConfig(
        source="instagram",
        medium="social",
        campaign="story",
    ),
}


def get_utm_config(campaign: UTMCampaign) -> UTMConfig:
    return UTM_CONFIGS[campaign]
