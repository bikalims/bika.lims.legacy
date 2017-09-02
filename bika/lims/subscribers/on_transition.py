import DateTime

def after_transition_handler(instance, event):

    # creation doesn't have a 'transition'
    if event.transition is None:
        return

    now = DateTime.DateTime()
    instance.setModificationDate(now)
