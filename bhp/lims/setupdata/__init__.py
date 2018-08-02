# -*- coding: utf-8 -*-
#
# Copyright 2018 Botswana Harvard Partnership (BHP)

from bhp.lims import logger
from bhp.lims.config import PRODUCT_NAME
from bika.lims import api
from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.exportimport.setupdata import WorksheetImporter
from bika.lims.idserver import renameAfterCreation
from bika.lims.interfaces import ISetupDataSetList
from bika.lims.utils import tmpID
from zope.interface import implements


class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname=PRODUCT_NAME)


class Analysis_Specifications(WorksheetImporter):

    def Import(self):
        logger.info("*** Custom import of Analysis Specifications ***")
        for row in self.get_rows(3):
            keyword = row.get('utestid')
            if not keyword:
                logger.warn("No keyword found")
                continue

            query = dict(portal_type="AnalysisService", getKeyword=keyword)
            analysis = api.search(query, 'bika_setup_catalog')
            if not analysis:
                logger.warn("No analysis service found for {}".format(keyword))
                continue
            if len(analysis) > 1:
                logger.warn("More than one service found for {}".format(keyword))
                continue
            analysis = api.get_object(analysis[0])

            # TODO No Sample Type defined in the file, just use Whole Blood
            st_title = row.get('sample_type', 'Whole Blood')
            query = dict(portal_type="SampleType", title=st_title)
            sample_type = api.search(query, 'bika_setup_catalog')
            if not sample_type:
                logger.warn("No sample type found for {}".format(st_title))
                continue
            if len(sample_type) > 1:
                logger.warn("More than one sample type found for {}".format(st_title))
                continue
            sample_type = api.get_object(sample_type[0])

            unit = row.get('utestid_units')
            min_spec = row.get('lln', '')
            max_spec = row.get('uln', '')
            gender = row.get('gender', 'a')
            gender = gender == 'mf' and 'a' or gender
            age_low = row.get('age_low', '')
            if age_low:
                age_low = '{}{}'.format(age_low, row.get('age_low_unit', 'd'))
            age_high = row.get('age_high', '')
            if age_high:
                age_high = '{}{}'.format(age_high, row.get('age_high_unit', 'd'))
            if not age_low and not age_high:
                logger.warn("Cannot create Spec, Age low and high not defined.")
                continue
            max_panic = row.get('panic_high_value', '')
            min_panic = row.get('panic_low_value', '')

            # TODO No Specs title defined in the file, just use sample type's
            specs_title = row.get('title', st_title)
            specs_key = []
            specs_key.append(specs_title)
            if gender:
                str_gender = gender.upper()
                if gender == 'a':
                    str_gender = 'MF'
                specs_key.append(str_gender)
            if age_low and age_high:
                specs_key.append('{} - {}'.format(age_low, age_high))
            elif age_low:
                specs_key.append('({}+)'.format(age_low))
            elif age_high:
                specs_key.append('(-{})'.format(age_high))
            specs_title = ' '.join(specs_key)

            specs_dict = {
                'keyword': analysis.getKeyword(),
                'min': min_spec,
                'max': max_spec,
                'minpanic': min_panic,
                'maxpanic': max_panic,
                'warn_min': '',
                'warn_max': '',
                'hidemin': '',
                'hidemax': '',
                'rangecomments': '',
            }

            query = dict(portal_type='AnalysisSpec', title=specs_title)
            aspec = api.search(query, 'bika_setup_catalog')
            if not aspec:
                # Create a new one
                folder = self.context.bika_setup.bika_analysisspecs
                _id = folder.invokeFactory('AnalysisSpec', id=tmpID())
                aspec = folder[_id]
                aspec.edit(title=specs_title)
                aspec.Schema().getField("Gender").set(aspec, gender)
                aspec.Schema().getField("Agefrom").set(aspec, age_low)
                aspec.Schema().getField("Ageto").set(aspec, age_high)
                aspec.unmarkCreationFlag()
                renameAfterCreation(aspec)

            elif len(aspec) > 1:
                logger.warn("More than one Analysis Specification found for {}"
                            .format(specs_title))
                continue
            else:
                aspec = api.get_object(aspec[0])

            result_range = aspec.Schema().getField('ResultsRange').get(aspec)
            result_range.append(specs_dict)
            aspec.Schema().getField('ResultsRange').set(aspec, result_range)
            aspec.setSampleType(sample_type.UID())
            aspec.reindexObject()
