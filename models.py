# -*- coding: UTF-8 -*-
"""
Models for Event_Log. 

Copyright (c) 2009 Nicholas H.Tollervey (http://ntoll.org/contact)

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in
the documentation and/or other materials provided with the
distribution.
* Neither the name of ntoll.org nor the names of its
contributors may be used to endorse or promote products
derived from this software without specific prior written
permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.contrib.auth.models import User
import django.dispatch
import datetime

############
# Exceptions
############

class UnableToLogEvent(Exception):
    """
    To be raised if unable to log an event 
    """

#########
# Signals
#########

# Fired when an event is logged
event_logged = django.dispatch.Signal()

###########
# Constants
###########

# Timezone representation taken from the hCalendar creator:
# http://microformats.org/code/hcalendar/creator
TIMEZONE = (
        ('-12:00', _('-12 (IDLW)')),
        ('-11:00', _('-11 (NT)')),
        ('-10:00', _('-10 (HST)')),
        ('-09:00', _('-9 (AKST)')),
        ('-08:00', _('-8 (PST/AKDT)')),
        ('-07:00', _('-7 (MST/PDT)')),
        ('-06:00', _('-6 (CST/MDT)')),
        ('-05:00', _('-5 (EST/CDT)')),
        ('-04:00', _('-4 (AST/EDT)')),
        ('-03:45', _('-3:45')),
        ('-03:30', _('-3:30')),
        ('-03:00', _('-3 (ADT)')),
        ('-02:00', _('-2 (AT)')),
        ('-01:00', _('-1 (WAT)')),
        ('Z', _('+0 (GMT/UTC)')),
        ('+01:00', _('+1 (CET/BST/IST/WEST)')),
        ('+02:00', _('+2 (EET/CEST)')),
        ('+03:00', _('+3 (MSK/EEST)')),
        ('+03:30', _('+3:30 (Iran)')),
        ('+04:00', _('+4 (ZP4/MSD)')),
        ('+04:30', _('+4:30 (Afghanistan)')),
        ('+05:00', _('+5 (ZP5)')),
        ('+05:30', _('+5:30 (India)')),
        ('+06:00', _('+6 (ZP6)')),
        ('+06:30', _('+6:30 (Burma)')),
        ('+07:00', _('+7 (WAST)')),
        ('+08:00', _('+8 (WST)')),
        ('+09:00', _('+9 (JST)')),
        ('+09:30', _('+9:30 (Central Australia)')),
        ('+10:00', _('+10 (AEST)')),
        ('+11:00', _('+11 (AEST(summer))')),
        ('+12:00', _('+12 (NZST/IDLE)')),
        )

########
# Models
########
class EventGroup(models.Model):
    """
    Allows you to define groups of events.
    
    Examples might include grouping by type, such as: meetings, deadlines, 
    reviews, assessments

    Alternatively, this can be used to indicate belonging to some long-term 
    series of events such as: project-x, workflow-y, procedure-z
    """
    name = models.CharField(
            _('Event Type Name'),
            max_length=256
            )
    description = models.TextField(
            _('Description'),
            blank=True
            )

    def __unicode__(self):
        return self.name

class EventHistory(models.Model):
    """
    Represents instances in time, or durations of time that log represent an 
    event.

    For single points in time just use the "start" field. For a period of time
    also use the "end" field.
    """
    title = models.CharField(
            _('Title'),
            max_length=256
            )
    description = models.TextField(
            _('Description'),
            blank=True
            )
    location = models.CharField(
            _('Location'),
            max_length=256,
            blank=True
            )
    url = models.URLField(
            _('URL'),
            verify_exists=False,
            blank=True
            )
    start = models.DateTimeField(_('Start'))
    end = models.DateTimeField(
            _('End'),
            null=True,
            blank=True
            )
    timezone = models.CharField(
            _('Timezone'),
            max_length=8,
            blank=True,
            choices=TIMEZONE,
            help_text=_("Hour(s) from GMT")
            )
    attendees = models.ManyToManyField(
            User,
            related_name='events',
            )
    types = models.ManyToManyField(
            EventType,
            related_name='events'
            )
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
            User,
            related_name='events_created'
            )

    def __unicode__(self):
        if self.end:
            date = u"%s - %s"%(self.start.strftime("%c"), self.end.strftime("%c"))
        else:
            date = self.start.strftime("%c")
        return u"%s (%s)"%(self.title, date)

    class Meta:
        ordering = ['-start', '-end', '-created_on']
        verbose_name = _('Event History')
        verbose_name_plural = _('Event Histories')
