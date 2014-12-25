from django.core.exceptions import PermissionDenied

from django.core.urlresolvers import reverse
from django.forms import Textarea, TextInput, FileField, Form
from django.forms.models import modelform_factory
from django.views.generic import View
from extra_views import InlineFormSet
from form_utils.forms import BetterModelForm
from form_utils.widgets import ImageWidget

from events.models import Event, EventImage, Transportation
from news.widgets import EESTECEditor


class EventMixin(View):
    parent_template = "events/event_detail.html"
    form_title = "Please fill in this form"

    def dispatch(self, request, *args, **kwargs):
        subject = Event.objects.get(slug=kwargs['slug'])
        ocs = subject.organizing_committee.all()
        for oc in ocs:
            if request.user in oc.privileged() or request.user.is_superuser or \
                            request.user in subject.organizers.all():
                return super(EventMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_success_url(self):
        return reverse("event", kwargs=self.kwargs)


class EventUpdateForm(BetterModelForm):
    class Meta:
        model = Event
        fieldsets = [
            ('General Information', {'fields': ['name', 'scope', 'category']}),
            ('Dates', {'fields': ['start_date', 'end_date', 'deadline']}),
            ('Additional Information', {'fields': ['participation_fee', 'location']}),
        ]


class TransportForm(BetterModelForm):
    class Meta:
        model = Transportation
        fields = (
            'arrival', 'arrive_by', 'arrival_number', 'departure', 'depart_by',
            'comment')
        widgets = {
            'arrival': TextInput(attrs={'class': 'datetime'}),
            'departure': TextInput(attrs={'class': 'datetime'}),
            'comment': Textarea(attrs={'rows': '1'}),
        }


class UploadEventsForm(Form):
    file = FileField()


class DescriptionForm(BetterModelForm):
    class Meta:
        model = Event
        fields = ('description',)
        widgets = {'description': EESTECEditor(include_jquery=False)}
        #'css': "/static/enet/css/wysiwyg.css"})}

class EventImageInline(InlineFormSet):
    model = EventImage
    form_class = modelform_factory(EventImage, widgets={'image': ImageWidget()})



