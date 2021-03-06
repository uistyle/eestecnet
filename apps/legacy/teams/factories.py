import factory

from apps.legacy.teams.models import Team


__author__ = 'swozn'
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class LegacyTeamFactory(factory.DjangoModelFactory):
    class Meta:
        model = Team

    name = factory.sequence(lambda x: str(x))
    thumbnail = factory.django.ImageField(color="blue")
    description = "description"
    category = "jlc"
    thumbsource = "thumbsource"
    teamstub = "teamstub"
    facebook = "http://www.facebook.com"
    website = "http://www.website.com"
    address = "address"
    lat = 19.0
    lng = 12.0
    founded = 1990
