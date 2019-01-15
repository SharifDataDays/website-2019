from django.urls import reverse
from django.utils.translation import ugettext as _

from apps.game.models import Competition


def menu(request):
    context = {
        'ai': {
            'navbar': {
                _('Home'): {
                    'dropdown': {
                        _('Main Page'): reverse('intro:index'),
                        _('Introduction'): reverse('intro:index') + '#intro',
                        _('Timeline'): reverse('intro:index') + '#timeline',
                        _('Content'): reverse('intro:index') + '#specials-grid',
                        _('Prizes'): reverse('intro:index') + '#prizes',
                        _('About Us'): reverse('intro:index') + '#about-us',
                        _('Contact Us'): reverse('intro:index') + '#contact-us',
                    }
                },
                _('Access'): {
                    'dropdown': {
                        _('Panel'): reverse('accounts:panel'),
#                        _('Resources'): 'https://aichallenge.sharif.edu/blog/2018/02/05/Server-Client-MapMaker/',
                        _('Blog and Q&A'): '/blog',
#                        _('Staff'): '/staff',
                    }
                },
            },
            'sidebar': {
                _('Home'): {
                    'dropdown': {
                        _('Introduction'): reverse('intro:index') + '#intro',
                        _('Timeline'): reverse('intro:index') + '#timeline',
                        _('Content'): reverse('intro:index') + '#specials-grid',
                        _('Prizes'): reverse('intro:index') + '#prizes',
                        _('Contact Us'): reverse('intro:index') + '#contact-us',
                    }
                },
                _('Blog'): {
                    'dropdown': {
#                        _('FAQ'): reverse('intro:faq'),
                        _('Blog and Q&A'): '/blog',
                    }
                },
#                _('Game'): {
#                    'dropdown': {
#                        _('Panel'): reverse('accounts:panel'),
#                        _('Game Viewer'): '/game/game_viewer',
#                        _('Map Maker'): '/game/map_maker',
#                    }
#                },
                _('Account'): {
                    'dropdown': {}
                },
#                _('Scoreboard'): {
#                    'dropdown': {},
#                },
            }
        }
    }


    if request.user.is_authenticated():
        context['ai']['sidebar'][_('Account')]['dropdown'][_('Logout')] = reverse('accounts:logout')
    else:
        context['ai']['sidebar'][_('Account')]['dropdown'][_('Login')] = reverse('accounts:login')

#    friendly_competitions = Competition.objects.filter(type='friendly')
#    for friendly_competition in friendly_competitions:
#        context['ai']['sidebar'][_('Scoreboard')]['dropdown'][friendly_competition.name] = reverse('game:scoreboard', args=[friendly_competition.id])

#    if request.user.is_authenticated:
#        if request.user.profile.panel_active_teampc:
#            if request.user.profile.panel_active_teampc.challenge.competitions.filter(
#                type='league'
#            ).exists():
#                context['ai']['sidebar'][_('Scoreboard')]['dropdown'][_('League')] = reverse('game:league_scoreboard', args=[
#                            request.user.profile.panel_active_teampc.challenge.id
#                        ])

    return context
