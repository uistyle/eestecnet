from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey
from guardian.shortcuts import assign_perm
from polymorphic import PolymorphicModel

from apps.accounts.models import Account
from common.models import Applicable, Confirmable, Confirmation
from common.util import Reversable


__author__ = 'Sebastian Wozny'
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your models here.
class BaseEvent(Applicable, Reversable):
    """ Model that stores basic information common to all events."""

    owner = ForeignKey('accounts.Account', editable=False)
    @property
    def organizers(self):
        return self.packages.get(name=self.name + '_organizers')

    @property
    def officials(self):
        return self.packages.get(name=self.name + '_officials')

    def save(self, **kwargs):
        """
        When an Event is first created two groups should always be created:
        Official participants and organizers. Organizers need the right to modify the
        event.
        """
        if self.pk:
            result = super(BaseEvent, self).save(**kwargs)
        else:
            result = super(BaseEvent, self).save(**kwargs)
            self.packages.create(name=self.name + '_officials')
            self.packages.create(name=self.name + '_organizers')
            label = self._meta.object_name
            assign_perm('change_' + label.lower(), self.organizers, self)

        return result


class Workshop(BaseEvent):
    """ Workshops as defined in the ROP. """
    pass

class Exchange(BaseEvent):
    """ Exchanges as defined in the ROP ."""
    pass

class Training(BaseEvent):
    """ Training Sessions held by EESTEC Trainers ."""
    pass


class ParticipationConfirmation(Confirmable, Confirmation, object):
    """
    A two stage confirmation that requires the organizers to accept a participant,
    before that participant is able to confirm their participation.
    """

    @property
    def acceptance(self):
        return self.confirmation_set.all()[0]
    def on_confirm(self):
        """
        When a participation is accepted by the organizing committee, the applicant
        should be granted rights to confirm their participation.
        """
        assign_perm('change_participationconfirmation', self.confirmable.user, self)
    def save(self, *args, **kwargs):
        if not self.pk:
            result = super(ParticipationConfirmation, self).save(*args, **kwargs)
            acceptance = Confirmation.objects.create(confirmable=self)
            assign_perm('change_confirmation',
                        self.confirmable.package.applicable.organizers, acceptance)

        else:
            result = super(ParticipationConfirmation, self).save(*args, **kwargs)

        self.confirmable.check_confirm()

        return result
