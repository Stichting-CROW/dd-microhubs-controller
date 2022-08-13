from string import Template

import notifications.telegram

def send_notifications(state_changes):
    for state_change in state_changes:
        if len(state_change.opened) > 0:
            text = get_open_microhub_text(state_change)
            notifications.telegram.send_msg(text, state_change.stop.municipality)
        if len(state_change.closed) > 0:
            text = get_close_microhub_text(state_change)
            notifications.telegram.send_msg(text, state_change.stop.municipality)

def get_open_microhub_text(state_change):
    open_microhub = Template("""
Microhub <strong>[$name_microhub]($url_microhub)</strong> weer <strong>beschikbaar</strong> \n\n $url_microhub
    """
    )
    stop = state_change.stop
    return open_microhub.substitute(name_microhub = stop.name, url_microhub = "https://dashboarddeelmobiliteit.nl/map/zones/" + stop.geography_id,
        modalities = ','.join(state_change.opened))

def get_close_microhub_text(state_change):
    close_microhub = Template("""
Microhub <strong>[$name_microhub]($url_microhub) </strong> \n\n $url_microhub
    """
    )
    stop = state_change.stop
    return close_microhub.substitute(name_microhub = stop.name, url_microhub = "https://dashboarddeelmobiliteit.nl/map/zones/" + stop.geography_id,
        modalities = ','.join(state_change.closed))
