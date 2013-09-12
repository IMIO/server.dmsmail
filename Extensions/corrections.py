
def correct_ref(self, change=''):
    """
        Correct empty ref number in dmsmail 0.1
    """
    pc = self.portal_catalog
    brains = pc(portal_type='dmsincomingmail', sort_on='created')
    prev_ref = ''
    out = []
    for brain in brains:
        if brain.internal_reference_number is not None:
            prev_ref = brain.internal_reference_number
        else:
            obj = brain.getObject()
            (begin, nb) = prev_ref.split('/')
            nbi = int(nb)
            new_ref = '%s/%d' % (begin, nbi+1)
            out.append("<a href='%s'>%s</a>, %s, %s" % (obj.absolute_url(), obj.Title(), prev_ref, new_ref))
            prev_ref = new_ref
            if change == '1':
                obj.internal_reference_no = prev_ref
                obj.reindexObject()
                out[-1] += " => %s" % obj.Title()
    return '\n<br />'.join(out)
