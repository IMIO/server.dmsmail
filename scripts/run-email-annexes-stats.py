# -*- coding: utf-8 -*-

from imio.helpers.security import setup_logger
# from imio.helpers.xhtml import object_link
from imio.pyutils.utils import safe_encode

import csv
import logging
import os
import tempfile


def stddev(data, ddof=0):
    """
    https://stackoverflow.com/a/27758326
    Calculates the population standard deviation
    by default; specify ddof=1 to compute the sample
    standard deviation.
    """
    def mean(data):
        """Return the sample arithmetic mean of data."""
        n = len(data)
        if n < 1:
            raise ValueError('mean requires at least one data point')
        return sum(data) / float(n)

    def _ss(data):
        """Return sum of square deviations of sequence data."""
        c = mean(data)
        ss = sum((x - c)**2 for x in data)
        return ss
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss / (n - ddof)
    return pvar**0.5


portal = obj  # noqa
setup_logger()
logger = logging.getLogger('catalog:')

pc = portal.portal_catalog
brains = pc.unrestrictedSearchResults(portal_type='dmsincoming_email')

results = []
stats = {
    'email_count': 0,
    'appendix_count': 0,
    'total_size': 0,
}
for brain in brains:
    email = brain.getObject()
    stats['email_count'] += 1
    for appendix in email.objectValues():
        if appendix.portal_type != 'dmsappendixfile':
            continue
        stats['appendix_count'] += 1
        size = appendix.file.getSize() // 1024
        stats['total_size'] += size
        results.append({
            "email_title": safe_encode(email.Title()),
            "filename": safe_encode(appendix.file.filename),
            "extension": safe_encode(os.path.splitext(appendix.file.filename)[-1]),
            "size (kB)": size,
            # "url": object_link(appendix)
            "url": "{}/{}".format(portal.absolute_url(), "/view")
        })

if results:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
        w = csv.DictWriter(temp_file, ["email_title", "filename", "extension", "size (kB)", "url"])
        w.writeheader()
        w.writerows(results)

        temp_file_path = temp_file.name

    logger.info('Email count: {}'.format(stats['email_count']))
    logger.info('Appendix count: {}'.format(stats['appendix_count']))
    logger.info('Average number of appendixes per email: {:.1f}'.format(float(stats['appendix_count'])
                                                                        / stats['email_count']))
    logger.info('Average size of appendix: {} kB'.format(stats['total_size'] / stats['appendix_count']))
    # logger.info('Average size of appendix per email: {} kB'.format(stats['total_size'] / stats['email_count']))
    try:
        logger.info('Standard deviation of appendix size: {} kb'.format(stddev([r['size (kB)'] for r in results])))
    except ValueError:
        logger.info('Too few samples to compute standard deviation')
    logger.info('Detailed CSV file created at {}'.format(temp_file_path))
else:
    logger.info('No results found')
